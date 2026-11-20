"""Check scoped selectors against the real nested navigation templates, offline."""
from pathlib import Path
import json, sys
import struct

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy

out=Path(sys.argv[1]).resolve()
m=json.loads((out/'manifest.json').read_text('utf8'))
tx=json.loads((out/'transaction.json').read_text('utf8'))
game=Path(tx['game']); W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'; S='ui-styles_assets_default.bundle'
skin_mode='--skin' in sys.argv
bundle_objects={}
for n,p in [(W,out/'game'/W),(G,game/G),(S,out/('skin' if skin_mode else 'game')/S),('common',game/'ui-styles_assets_common.bundle')]:
    bundle_objects[n]={o.path_id:o for o in UnityPy.load(str(p)).objects}
guid_objects={}
for n in [W,G]:
    oo=bundle_objects[n];meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
    for guid,entry in meta['m_Container']:
        if entry['asset']['m_FileID']==0:
            guid_objects.setdefault(guid,[]).append((n,entry['asset']['m_PathID']))
cache={}
def tree(n,pid):
    if (n,pid) not in cache:cache[n,pid]=bundle_objects[n][pid].read_typetree()
    return cache[n,pid]

def template(guid):
    for n,pid in guid_objects.get(guid,[]):
        d=tree(n,pid)
        if 'inlineSheet' in d:return n,pid
    return None

