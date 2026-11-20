import datetime,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'CA170和CA180图片替换-V60-20261027';F=O/'图片及引用校验记录.json';m=json.loads(F.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
if '--installed' in sys.argv:
 assert all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
 assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
 m.update(installed=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),installed_hash_verified=True)
 (R/'current-custom-textures.json').write_bytes((O/'当前175张有效图片恢复来源.json').read_bytes());F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print('V60 installed and current image source updated.');sys.exit(0)
(O/'回退'/'current-custom-textures.json').write_bytes((R/'current-custom-textures.json').read_bytes())
install=O/'安装.ps1';s=install.read_text('utf-8-sig')
guards='\n'.join("if((Get-FileHash -LiteralPath '"+p+"' -Algorithm SHA256).Hash.ToLower() -ne '"+h+"'){throw 'Related resource version changed; revalidate before installing.'}" for p,h in m['protected_sha256'].items())
s=s.replace('$items=@(',guards+'\n$items=@(',1)
s+="& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' --installed\nif($LASTEXITCODE -ne 0){throw 'Metadata update failed.'}\n"
install.write_text(s,'utf-8-sig')
p=O/'回退.ps1';s=p.read_text('utf-8-sig');s+="Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination '"+str(R/'current-custom-textures.json')+"' -Force\n";p.write_text(s,'utf-8-sig')
(O/'说明.txt').write_text('V60：只替换 CA170、CA180 的纹理内容，保留名称及 Path ID：CA170=-910000000000144，CA180=-910000000000007。\n图片原尺寸及透明度保留，沿用 DXT5 单级 mipmap，存在正常压缩误差。所有其他对象、CAB、资源目录、预加载、原生资源流不变。\n现有29处两图引用解析及纹理字节哈希验证通过。两份 catalog 中各82条自定义 VisualTreeAsset/VisualFunction 的 GUID、类型、实际对象及所属包为首项和 backgrounds 依赖验证通过。\n不修改当前切图规则、布局、评分公式及 catalog。70个禁用 ID 保持未占用，有效图片仍为175张。\n安装前退出游戏，运行安装.ps1，同步游戏与皮肤目录并更新后续恢复来源。回退.ps1恢复原背景包和恢复来源清单。游戏实际显示待重启后确认。','utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command',"Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],capture_output=True,text=True)
if not proc.stdout.strip():
 subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(install)],check=True)
else:print('Game running: pending installation.',flush=True)
m=json.loads(F.read_text('utf8'))
with zipfile.ZipFile(O.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in O.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(O))
with zipfile.ZipFile(O.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'installed':m['installed'],'verified_image_references':len(m['verified_existing_ui_references']),'active_images':175,'zip_bytes':O.with_suffix('.zip').stat().st_size}))
