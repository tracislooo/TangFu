from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
b=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');L='ui-tileslayouts_assets_all.bundle';oo={o.path_id:o for o in UnityPy.load(str(b/L)).objects}
for pid in [3901662990989568885,1332213496068314481,-930000000001004,-950000000000232]:
 d=oo[pid].read_typetree();print(pid,d.keys())
 if pid in [-930000000001004,-950000000000232]:print(json.dumps(d,ensure_ascii=False)[:1800])
 else:
  for k,v in d.items():
   if isinstance(v,list):print(k,len(v),json.dumps(v[0],ensure_ascii=False)[:700] if v else '')
p=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large');print('SAVED',p.exists());print(p.read_bytes()[:450] if p.exists() else '')
