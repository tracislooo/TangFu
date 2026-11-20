exec((__import__('pathlib').Path(__file__).parent/'inspect-tangfu-view-sources.py').read_text('utf8').split('for key in')[0])
for key in ['gameworld','global']:
 e=UnityPy.load(str(p/f'ui-visualtreeassets_assets_{key}visualtreeassetpreload.bundle'));oo={o.path_id:o for o in e.objects};mt=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
 for g,item in mt['m_Container']:
  if g!='bc6b9fc730e9431488ec9a0f76587bf1':continue
  ob=oo[item['asset']['m_PathID']];d=ob.read_typetree()
  if 'inlineSheet' not in d:continue
  (out/'TableMenuRow.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  rr={r['rid']:r for r in d['references']['RefIds']}
  for i,r in rr.items():
   a=r.get('data',{})
   if 'm_Parent' not in a:continue
   dd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(i,a.get('m_FullTypeName'),a.get('m_TemplateAlias'),{k:v for k,v in dd.items() if 'Binding' in k or k=='name'})
