from pathlib import Path
import hashlib, json
R = Path(__file__).resolve().parent
out = Path(json.loads((R / 'pending-nonmatch-module-opacity.json').read_text('utf8'))['patch'])
assert json.loads((out / 'verification.json').read_text('utf8'))['passed']
m = json.loads((out / 'manifest.json').read_text('utf8'))
tx = json.loads((out / 'transaction.json').read_text('utf8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
entry = R / 'apply-page-surfaces-theme.py'
text = entry.read_text('utf8')
needle = 'R=Path(__file__).resolve().parent\n'
block = '''if '--nonmatch-modules' in sys.argv or (len(sys.argv) == 1 and global_theme_index.exists() and json.loads(global_theme_index.read_text('utf8')).get('nonmatch_module_backgrounds', {}).get('installed', False)):
 import runpy
 runpy.run_path(str(Path(__file__).resolve().with_name('apply-nonmatch-module-opacity.py')),run_name='__main__')
 raise SystemExit(0)
'''
if block not in text:
    assert needle in text
    text = text.replace(needle, block + needle, 1)
statepath = R / 'current-ui-surface-theme.json'
state = json.loads(statepath.read_text('utf8'))
state['nonmatch_module_backgrounds'] = {
    'installed':True, 'background_opacity':.3, 'color':'preserve current RGB',
    'condition':'game.IsDuringMatch == false', 'native_function':'d47d9f6bfe419344692270d5af16c5ef',
    'install_record':str(out / 'manifest.json'), 'script':str(R / 'apply-nonmatch-module-opacity.py'),
    'runtime_verified':False, 'includes':'native selectable tiles, blocks and module surfaces',
    'page_card_frame_changed':False, 'text_icons_opacity_changed':False,
    'counts':{a['target']:a['module_backgrounds'] for a in m['audits']}}
guidepath = R / 'FM27界面配色维护说明-更新后重做.md'
note = '\n\n2026-11-13：非比赛模块背景不透明度改为30%（用户已确认 alpha=0.3）。保留背景原RGB、文字图标和布局；普通页面外层 Card-frame 与顶部导航维持原设置。使用原生 game.IsDuringMatch 与 BindBoolToAorBUssClass 动态切换，比赛时保留原始背景样式。覆盖原生可选择贴片及模块背景类；已有完全透明区域保持透明。原内联背景迁移到高优先级私有USS规则作为比赛/未绑定时的基线，30%规则只匹配非比赛状态类；不使用整控件 opacity。维护入口 apply-page-surfaces-theme.py --nonmatch-modules，具体脚本 apply-nonmatch-module-opacity.py。独立皮肤缺失的原生函数包按游戏资源解析，不复制旧整包。更新后按新资源重新生成与校验；勿重跑旧全局不透明模块脚本。补丁记录：' + str(out / 'manifest.json') + '。静态校验通过，游戏内显示尚未验证。\n'
files = {entry:text, statepath:json.dumps(state, ensure_ascii=False, indent=2), guidepath:guidepath.read_text('utf8') + note}
for path, content in files.items():
    old = path.read_bytes(); new = content.encode('utf8')
    src = out / 'workspace' / path.name; bak = out / 'backup-workspace' / path.name
    src.parent.mkdir(exist_ok=True); bak.parent.mkdir(exist_ok=True)
    src.write_bytes(new); bak.write_bytes(old)
    tx['sources'][str(path)] = str(src); tx['before'][str(path)] = str(bak)
    m['before_sha256'][str(path)] = sha(old); m['after_sha256'][str(path)] = sha(new)
    m['protected_sha256'].pop(str(path), None)
for name in ['apply-nonmatch-module-opacity.py', 'verify-nonmatch-module-opacity.py']:
    (out / name).write_bytes((R / name).read_bytes())
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
(out / 'README.txt').write_text('非比赛模块背景不透明度30%；保留RGB、内容不透明度、外层Card-frame与比赛原背景。\n正常退出游戏后运行install.ps1。restore.ps1带当前文件哈希保护，不覆盖后续修改。\nverification.json为离线校验，不等同于游戏内验证。\n', 'utf8')
print(out)
