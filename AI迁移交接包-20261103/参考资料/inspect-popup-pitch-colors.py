from pathlib import Path
import sys,json
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
P=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')
e=UnityPy.load(str(P));obs={o.path_id:o for o in e.objects}
for pid in [-960000000003030,-960000000003040]:
 d=obs[pid].read_typetree();s=obs[d['inlineSheet']['m_PathID']].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
 print('ASSET',pid,d['m_Name'])
 for rid,r in rr.items():
  a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
  if pid==-960000000003030 or name.startswith('PositionZoneColourFill_'):
   print('NODE',rid,name,a.get('m_FullTypeName'),json.dumps(sd)[:2200])
   rule=a.get('m_RuleIndex',-1)
   if rule>=0:
    props=s['m_Rules'][rule]['m_Properties'];values=[]
    for p in props:
     pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
     values.append((p['m_Id'],[s[pool[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in pool else v for v in p['m_Values']]))
    print('STYLE',values)
print('SNAPSHOT',[(k,type(v).__name__) for k,v in json.loads((R/'球员弹窗最终版本资源快照.json').read_text('utf8')).items()])
