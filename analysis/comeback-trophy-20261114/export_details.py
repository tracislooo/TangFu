from pathlib import Path
import sys,json,re
O=Path(__file__).parent;sys.path.insert(0,str(O.parents[1]/'.codex-deps'))
import UnityPy
src=Path(r'K:\桌面\FM27 Comeback Skin v1.8.3\Skin files')
e=UnityPy.load(str(src/'ui-styles_assets_default.bundle'))
for ob in e.objects:
 if ob.type.name=='Texture2D' and ob.peek_name().startswith('fmet-cab_'):
  d=ob.read();d.image.save(O/(d.m_Name+'.png'));print(d.m_Name,d.m_Width,d.m_Height)
e=UnityPy.load(str(src/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'))
ab=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle')
for key,v in ab['m_Container']:
 if key in ('31ffa54435a873f41ac1574b92fc89a8','6c64bbef698f0ef41abfed580c7fdf18'):print('GUID',key,v)
d=json.loads((O/'objects/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload__-5495443699739417454.json').read_text('utf8'))
for r in d['references']['RefIds']:
 a=r.get('data',{})
 if a.get('name') in ('FMETCabWon','FMETCabTrophySlot','FMETCabSeveral','FMETCabTrophy','FMETCabLogo'):
  args=a['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']
  print(a['name'],bytes(args).hex(),repr(bytes(args)))
