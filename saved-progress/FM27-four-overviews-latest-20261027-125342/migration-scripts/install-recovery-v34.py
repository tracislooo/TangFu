import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
OUT = ROOT / '修复函数版本报错-v34'
NAME = 'ui-visualfunctions_assets_all.bundle'
GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
check = subprocess.run(['powershell', '-NoProfile', '-Command',
    'if(Get-Process -Name fm -ErrorAction SilentlyContinue){exit 1}else{exit 0}'], capture_output=True)
assert check.returncode == 0, 'Game is running; cannot replace bundles.'
assert sha(GAME / NAME) == 'ec3ac9447bd5af750b44a95d277776f597cc63df18df09457233e5b9056ad4d3'
global_name = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before_global = sha(GAME / global_name)
backup = ROOT / 'v34安装前备份'
backup.mkdir(exist_ok=True)
assert not (backup / NAME).exists()
shutil.copyfile(GAME / NAME, backup / NAME)
shutil.copyfile(OUT / NAME, GAME / NAME)
assert sha(GAME / NAME) == sha(OUT / NAME)
assert sha(GAME / global_name) == before_global
text = '''函数版本报错修复 v34

修复 Player.log 的 Boolean -> BindingPath 参数类型错误。
上一版从 G:/Doc/skins/27_01 恢复的函数包，与当前游戏实际使用的函数版本不一致。
例如 BindAttributePositionColour：当前界面要求 BindingPath + 两个 Boolean 参数，
该恢复包却要求多个 BindingPath 参数，导致战术界面 SIStyleSetter 读取失败。

本文件从 v32 的修改前快照恢复 SetSIRenderTextureImage 原始函数；
删除我们新增的 95 个节点、10 张贴图及对应预加载记录和 Texture2D 类型。
其余函数保留修改前实际使用的内容，没有导入旧版本的其他函数。
校验：397 个原有对象完整保留；除已撤销修改的函数和元数据外，其他对象二进制内容不变。
重新压缩后文件 SHA256 与旧文件可能不同，已校验对象内容。

已自动替换当前游戏安装目录里的 ui-visualfunctions_assets_all.bundle。
本包只含此函数文件，不需要重新安装 global/gameworld/backgrounds。
手动安装：退出游戏，把同名文件覆盖至：
F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/

四项统计的 global 仍是 v33 检测版：图文 75%，固定中性图片，i 标记用于读取类型检测。
此修复不代表最终分档图片已完成；游戏运行结果仍需重启验证。
请勿再次使用 v33 包内旧版本的 visualfunctions 文件。
'''
(OUT / '安装说明.txt').write_text(text, encoding='utf-8-sig')
manifest_path = OUT / '恢复校验.json'
m = json.loads(manifest_path.read_text(encoding='utf-8'))
m.update(installed_path=str(GAME / NAME), installed_sha256=sha(GAME / NAME),
    global_unchanged_sha256=before_global, previous_incompatible_backup=str(backup / NAME))
manifest_path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8')
zip_path = OUT.with_suffix('.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        z.write(path, path.name)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
print(json.dumps({'zip': str(zip_path), 'installed': str(GAME / NAME),
    'functions_sha256': sha(GAME / NAME), 'global_unchanged': True}, ensure_ascii=True))