nodes=[];missing=set()
def expand(n,pid,parent=None,stack=()):
    if (n,pid) in stack:return
    d=tree(n,pid);rr={r['rid']:r for r in d['references']['RefIds']}
    aliases={a['alias']:a['path'] for a in d['m_Usings']}
    sheet=tree(n,d['inlineSheet']['m_PathID'])
    def walk(rid,p):
        rec=rr[rid]['data'];sd=rr.get(rec.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        if 'm_FullTypeName' not in rec:
            for c in rec.get('m_Children',[]):walk(c['rid'],p)
            return
        typ=rec['m_FullTypeName'].rsplit('.',1)[-1]
        if typ=='UXML':
            for c in rec['m_Children']:walk(c['rid'],p)
            return
        classes=set(rec.get('m_Classes',[]))
        if typ=='SIGradient':classes.add('sigradient')
        if typ=='SIText':classes.add('sitext')
        idx=rec.get('m_RuleIndex',-1);inline=sheet['m_Rules'][idx]['m_Properties'] if idx>=0 else []
        node={'type':typ or 'TemplateContainer','name':sd.get('name',''),'classes':classes,
              'parent':p,'template':d['m_Name'],'rid':rid,'sheet':sheet,'inline':inline}
        nodes.append(node)
        alias=sd.get('templateId')
        if alias and alias!='StandardTextTooltip':
            target=template(aliases.get(alias,''))
            if target:expand(*target,node,stack+((n,pid),))
            else:missing.add((d['m_Name'],alias))
        for c in rec.get('m_Children',[]):walk(c['rid'],node)
    roots=[r['rid'] for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.UXML']
    assert len(roots)==1
    walk(roots[0],parent)

nav=next(o for o in bundle_objects[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PrimaryNavigationBar')
expand(W,nav.path_id)
sheet=next(o.read_typetree() for o in bundle_objects[S].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
first=m['verification']['appended_scoped_rules'][0]['index']
new_rules=sheet['m_Rules'][first:]
native=[]
for bn in [S,'common']:
    for ob in bundle_objects[bn].values():
        if ob.type.name!='MonoBehaviour':continue
        d=ob.read_typetree()
        for i,r in enumerate(d.get('m_Rules',[])):
            if bn==S and ob.path_id==-1868520061851585845 and i>=first:continue
            if any(p['m_Id'] in [65536,196610,458752] or p['m_CustomName'] in ['--start-colour','--end-colour'] for p in r['m_Properties']):
                native.append((d,r))

def ancestry(node):
    result=[]
    while node is not None:result.append(node);node=node['parent']
    return result

def simple(node,sel,state):
    for p in sel['m_Parts']:
        typ,v=p['m_Type'],p['m_Value']
        if typ==1:continue
        if typ==2 and node['type']!=v:return False
        if typ==3 and v not in node['classes']:return False
        if typ==6 and node['name']!=v:return False
        if typ==4 and v not in state:return False
        if typ not in [1,2,3,4,6]:return False
    return True

def matches(node,sel,state):
    sequence=sel['m_Selectors']
    def at(current,index):
        if current is None or not simple(current,sequence[index],state):return False
        if index==0:return True
        relation=sequence[index]['m_PreviousRelationship']
        if relation==1:return at(current['parent'],index-1)
        assert relation==2,relation
        return any(at(a,index-1) for a in ancestry(current)[1:])
    return at(node,len(sequence)-1)

def resolved(sh,prop):
    handles=prop['m_Values']
    if len(handles)!=1:return None
    h=handles[0];pool={2:'floats',4:'colors'}
    return sh[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else None

def applied(node,state):
    values={}
    for rule in new_rules:
        specificity=max((s['m_Specificity'] for s in rule['m_ComplexSelectors'] if matches(node,s,state)),default=-1)
        if specificity<0:continue
        for prop in rule['m_Properties']:
            key=prop['m_CustomName'] or prop['m_Id']
            if specificity>=values.get(key,(-1,None))[0]:values[key]=(specificity,resolved(sheet,prop))
    return values

black={'r':0.,'g':0.,'b':0.,'a':1.};white={'r':1.,'g':1.,'b':1.,'a':1.}
ink=lambda n:any('fm27-fixed-nav-ink' in a['classes'] for a in ancestry(n))
cont=lambda n:any(a['name']=='ContinueButton' for a in ancestry(n))
badge=lambda n:any(a['name'] in ['ClubIcon','NationIcon'] or a['template'] in ['ClubIcon','NationIcon'] for a in ancestry(n))
states=[{'enabled'},{'enabled','hover'},{'enabled','active'},{'enabled','checked'},{'disabled'}]
text_nodes=[n for n in nodes if ink(n) and n['type']=='SIText']
gradient_nodes=[n for n in nodes if cont(n) and n['type']=='SIGradient']
button_text=[n for n in nodes if cont(n) and n['type']=='SIText']
badge_nodes=[n for n in nodes if badge(n)]
icons=[n for n in nodes if ink(n) and (any(c.startswith(('nd-','ui-concepts-','game-concepts-transfer_')) for c in n['classes']) or 'portal-image' in n['classes']) and n['type']!='SIText']
assert text_nodes and len(gradient_nodes)==2 and button_text and badge_nodes
assert icons
def color(code):
    return dict(zip(['r','g','b','a'],[struct.unpack('<f',struct.pack('<f',int(code[i:i+2],16)/255))[0] for i in [0,2,4]]+[1.]))
checks=0
for state in states:
    for n in text_nodes:
        assert applied(n,state).get(65536,(None,None))[1]==black,('Not black',n['template'],n['name'],state)
    for n in button_text:
        assert applied(n,state).get(65536,(None,None))[1]==white,('Not white',n['name'],state)
    for n in icons:
        assert applied(n,state).get(196610,(None,None))[1]==black,('Icon not black',n['template'],n['name'],n['classes'],state)
    for n in gradient_nodes:
        values=applied(n,state)
        assert values['--start-colour'][1]==color('35C6E8') and values['--end-colour'][1]==color('078BC4')
        assert 458767 not in values, 'Ordinary-nav gradient hiding leaked into continue button'
    for n in badge_nodes:
        assert not applied(n,state),('Badge affected',n['template'],n['name'])
    # Confirm appended colors win over all matching native stylesheet rules.
    for n in text_nodes+gradient_nodes+button_text+icons:
        new=applied(n,state)
        wanted=[65536] if n['type']=='SIText' else ['--start-colour','--end-colour'] if n['type']=='SIGradient' else [196610]
        for key in wanted:
            for p in n['inline']:
                if (p['m_CustomName'] or p['m_Id'])==key:
                    assert resolved(n['sheet'],p)==new[key][1],('Conflicting inline color',n['template'],n['name'],key)
            for sh,r in native:
                if not any((p['m_CustomName'] or p['m_Id'])==key for p in r['m_Properties']):continue
                weight=max((s['m_Specificity'] for s in r['m_ComplexSelectors'] if matches(n,s,state)),default=-1)
                assert weight<new[key][0],('Native style can override palette',n['template'],n['name'],key,weight,new[key][0])
            checks+=1

# The same selectors must match nothing in a separately instantiated second row.
start=len(nodes)
secondary=next(o for o in bundle_objects[W].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='SecondaryNavigationBar')
expand(W,secondary.path_id)
for n in nodes[start:]:assert not applied(n,{'enabled','hover','active','checked'}),('Second-row leak',n['name'])
result={'passed':True,'validation':'Offline template/selector checks, not in-game rendering',
        'navigation_nodes_expanded':start,'ordinary_text_nodes_black':len(text_nodes),
        'functional_icons_black':len(icons),'style_base':'skin' if skin_mode else 'game',
        'continue_text_nodes_white':len(button_text),'native_gradients_lake_blue':len(gradient_nodes),
        'badge_nodes_unaffected':len(badge_nodes),'secondary_nodes_unaffected':len(nodes)-start,
        'states':['normal','hover','pressed','checked','disabled'],'cascade_checks':checks,
        'unexpanded_dynamic_templates':sorted(missing),'runtime_verified':False}
(out/('selector-verification-skin.json' if skin_mode else 'selector-verification.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False))
