from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';BG='ui-backgrounds_assets_common.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
before={p/W:(p/W).read_bytes() for p in [GAME,SKIN]}
assert before[GAME/W]==before[SKIN/W],'World bundles differ; inspect both versions before editing.'
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in [folder/G,folder/BG,folder/'ui-styles_assets_default.bundle',folder/'ui-tileslayouts_assets_all.bundle',folder/'ui-textures_assets_all.bundle'] if p.exists()}
for folder in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:
  p=folder/n
  if p.exists():protected[p]=sha(p.read_bytes())
e=UnityPy.load(before[GAME/W]);obs={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
oldwrite=TypeTreeHelper.write_value
helper=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<style-helpers>','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
expected={};routes=[]
def dimension(s,n,k):
 p=next(p for p in s['m_Rules'][n['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==k)
 h=p['m_Values'][0];assert h['m_ValueType']==3
 return s['dimensions'][h['valueIndex']]['value']
for pid,content in [(-3760232355926433866,1010),(-498859349613660051,70007),(-1857952619964471988,80013)]:
 obj=obs[pid];d=obj.read_typetree();old=copy.deepcopy(d);rr=refs(d)
 assert not any(r.get('data',{}).get('name') in ['PlayerPopupCanvas75','PlayerPopupViewport75'] for r in rr.values()),'75% wrapper already installed; do not scale twice.'
 so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
 target=rr[content];click=pid==-1857952619964471988
 design_height=676 if click else 620
 assert dimension(s,target,131105)==1342 and dimension(s,target,131087)==design_height
 prototype=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement' and r.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2)
 nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 node=copy.deepcopy(prototype);sd=copy.deepcopy(rr[node['data']['m_SerializedData']['rid']]);node['rid']=nr;sd['rid']=nr+1
 node['data'].update(m_Id=ni,m_Children=[],m_SerializedData={'rid':sd['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 sd['data'].update(uxmlAssetId=ni,name='PlayerPopupViewport75' if click else 'PlayerPopupCanvas75',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 # New nodes are unbound visual containers. All original serialized data stays identical.
 sd['data']['bindings']=[]
 if click:
  parent=rr[target['data']['m_Parent']['rid']]
  parent['data']['m_Children']=[{'rid':nr} if c['rid']==content else c for c in parent['data']['m_Children']]
  node['data'].update(m_Parent={'rid':parent['rid']},m_Children=[{'rid':content}]);target['data']['m_Parent']={'rid':nr}
  viewport=node;canvas=target
 else:
  node['data'].update(m_Parent={'rid':content},m_Children=copy.deepcopy(target['data']['m_Children']))
  for child in node['data']['m_Children']:rr[child['rid']]['data']['m_Parent']={'rid':nr}
  target['data']['m_Children']=[{'rid':nr}];viewport=target;canvas=node
  st.box(canvas,0,0,1342,620)
 st.edit(viewport,[st.p(131102,st.en('relative')),st.p(131105,st.px(1006.5)),st.p(131097,st.px(1006.5)),st.p(131095,st.px(1006.5)),st.p(131087,st.px(design_height*.75)),st.p(131096,st.px(design_height*.75)),st.p(131094,st.px(design_height*.75)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(262150,st.px(0)),st.p(262151,st.px(0)),st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})),st.p(65551,st.en('visible'))])
 st.edit(canvas,[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.px(0)),st.p(327681,st.num(.75),st.num(.75)),st.p(327682,st.pct(0),st.pct(0))])
 d['references']['RefIds'].extend([node,sd]);rr=refs(d)
 # Only hierarchy links and two inline style indices may change on existing nodes.
 for rid,oldr in refs(old).items():
  current=copy.deepcopy(rr[rid])
  if 'm_Parent' in oldr.get('data',{}):
   for key in ['m_Parent','m_Children','m_RuleIndex']:
    if key in oldr['data']:current['data'][key]=oldr['data'][key]
  assert current==oldr,('Existing data/bindings changed',pid,rid)
 visited=set();element_ids=set()
 def walk(rid):
  assert rid not in visited;visited.add(rid);a=rr[rid]['data'];assert a['m_Id'] not in element_ids;element_ids.add(a['m_Id'])
  sr=a.get('m_SerializedData',{}).get('rid',-2)
  if sr!=-2:assert rr[sr]['data']['uxmlAssetId']==a['m_Id']
  for child in a.get('m_Children',[]):assert rr[child['rid']]['data']['m_Parent']=={'rid':rid};walk(child['rid'])
 walk(d['m_VisualTree']['rid'])
 assert all(r['rid'] in visited for r in rr.values() if 'm_Parent' in r.get('data',{}))
 assert dimension(s,viewport,131105)==1006.5 and dimension(s,viewport,131087)==design_height*.75
 for o,data in [(obj,d),(so,s)]:o.save_typetree(data);expected[o.path_id]=data
 routes.append({'name':d['m_Name'],'viewport_rid':viewport['rid'],'canvas_rid':canvas['rid'],'design_size':[1342,design_height],'display_size':[1006.5,design_height*.75],'scale':[.75,.75],'origin':[0,0]})
outbytes=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(outbytes).objects};assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True),i
 else:assert sha(o.get_raw_data())==hashes[i],i
# Validate current installed registrations, using actual V61-era objects and texture registry.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
audits=[]
for folder in [GAME,SKIN]:
 catpath=GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin';cat=cm.Catalog(catpath.read_bytes());count=0
 for bn,en in [(W,UnityPy.load(outbytes)),(G,UnityPy.load(str(folder/G)))]:
  oo={o.path_id:o for o in en.objects};meta=next(o.read_typetree() for o in en.objects if o.type.name=='AssetBundle')
  for guid,entry in meta['m_Container']:
   if len(guid)!=32 or any(c not in '0123456789abcdef' for c in guid) or entry['asset']['m_FileID']!=0:continue
   o=oo.get(entry['asset']['m_PathID'])
   if o is None or o.type.name!='MonoBehaviour' or not(-1000000000000000<o.path_id<-900000000000000):continue
   data=o.read_typetree();kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in data else 'SI.VisualScripting.VisualFunction' if 'm_nodes' in data else None
   if kind is None:continue
   for loc in cat.locations(guid):
    v=cat.location(loc);assert v['type'][1]==kind and v['internal']==guid and v['dependencies']
    assert cat.location(v['dependencies'][0])['internal'].replace('\\','/').endswith('/'+bn)
    if guid=='64033a72b9925c8dad3b08826077c328':assert any(cat.location(x)['internal'].replace('\\','/').endswith('/'+BG) for x in v['dependencies'])
   count+=1
 audits.append({'catalog':str(catpath),'custom_vta_and_function_registrations':count})
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];retired_ids={int(t['path_id']) for t in reserved};retired_names={t['name'].lower() for t in reserved}
be=UnityPy.load(str(GAME/BG));bo={o.path_id:o for o in be.objects};bm=next(o.read_typetree() for o in be.objects if o.type.name=='AssetBundle')
assert retired_ids.isdisjoint(bo)
assert all(o.peek_name().lower() not in retired_names for o in be.objects if o.type.name=='Texture2D')
assert all(k.lower() not in retired_names and v['asset']['m_PathID'] not in retired_ids for k,v in bm['m_Container'])
assert all(p['m_PathID'] not in retired_ids for p in bm['m_PreloadTable'])
active=json.loads((R/'current-custom-textures.json').read_text('utf8'));assert len(active['textures'])==active['active_custom_texture_count']==176
assert all(int(t['path_id']) in bo and bo[int(t['path_id'])].peek_name()==t['name'] for t in active['textures'])
for pid,name in [(-910000000000143,'CA150'),(-910000000000144,'CA170'),(-910000000000145,'kunshan stadium')]:assert bo[pid].peek_name()==name
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S');out=R/('player-popups-scale75-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
(out/W).write_bytes(outbytes)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p in before:p.write_bytes(outbytes);assert p.read_bytes()==outbytes
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'routes':routes,'existing_bindings_events_textures_formulas_and_inner_layout_preserved':True,'main_player_pages_and_global_bundle_unchanged':True,'unrelated_world_objects_unchanged':len(obs)-len(expected),'catalog_audits':audits,'active_texture_count':176,'retired_70_absent':True,'catalogs_and_protected_bundles_unchanged':True,'after_sha256':sha(outbytes)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
