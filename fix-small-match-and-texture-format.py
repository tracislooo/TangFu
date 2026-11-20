from pathlib import Path
import sys,json,hashlib,copy,datetime,subprocess
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
sha=lambda b:hashlib.sha256(b).hexdigest()
GAME=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
OUT=R/('small-match-texture-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
def exited():return not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip()
assert exited(),'Exit game first'
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle')}
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:
  if (f/n).exists():protected[f/n]=sha((f/n).read_bytes())
payload={};before={};changes=[];th={}
for label,folder in [('game',GAME),('skin',SKIN)]:
 for name in ['ui-tileslayouts_assets_all.bundle','ui-backgrounds_assets_common.bundle','ui-backgrounds_assets_.bundle']:
  p=folder/name;raw=p.read_bytes();e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};original={pid:sha(o.get_raw_data()) for pid,o in oo.items()};expected={};pixels={};new=set()
  if 'tileslayouts' in name:
   metaob=next(o for o in oo.values() if o.type.name=='AssetBundle');meta=metaob.read_typetree()
   for index,n in enumerate(['MatchExperienceHumanGridCompositionSet','MatchExperienceHumanGridCompositionSet-NoLeague','MatchExperienceGridCompositionSet','MatchExperienceGridCompositionSet-NoLeague']):
    ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==n);d=ob.read_typetree();mapping=d['m_gridBreakpointCompositionData'];small=next(v for v in mapping['m_values'] if v['m_key']==1)
    old=oo[small['m_value'][0]['m_PathID']];layout=old.read_typetree()
    if layout['m_gridBreakpoint']==1:continue
    pid=-941111202600001-index;assert pid not in oo
    layout=copy.deepcopy(layout);layout['m_Name']=n+'_SmallCompatible';layout['m_gridBreakpoint']=1
    clone=copy.copy(old);clone.path_id=pid;clone.data=None;clone._read_until=None;clone.assets_file.objects[pid]=clone;clone.save_typetree(layout);new.add(pid);expected[pid]=layout
    small['m_value']=[{'m_FileID':0,'m_PathID':pid}]
    ob.save_typetree(d);expected[ob.path_id]=d
    entries=[v for _,v in meta['m_Container'] if v['asset']['m_FileID']==0 and v['asset']['m_PathID']==ob.path_id];assert entries
    for entry in entries:
     span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]);span.append({'m_FileID':0,'m_PathID':pid});entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
    changes.append({'folder':label,'set':n,'breakpoint':1,'old_breakpoint':3,'new_layout':pid})
   if new:metaob.save_typetree(meta);expected[metaob.path_id]=meta
  else:
   for o in oo.values():
    if o.type.name!='Texture2D':continue
    d=o.read_typetree()
    if d['m_TextureFormat'] not in [10,12] or not(d['m_Width']%4 or d['m_Height']%4):continue
    tex=o.read();im=tex.image.convert('RGBA');pixels[o.path_id]=(im.size,sha(im.tobytes()));tex.set_image(im,target_format=4);tex.save();expected[o.path_id]=d
    changes.append({'folder':label,'texture':d['m_Name'],'path_id':o.path_id,'pixels_preserved':True})
  if not expected:continue
  data=e.file.save(packer='lz4');cc={o.path_id:o for o in UnityPy.load(data).objects};assert set(cc)==set(original)|new
  for pid,o in cc.items():
   if pid in pixels:
    d=o.read_typetree();allowed={'m_CompleteImageSize','m_TextureFormat','image data','m_StreamData','m_MipCount','m_MipMap'};assert d['m_TextureFormat']==4;assert all(d[k]==v for k,v in expected[pid].items() if k not in allowed)
    im=o.read().image.convert('RGBA');assert (im.size,sha(im.tobytes()))==pixels[pid]
    if label=='game':th[pid]=sha(o.get_raw_data())
   elif pid in expected:assert o.read_typetree()==expected[pid]
   else:assert sha(o.get_raw_data())==original[pid]
  for sub,b in [('backup-'+label,raw),(label,data)]:
   q=OUT/sub/name;q.parent.mkdir(exist_ok=True);q.write_bytes(b)
  before[p]=raw;payload[p]=data;print(label,name,len(expected),flush=True)
registry=R/'current-custom-textures.json';reg=json.loads(registry.read_bytes());old=registry.read_bytes()
for t in reg['textures']:
 if int(t['path_id']) in th:t['texture_sha256']=th[int(t['path_id'])];t['texture_format_id']=4
common=GAME/'ui-backgrounds_assets_common.bundle'
if common in payload:reg.update(authoritative_source_bundle=str(OUT/'game'/common.name),source_bundle_sha256=sha(payload[common]),manifest=str(OUT/'manifest.json'))
if th:before[registry]=old;payload[registry]=json.dumps(reg,ensure_ascii=False,indent=2).encode();(OUT/'backup-registry.json').write_bytes(old)
files=[{'target':str(p),'before':sha(before[p]),'after':sha(b)} for p,b in payload.items()]
report={'installed':False,'files':files,'changes':changes,'runtime_verified':False};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
lines=["$ErrorActionPreference='Stop'","if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for row in files:lines.append("if ((Get-FileHash -LiteralPath '"+row['target']+"').Hash.ToLower() -ne '"+row['after']+"') { throw 'Later changes detected' }")
for p in payload:
 backup=OUT/'backup-registry.json' if p==registry else OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name
 lines.append("Copy-Item -LiteralPath '"+str(backup)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(lines),'utf-8-sig')
assert exited(),'Game running; prepared only'
assert all(p.read_bytes()==b for p,b in before.items());assert all(sha(p.read_bytes())==h for p,h in protected.items())
try:
 for p,b in payload.items():p.write_bytes(b);assert sha(p.read_bytes())==sha(b)
 assert all(sha(p.read_bytes())==h for p,h in protected.items() if p not in payload)
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'output':str(OUT),'installed_files':len(files),'changes':len(changes)}))
