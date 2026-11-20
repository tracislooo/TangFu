from pathlib import Path
import sys,json,hashlib,shutil,importlib.util
r=Path.cwd();sys.path.insert(0,str(r/'.codex-deps'));import UnityPy
out=Path(json.loads((r/'old-left-fc-binding-route-prepared.json').read_text('utf8'))['output']);m=json.loads((out/'manifest.json').read_text('utf8'));assert m['installed']
loc=json.loads((r/'current-game-location.json').read_text('utf8'));key='e898cf8de19d543984f58379abb35340';page=-950000000000162
spec=importlib.util.spec_from_file_location('cat',r/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
checks=[]
for tag,root in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 w={o.path_id:o for o in UnityPy.load(str(root/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
 l={o.path_id:o for o in UnityPy.load(str(root/'ui-tileslayouts_assets_all.bundle')).objects}
 desc=l[-950000000000230].read_typetree();assert desc['<ID>k__BackingField']=='PlayerOverviewLeftFC';assert desc['m_directTitlePath']['m_path']=='OverviewLeftFCVariantTitle'
 assert all(c['AssetRef']['m_AssetGUID']==key for c in desc['<Configurations>k__BackingField'])
 ts=l[1332213496068314481].read_typetree();assert {'m_FileID':0,'m_PathID':-950000000000230}in ts['m_gridElementDescriptions']
 meta=next(o.read_typetree()for o in w.values()if o.type.name=='AssetBundle');entries=[v for k,v in meta['m_Container']if k==key];assert len(entries)==1 and entries[0]['asset']=={'m_FileID':0,'m_PathID':page}
 doc=w[page].read_typetree();rr={x['rid']:x for x in doc['references']['RefIds']};names=[x.get('data',{}).get('name')for x in rr.values()]
 assert 'ApprovedHeaderCareerPlayerContext'in names and 'OldLeftFCIdentityAttributesDivider'in names
 assert rr[1221]['data']['m_Parent']=={'rid':1188};assert rr[1188]['data']['m_Children'][0]=={'rid':1221}
 cat=cm.Catalog(((root.parent if tag=='game'else root)/'catalog.bin').read_bytes());locations=[i for i in cat.locations(key)if cat.location(i)['type'][1].endswith('VisualTreeAsset')];assert len(locations)==1
 cl=cat.location(locations[0]);assert cl['internal']==key and locations[0]in cat.locations('GameWorldVisualTreeAssetPreload');assert cat.location(cl['dependencies'][0])['internal'].endswith('ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
 checks.append(dict(target=tag,title_key='OverviewLeftFCVariantTitle',description=-950000000000230,guid=key,unique_page=page,career_module_present=True,id_above_name=True,catalog_and_preload_valid=True))
cache=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large';layout=json.loads(cache.read_text('utf8'))
assert all(cfg['AssetRef']['m_AssetGUID']==key for c in layout['m_gridComponents']if c['m_elementID']=='PlayerOverviewLeftFC'for cfg in c['m_gridElementConfigs'])
sha=lambda b:hashlib.sha256(b).hexdigest();tx=json.loads((out/'transaction.json').read_text('utf8'))
for row in tx:assert sha(Path(row['target']).read_bytes())==row['after']
report=dict(passed=True,files=len(tx),route_checks=checks,selected_cache_guid_valid=True,runtime_verified=False)
(out/'verification-installed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');shutil.copy2(r/'fix-old-left-fc-binding-route.py',out/'fix-old-left-fc-binding-route.py')
state=json.loads((r/'current-old-left-fc-hidden-overview.json').read_text('utf8'));state.update(page=page,manifest=str(out/'manifest.json'),verification=str(out/'verification-installed.json'),script=str(r/'fix-old-left-fc-binding-route.py'),guid=key,unique_registration=True,saved_cache_guid_corrected=True,installed=True,runtime_verified=False)
(r/'current-old-left-fc-hidden-overview.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=False))

