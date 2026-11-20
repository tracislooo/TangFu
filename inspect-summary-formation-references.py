from pathlib import Path
import sys,json
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
T='ui-tileslayouts_assets_all.bundle'
CK='<Configurations>k__BackingField'
out={}
for bn in [T,M,G]:
 e=UnityPy.load(str(GAME/bn));result=[]
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  if bn==T and any(s in n for s in ['TeamReport','TeamFormationAdaptive','MatchExperience']):
   d=o.read_typetree();v={'pid':o.path_id,'name':n}
   for k in [CK,'m_gridElementDescriptions','m_gridCompositions','m_gridCompositionSet']:
    if k in d:v[k]=d[k]
   if 'm_gridComponents' in d:v['slots']=[{k:b[k] for k in ['m_elementID','m_configDescriptions','m_gridElementConfigs','m_location']} for b in d['m_gridComponents']]
   result.append(v)
  if bn!=T and (n in ['HalfTimeTeamReport','FullTimeTeamReport','PastMatchTeamReport','OverviewPrototype'] or 'Formation' in n):
   d=o.read_typetree()
   if 'references' not in d:continue
   rr={r['rid']:r.get('data',{}) for r in d['references']['RefIds']}
   panels=[{'rid':i,'parent':a.get('m_Parent'), 'data':rr.get(a.get('m_SerializedData',{}).get('rid'),{})} for i,a in rr.items() if a.get('m_FullTypeName')=='FM.UI.FMTacticsPanel']
   groups=[{'rid':i,**a} for i,a in rr.items() if 'GridCompositionSets' in a or 'Bindings' in a]
   result.append({'pid':o.path_id,'name':n,'usings':d.get('m_Usings'),'panels':panels,'groups':groups})
 out[bn]=result
(R/'summary-formation-reference-inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
for bn,rows in out.items():
 print(bn)
 for row in rows:
  if 'slots' in row and ('TeamReport' in row['name'] and ('Large' in row['name'])):
   print(row['name'],[(b['m_elementID'],b['m_location'],[(c['AssetRef']['m_AssetGUID'],c['Description']) for c in b['m_gridElementConfigs']]) for b in row['slots']])
  if row.get('panels'):print(row['name'],row['pid'],[(p['rid'],p['data'].get('Orientation'),p['data'].get('FlipPositions')) for p in row['panels']])
  if row.get('groups'):print(row['name'],'GROUPS',str(row['groups'])[:1800])
