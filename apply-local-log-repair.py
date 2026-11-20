from pathlib import Path
import sys,json,hashlib,datetime,copy,subprocess
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
sha=lambda b:hashlib.sha256(b).hexdigest()
AA=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');GAME=AA/'StandaloneWindows64';SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
OUT=R/('local-log-repair-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
payloads={};before={};rows=[];texture_hashes={}
reserved={int(t['path_id']) for t in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle')}
for label,folder in [('game',GAME),('skin',SKIN)]:
 for p in sorted(folder.glob('*.bundle')):
  if not any(s in p.name for s in ['ui-visualtreeassets','ui-styles','ui-backgrounds_assets_common.bundle','ui-backgrounds_assets_.bundle']):continue
  raw=p.read_bytes();e=UnityPy.load(raw);orig={o.path_id:sha(o.get_raw_data()) for o in e.objects};expected={};pixels={}
  for o in e.objects:
   if o.type.name=='Texture2D':
    d=o.read_typetree()
    if d['m_TextureFormat'] not in [10,12] or not(d['m_Width']%4 or d['m_Height']%4):continue
    assert o.path_id not in reserved
    tex=o.read();im=tex.image.convert('RGBA');pixels[o.path_id]=(im.size,sha(im.tobytes()))
    tex.set_image(im,target_format=4);tex.save();expected[o.path_id]=o.read_typetree()
    rows.append({'target':str(p),'texture':o.peek_name(),'path_id':o.path_id,'fix':'DXT to RGBA32','pixels_unchanged':True})
   elif o.type.name=='MonoBehaviour':
    d=o.read_typetree()
    if 'm_Rules' not in d:continue
    count=0
    for rule in d['m_Rules']:
     for prop in rule['m_Properties']:
      if prop['m_Id']!=458753:continue
      for h in prop['m_Values']:
       if h['m_ValueType']==7 and d['strings'][h['valueIndex']]=='none':h.update(m_ValueType=1,valueIndex=6);count+=1
    if count:o.save_typetree(d);expected[o.path_id]=d;rows.append({'target':str(p),'style':o.path_id,'fixed_values':count})
  if not expected:continue
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};assert check.keys()==orig.keys()
  for pid,o in check.items():
   if pid in pixels:
    actual=o.read_typetree(); assert actual['m_TextureFormat']==4
    allowed={'m_CompleteImageSize','m_TextureFormat','image data','m_StreamData','m_MipCount','m_MipMap'}
    assert all(actual[k]==v for k,v in expected[pid].items() if k not in allowed)
   elif pid in expected:assert o.read_typetree()==expected[pid]
   else:assert sha(o.get_raw_data())==orig[pid]
   if pid in pixels:
    im=o.read().image.convert('RGBA');assert (im.size,sha(im.tobytes()))==pixels[pid]
    if label=='game':texture_hashes[pid]=sha(o.get_raw_data())
  if 'backgrounds' in p.name:
   assert reserved.isdisjoint(check)
   meta=next(o.read_typetree() for o in check.values() if o.type.name=='AssetBundle')
   assert all(v['asset']['m_PathID'] not in reserved for _,v in meta['m_Container'])
   assert all(v['m_PathID'] not in reserved for v in meta['m_PreloadTable'])
  before[p]=raw;payloads[p]=data
  (OUT/('backup-'+label)).mkdir(exist_ok=True);(OUT/('backup-'+label)/p.name).write_bytes(raw)
  (OUT/label).mkdir(exist_ok=True);(OUT/label/p.name).write_bytes(data)
  print(label,p.name,len(expected),flush=True)
registry=R/'current-custom-textures.json';old=registry.read_bytes();reg=json.loads(old)
for t in reg['textures']:
 pid=int(t['path_id'])
 if pid in texture_hashes:t['texture_sha256']=texture_hashes[pid];t['texture_format_id']=4
common=GAME/'ui-backgrounds_assets_common.bundle'
if common in payloads:
 reg['authoritative_source_bundle']=str(OUT/'game'/common.name);reg['source_bundle_sha256']=sha(payloads[common]);reg['manifest']=str(OUT/'manifest.json')
before[registry]=old;payloads[registry]=json.dumps(reg,ensure_ascii=False,indent=2).encode('utf8');(OUT/'backup-current-custom-textures.json').write_bytes(old)
files=[{'target':str(p),'before':sha(before[p]),'after':sha(b)} for p,b in payloads.items()]
manifest={'installed':False,'files':files,'changes':rows,'unresolved':['playbacktime visual function c0b4248e39d6df84d978dd6f8a209dcf requires matching original function resource'],'runtime_tested':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference="Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p,b in payloads.items():restore.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Files changed; restore stopped' }")
for p in payloads:
 backup=OUT/'backup-current-custom-textures.json' if p==registry else OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name
 restore.append("Copy-Item -LiteralPath '"+str(backup)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Game running; prepared only'
assert all(sha(p.read_bytes())==h for p,h in protected.items())
assert all(p.read_bytes()==b for p,b in before.items())
try:
 for p,b in payloads.items():p.write_bytes(b);assert sha(p.read_bytes())==sha(b)
 assert all(sha(p.read_bytes())==h for p,h in protected.items() if p not in payloads)
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
manifest['installed']=True;(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'output':str(OUT),'installed_files':len(files),'texture_changes':sum('texture' in x for x in rows),'style_objects':sum('style' in x for x in rows)}))
