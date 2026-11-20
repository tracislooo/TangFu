"""Package the complete installed modifications with the contract template repair."""
from pathlib import Path
import datetime, hashlib, json, zipfile

R = Path(__file__).resolve().parent
AA = Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BASE = R/'pinned-1-14-update-20261029-122441'
FIX = R/'contract-offer-template-ids-fix-20261029-190743'
base = json.loads((BASE/'manifest.json').read_text('utf8'))
fix = json.loads((FIX/'manifest.json').read_text('utf8'))
registry = json.loads((R/'current-custom-textures.json').read_text('utf8'))
assert base['installed'] and fix['installed'] and fix['installed_verified']
sha = lambda b: hashlib.sha256(b).hexdigest()
expected = dict(base['after_sha256'])
expected['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'] = fix['after_sha256']
files = []
for name, digest in expected.items():
    path = AA/'StandaloneWindows64'/name
    assert sha(path.read_bytes()) == digest, ('Unexpected installed change', name)
    if (SKIN/name).exists():
        assert sha((SKIN/name).read_bytes()) == digest, ('Skin differs from installed game', name)
    files.append((path, 'aa/StandaloneWindows64/'+name, digest))
catalog = (AA/'catalog.bin').read_bytes()
assert (AA/'catalog.hash').read_text('ascii').strip() == hashlib.md5(catalog).hexdigest()
assert catalog == (SKIN/'catalog.bin').read_bytes()
assert (AA/'catalog.hash').read_bytes() == (SKIN/'catalog.hash').read_bytes()
for name in ['catalog.bin', 'catalog.hash']:
    path = AA/name
    files.append((path, 'aa/'+name, sha(path.read_bytes())))
assert len(files) == 16
assert sha((AA/'StandaloneWindows64/ui-backgrounds_assets_common.bundle').read_bytes()) == registry['source_bundle_sha256']
assert registry['version'] == 73 and registry['active_custom_texture_count'] == 180
assert fix['consumer_audits'] == [{'consumer': 'ContractNegotiationTool', 'overrides': 66, 'resolved_before': 0, 'resolved_after': 66}]

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
dest = R/('FM27-完整皮肤修改包-含合同页面修复-'+stamp+'.zip')
readme = '''FM27 完整皮肤修改包（含提供合同页面空白修复）

本包已经合并之前的全部1–14项修改和最新合同页面修复，可作为一套完整安装，无需叠加旧补丁。
包含14个修改后的bundle及配套catalog.bin、catalog.hash，共16个游戏文件。

安装步骤：
1. 完全退出 Football Manager 27。
2. 找到游戏安装目录。Steam用户可从游戏“属性 → 已安装文件 → 浏览”打开。
3. 先备份游戏 fm_Data/StreamingAssets/aa 中本包涉及的同名文件。
4. 将本包的 aa 文件夹复制到游戏 fm_Data/StreamingAssets/ 目录，合并文件夹并覆盖同名文件。
   安装后的结构应为：游戏目录/fm_Data/StreamingAssets/aa/catalog.bin
                         游戏目录/fm_Data/StreamingAssets/aa/StandaloneWindows64/*.bundle
5. catalog.bin、catalog.hash 和所有bundle必须整套使用，不能混用旧补丁。
6. 启动游戏。需要回退时，退出游戏后用自己安装前的备份恢复。

适用版本：本包基于2026-10-29本机游戏更新后的原生资源制作。其他资源版本需要适配。
外部球员头像、队徽等独立graphics图片包不包含在内。

验证情况：资源文件、catalog、模板绑定和压缩包内容已校验。
合同页面66处绑定全部可解析。按用户要求未启动游戏或控制桌面进行画面和交互实测。
比赛轮播重启后的选择记忆及主裁判姓名仍是此前记录的未完成项，不作为本包已实现功能。

详细修改内容见“修改说明.md”，文件SHA-256见“文件校验清单.json”。
'''
notes = (BASE/'修改说明.md').read_text('utf8')
start = notes.index('1. 图片：')
end = notes.index('\n新版已删除的序列化字段')
notes = '# FM27 完整修改内容\n\n'+notes[start:end]+'''

15. 提供合同页面：修正合同模板与更新后页面的控件ID错配。66处模板覆盖由全部失效恢复为全部可解析，保留现有样式和自定义子模板。此次修改没有更改图片、公式、其他页面对象或catalog。

本包是当前已安装资源的合并快照。保留V73的180张有效自定义图片和原生背景覆盖；不包含永久停用的70张图片或已删除的TF patch原图。

文件、引用、模板路径及压缩包完整性检查通过；未进行游戏内实测。
'''
report = {'created': stamp, 'timezone': 'America/Denver', 'complete_package': True, 'game_files': len(files), 'files': [{'path': arc, 'size': path.stat().st_size, 'sha256': digest} for path, arc, digest in files], 'matches_current_installed_files': True, 'catalog_hash_verified': True, 'image_registry_version': 73, 'active_custom_images': 180, 'contract_overrides_resolved': 66, 'contract_overrides_total': 66, 'runtime_tested': False}
with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path, arc, digest in files:
        archive.write(path, arc)
    archive.writestr('安装说明.txt', readme.encode('utf-8-sig'))
    archive.writestr('修改说明.md', notes.encode('utf8'))
    archive.writestr('文件校验清单.json', json.dumps(report, ensure_ascii=False, indent=2).encode('utf8'))
with zipfile.ZipFile(dest) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(files)+3
    for path, arc, digest in files:
        assert sha(archive.read(arc)) == digest, arc
assert all(sha(path.read_bytes()) == digest for path, arc, digest in files)
checksum = sha(dest.read_bytes())
dest.with_suffix('.zip.sha256.txt').write_text(checksum+'  '+dest.name+'\n', 'utf8')
print(json.dumps({'zip': str(dest), 'size_mib': round(dest.stat().st_size/1024**2, 1), 'game_files': len(files), 'verified': True, 'sha256': checksum}, ensure_ascii=False))
