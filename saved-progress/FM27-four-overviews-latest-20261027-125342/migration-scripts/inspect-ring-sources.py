from pathlib import Path
import json,re,sys
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def walk(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='m_argumentBytes' and x:
    print('ARGS',re.findall(r'[ -~]{4,}',bytes(x).decode('latin1')))
   elif k in ['m_path','DebugDisplay','m_FullTypeName'] and x:print(k,x)
   elif isinstance(x,dict):walk(x)
for o in objects.values():
 if o.type.name=='MonoBehaviour' and o.peek_name() in ['PlayerConditionCell','PlayerConditionTooltipBlock','PlayerFatigueIconCell','FatigueBlock','MatchSharpnessBlock','PlayerMatchSharpnessTile_2x2']:
  d=o.read_typetree();print('\nASSET',o.path_id,d['m_Name'])
  for r in d.get('references',{}).get('RefIds',[]):
   a=r.get('data',{})
   if any(k in a for k in ['TextBinding','Binding','BindFunction']):print('RID',r['rid']);walk(a)
print('PANEL',named('OverviewHiddenAttributesPanel')['rid'])
for name in ['OverviewHiddenAttributesPanel','OverviewHiddenAttributeRow1','OverviewHiddenAttributeRow2']:
 n=named(name);print(name,n['rid'],[(p['m_Id'],property_value(n,p['m_Id'])) for p in sheet['m_Rules'][n['data']['m_RuleIndex']]['m_Properties']])
cur=named('OverviewHiddenAttributesPanel')['rid']
while cur in rr:
 a=rr[cur]['data'];print('ANCESTOR',cur,a.get('m_Parent'),a.get('m_FullTypeName'), [(p['m_Id'],property_value(rr[cur],p['m_Id'])) for p in sheet['m_Rules'][a['m_RuleIndex']]['m_Properties']] if a.get('m_RuleIndex',-1)>=0 else [])
 cur=a.get('m_Parent',{}).get('rid')
for bundle in []:
 for o in UnityPy.load(str(GAME/bundle)).objects:
  if o.type.name=='MonoBehaviour' and o.peek_name() in ['FatigueDataCollection','SharpnessDataCollection','RawConditionDataCollection','ConditionRangesDataCollection']:
   print('COLLECTION',o.peek_name(),json.dumps(o.read_typetree(),ensure_ascii=False))
