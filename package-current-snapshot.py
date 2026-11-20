from pathlib import Path
import json, hashlib, zipfile, datetime

root = Path.cwd()
aa = Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa')
read = lambda p: json.loads(p.read_text('utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
assert read(root/'current-sidebar-version.json')['current_game_mode'] == 'non-sidebar'
names = set(read(root/'pinned-1-14-update-20261029-122441/manifest.json')['after_sha256'])
names.update(read(root/'main-1-14-rebuild-20261102-101644/manifest.json')['after_sha256'])
files = [(aa/'StandaloneWindows64'/n, 'aa/StandaloneWindows64/'+n) for n in sorted(names)]
files += [(aa/n, 'aa/'+n) for n in ('catalog.bin', 'catalog.hash')]
assert (aa/'catalog.hash').read_text().strip() == hashlib.md5((aa/'catalog.bin').read_bytes()).hexdigest()
registry = read(root/'current-custom-textures.json')
assert sha((aa/'StandaloneWindows64/ui-backgrounds_assets_common.bundle').read_bytes()) == registry['source_bundle_sha256']
rows = [{'path': arc, 'size': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p, arc in files]
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
dest = root/f'FM27-当前游戏主版本-无侧栏-{stamp}.zip'
report = {'created': stamp, 'source': str(aa), 'mode': 'non-sidebar', 'files': rows, 'image_registry_version': registry['version'], 'runtime_tested': False}
instructions = '''FM27 当前游戏主版本（无侧栏）

全部游戏文件直接取自当前安装目录，包含当前已安装修改及配套 catalog.bin、catalog.hash。
保留当前背景、界面配色、页面修复及洗牌球员卡修改；不加入独立侧栏版本。

安装：退出游戏并备份对应原文件，将本包 aa 文件夹复制到游戏 fm_Data/StreamingAssets/ 下，合并覆盖。
本机游戏：F:/Steam/steamapps/common/Football Manager 27
catalog 和 bundle 必须配套使用。本包对应打包时本机游戏版本，不含完整游戏程序、存档及外部头像队徽包。
已校验压缩包完整性和全部文件 SHA256，未启动游戏进行画面及交互验证。
'''
with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p, arc in files:
        z.write(p, arc)
    z.writestr('安装说明.txt', instructions.encode('utf-8-sig'))
    z.writestr('文件校验清单.json', json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8'))
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for row in rows:
        assert sha(z.read(row['path'])) == row['sha256'], row['path']
for (p, arc), row in zip(files, rows):
    assert sha(p.read_bytes()) == row['sha256'], f'Source changed: {arc}'
print(json.dumps({'zip': str(dest), 'size_mib': round(dest.stat().st_size/1024**2, 1), 'game_files': len(files), 'verified': True}, ensure_ascii=False))
