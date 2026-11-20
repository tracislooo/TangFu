exec((__import__('pathlib').Path(__file__).parent/'inspect-tangfu-view-sources.py').read_text('utf8').split("for key in")[0])
targets={'48ee712ad3785c4a92b20314e4dac8be','975b939baf439c944abc1b0be94bfc76','507cad257149560da09883b61c9626fa','beff1ac88ec3f8f4590232b091c3ddd7','f98e27d389a970a47a27a60ca1d918a7'}
for name in ['gameworld','global']:
 e=UnityPy.load(str(p/f'ui-visualtreeassets_assets_{name}visualtreeassetpreload.bundle'));oo={o.path_id:o for o in e.objects};mt=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
 for g,en in mt['m_Container']:
  ob=oo.get(en['asset']['m_PathID'])
  if g not in targets or not ob or ob.type.name!='MonoBehaviour':continue
  d=ob.read_typetree()
  if 'inlineSheet' not in d:continue
  s=oo[d['inlineSheet']['m_PathID']].read_typetree();rr={x['rid']:x for x in d['references']['RefIds']}
  (out/(ob.peek_name()+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  print('CELL',name,g,ob.path_id,ob.peek_name(),d['m_Usings'])
  for i,x in rr.items():
   a=x.get('data',{})
   if 'm_Parent' not in a:continue
   sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   print(i,a['m_Parent']['rid'],a.get('m_TemplateAlias') or a.get('m_FullTypeName'),sd.get('name'),a.get('m_Classes'))
