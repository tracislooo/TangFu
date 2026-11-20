from pathlib import Path
import subprocess
boot=Path('set-tactics-selected-tabs-lake-blue.py').read_text('utf8').split('outputs={};checks=[]')[0].replace('tactics-selected-tabs-lake-blue-','tactics-stars-outline-black-')
exec(compile(boot,'current-styles-only-backup','exec'))
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 e=UnityPy.load(before[folder/G]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};edited={};count=0
 for pid,o in oo.items():
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree();hits=0
  for rule in d.get('m_Rules',[]):
   if not any(p['m_Value']=='tf-tactics-star-outline' for sel in rule['m_ComplexSelectors'] for s in sel['m_Selectors'] for p in s['m_Parts']):continue
   for prop in rule['m_Properties']:
    if prop['m_Id'] in [196610,65536]:
     d['colors'].append({'r':0.,'g':0.,'b':0.,'a':1.});prop['m_Values']=[{'m_ValueType':4,'valueIndex':len(d['colors'])-1}]
   hits+=1
  if hits:o.save_typetree(d);edited[pid]=d;count+=hits
 assert count==2 and len(edited)==2
 data=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==oo.keys()
 for pid,o in saved.items():
  if pid in edited:assert o.read_typetree()==edited[pid]
  else:assert sha(o.get_raw_data())==hh[pid]
 outputs[folder/G]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/G).write_bytes(data)
 checks.append({'target':str(folder/G),'star_outline':'#000000','alpha':1,'only_private_outline_style_changed':True,'roundtrip':True})
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('仅将战术卡片专用星形描边颜色改为纯黑#000000/100%不透明；其余布局、体能宽度及底色、球场和分支差异保持当前。资源回读及无关对象核验通过，游戏内效果待验收。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
