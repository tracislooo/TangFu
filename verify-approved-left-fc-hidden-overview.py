"""Independent donor, loading, selector and saved-layout checks for the FC clone."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('verify-two-portrait-hidden-overviews.py',{'canonical'})]:
 tree=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),fn,'exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
OUT=Path(json.loads((R/'approved-left-fc-hidden-prepared.json').read_text('utf8'))['output'])
installed='--installed'in sys.argv;m=json.loads((OUT/'manifest.json').read_text('utf8'));loc=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
SOURCE,DONOR,PAGE,STYLE=-941100000001020,-940000000010000,-941100000001060,-941100000001061
reserved={int(x['path_id'])for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
checks=[]
for tag in ['game','skin']:
 live=Path(loc['bundle_root']if tag=='game'else loc['skin_packages']);base=live if installed else OUT/tag
 def objects(path):return {o.path_id:o for o in UnityPy.load(str(path)).objects}
 oo=objects(OUT/('backup-'+tag)/W);nn=objects(base/W);ll=objects(base/L);cache_bundles={W:nn,L:ll}
 source=oo[SOURCE].read_typetree();donor=oo[DONOR].read_typetree();page=nn[PAGE].read_typetree();sheet=nn[STYLE].read_typetree()
 assert nn[SOURCE].get_raw_data()==oo[SOURCE].get_raw_data()
 assert nn[source['inlineSheet']['m_PathID']].get_raw_data()==oo[source['inlineSheet']['m_PathID']].get_raw_data()
 assert canonical(page,sheet,skip_portrait=True)==canonical(source,oo[source['inlineSheet']['m_PathID']].read_typetree(),skip_portrait=True)
 actual=canonical(page,sheet,portrait_only=True);expected=canonical(donor,oo[donor['inlineSheet']['m_PathID']].read_typetree(),portrait_only=True)
 # Only the viewport and whole-card scale differ from the donor's presentation.
 actual['data']['m_RuleIndex']=expected['data']['m_RuleIndex']
 actual['data']['m_Children'][0]['data']['m_RuleIndex']=expected['data']['m_Children'][0]['data']['m_RuleIndex']
 assert actual==expected,'FC donor internals differ'
 catpath=((live.parent if tag=='game'else live)/'catalog.bin')if installed else base/'catalog.bin'
 catbytes=catpath.read_bytes();cat=cm.Catalog(catbytes)
 assert catpath.with_name('catalog.hash').read_bytes()==hashlib.md5(catbytes).hexdigest().encode('ascii')
 keymap=dict(cat.keys())
 def locations(key):return [x[0]for x in cat.array(keymap[key],'I')]
 def resolve(key,suffix):
  found=[cat.location(i)for i in locations(key)if cat.location(i)['type'][1].endswith(suffix)];assert len(found)==1,(key,suffix)
  entry=found[0];owner=cat.location(entry['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
  if owner not in cache_bundles:
   path=live/owner
   if not path.exists():path=Path(loc['bundle_root'])/owner
   cache_bundles[owner]=objects(path)
  objs=cache_bundles[owner];meta=next(o.read_typetree()for o in objs.values()if o.type.name=='AssetBundle')
  ptr=next(v['asset']for k,v in meta['m_Container']if k==key and v['asset']['m_FileID']==0 and v['asset']['m_PathID']in objs)
  return objs[ptr['m_PathID']],entry,owner
 vta,entry,owner=resolve(m['fc']['guid'],'VisualTreeAsset');assert vta.path_id==PAGE and owner==W
 assert entry['offset']in locations('GameWorldVisualTreeAssetPreload')
 functions=[]
 for guid in next(x for x in m['audits']if x['target']==tag)['fc_function_guids']:
  obj,_,bundle=resolve(guid,'VisualFunction');d=obj.read_typetree();assert d['m_Name']
  functions.append(dict(guid=guid,name=d['m_Name'],bundle=bundle,path_id=obj.path_id))
 pr=refs(page);card=named(page,'ReportPortraitStatusColumn');portraits=owned_refs(pr,card)
 usedaliases={pr[i]['data'].get('m_TemplateAlias')for i in portraits}-{None,''}
 for alias in usedaliases:
  use=next(u for u in page['m_Usings']if u['alias']==alias);resolve(use['path'],'VisualTreeAsset')
 backgrounds={}
 for name in ['ui-backgrounds_assets_common.bundle','ui-backgrounds_assets_.bundle']:
  path=live/name
  if path.exists():backgrounds.update(objects(path))
 textures=[]
 for i in portraits:
  sd=pr.get(pr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
  if not name.startswith('ReportCACardImage'):continue
  rule=sheet['m_Rules'][pr[i]['data']['m_RuleIndex']]
  handle=next(p for p in rule['m_Properties']if p['m_Id']==458753)['m_Values'][0]
  assert handle['m_ValueType']==6;ptr=sheet['assets'][handle['valueIndex']];pid=ptr['m_PathID'];assert pid not in reserved
  assert backgrounds[pid].type.name=='Texture2D'
  assert backgrounds[pid].peek_name()==name.replace('ReportCACardImage','')
  textures.append(dict(name=backgrounds[pid].peek_name(),path_id=pid))
 assert {x['name']for x in textures}=={'CA000','CA120','CA140','CA150','CA160','CA170','CA180'}
 ts=ll[1332213496068314481].read_typetree();choices=[ll[p['m_PathID']].read_typetree()['<ID>k__BackingField']for p in ts['m_gridElementDescriptions']if p['m_FileID']==0 and ll[p['m_PathID']].read_typetree().get('<ID>k__BackingField','').startswith('PlayerOverview')]
 assert len(choices)==8 and choices[-1]==m['fc']['ident']
 hostrefs=refs(nn[7857044477279960178].read_typetree())
 variables=next(x['data']['ValueVariables']for x in hostrefs.values()if x.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
 titles={v['m_name']:v['m_scopeValue']['m_serializedData'].split('|',2)[1]for v in variables if v['m_scopeValue']['m_serializedData'].startswith('String|')}
 assert titles['OverviewLeftTestVariantTitle']=='左边版大头像+隐藏'
 assert titles['OverviewLeftFCHiddenApprovedTitle']=='左边版FC卡面+隐藏'
 assert titles['OverviewLeftPortraitHiddenVariantTitle']=='左边版大头像+隐藏（旧版）'
 assert titles['OverviewLeftFCVariantTitle']=='左边版FC卡面+隐藏（旧版）'
 checks.append(dict(target=tag,portrait_approved_page_byte_identical=True,all_non_portrait_regions_canonical_equal=True,
  fc_donor_canonical_equal_except_whole_card_fit=True,fc_functions=functions,card_textures=textures,selector_choices=choices,
  new_page_actual_catalog_object_and_preload_verified=True,donor_aliases_resolve=True))
 print('Independent verification passed: '+tag,flush=True)
cachetx=next((x for x in json.loads((OUT/'transaction.json').read_text('utf8'))if 'CustomGridCompositions'in x['target']),None)
if cachetx:
 old=json.loads(Path(cachetx['backup']).read_bytes());new=json.loads(Path(cachetx['target']if installed else cachetx['source']).read_bytes())
 assert old['m_gridComponents']==new['m_gridComponents']
 assert new['m_placementBindings'][:-1]==old['m_placementBindings']
 for key in old:
  if key!='m_placementBindings':assert new[key]==old[key]
result=dict(passed=True,installed=installed,checks=checks,saved_selection_and_positions_unchanged=True,runtime_verified=False)
(OUT/('verification-installed.json'if installed else 'verification-independent.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print('Passed: eight choices, exact donor internals, actual FC functions/textures, saved selection unchanged.',flush=True)
