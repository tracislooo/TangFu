exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for o in obs.values():
 if o.type.name=='MonoBehaviour' and o.peek_name() in ['PlayerConditionCell','PlayerConditionCellInMatch','PlayerConditionIconCell','PlayerConditionIconCellNoBorder','TacticsPlayerSelectionTableBlock']:
  d=o.read_typetree();Path('inspect-'+o.peek_name()+'.json').write_text(json.dumps(d,indent=2));print('CELL',o.peek_name(),o.path_id)
  for r in d.get('references',{}).get('RefIds',[]):
   a=r.get('data',{});
   if any(k in a for k in ['TextBinding','Binding','Mappings','TableViewSettings']):print(r['rid'],str(a)[:2200])
for bn,names in [('ui-tablefactories_assets_all.bundle',['PlayerTableFactory']),('ui-tableviews_assets_all.bundle',[])]:
 for o in UnityPy.load(str(p.parent/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  if names and n not in names:continue
  if not names and not any(t in n.lower() for t in ['tactic','selection']):continue
  d=o.read_typetree();Path('inspect-'+n+'.json').write_text(json.dumps(d,indent=2));print('TABLE',n,o.path_id)
  def walk(v):
   if isinstance(v,dict):
    if v.get('m_id') in ['condition','condition-icon','raw-condition']:print(json.dumps(v))
    for x in v.values():walk(x)
   elif isinstance(v,list):
    for x in v:walk(x)
  walk(d)
