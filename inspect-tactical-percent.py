from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps')
import UnityPy
p=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for bn in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-datacollections_assets_all.bundle']:
 e=UnityPy.load(str(p/bn))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  if n not in ['TacticalEffectivenessGauge','TacticalEffectivenessPercentageGauge','TacticalEffectivenessKeyFactorRow','TacticalEffectivenessTooltip','TacticalEffectivenessGaugeDataCollection','TacticalEffectivenessGaugeIntensityDataCollection']:continue
  d=o.read_typetree();Path('inspect-'+n+'.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  print(n,o.path_id)
  if 'references' not in d:continue
  r={a['rid']:a for a in d['references']['RefIds']}
  for i,a in r.items():
   x=a.get('data',{})
   if 'm_Parent' not in x:continue
   sd=r.get(x.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   print(i,x.get('m_FullTypeName'),x.get('m_TemplateAlias'),x.get('m_Classes'),json.dumps(sd,ensure_ascii=False))
