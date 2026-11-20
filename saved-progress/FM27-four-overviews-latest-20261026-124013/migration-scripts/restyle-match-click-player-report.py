from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={p:(p/W).read_bytes() for p in [GAME,SKIN]};assert before[GAME]==before[SKIN]
env=UnityPy.load(before[GAME]);obs={o.path_id:o for o in env.objects};hashes={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in obs.items()}
oldwrite=TypeTreeHelper.write_value
helpers=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def named(name):
    a=[o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name];assert len(a)==1,name
    return a[0]
obj=named('MatchPlayerReport');doc=obj.read_typetree();original=copy.deepcopy(doc);origrefs={r['rid']:r for r in doc['references']['RefIds']}
sheetobj=obs[doc['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet)
preview=named('PlayerReportPreviewTooltip').read_typetree();pr={r['rid']:r for r in preview['references']['RefIds']};ps=obs[preview['inlineSheet']['m_PathID']].read_typetree()
ge=UnityPy.load(str(GAME/G));baseobj=next(o for o in ge.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='FigmaBaseCardTemplate');base=baseobj.read_typetree();bs=next(o for o in ge.objects if o.path_id==base['inlineSheet']['m_PathID']).read_typetree();br={r['rid']:copy.deepcopy(r) for r in base['references']['RefIds']}
template=next(r for r in origrefs.values() if r.get('data',{}).get('m_TemplateAlias')=='FigmaBaseCardTemplate')
overrides=template['data']['m_SerializedDataOverride']
# Apply direct overrides and forward nested header overrides to their original templates.
next_override=90000
for override in overrides:
    path=override['m_ElementIdsPath'];value=copy.deepcopy(origrefs[override['m_SerializedData']['rid']])
    if len(path)==1:
        node=next(r for r in br.values() if r.get('data',{}).get('m_Id')==path[0])
        sd=br[node['data']['m_SerializedData']['rid']]['data']
        for k,flag in value['data'].items():
            if k.endswith('_UxmlAttributeFlags') and flag==1:
                field=k[:-len('_UxmlAttributeFlags')]
                sd[field]=copy.deepcopy(value['data'][field]);sd[k]=1
    else:
        node=next(r for r in br.values() if r.get('data',{}).get('m_Id')==path[0])
        assert node['type']['class']=='TemplateAsset'
        value['rid']=next_override;next_override+=1;br[value['rid']]=value
        ov=copy.deepcopy(override);ov['m_ElementIdsPath']=path[1:];ov['m_SerializedData']={'rid':value['rid']}
        node['data']['m_SerializedDataOverride'].append(ov)

# Copy the card shell into this report only, retaining native close/navigation controls.
rr={i:copy.deepcopy(origrefs[i]) for i in [1000,1001,1002,1003,1005]}
ids={i:80000+j for j,i in enumerate(sorted(i for i in br if i not in [-2,1000]))};ids[1000]=1002
def rename(v,mapping):
    if isinstance(v,dict):
        if set(v)=={'rid'}:return {'rid':mapping.get(v['rid'],v['rid'])}
        return {k:rename(x,mapping) for k,x in v.items()}
    if isinstance(v,list):return [rename(x,mapping) for x in v]
    return v
def import_style(src,index,cache):
    if index in cache:return cache[index]
    rule=copy.deepcopy(src['m_Rules'][index]);rule['m_ComplexSelectors']=[]
    for p in rule['m_Properties']:
        for h in p['m_Values']:
            if h['m_ValueType'] in poolmap:
                pool=poolmap[h['m_ValueType']];value=copy.deepcopy(src[pool][h['valueIndex']]);h['valueIndex']=len(sheet[pool]);sheet[pool].append(value)
    cache[index]=len(sheet['m_Rules']);sheet['m_Rules'].append(rule)
    return cache[index]
cache={}
for i,r in br.items():
    if i in [-2,1000]:continue
    r=rename(r,ids);r['rid']=ids[i];a=r.get('data',{})
    if a.get('m_RuleIndex',-1)>=0:a['m_RuleIndex']=import_style(bs,a['m_RuleIndex'],cache)
    rr[r['rid']]=r
rr[1002]['data']['m_Children']=[{'rid':ids[1001]}]
doc['m_Usings']=copy.deepcopy(base['m_Usings'])

# Replace the old grid by the live popup's complete fixed content, adapting the panel's player parameter.
content=next(r for r in pr.values() if pr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='FixedPlayerPreview1280x620')
def managed_ids(v):
    if isinstance(v,dict):
        if set(v)=={'rid'}:
            if v['rid']!=-2:yield v['rid']
        else:
            for k,x in v.items():
                if k!='m_Parent':yield from managed_ids(x)
    elif isinstance(v,list):
        for x in v:yield from managed_ids(x)
keep=set();todo=[content['rid']]
while todo:
    i=todo.pop()
    if i in keep:continue
    keep.add(i);todo.extend(managed_ids(pr[i].get('data',{})))
pm={i:100000+j for j,i in enumerate(sorted(keep))}
grid=rr[ids[1024]];parent=rr[grid['data']['m_Parent']['rid']];old_grid_sd=grid['data']['m_SerializedData']['rid']
parent['data']['m_Children']=[{'rid':pm[content['rid']]} if c['rid']==grid['rid'] else c for c in parent['data']['m_Children']]
del rr[grid['rid']];del rr[old_grid_sd]
pcache={}
for i in sorted(keep):
    r=rename(copy.deepcopy(pr[i]),pm);r['rid']=pm[i];a=r.get('data',{})
    if i==content['rid']:a['m_Parent']={'rid':parent['rid']}
    if a.get('m_RuleIndex',-1)>=0:a['m_RuleIndex']=import_style(ps,a['m_RuleIndex'],pcache)
    if a.get('name')=='FixedPlayerPreview1280x620':
        a['name']='MatchClickPlayerReportFCLayout'
        for m in a['Mappings']:
            if m['to']['m_path']=='binding':m['to']['m_path']='player'
            elif m['to']['m_path']=='reportcontextteam':m['to']['m_path']='team'
    rr[r['rid']]=r
doc['m_Usings'].extend(copy.deepcopy(preview['m_Usings']))
assert len({u['alias'] for u in doc['m_Usings']})==len(doc['m_Usings'])
transparent=st.h(4,{'r':0.0,'g':0.0,'b':0.0,'a':0.0})
for i in [1012,1014,1016,1017,1018]:
    st.edit(rr[ids[i]],[st.p(458752,copy.deepcopy(transparent)),st.p(262150,st.px(0)),st.p(262151,st.px(0))])
for i in [1014]:
    st.edit(rr[ids[i]],[st.p(131105,st.px(1280)),st.p(131097,st.px(1280)),st.p(131095,st.px(1280)),
                        st.p(131087,st.px(676)),st.p(131096,st.px(676)),st.p(131094,st.px(676))])
st.edit(parent,[st.p(131105,st.px(1280)),st.p(131087,st.px(620)),st.p(131096,st.px(620)),st.p(131094,st.px(620))])
st.edit(rr[ids[1016]],[st.p(131081,st.en('none'))])
doc['references']['RefIds']=list(rr.values())

# Validate all managed links and unchanged shared report resources.
seen=set();element_ids=set()
def walk(i):
    assert i not in seen;seen.add(i);a=rr[i]['data'];assert a['m_Id'] not in element_ids;element_ids.add(a['m_Id'])
    for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']['rid']==i;walk(c['rid'])
walk(doc['m_VisualTree']['rid'])
for r in rr.values():
    a=r.get('data',{})
    if 'm_Parent' in a:assert r['rid'] in seen
    for i in managed_ids(a):assert i in rr
    sd=a.get('m_SerializedData',{}).get('rid',-2)
    if sd!=-2:assert rr[sd]['data']['uxmlAssetId']==a['m_Id']
obj.save_typetree(doc);sheetobj.save_typetree(sheet)
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(obs)
for i,o in check.items():
    if i in [obj.path_id,sheetobj.path_id]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(doc if i==obj.path_id else sheet,sort_keys=True),(i,'serialization')
    else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==hashes[i],i
out=R/('match-click-player-report-fc-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[p])
(out/W).write_bytes(output)
for p,b in before.items():assert (p/W).read_bytes()==b
try:
    for p in [GAME,SKIN]:(p/W).write_bytes(output)
    for p in [GAME,SKIN]:assert (p/W).read_bytes()==output
except BaseException:
    for p,b in before.items():(p/W).write_bytes(b)
    raise
report={'installed':True,'runtime_verified':False,'backup':str(out),'target':'MatchPlayerReport','content':'current fixed FC hover layout',
        'native_card_controller_and_header_controls_retained':True,'main_player_page_unchanged':True,'unrelated_assets_verified':len(obs)-2}
(out/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report))
