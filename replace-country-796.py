import copy,datetime,hashlib,importlib.util,json,os,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image
O=R/'country-796-replacement-20261117';M=O/'manifest.json';REG=R/'current-custom-textures.json';BN='ui-backgrounds_assets_common.bundle';PID=-910000000000186
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
if '--install' in sys.argv or '--rollback' in sys.argv:
 m=json.loads(M.read_text('utf8'));back='--rollback' in sys.argv
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 if p.stdout.strip():print('GAME_RUNNING_PENDING_INSTALL');sys.exit(0)
 changes=[]
 for x in m['install_files']:
  p=Path(x['target']);assert 'Project Taco' not in str(p);old=p.read_bytes();new=(O/x['backup' if back else 'source']).read_bytes()
  assert sha(old)==x['after_sha256' if back else 'before_sha256'],str(p)
  assert sha(new)==x['before_sha256' if back else 'after_sha256'];changes.append((p,old,new))
 assert sha(REG.read_bytes())==m['registry_after_sha256' if back else 'registry_before_sha256']
 changes.append((REG,REG.read_bytes(),(O/('backup/registry.json' if back else 'current-custom-textures.json')).read_bytes()))
 if not back:
  for p,h in m['reference_files_sha256'].items():assert sha(Path(p).read_bytes())==h,'References changed: '+p
 try:
  for p,old,new in changes:
   tmp=p.with_name(p.name+'.TFWPS.tmp');tmp.write_bytes(new);os.replace(tmp,p);assert p.read_bytes()==new
 except BaseException:
  for p,old,new in changes:p.write_bytes(old)
  raise
 m.update(installed=not back,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(M,m)
 print('ROLLED_BACK' if back else 'INSTALLED');sys.exit(0)
assert not O.exists();loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);S=Path(loc['skin_packages']);AA=Path(loc['aa_root'])
regraw=REG.read_bytes();reg=json.loads(regraw);banned={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}|{-910000000000001,-910000000000002,-910000000000146}
src=Path('K:/\u684c\u9762/27skin/PICTURE/country-new/796.png');srcraw=src.read_bytes()
with Image.open(src) as im:im=im.convert('RGBA')
outputs={};before={};reference_files={};audits=[];newrow=None
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for folder,catdir in [(G,AA),(S,S)]:
 p=folder/BN;raw=p.read_bytes();before[p]=raw;e=UnityPy.load(raw);a=e.assets[0];obj=a.objects[PID];assert obj.peek_name()=='796';oldtree=obj.read_typetree();t=copy.deepcopy(oldtree)
 pixels,fmt=image_to_texture2d(im,4,obj.platform,t['m_PlatformBlob']);assert int(fmt)==4
 t.update(m_TextureFormat=4,m_Width=im.width,m_Height=im.height,m_CompleteImageSize=len(pixels),m_MipCount=1);t['image data']=pixels;t['m_StreamData']={'offset':0,'size':0,'path':''};obj.save_typetree(t)
 out=e.file.save(packer='lz4');saved=UnityPy.load(out);sa=saved.assets[0];assert sa.name==a.name and set(sa.objects)==set(a.objects)
 for i,o in a.objects.items():
  if i!=PID:assert sa.objects[i].get_raw_data()==o.get_raw_data()
 for key,f in e.file.files.items():
  if key!=a.name:assert saved.file.files[key].bytes==f.bytes
 assert sa.objects[PID].read_typetree()==t and sa.objects[PID].read().image.convert('RGBA').tobytes()==im.tobytes()
 assert banned.isdisjoint(sa.objects)
 meta=next(o.read_typetree() for o in sa.objects.values() if o.type.name=='AssetBundle')
 assert all(x['m_PathID'] not in banned for x in meta['m_PreloadTable']) and all(x['asset']['m_PathID'] not in banned for k,x in meta['m_Container'])
 ent=dict(meta['m_Container'])['796'];assert ent['asset']=={'m_FileID':0,'m_PathID':PID}
 assert ent['asset'] in meta['m_PreloadTable'][ent['preloadIndex']:ent['preloadIndex']+ent['preloadSize']]
 outputs[p]=out
 row={'name':'796','path_id':str(PID),'texture_format_id':4,'size':list(im.size),'texture_sha256':sha(sa.objects[PID].get_raw_data()),'decoded_alpha_range':list(im.getchannel('A').getextrema())}
 if newrow:assert row==newrow
 newrow=row
O.mkdir();(O/'backup').mkdir();(O/'source.png').write_bytes(srcraw);files=[]
for p,out in outputs.items():
 tag='game' if p.parent==G else 'skin';name=tag+'-'+p.name;backup='backup/'+name;(O/name).write_bytes(out);(O/backup).write_bytes(before[p]);files.append(dict(target=str(p),source=name,backup=backup,before_sha256=sha(before[p]),after_sha256=sha(out)))
reg['textures'][next(i for i,x in enumerate(reg['textures']) if x['name']=='796')].update(newrow,archived_source=str(O/'source.png'))
reg.update(version=81,date='2026-11-17',authoritative_source_bundle=str(O/('game-'+BN)),source_bundle_sha256=sha(outputs[G/BN]),manifest=str(M));assert len(reg['textures'])==reg['active_custom_texture_count']==214
(O/'backup/registry.json').write_bytes(regraw);dump(O/'current-custom-textures.json',reg)
dump(M,dict(installed=False,runtime_verified=False,texture=newrow,lossless_rgba_match=True,source_sha256=sha(srcraw),existing_other_objects_and_streams_unchanged=True,reference_audits=audits,reference_files_sha256=reference_files,install_files=files,registry_before_sha256=sha(regraw),registry_after_sha256=sha((O/'current-custom-textures.json').read_bytes())))
for back in [False,True]:
 (O/('restore.ps1' if back else 'install.ps1')).write_text("$ErrorActionPreference='Stop'\n& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' "+('--rollback' if back else '--install')+"\nif($LASTEXITCODE -ne 0){throw 'Failed.'}\n",'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in reference_files.items():assert sha(Path(p).read_bytes())==h
assert REG.read_bytes()==regraw
print(json.dumps({'prepared':True,'size':list(im.size),'references_verified':len(audits)}))
