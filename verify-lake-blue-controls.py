"""Offline checks of real templates, stylesheet cascade, and protected UI roles."""
from pathlib import Path
import ast, copy, json, struct, sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]).resolve();tag='skin' if '--skin' in sys.argv else 'game'
m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
folder=Path(tx[tag]);G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
S='ui-styles_assets_default.bundle';C='ui-styles_assets_common.bundle'
VTAS=sorted({p.name for p in Path(tx['game']).glob('*visualtree*.bundle')}|{G,W})
ACTION='fm27-lake-action';GRAD='fm27-lake-action-gradient'
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
engine=ast.parse((R/'verify-primary-navigation-palette.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in engine.body if isinstance(n,ast.FunctionDef) and n.name in ['ancestry','simple','matches']],type_ignores=[]),'<native-selector-matcher>','exec'))

def color(code):
    return dict(zip(['r','g','b','a'],[struct.unpack('<f',struct.pack('<f',int(code[i:i+2],16)/255))[0] for i in [0,2,4]]+[1.]))
LEFT=color('35C6E8');RIGHT=color('078BC4');WHITE=color('FFFFFF');BLACK=color('000000')
states=[({'enabled'},(LEFT,RIGHT)),({'enabled','hover'},(color('50D2EE'),color('119DD5'))),
        ({'enabled','active'},(color('24AFD1'),color('067BAE'))),({'disabled'},(LEFT,RIGHT))]
objects={};oldobjects={};trees={};guidmap={}
for name in VTAS+[S,C]:
    p=out/tag/name if (out/tag/name).exists() else folder/name
    if not p.exists():p=Path(tx['game'])/name
    objects[name]={o.path_id:o for o in UnityPy.load(str(p)).objects}
    backup=out/('backup-'+tag)/name
    original=backup if backup.exists() else folder/name
    if not original.exists():original=Path(tx['game'])/name
    oldobjects[name]={o.path_id:o for o in UnityPy.load(str(original)).objects}
    if name not in VTAS:continue
    meta=next(o.read_typetree() for o in objects[name].values() if o.type.name=='AssetBundle')
    for guid,entry in meta['m_Container']:
        if entry['asset']['m_FileID']==0:guidmap.setdefault(guid,[]).append((name,entry['asset']['m_PathID']))

def tree(bn,pid):
    if (bn,pid) not in trees:trees[bn,pid]=objects[bn][pid].read_typetree()
    return trees[bn,pid]
def named(bn,name):return next(o.path_id for o in objects[bn].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def target(guid):
    for bn,pid in guidmap.get(guid,[]):
        if 'inlineSheet' in tree(bn,pid):return bn,pid
    return None

sheets=[]
for bn in [C,S]:
    source=[o.read_typetree() for o in objects[bn].values() if o.type.name=='MonoBehaviour']
    sheets.extend(d for d in source if 'm_Rules' in d and d['m_Name']!='AlwaysAppliedStyleSheet')
    sheets.extend(d for d in source if d.get('m_Name')=='AlwaysAppliedStyleSheet')
defs={};rules=[]
for sh in sheets:
    for r in sh['m_Rules']:
        for p in r['m_Properties']:
            if p['m_Id']==-1:defs[p['m_CustomName']]=(sh,p)
        rules.append((sh,r))
def value(sh,p,seen=()):
    hs=p['m_Values']
    if len(hs)==1:
        h=hs[0]
        return sh[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h
    if len(hs)>=3 and hs[0]['m_ValueType']==10:
        key=sh['strings'][hs[2]['valueIndex']]
        if key in defs and key not in seen:return value(*defs[key],seen+(key,))
    return None

# Index by the final selector to keep full cascade checks bounded on large sheets.
index={}
for order,(sh,r) in enumerate(rules):
    for sel in r['m_ComplexSelectors']:
        part=next((p for p in sel['m_Selectors'][-1]['m_Parts'] if p['m_Type'] in [6,3,2]),None)
        key=(part['m_Type'],part['m_Value']) if part else (1,'*')
        index.setdefault(key,[]).append((order,sh,r,sel))
def applied(n,state):
    result={};candidates=[]
    for key in [(1,'*'),(2,n['type']),(6,n['name'])]+[(3,c) for c in n['classes']]:candidates.extend(index.get(key,[]))
    for order,sh,r,sel in candidates:
        if not matches(n,sel,state):continue
        for p in r['m_Properties']:
            key=p['m_CustomName'] or p['m_Id'];weight=(sel['m_Specificity'],order)
            if weight>=result.get(key,((-1,-1),None))[0]:result[key]=(weight,value(sh,p))
    for p in n['inline']:
        result[p['m_CustomName'] or p['m_Id']]=((1000000,0),value(n['sheet'],p))
    return result
def prop(n,key,state):
    for a in ancestry(n) if key==65536 else [n]:
        v=applied(a,state).get(key)
        if v is not None:return v[1]
    return None

nodes=[];missing=set()
def expand(bn,pid,parent=None,stack=()):
    if (bn,pid) in stack:return
    d=tree(bn,pid);rr={r['rid']:r for r in d['references']['RefIds']};aliases={a['alias']:a['path'] for a in d['m_Usings']}
    sh=tree(bn,d['inlineSheet']['m_PathID']) if d['inlineSheet']['m_PathID'] else {'m_Rules':[]}
    def walk(rid,p):
        a=rr[rid].get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        if 'm_FullTypeName' not in a:
            for c in a.get('m_Children',[]):walk(c['rid'],p)
            return
        typ=a['m_FullTypeName'].rsplit('.',1)[-1]
        if typ=='UXML':
            for c in a.get('m_Children',[]):walk(c['rid'],p)
            return
        cls=set(a.get('m_Classes',[]))
        if typ=='SIGradient':cls.add('sigradient')
        if typ=='SIText':cls.add('sitext')
        idx=a.get('m_RuleIndex',-1)
        n={'type':typ or 'TemplateContainer','name':sd.get('name',''),'classes':cls,'parent':p,
           'doc':(bn,pid),'rid':rid,'sheet':sh,'inline':sh['m_Rules'][idx]['m_Properties'] if idx>=0 else [],'data':sd}
        nodes.append(n)
        alias=sd.get('templateId')
        if alias and alias!='StandardTextTooltip':
            dest=target(aliases.get(alias,''))
            if dest:expand(*dest,n,stack+((bn,pid),))
            else:missing.add((d['m_Name'],alias))
        for c in a.get('m_Children',[]):walk(c['rid'],n)
    walk(d['m_VisualTree']['rid'],parent)

checks=0;button_count=0;gradient_count=0;text_count=0;icon_count=0;expected_buttons=0
for path,report in m['verification']['bundle_changes'].items():
    if Path(path).parent!=folder:continue
    bn=Path(path).name
    if bn not in VTAS:continue
    for item in report['templates']:
        expected_buttons+=len(item['buttons'])
        start=len(nodes);expand(bn,int(item['path_id']));local=nodes[start:]
        buttons=[n for n in local if n['doc']==(bn,int(item['path_id'])) and n['rid'] in item['buttons']]
        assert len(buttons)==len(item['buttons'])
        for btn in buttons:
            button_count+=1
            descendants=[n for n in local if any(a is btn for a in ancestry(n))]
            gradients=[n for n in descendants if GRAD in n['classes']]
            texts=[n for n in descendants if n['type']=='SIText']
            icons=[n for n in descendants if n['name'] in ['leading-icon','trailing-icon','primary-icon-image'] or any(c in n['classes'] for c in ['ui-concepts-tick_small','ui-concepts-chevron-right_small','ui-concepts-chevron-left_small','ui-concepts-continue_medium','ui-concepts-person_small'])]
            assert gradients,(item['name'],btn['name'],'No gradient')
            for state,ends in states:
                for grad in gradients:
                    assert prop(grad,'--start-colour',state)==ends[0] and prop(grad,'--end-colour',state)==ends[1],('Gradient mismatch',item['name'],btn['name'],state,prop(grad,'--start-colour',state),prop(grad,'--end-colour',state))
                    if 'disabled' in state:assert abs(prop(grad,458767,state)-.25)<1e-6
                    checks+=1
                if 'enabled' in state:
                    for n in texts:
                        assert prop(n,65536,state)==WHITE,('Label not white',item['name'],n['name'],state,prop(n,65536,state));checks+=1
                    for n in icons:
                        assert prop(n,196610,state)==WHITE,('Icon not white',item['name'],n['name'],state,prop(n,196610,state));checks+=1
            gradient_count+=len(gradients);text_count+=len(texts);icon_count+=len(icons)

# Verify the supplied load/save flows against their actual nested templates.
flow_checks=[]
for bn,name in [(G,'LoadGameBottomBar'),(G,'SaveGameBottomBar'),(G,'LoadGameLoadingScreen'),(G,'ApplicationProgressPanel'),(W,'SavingInProgressPanel')]:
    pid=named(bn,name);start=len(nodes);expand(bn,pid);local=nodes[start:]
    for n in local:
        if n['type']=='SIText' and {'modal-text-primary','colours-brand-foundation-horizon'}.intersection(n['classes']):
            assert prop(n,65536,{'enabled'})==LEFT,(name,n['name'],'Emphasis not lake blue');checks+=1
        if n['type']=='SIProgressBar':
            assert value(*defs['--data-progress-indicator-foreground'])==LEFT
            # Native serialized progress values, min/max and update bindings are unchanged.
            old=oldobjects[n['doc'][0]][n['doc'][1]].read_typetree();orr={r['rid']:r for r in old['references']['RefIds']}
            olddata=orr[orr[n['rid']]['data']['m_SerializedData']['rid']]['data'];assert n['data']==olddata
            checks+=1
    flow_checks.append({'template':name,'nodes':len(local)})

# Existing fixed gray/black header must survive global palette rules.
start=len(nodes);expand(W,named(W,'PrimaryNavigationBar'));nav=nodes[start:]
main=next(n for n in nav if n['name']=='MainNav');assert prop(main,458752,{'enabled'})==color('E7E7E7')
for state,ends in states:
    for n in nav:
        chain=ancestry(n)
        if any('fm27-fixed-nav-ink' in a['classes'] for a in chain) and n['type']=='SIText':
            assert prop(n,65536,state)==BLACK,('Header text regression',n['name']);checks+=1
        if GRAD in n['classes'] and any(a['name']=='ContinueButton' for a in chain):
            assert prop(n,'--start-colour',state)==ends[0] and prop(n,'--end-colour',state)==ends[1],('Header button gradient regression',state)
            checks+=1

# Protected roles and decorative rules are compared directly, without treating
# equal purple RGB values as authorization to change semantic or background roles.
protected_rules=0
for bn in [S,C]:
    for pid,ob in oldobjects[bn].items():
        if ob.type.name!='MonoBehaviour':continue
        old=ob.read_typetree()
        if 'm_Rules' not in old:continue
        new=objects[bn][pid].read_typetree()
        for i,r in enumerate(old['m_Rules']):
            if any(any(x in json.dumps(sel) for x in ['injury','fatigue','sharpness','linear-ranges','communication-feedback-negative','communication-feedback-positive','brand-theme','colours-base-purple','colours-base-pink']) for sel in r['m_ComplexSelectors']):
                # Dedicated custom variables may share the :root rule; check each
                # other property rather than accepting a whole root rewrite.
                for p in r['m_Properties']:
                    if p['m_CustomName'] in ['--modal-text-primary','--data-progress-indicator-foreground','--buttons-primary-surface-default','--buttons-primary-surface-hover']:continue
                    assert p in new['m_Rules'][i]['m_Properties'],('Protected role changed',old['m_Name'],i)
                protected_rules+=1
assert button_count==expected_buttons and button_count>=90 and gradient_count>=button_count,(button_count,expected_buttons,gradient_count)
result={'passed':True,'style_base':tag,'validation':'Offline native-template and stylesheet cascade checks; no runtime rendering',
    'primary_buttons':button_count,'gradient_layers':gradient_count,'white_labels':text_count,'white_icons':icon_count,
    'palette_checks':checks,'protected_semantic_and_brand_rules':protected_rules,'sample_flows':flow_checks,
    'progress_values_and_bindings_unchanged':True,'top_gray_black_regression_passed':True,'unexpanded_templates':sorted(missing),'runtime_verified':False}
(out/('controls-verification-'+tag+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False))
