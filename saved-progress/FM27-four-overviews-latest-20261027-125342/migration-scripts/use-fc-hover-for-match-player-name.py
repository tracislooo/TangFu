from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={p:(p/W).read_bytes() for p in [GAME,SKIN]};assert before[GAME]==before[SKIN]
env=UnityPy.load(before[GAME]);obs={o.path_id:o for o in env.objects}
hashes={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in obs.items()}
oldwrite=TypeTreeHelper.write_value
helpers=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def named(name):
    a=[o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name];assert len(a)==1,name
    return a[0]
row=named('PlayerCellInMatch');doc=row.read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']}
sheetobj=obs[doc['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet)
preview=named('PlayerReportPreviewTooltip');pd=preview.read_typetree();pr={r['rid']:r for r in pd['references']['RefIds']};ps=obs[pd['inlineSheet']['m_PathID']].read_typetree()
textsd=next(r for r in rr.values() if r.get('data',{}).get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path','').lower()=='player.initialsurname')
textnode=next(r for r in rr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==textsd['rid'])
assert textsd['data']['EnableEmbeddedLinks']==1
parent=rr[textnode['data']['m_Parent']['rid']]

# A native NavigableLink preserves player navigation without the embedded-link hover.
ge=UnityPy.load(str(GAME/G));native=next(o for o in ge.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='text-cell-medium').read_typetree()
nr={r['rid']:r for r in native['references']['RefIds']}
navsd=next(r for r in nr.values() if r['type']['class']=='NavigableLink/UxmlSerializedData')
navnode=next(r for r in nr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==navsd['rid'])
remapsd=next(r for r in rr.values() if r['type']['class']=='BindingRemapper/UxmlSerializedData')
remapnode=next(r for r in rr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==remapsd['rid'])
rid=70000;eid=1980000000
def pair(a,b,parent_id,name):
    global rid,eid
    a,b=copy.deepcopy(a),copy.deepcopy(b);a['rid'],b['rid']=rid,rid+1;rid+=2
    a['data'].update(m_Id=eid,m_Parent={'rid':parent_id},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_SerializedData={'rid':b['rid']})
    b['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1);eid+=1
    rr[a['rid']],rr[b['rid']]=a,b
    return a,b
scope,ss=pair(remapnode,remapsd,parent['rid'],'MatchPlayerNameHoverScope')
ss['data']['Mappings']=[{'m_serialisedType':0,'from':k,'to':{'m_path':v},'type':{'id':t}} for k,v,t in
                       [('binding','player',1145176065),('reportcontextteam','team',1145176088)]]
ss['data']['Mappings_UxmlAttributeFlags']=1
parent['data']['m_Children']=[{'rid':scope['rid']} if c['rid']==textnode['rid'] else c for c in parent['data']['m_Children']]
link,ls=pair(navnode,navsd,scope['rid'],'MatchPlayerNameNavigation')
scope['data']['m_Children']=[{'rid':link['rid']}]
textnode['data']['m_Parent']={'rid':link['rid']}
link['data']['m_Children']=[{'rid':textnode['rid']}]
textsd['data']['EnableEmbeddedLinks']=0;textsd['data']['EnableEmbeddedLinks_UxmlAttributeFlags']=1

# Copy the current popup content directly under the name, without an extra visible icon.
popup=next(r for r in pr.values() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.Tooltip')
def ids(v):
    if isinstance(v,dict):
        if set(v)=={'rid'}:
            if v['rid']!=-2:yield v['rid']
        else:
            for k,x in v.items():
                if k!='m_Parent':yield from ids(x)
    elif isinstance(v,list):
        for x in v:yield from ids(x)
keep=set();todo=[popup['rid']]
while todo:
    i=todo.pop()
    if i in keep:continue
    keep.add(i);todo.extend(ids(pr[i].get('data',{})))
ridmap={i:rid+j for j,i in enumerate(sorted(keep))};rid+=len(keep)
elementmap={r['data']['m_Id']:eid+j for j,r in enumerate([pr[i] for i in sorted(keep) if 'm_Id' in pr[i].get('data',{})])}
def remap(v):
    if isinstance(v,dict):
        if set(v)=={'rid'}:return {'rid':ridmap.get(v['rid'],v['rid'])}
        return {k:elementmap.get(x,x) if k in ['m_Id','uxmlAssetId','m_ParentId'] else remap(x) for k,x in v.items()}
    if isinstance(v,list):return [remap(x) for x in v]
    return v
rulemap={}
def import_rule(index):
    if index in rulemap:return rulemap[index]
    rule=copy.deepcopy(ps['m_Rules'][index]);rule['m_ComplexSelectors']=[]
    for p in rule['m_Properties']:
        for h in p['m_Values']:
            if h['m_ValueType'] in poolmap:
                pool=poolmap[h['m_ValueType']];value=copy.deepcopy(ps[pool][h['valueIndex']]);h['valueIndex']=len(sheet[pool]);sheet[pool].append(value)
    rulemap[index]=len(sheet['m_Rules']);sheet['m_Rules'].append(rule)
    return rulemap[index]
for i in sorted(keep):
    r=remap(copy.deepcopy(pr[i]));r['rid']=ridmap[i];a=r.get('data',{})
    if i==popup['rid']:a['m_Parent']={'rid':link['rid']}
    if a.get('m_RuleIndex',-1)>=0:a['m_RuleIndex']=import_rule(a['m_RuleIndex'])
    rr[r['rid']]=r
link['data']['m_Children'].append({'rid':ridmap[popup['rid']]})
existing={u['alias']:u for u in doc['m_Usings']}
for u in pd['m_Usings']:
    if u['alias'] in existing:assert existing[u['alias']]==u
    else:doc['m_Usings'].append(copy.deepcopy(u))
doc['references']['RefIds']=list(rr.values())

seen=set()
def walk(i):
    assert i not in seen;seen.add(i);a=rr[i]['data']
    for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']['rid']==i;walk(c['rid'])
walk(doc['m_VisualTree']['rid'])
for r in rr.values():
    a=r.get('data',{})
    if 'm_Parent' in a:assert r['rid'] in seen
    sd=a.get('m_SerializedData',{}).get('rid',-2)
    if sd!=-2:assert rr[sd]['data']['uxmlAssetId']==a['m_Id']
row.save_typetree(doc);sheetobj.save_typetree(sheet)
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(obs)
for i,o in check.items():
    if i in [row.path_id,sheetobj.path_id]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(doc if i==row.path_id else sheet,sort_keys=True)
    else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[i],i
out=R/('match-player-name-fc-hover-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[p])
(out/W).write_bytes(output)
for p,b in before.items():assert (p/W).read_bytes()==b
try:
    for p in [GAME,SKIN]:(p/W).write_bytes(output)
    for p in [GAME,SKIN]:assert (p/W).read_bytes()==output
except BaseException:
    for p,b in before.items():(p/W).write_bytes(b)
    raise
report={'installed':True,'runtime_verified':False,'backup':str(out),'changed_assets':['PlayerCellInMatch','PlayerCellInMatch inline stylesheet'],
        'name_hover':'current FC popup content','player_navigation':'native NavigableLink','name_binding':'player.InitialSurname',
        'unrelated_assets_verified':len(obs)-2}
(out/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report))
