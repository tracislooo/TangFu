from pathlib import Path
import ast, copy, datetime, hashlib, json, sys
R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before = {p/n: (p/n).read_bytes() for p in [GAME, SKIN] for n in [W, G]}
for n in [W, G]: assert before[GAME/n] == before[SKIN/n]
env = {n: UnityPy.load(before[GAME/n]) for n in [W, G]}
obs = {n: {o.path_id:o for o in e.objects} for n,e in env.items()}
oldhashes = {n: {i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in os.items()} for n,os in obs.items()}
expected = {W:{}, G:{}}
oldwrite = TypeTreeHelper.write_value
helper = ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value = write
poolmap = {2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
struct = __import__('struct')
def named(n,name):
    matches=[o for o in obs[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name]
    assert len(matches)==1,(name,len(matches))
    return matches[0]
def save(n,o,d):
    o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
def clone(n,source,pid,d):
    assert pid not in obs[n]
    o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o
    save(n,o,d)
    return o

# Make a private fixed-height SMALL table. Shared player page tables stay intact.
source=named(G,'AttributesTableSmall')
table=source.read_typetree()
table['m_Name']='TooltipFixed_AttributesTableSmall'
TABLE, STYLE=-960000000003020,-960000000003021
stylesource=obs[G][table['inlineSheet']['m_PathID']]
tablesheet=stylesource.read_typetree();tablesheet['m_Name']='TooltipFixed_AttributesTableSmall_Style'
table['inlineSheet']={'m_FileID':0,'m_PathID':STYLE}
ts=Styles(tablesheet)
trs={r['rid']:r for r in table['references']['RefIds']}
list_heights=[]
for r in trs.values():
    if r['type']['class']!='StreamedObjectList/UxmlSerializedData':continue
    d=r['data']
    d['HorizontalScrollerVisibility']=d['VerticalScrollerVisibility']=2
    d['HorizontalScrollerVisibility_UxmlAttributeFlags']=d['VerticalScrollerVisibility_UxmlAttributeFlags']=1
    d['FixedElementSize']=20.0;d['FixedElementSize_UxmlAttributeFlags']=1
    d['DynamicElements']=0;d['DynamicElements_UxmlAttributeFlags']=1
    node=next(v for v in trs.values() if v.get('data',{}).get('m_SerializedData',{}).get('rid')==r['rid'])
    height=d['NumPreviewElements']*20
    ts.edit(node,[ts.p(131087,ts.px(height)),ts.p(131096,ts.px(height)),ts.p(131094,ts.px(height)),
                  ts.p(131084,ts.num(0)),ts.p(131085,ts.num(0))])
    list_heights.append(height)
assert max(list_heights)==280
root=trs[table['m_VisualTree']['rid']]
for ptr in root['data']['m_Children']:
    ts.edit(trs[ptr['rid']],[ts.p(131087,ts.px(400)),ts.p(131096,ts.px(0)),ts.p(131094,ts.px(400)),
                            ts.p(131105,ts.pct(100)),ts.p(131097,ts.px(0)),ts.p(131085,ts.num(0))])
clone(G,source,TABLE,table);clone(G,stylesource,STYLE,tablesheet)

# Bind only the tooltip-specific wrapper to the private SMALL table via a direct PPtr.
wrapper=named(W,'TooltipOnly_AttributesTableSmall')
wd=wrapper.read_typetree()
global_cab=source.assets_file.name.lower()
external=next((i+1 for i,ext in enumerate(wrapper.assets_file.externals) if ext.name.lower()==global_cab),None)
if external is None:
    ext=copy.copy(wrapper.assets_file.externals[0]);ext.guid=bytes(16);ext.type=0
    ext.path=f'archive:/{source.assets_file.name}/{source.assets_file.name}'
    wrapper.assets_file.externals.append(ext);external=len(wrapper.assets_file.externals)
using=next(u for u in wd['m_Usings'] if u['alias']=='AttributesTableSmall')
using['asset']={'m_FileID':external,'m_PathID':TABLE}
save(W,wrapper,wd)
bundle=next(o for o in obs[W].values() if o.type.name=='AssetBundle')
metadata=bundle.read_typetree()
if source.assets_file.name not in metadata['m_Dependencies']:metadata['m_Dependencies'].append(source.assets_file.name)
for key,entry in metadata['m_Container']:
    if entry['asset']!={'m_FileID':0,'m_PathID':wrapper.path_id}:continue
    span=copy.deepcopy(metadata['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
    span.append({'m_FileID':external,'m_PathID':TABLE})
    entry['preloadIndex']=len(metadata['m_PreloadTable']);entry['preloadSize']=len(span)
    metadata['m_PreloadTable'].extend(span)
save(W,bundle,metadata)

# Replace the normal-player grid with explicit fixed rectangles in the existing switch.
preview=named(W,'PlayerReportPreviewTooltip');pd=preview.read_typetree()
rs={r['rid']:r for r in pd['references']['RefIds']}
sheetobj=obs[W][pd['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet)
grid_sd=next(r for r in rs.values() if r.get('data',{}).get('Bindings',{}).get('m_gridCompositionSet',{}).get('m_PathID')==-241840581472044354)
gridnode=next(r for r in rs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==grid_sd['rid'])
oldrule=sheet['m_Rules'][gridnode['data']['m_RuleIndex']]
heightprop=next(p for p in oldrule['m_Properties'] if p['m_Id']==131087)
assert sheet['dimensions'][heightprop['m_Values'][0]['valueIndex']]['value']==640
source_remap=named(W,'PlayerAttributesTooltipBlock').read_typetree()
remap_sd=next(r for r in source_remap['references']['RefIds'] if r['type']['class']=='BindingRemapper/UxmlSerializedData')
remap_node=next(r for r in source_remap['references']['RefIds'] if r.get('data',{}).get('m_SerializedData',{}).get('rid')==remap_sd['rid'])
node=copy.deepcopy(remap_node);sd=copy.deepcopy(remap_sd)
node['rid']=gridnode['rid'];sd['rid']=grid_sd['rid']
node['data'].update(m_Id=gridnode['data']['m_Id'],m_Parent=gridnode['data']['m_Parent'],m_Children=[],
                    m_SerializedData={'rid':sd['rid']},m_Classes=[],m_RuleIndex=-1,m_Properties=[])
sd['data'].update(uxmlAssetId=node['data']['m_Id'],name='FixedPlayerPreview1280x640',name_UxmlAttributeFlags=1)
sd['data']['Mappings']=[{'m_serialisedType':0,'from':name,'to':{'m_path':path},'type':{'id':typ}}
                       for name,path,typ in [('person','binding',1145176065),('player','binding',1145176065),
                                              ('team','reportcontextteam',1145176088),('isonmainscreen','const.False',0)]]
sd['data']['Mappings_UxmlAttributeFlags']=1
st.edit(node,[st.p(131102,st.en('relative')),st.p(131105,st.px(1280)),st.p(131087,st.px(640)),
              st.p(131097,st.px(1280)),st.p(131095,st.px(1280)),st.p(131096,st.px(640)),st.p(131094,st.px(640)),
              st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(262150,st.px(0)),st.p(262151,st.px(0))],reset=True)
rs[node['rid']]=node;rs[sd['rid']]=sd
templatedoc=wrapper.read_typetree();template=next(r for r in templatedoc['references']['RefIds'] if r['type']['class']=='TemplateAsset')
template_sd=next(r for r in templatedoc['references']['RefIds'] if r['rid']==template['data']['m_SerializedData']['rid'])
regions=[('FCPlayerCard','64033a72b9925c8dad3b08826077c328',12,12,400,616),
         ('PlayerHeader','ff1d7cbb16b72f946b282c7351e2a441',424,12,844,64),
         ('SmallAttributes','d7961b53b2635ae7b8996007ff34bf6b',424,88,844,400),
         ('CoachScoutReport','e8d123de5cdb49d4b9389e46d5d800bd',424,500,332,128),
         ('PlayerMood','ae2ca2f9ed113b041a85340453caf0dc',768,500,166,128),
         ('PlayerPosition','b1a562d58dc38cf49b773e91b7144203',946,500,322,128)]
rid=60000;eid=1960000000
for alias,guid,x,y,w,h in regions:
    a,b=copy.deepcopy(template),copy.deepcopy(template_sd)
    a['rid'],b['rid']=rid,rid+1;rid+=2
    a['data'].update(m_Id=eid,m_Parent={'rid':node['rid']},m_Children=[],m_SerializedData={'rid':b['rid']},m_RuleIndex=-1,
                     m_Classes=[],m_Properties=[],m_TemplateAlias=alias,m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[])
    b['data'].update(uxmlAssetId=eid,name='Fixed_'+alias,name_UxmlAttributeFlags=1,templateId=alias,
                     templateId_UxmlAttributeFlags=1,template={'m_FileID':0,'m_PathID':0})
    eid+=1
    st.box(a,x,y,w,h)
    st.edit(a,[st.p(131095,st.px(w)),st.p(131094,st.px(h)),st.p(458768,st.en('visible'))])
    rs[a['rid']],rs[b['rid']]=a,b
    node['data']['m_Children'].append({'rid':a['rid']})
    pd['m_Usings'].append({'alias':alias,'path':guid,'asset':{'m_FileID':0,'m_PathID':0}})
pd['references']['RefIds']=list(rs.values())
save(W,preview,pd);save(W,sheetobj,sheet)

# Validate full binding hierarchy, exact rectangles and the shared resources before installation.
for data,s in [(pd,sheet),(table,tablesheet)]:
    rr={r['rid']:r for r in data['references']['RefIds']}
    assert len(rr)==len(data['references']['RefIds'])
    for r in rr.values():
        a=r.get('data',{})
        for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']['rid']==r['rid']
        i=a.get('m_SerializedData',{}).get('rid',-2)
        if i!=-2:assert rr[i]['data']['uxmlAssetId']==a['m_Id']
        if a.get('m_RuleIndex',-1)>=0:assert a['m_RuleIndex']<len(s['m_Rules'])
for i,(_,_,x,y,w,h) in enumerate(regions):
    assert x>=0 and y>=0 and x+w<=1280 and y+h<=640
    for _,_,x2,y2,w2,h2 in regions[i+1:]:assert x+w<=x2 or x2+w2<=x or y+h<=y2 or y2+h2<=y
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    reread={o.path_id:o for o in UnityPy.load(b).objects}
    assert set(reread)==set(obs[n])|set(expected[n])
    for i,o in reread.items():
        if i in expected[n]:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[n][i],sort_keys=True),(n,i)
        else:assert hashlib.sha256(o.get_raw_data()).hexdigest()==oldhashes[n][i],(n,i)
assert source.path_id not in expected[G] and stylesource.path_id not in expected[G]
assert -930000000001001 not in expected[W]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('hover-fixed-regions-'+stamp);out.mkdir()
for tag,p in [('game',GAME),('skin',SKIN)]:
    backup=out/('backup-'+tag);backup.mkdir()
    for n in [W,G]:(backup/n).write_bytes(before[p/n])
for n,b in outputs.items():(out/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
try:
    for p in [GAME,SKIN]:
        for n,b in outputs.items():(p/n).write_bytes(b)
    for p in [GAME,SKIN]:
        for n,b in outputs.items():assert (p/n).read_bytes()==b
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report={'installed':True,'runtime_verified':False,'output':str(out),'width_before':1080,'width_after':1280,'height_unchanged':640,
        'layout':'fixed rectangles; native fantasy-draft branch preserved','regions':regions,'private_small_max_attribute_list_height':max(list_heights),
        'private_small_scrollers':'Hidden','main_page_and_shared_small_unchanged':True}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True,indent=2))
