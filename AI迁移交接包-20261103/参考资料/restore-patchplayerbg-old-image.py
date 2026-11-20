import copy,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
sha=lambda b:hashlib.sha256(b).hexdigest();P=-910000000000147;BN='ui-backgrounds_assets_common.bundle'
SOURCE=R/'patchplayerbg-replacement-20261103';O=R/'patchplayerbg-old-image-restored-20261103'
assert not O.exists();loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);S=Path(loc['skin_packages'])
oldreg=json.loads((SOURCE/'backup/registry.json').read_text('utf8'));oldrow=next(x for x in oldreg['textures'] if x['name']=='patchplayerbg');regpath=R/'current-custom-textures.json';regraw=regpath.read_bytes();reg=json.loads(regraw)
sm=json.loads((SOURCE/'manifest.json').read_text('utf8'));outputs={};before={};records=[]
for folder in [G,S]:
 target=folder/BN;x=next(x for x in sm['install_files'] if x['target']==str(target));oldenv=UnityPy.load((SOURCE/x['backup']).read_bytes());old=oldenv.assets[0].objects[P];assert sha(old.get_raw_data())==oldrow['texture_sha256']
 raw=target.read_bytes();before[target]=raw;e=UnityPy.load(raw);a=e.assets[0];assert a.objects[P].peek_name()=='patchplayerbg';a.objects[P].set_raw_data(old.get_raw_data());out=e.file.save(packer='lz4');check=UnityPy.load(out);ca=check.assets[0]
 assert set(ca.objects)==set(a.objects) and ca.name==a.name
 for i,obj in a.objects.items():
  if i!=P:assert ca.objects[i].get_raw_data()==obj.get_raw_data()
 for k,f in e.file.files.items():
  if k!=a.name:assert check.file.files[k].bytes==f.bytes
 assert ca.objects[P].get_raw_data()==old.get_raw_data();assert ca.objects[P].read().image.tobytes()==old.read().image.tobytes();outputs[target]=out
 records.append({'target':str(target),'before_sha256':sha(raw),'after_sha256':sha(out),'old_texture_sha256':sha(old.get_raw_data()),'all_other_objects_and_preloads_preserved':True})
O.mkdir();(O/'backup').mkdir();(O/'backup/registry.json').write_bytes(regraw)
for target,out in outputs.items():
 tag='game' if target.parent==G else 'skin';(O/(tag+'-'+BN)).write_bytes(out);(O/'backup'/(tag+'-'+BN)).write_bytes(before[target])
reg['textures'][next(i for i,x in enumerate(reg['textures']) if x['name']=='patchplayerbg')]=copy.deepcopy(oldrow)
reg.update(date='2026-11-03',authoritative_source_bundle=str(O/('game-'+BN)),source_bundle_sha256=sha(outputs[G/BN]),manifest=str(O/'manifest.json'))
regnew=json.dumps(reg,ensure_ascii=False,indent=2).encode('utf8');(O/'current-custom-textures.json').write_bytes(regnew)
m={'installed':False,'runtime_verified':False,'restored_old_texture_only':True,'retained_preload_repairs':True,'install_files':records};mp=O/'manifest.json';mp.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print('GAME_RUNNING_PENDING_INSTALL');sys.exit(0)
for p,b in before.items():assert p.read_bytes()==b
assert regpath.read_bytes()==regraw
changes=[(p,b,outputs[p]) for p,b in before.items()]+[(regpath,regraw,regnew)]
try:
 for p,b,out in changes:
  tmp=p.with_name(p.name+'.oldimage.tmp');tmp.write_bytes(out);os.replace(tmp,p);assert p.read_bytes()==out
except BaseException:
 for p,b,out in changes:p.write_bytes(b)
 raise
m.update(installed=True,installed_hash_verified=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());mp.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
sm.update(installed=False,old_image_restored=True,selective_rollback_manifest=str(mp),preload_repairs_retained=True);(SOURCE/'manifest.json').write_text(json.dumps(sm,ensure_ascii=False,indent=2),'utf8')
p=R/'AGENTS.md';s=p.read_text('utf8');s=s.replace('- 2026-11-03：patchplayerbg 使用用户最新 PNG 替换，原名称与 Path ID -910000000000147 沿用，RGBA32 原尺寸无损。已验证游戏与独立皮肤现有战术卡片背景层引用及目录依赖，沿用原关联。恢复来源 current-custom-textures.json；记录 patchplayerbg-replacement-20261103/manifest.json；未改普通 Card-frame 和纯色模块。','- 2026-11-03：按用户要求，patchplayerbg 已恢复本次替换前旧图，沿用名称和 Path ID -910000000000147；仅逆向恢复纹理数据，保留预加载补齐、原关联及后续页面修改。恢复来源已更新 current-custom-textures.json，记录 patchplayerbg-old-image-restored-20261103/manifest.json；本次蓝白新图不再作为恢复来源。');p.write_text(s,'utf8')
print(json.dumps({'installed':True,'old_image_restored':True,'other_objects_preserved':True,'targets':len(records)}))
