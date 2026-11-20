exec((__import__('pathlib').Path(__file__).parent/'inspect-tangfu-view-sources.py').read_text('utf8').split('for key in')[0])
V='ui-tableviews_assets_all.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
ve=UnityPy.load(str(p/V));vo={o.path_id:o for o in ve.objects};mt=next(o.read_typetree() for o in vo.values() if o.type.name=='AssetBundle');targets={}
for key,item in mt['m_Container']:
 ob=vo.get(item['asset']['m_PathID'])
 if ob and ob.type.name=='MonoBehaviour' and 'FirstTeamSquadAndYouth' in (ob.peek_name() or ''):targets[key]=ob.peek_name();print('COLLECTION',ob.path_id,key,ob.peek_name())
lines=[]
for n in [W,G]:
 e=UnityPy.load(str(p/n));oo={o.path_id:o for o in e.objects}
 for ob in oo.values():
  if ob.type.name!='MonoBehaviour':continue
  name=ob.peek_name();d=ob.read_typetree()
  if 'inlineSheet' not in d:continue
  relevant=[g for g in targets if g in json.dumps(d)]
  if not relevant and not re.search('Table.*(Dropdown|View.*Select)|TableView|View.*Dropdown',name,re.I):continue
  (out/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  lines.append((n,name,ob.path_id,relevant));rr={r['rid']:r for r in d['references']['RefIds']}
  for rid,r in rr.items():
   a=r.get('data',{})
   if 'Dropdown' not in a.get('m_FullTypeName',''):continue
   data=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});lines.append((rid,data))
(out/'selectors.txt').write_text(json.dumps(lines,ensure_ascii=False,indent=2),'utf8');print(str(out/'selectors.txt'))
