from pathlib import Path
import sys,json,importlib.util
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
bn=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle']
new={n:UnityPy.load(str(G/n)) for n in bn};old={n:UnityPy.load(str(S/n)) for n in bn}
idx={}
for n,e in new.items():
 for o in e.objects:
  if o.type.name=='AssetBundle':
   for k,v in o.read_typetree()['m_Container']:idx[k]=(n,v['asset']['m_PathID'])
for n,e in old.items():
 oo={o.path_id:o for o in e.objects};meta=next(o for o in oo.values() if o.type.name=='AssetBundle').read_typetree()
 print('OLD MAPPED',n)
 for k,v in meta['m_Container']:
  pid=v['asset']['m_PathID'];o=oo.get(pid)
  if o and o.type.name=='MonoBehaviour' and (abs(pid)<10**15 or o.peek_name() in ['PersonPicture','PlayerReportHeaderMaxTeamSection','PlayerReportHeaderScoutSection','report-player-banner-max','PlayerReportOverviewComposition-Large','PlayerReportOverview','PlayerReportHeader']):print(k,pid,o.peek_name(),'->',idx.get(k))
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
oc=c.Catalog((S/'catalog.bin').read_bytes());nc=c.Catalog((G.parent/'catalog.bin').read_bytes());nkeys=dict(nc.keys());oldextra=[(k,l) for k,l in oc.keys() if isinstance(k,str) and len(k)==32 and k not in nkeys]
print('CAT EXTRA',len(oldextra))
for k,l in oldextra:
 loc=oc.array(l,'I')[0][0];v=oc.location(loc);print(k,v['type'][1],[(oc.location(d)['primary'],oc.location(d)['internal']) for d in v['dependencies']])
