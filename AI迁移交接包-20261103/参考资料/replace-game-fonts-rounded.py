import sys,json,hashlib,datetime,copy,io
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from fontTools.ttLib import TTFont
source=Path('K:/桌面/27skin/fonts/FM圆体.ttf');data=source.read_bytes();font=TTFont(io.BytesIO(data));cmap=font.getBestCmap()
assert all(cp in cmap for cp in [0x4e2d,0x6587,0x7403,0x5458,65,97,48])
sha=lambda b:hashlib.sha256(b).hexdigest()
game=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');skin=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
out=R/('font-rounded-replacement-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir(); (out/source.name).write_bytes(data)
targets={'NotoSansSC-Regular','ABCSocial-Regular','GT-America-Standard-Black','NotoSans-Regular','FMUniverse-Regular'}
report={'font_family':font['name'].getDebugName(1),'character_count':len(cmap),'source':str(source),'source_sha256':sha(data),'installed':False,'runtime_verified':False,'bundles':[]};pending=[]
for group in ['production','fmuniverse']:
 name='ui-fonts_assets_'+group+'.bundle';p=game/name;before=p.read_bytes();env=UnityPy.load(before);objects={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in objects.items()};changed=set();fontids=set();names=[]
 for o in objects.values():
  if o.type.name=='Font':
   d=o.read_typetree()
   if d['m_Name'] in targets:
    names.append(d['m_Name']);d['m_FontData']=list(data);d['m_FontNames']=[font['name'].getDebugName(1)];o.save_typetree(d);changed.add(o.path_id);fontids.add(o.path_id)
 for o in objects.values():
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if d.get('m_SourceFontFile',{}).get('m_PathID') not in fontids:continue
  assert d['m_AtlasPopulationMode']==1
  d['m_GlyphTable']=[];d['m_CharacterTable']=[];d['m_UsedGlyphRects']=[]
  border=0 if d['m_AtlasRenderMode']&16 else 1
  d['m_FreeGlyphRects']=[{'m_X':0,'m_Y':0,'m_Width':d['m_AtlasWidth']-border,'m_Height':d['m_AtlasHeight']-border}]
  d['m_AtlasTextureIndex']=0;d['m_IsMultiAtlasTexturesEnabled']=True;d['m_ClearDynamicDataOnBuild']=True
  for k,v in d.get('m_FontFeatureTable',{}).items():
   if isinstance(v,list):d['m_FontFeatureTable'][k]=[]
  face=d['m_FaceInfo'];units=font['head'].unitsPerEm;scale=face['m_PointSize']/units;h=font['hhea'];os=font['OS/2']
  face.update(m_FamilyName=font['name'].getDebugName(1),m_StyleName=font['name'].getDebugName(2),m_UnitsPerEM=units,m_AscentLine=h.ascent*scale,m_DescentLine=h.descent*scale,m_LineHeight=(h.ascent-h.descent+h.lineGap)*scale)
  if getattr(os,'sCapHeight',0):face['m_CapLine']=os.sCapHeight*scale
  if getattr(os,'sxHeight',0):face['m_MeanLine']=os.sxHeight*scale
  o.save_typetree(d);changed.add(o.path_id)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objects)
 for i,o in check.items():
  if i not in changed:assert sha(o.get_raw_data())==hashes[i]
  elif i in fontids:assert bytes(o.read_typetree()['m_FontData'])==data
  else:assert o.read_typetree()['m_CharacterTable']==[]
 (out/name).write_bytes(output)
 for tag,folder in [('game',game)]:
  dest=folder/name
  if tag=='skin' and not dest.exists():continue
  backup=out/('backup-'+tag);backup.mkdir(exist_ok=True);(backup/name).write_bytes(dest.read_bytes());pending.append((dest,dest.read_bytes(),output))
 report['bundles'].append({'name':name,'fonts':names,'changed_objects':sorted(changed),'before_sha256':sha(before),'after_sha256':sha(output),'unrelated_objects_verified':len(objects)-len(changed)})
assert sum(len(b['fonts']) for b in report['bundles'])==5; assert {n for b in report['bundles'] for n in b['fonts']}==targets
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
try:
 for p,old,new in pending:assert p.read_bytes()==old;p.write_bytes(new);assert p.read_bytes()==new
except BaseException:
 for p,old,new in pending:p.write_bytes(old)
 raise
report['installed']=True;report['destinations']=[str(p) for p,_,_ in pending]
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
restore=['$ErrorActionPreference = "Stop"']
for p,_,_ in pending:
 tag='backup-game' if p.parent==game else 'backup-skin';backup=out/tag/p.name
 restore.append("Copy-Item -LiteralPath '"+str(backup).replace("'","''")+"' -Destination '"+str(p).replace("'","''")+"' -Force")
(out/'restore.ps1').write_text('\n'.join(restore),encoding='utf-8-sig')
print(json.dumps({'output':str(out),**report},ensure_ascii=True,indent=2))

