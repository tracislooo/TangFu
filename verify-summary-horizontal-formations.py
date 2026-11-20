from pathlib import Path
import sys,json,hashlib,importlib.util
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]);manifest=json.loads((out/'manifest.json').read_text('utf8'))
tx=json.loads((out/'transaction.json').read_text('utf8'))
spec=importlib.util.spec_from_file_location('verify_summary_catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';T='ui-tileslayouts_assets_all.bundle'
CK='<Configurations>k__BackingField'
checks=[]
for tag in ['game','skin']:
 data={}
 for bn in [G,T]:
  src=out/(('skin-' if tag=='skin' else '')+bn)
  objects={o.path_id:o for o in UnityPy.load(src.read_bytes()).objects}
  data[bn]=objects
  old={o.path_id:o for o in UnityPy.load((out/('backup-'+tag)/bn).read_bytes()).objects}
  permitted={o.path_id for o in old.values() if o.type.name=='AssetBundle'}
  if bn==T:permitted|={o.path_id for o in old.values() if o.type.name=='MonoBehaviour' and o.peek_name() in manifest['checks'][0 if tag=='game' else 1]['report_assets_changed']}
  for pid,ob in old.items():
   if pid not in permitted:assert objects[pid].get_raw_data()==ob.get_raw_data(),('Original resource changed',tag,bn,pid)
  if bn==G:assert len(objects)==len(old)+4
  else:assert len(objects)==len(old)+2
 meta=next(o.read_typetree() for o in data[G].values() if o.type.name=='AssetBundle')
 guidmap={k:v for k,v in meta['m_Container']}
 summary_guids=set()
 for side in ['Home','Away']:
  ob=next(o for o in data[G].values() if o.type.name=='MonoBehaviour' and o.peek_name()=='Summary'+side+'HorizontalFormation')
  doc=ob.read_typetree();rr={r['rid']:r.get('data',{}) for r in doc['references']['RefIds']}
  panels=[rr[a['m_SerializedData']['rid']] for a in rr.values() if a.get('m_FullTypeName')=='FM.UI.FMTacticsPanel']
  assert len(panels)==4 and all(p['Orientation']==1 and p['FlipPositions']==(1 if side=='Home' else 0) for p in panels)
  guid=next(k for k,v in guidmap.items() if v['asset']['m_PathID']==ob.path_id);summary_guids.add(guid)
  entry=guidmap[guid];span=meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]
  assert {'m_FileID':0,'m_PathID':doc['inlineSheet']['m_PathID']} in span
 cat=cm.Catalog((out/(tag+'-catalog.bin')).read_bytes())
 preload=set(cat.locations('GlobalVisualTreeAssetPreload'))
 for guid in summary_guids:
  loc=cat.locations(guid);assert len(loc)==1 and loc[0] in preload
  info=cat.location(loc[0]);assert info['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
  assert G in cat.location(info['dependencies'][0])['internal']
 layouts=[]
 for ob in data[T].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name() not in manifest['checks'][0 if tag=='game' else 1]['summary_layouts']:continue
  tr=ob.read_typetree();sets=data[T][tr['m_gridElementSet']['m_PathID']].read_typetree()
  available={p['m_PathID'] for p in sets['m_gridElementDescriptions']}
  found=[]
  for block in tr['m_gridComponents']:
   if block['m_elementID'] not in ['HomeTeamFormationAdaptive','AwayTeamFormationAdaptive']:continue
   configs=block['m_gridElementConfigs'];assert len(configs)==1
   cfg=configs[0];dp=cfg['Description']['m_PathID'];assert dp in available
   desc=data[T][dp].read_typetree();assert desc['m_Name'].startswith('Summary')
   assert cfg in desc[CK] and cfg['AssetRef']['m_AssetGUID'] in summary_guids
   assert desc['<ID>k__BackingField']==block['m_elementID']
   found.append(block['m_elementID'])
  assert set(found)=={'HomeTeamFormationAdaptive','AwayTeamFormationAdaptive'}
  layouts.append(tr['m_Name'])
 assert len(layouts)==6
 checks.append({'variant':tag,'six_summary_layouts_resolve_to_horizontal_private_templates':True,'all_original_global_objects_byte_identical':True,'only_expected_summary_tiles_objects_changed':True,'owner_first_catalog_and_actual_preload_verified':True})
for row in tx:
 src=Path(row['source']);assert hashlib.sha256(src.read_bytes()).hexdigest()==row['after']
result={'passed':True,'checks':checks,'runtime_verified':False}
(out/'independent-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(result,ensure_ascii=False))
