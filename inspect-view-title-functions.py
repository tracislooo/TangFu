exec((__import__('pathlib').Path(__file__).parent/'inspect-tangfu-view-sources.py').read_text('utf8').split('for key in')[0])
n='ui-visualfunctions_assets_all.bundle';e=UnityPy.load(str(p/n));oo={o.path_id:o for o in e.objects};mt=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle');guid={v['asset']['m_PathID']:g for g,v in mt['m_Container']}
lines=[]
for o in oo.values():
 if o.type.name!='MonoBehaviour':continue
 name=o.peek_name()
 if not re.search('equal|compare|string|replace|format',name,re.I):continue
 d=o.read_typetree()
 if 'm_nodes' not in d:continue
 lines.append((o.path_id,guid.get(o.path_id),name));
 if re.search('equal|replace|greater|less|CompareTwo',name,re.I):(out/('VF-'+name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
(out/'title-function-names.json').write_text(json.dumps(lines,indent=2),'utf8');print(lines[:100])
