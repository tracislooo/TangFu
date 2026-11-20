exec((__import__('pathlib').Path(__file__).parent/'inspect-tangfu-view-sources.py').read_text('utf8').split('for key in')[0])
target=b'6e59432dfa6b8b84f98b8b300ff37d2b';lines=[]
for key in ['gameworld','global']:
 e=UnityPy.load(str(p/f'ui-visualtreeassets_assets_{key}visualtreeassetpreload.bundle'))
 for ob in e.objects:
  if ob.type.name!='MonoBehaviour':continue
  d=ob.read_typetree()
  if 'inlineSheet' not in d:continue
  for r in d['references']['RefIds']:
   data=r.get('data',{});args=data.get('BindChoicesFunction',{}).get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
   if target not in bytes(args):continue
   lines.append((key,ob.peek_name(),ob.path_id,r['rid'],list(data)))
   (out/('dropdown-'+ob.peek_name()+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
print(lines)
e=UnityPy.load(str(p/'ui-visualfunctions_assets_all.bundle'))
for ob in e.objects:
 if ob.type.name=='MonoBehaviour' and ob.peek_name()=='BindAndCompareTwoIntsToSwitch':
  d=ob.read_typetree();(out/'IntSwitchFunction.json').write_text(json.dumps(d,indent=2),'utf8');print('switch',ob.path_id);print(json.dumps(d.get('m_inputs',{})))
