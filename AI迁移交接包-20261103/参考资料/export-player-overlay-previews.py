import sys,json
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');P=R/'player-page-layer-inspection'
bg=UnityPy.load(str(G/'ui-backgrounds_assets_common.bundle'))
for o in bg.objects:
 if o.type.name=='Texture2D' and o.peek_name() in ['PlayerTopBackground','PlayerTopBlueLight']:
  d=o.read();d.image.save(str(P/(d.m_Name+'.png')));print('TEXTURE',d.m_Name,o.path_id)
for n in ['OverviewToggle_FullOverview','OverviewToggle_PortraitAttributes','PlayerReportHeader','ReportIconsBelowPlayerTopBackground']:
 t=json.loads((P/(n+'.json')).read_text('utf8'));s=json.loads((P/(n+'-style.json')).read_text('utf8'));rr={r['rid']:r for r in t['references']['RefIds']}
 for r in rr.values():
  d=r.get('data',{});sd=rr.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
  if name not in ['PlayerTopBackgroundTextureLayer','ReportBlueLightBelowPlayerTopBackground']:continue
  print('LAYER',n,name,'rule',d.get('m_RuleIndex'))
  for p in s['m_Rules'][d['m_RuleIndex']]['m_Properties']:
   if p['m_Id'] not in [458753,458767,131105,131087,327681]:continue
   vals=[]
   for v in p['m_Values']:
    a={6:'assets',2:'floats',3:'dimensions'}.get(v['m_ValueType']);vals.append(s[a][v['valueIndex']] if a else v)
   print(p['m_Id'],vals)
