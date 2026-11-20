"""Read live and pre-global templates used by names, portraits, menus and gauges."""
from pathlib import Path
import json,sys,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
loc=json.loads((R/'current-game-location.json').read_text('utf8'));base=Path(loc['bundle_root'])
trial=Path(json.loads((R/'current-global-light-theme.json').read_text('utf8'))['record'])
names={'TacticsPositionCombined','TacticsPositionDetailed','PersonPicture','PersonPictureNoLink','TacticsPlayerPicture',
       'PlayerNameButton','ClubNameButton','TeamNameButton','CompetitionNameButton','text-cell-medium',
       'TacticalEffectivenessGauge','TacticalEffectivenessPercentageGauge','TacticalPlannerSubsBlock',
       'CompactComplexityFactorRow','GenericModalDialog','GameWorldBackground'}
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
result=[]
for short in ['gameworld','global']:
 bn=f'ui-visualtreeassets_assets_{short}visualtreeassetpreload.bundle'
 oo={o.path_id:o for o in UnityPy.load(str(base/bn)).objects};old={o.path_id:o for o in UnityPy.load(str(trial/'backup-game'/bn)).objects}
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name() or ''
  if name not in names and not re.search(r'NameButton|Percentage|Cascading|FloatingBlock|arrow|icon.*16',name,re.I):continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  sh=oo[d['inlineSheet']['m_PathID']].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
  od=old[o.path_id].read_typetree();osh=old[od['inlineSheet']['m_PathID']].read_typetree();orr={r['rid']:r for r in od['references']['RefIds']}
  nodes=[]
  for rid,r in rr.items():
   a=r.get('data',{})
   if 'm_Parent' not in a:continue
   sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   i=a.get('m_RuleIndex',-1);oi=orr[rid].get('data',{}).get('m_RuleIndex',-1)
   def props(s,i):
    return [{'id':p['m_Id'],'name':p.get('m_CustomName',''),'values':[s[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else h for h in p['m_Values']]} for p in s['m_Rules'][i]['m_Properties']] if i>=0 else []
   n={'rid':rid,'type':a.get('m_FullTypeName'),'name':sd.get('name'),'template':sd.get('templateId'),
      'classes':a.get('m_Classes',[]),'parent':a['m_Parent']['rid'],'props':props(sh,i),'before_props':props(osh,oi),'data':sd}
   nodes.append(n)
  result.append({'bundle':bn,'name':name,'id':o.path_id,'nodes':nodes,'usings':d.get('m_Usings',[])})
  if name in names:
   print(name,o.path_id)
   for n in nodes:
    if ('SIText' in (n['type'] or '') or 'PersonPicture' in (n['template'] or '') or
       'portrait' in (n['name'] or '').lower() or 'InnerSurface' in (n['name'] or '') or 'NameButton' in name or name=='PersonPicture'):
     print(n['rid'],n['type'],n['name'],n['template'],n['classes'])
     print('PAINT',[(p['id'],p['values']) for p in n['props'] if p['id'] in [65536,458752,196610,458753]])
     print('DATA',{k:v for k,v in n['data'].items() if any(x in k.lower() for x in ['color','colour','tint','class'])})
(R/'light-ui-inspection'/'regressions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
