import datetime,hashlib,json,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'TF-skin-V1图片新增-V66-20261029';F=O/'图片及引用校验记录.json';m=json.loads(F.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
if '--commit' in sys.argv:
 assert all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
 assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
 (R/'current-custom-textures.json').write_bytes((O/'更新后的有效图片恢复来源.json').read_bytes())
 m.update(installed=True,installed_hash_verified=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 p=R/'AGENTS.md';s=p.read_text('utf8').replace('当前有效自定义图片为 178 张','当前有效自定义图片为 179 张')
 s+='\n- V66 新增纹理 `TF skin V1`，Path ID `-910000000000149`，须沿用；本次仅加入 backgrounds，未设置界面关联。\n';p.write_text(s,'utf8')
 print('V66 installed; active image registry updated to 179.');sys.exit(0)
if '--package' in sys.argv:
 with zipfile.ZipFile(O.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in O.rglob('*'):
   if f.is_file():z.write(f,f.relative_to(O))
 with zipfile.ZipFile(O.with_suffix('.zip')) as z:assert z.testzip() is None
 print(json.dumps({'installed':m['installed'],'active_images':179,'source_size':m['textures'][0]['size'],'path_id':m['textures'][0]['path_id']}));sys.exit(0)
(O/'回退'/'current-custom-textures.json').write_bytes((R/'current-custom-textures.json').read_bytes())
p=O/'安装.ps1';s=p.read_text('utf-8-sig');s+="& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' --commit\nif($LASTEXITCODE -ne 0){throw 'Registry update failed.'}\n";p.write_text(s,'utf-8-sig')
p=O/'回退.ps1';s=p.read_text('utf-8-sig');s+="Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination '"+str(R/'current-custom-textures.json')+"' -Force\n";p.write_text(s,'utf-8-sig')
rec=m['textures'][0]
(O/'说明.txt').write_text('V66：新增 TF skin V1 纹理，Path ID -910000000000149，包内 m_FileID=0。\n所属 ui-backgrounds_assets_common.bundle；CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8；资源目录键 tf skin v1。\n保留原尺寸 '+str(rec['size'][0])+'×'+str(rec['size'][1])+'；DXT5 单级 mipmap，存在正常压缩误差；不裁剪或缩放源图。\n保留原生资源和已有图片，仅扩展一条纹理对象、目录、预加载记录。有效图片179张，70个永久停用 ID 均未占用。\n不修改现有界面、菜单球场背景、卡面切换规则、评分函数或 catalog；本次只入包，不设置 TF skin V1 界面关联。\n安装前退出游戏，运行安装.ps1 同步游戏及皮肤目录并更新恢复来源清单。含原包备份及回退.ps1。','utf-8-sig')
(O/'资源位置.txt').write_text('名称：TF skin V1\nPath ID：-910000000000149\n包内 m_FileID：0\nCAB：CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8\nBundle：ui-backgrounds_assets_common.bundle\n容器键：tf skin v1\n跨包引用的 m_FileID 按引用方 externals 索引+1确定。\n','utf-8-sig')
print('Installer prepared.')
