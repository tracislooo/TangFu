from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'))
import UnityPy
p=Path('tactics-transparent-panels-card-reflow-v7-20261028-103935/backup-game/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
o={o.path_id:o for o in UnityPy.load(str(p)).objects}
for pid in [-4411574370150944845,3412805035020634299]:
 d=o[pid].read_typetree();s=o[d['inlineSheet']['m_PathID']].read_typetree()
 for a in d['references']['RefIds']:
  if 'FMTactics' in a.get('data',{}).get('m_FullTypeName',''):
   r=s['m_Rules'][a['data']['m_RuleIndex']]['m_Properties']
   print(pid,a['rid'],[(v['m_Id'],[s['colors'][h['valueIndex']] if h['m_ValueType']==4 else h for h in v['m_Values']]) for v in r if v['m_Id']==458752])
