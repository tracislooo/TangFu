import datetime,hashlib,json,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'七张CA更新及新增150和170-V59-20261027';F=O/'图片及引用校验记录.json';m=json.loads(F.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
if '--installed' in sys.argv:
 assert all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
 assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
 m.update(installed=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),installed_hash_verified=True)
 (R/'current-custom-textures.json').write_bytes((O/'当前175张有效图片恢复来源.json').read_bytes())
 p=R/'AGENTS.md';text=p.read_text('utf8').replace('当前有效自定义图片为 173 张','当前有效自定义图片为 175 张（V59 新增 CA150、CA170）');p.write_text(text,'utf8')
 F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print('Installed V59; current texture registry updated to 175.');sys.exit(0)
# Make manual installation apply the validated registry and preserve catalog repairs.
install=O/'安装.ps1';s=install.read_text('utf-8-sig')
guards='\n'.join("if((Get-FileHash -LiteralPath '"+p+"' -Algorithm SHA256).Hash.ToLower() -ne '"+h+"'){throw 'Related resource version changed; revalidate package before installing.'}" for p,h in m['protected_sha256'].items())
s=s.replace('$items=@(',guards+'\n$items=@(',1)
s+="& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'finish-seven-ca-v59.py')+"' --installed\nif($LASTEXITCODE -ne 0){throw 'Registry finalization failed.'}\n"
install.write_text(s,'utf-8-sig')
(O/'说明.txt').write_text('V59：同名更新 CA000、CA120、CA140、CA160、CA180；新增 CA150、CA170，Path ID 分别为 -910000000000143、-910000000000144。\n图片原尺寸及透明度保留，DXT5 单级 mipmap，存在正常压缩误差。原图片 ID、CAB、目录及预加载记录保留，仅新增两条图片目录及预加载。\n新增两张已可供引用；本包未修改卡面自动切换区间，是否新增150/170两档等待用户选择。\n55处现存卡面图片引用解析校验通过。游戏及皮肤 catalog 各82个自定义 VTA/VisualFunction 的 GUID、类型、实际对象及首项所属包和背景依赖均核对通过，未修改 catalog 或评分公式。\n70个永久停用ID保持未占用。自定义图片新增后共175张。\n打包时游戏运行，尚未安装。退出游戏后运行安装.ps1，同步游戏和皮肤目录，并更新当前有效图片恢复清单。安装脚本包含版本/哈希核对。\n回退.ps1只回退背景包；完整旧包已分别备份。游戏内显示待安装重启后确认。','utf-8-sig')
(O/'175张图片资源ID对照.txt').write_text('名称\tPath ID\t纹理对象SHA256\n'+'\n'.join(t['name']+'\t'+t['path_id']+'\t'+t['texture_sha256'] for t in json.loads((O/'当前175张有效图片恢复来源.json').read_text('utf8'))['textures']),'utf-8-sig')
with zipfile.ZipFile(O.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(O))
with zipfile.ZipFile(O.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'prepared':True,'installed':m['installed'],'active_after_install':175,'zip_bytes':O.with_suffix('.zip').stat().st_size}))
