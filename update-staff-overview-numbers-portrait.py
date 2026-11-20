"""Show native staff attribute numbers and reuse the player's complete portrait."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('staff-overview-numbers-full-portrait-' + stamp)
OUT.mkdir()
before = {folder / W: (folder / W).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME / W] == before[SKIN / W], 'Game and skin bundles differ'
for p, b in before.items():
    target = OUT / ('backup-game' if p.parent == GAME else 'backup-skin') / p.name
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(b)

protected = {}
for folder in [GAME, SKIN]:
    for name in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
                 'ui-backgrounds_assets_common.bundle', 'ui-tileslayouts_assets_all.bundle']:
        protected[folder / name] = sha((folder / name).read_bytes())
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin', SKIN / 'catalog.hash']:
    if p.exists():
        protected[p] = sha(p.read_bytes())

env = UnityPy.load(before[GAME / W])
objects = {o.path_id: o for o in env.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
oldwrite = TypeTreeHelper.write_value
src = ast.parse((R / 'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.FunctionDef)
    and n.name in {'write', 'val', 'px', 'pct', 'en', 'num', 'prop', 'rule', 'override'}],
    type_ignores=[]), 'serialization-and-styles', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
src = ast.parse((R / 'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.FunctionDef)
    and n.name == 'validate_ui'], type_ignores=[]), 'ui-validator', 'exec'))

def refs(d):
    return {r['rid']: r for r in d['references']['RefIds']}

changed = {}
attribute_audit = []
# The native style functions already consume this exact 1-20 PropertyValue.
# Keep those functions, their thresholds, translations and role highlighting.
for pid in [5904429056627683184, 1142760536872937931]:
    doc = objects[pid].read_typetree()
    original = copy.deepcopy(doc)
    hits = []
    for r in doc['references']['RefIds']:
        data = r.get('data', {})
        text = data.get('TextBinding', {})
        if text.get('m_direct', {}).get('Path', {}).get('m_path') == 'attributebind.DisplayString':
            assert text['m_kind'] == 1
            text['m_direct']['Path']['m_path'] = 'attributebind.PropertyValue'
            data['DebugDisplay'] = '15'
            hits.append(r['rid'])
    assert len(hits) == 1, (doc['m_Name'], hits)
    rr, oldrr = refs(doc), refs(original)
    # Verify a native style setter uses this same property as a numeric lookup.
    assert any(b'attributebind.PropertyValue' in bytes(r.get('data', {}).get('BindFunction', {})
        .get('m_inputs', {}).get('m_variable', {}).get('m_argumentBytes', []))
        for r in original['references']['RefIds'])
    for rid, r in rr.items():
        if rid in hits:
            restored = copy.deepcopy(r)
            restored['data']['TextBinding'] = oldrr[rid]['data']['TextBinding']
            restored['data']['DebugDisplay'] = oldrr[rid]['data']['DebugDisplay']
            assert restored == oldrr[rid]
        else:
            assert r == oldrr[rid]
    validate_ui(doc, objects[doc['inlineSheet']['m_PathID']].read_typetree())
    objects[pid].save_typetree(doc)
    changed[pid] = doc
    attribute_audit.append({'name': doc['m_Name'], 'path_id': str(pid),
        'source': 'attributebind.PropertyValue', 'native_colours_and_names_preserved': True})

HEADER = -4246927470610052519
PLAYER = -930000000001003
PORTRAIT = -910000000000101
player = objects[PLAYER].read_typetree()
source = next(u for u in player['m_Usings'] if u['alias'] == 'MovedBanner_ReportMiddleSquarePersonPicture')
assert source['asset'] == {'m_FileID': 0, 'm_PathID': PORTRAIT}
portrait = objects[PORTRAIT].read_typetree()
portrait_style = objects[portrait['inlineSheet']['m_PathID']].read_typetree()
# Confirm every licensed / generated / fallback image branch uses containment.
image_branches = []
for r in portrait['references']['RefIds']:
    a = r.get('data', {})
    if a.get('m_FullTypeName') == 'SI.Bindable.SIImage':
        props = portrait_style['m_Rules'][a['m_RuleIndex']]['m_Properties']
        mode = next(p for p in props if p['m_Id'] == 262153)['m_Values'][0]
        assert portrait_style['strings'][mode['valueIndex']] == 'scale-to-fit'
        image_branches.append(r['rid'])
assert len(image_branches) == 4

doc = objects[HEADER].read_typetree()
original = copy.deepcopy(doc)
sid = doc['inlineSheet']['m_PathID']
sheet = objects[sid].read_typetree()
rr = refs(doc)
using = next(u for u in doc['m_Usings'] if u['alias'] == 'PersonPicture')
using.update(copy.deepcopy(source))
using['alias'] = 'PersonPicture'
assert rr[1025]['data']['m_TemplateAlias'] == 'PersonPicture'
assert rr[rr[1016]['data']['m_SerializedData']['rid']]['data']['name'] == 'PersonPictureFrame'
# A square, centered frame with explicit bounds prevents the old thumbnail
# class and bottom alignment from clipping or collapsing the contained image.
rr[1016]['data']['m_Classes'] = ['align-items-center', 'justify-content-center']
rr[1025]['data']['m_Classes'] = []
override(rr[1016]['data'], [prop(131105, px(226)), prop(131087, px(226)),
    prop(131095, px(226)), prop(131094, pct(100)), prop(131097, px(0)),
    prop(131096, px(0)), prop(131084, num(0)), prop(131085, num(1)),
    prop(131074, en('center')), prop(131073, en('center')),
    prop(131088, en('center')), prop(262150, px(0)), prop(262151, px(0)),
    prop(131099, px(0)), prop(131100, px(0)), prop(131101, px(0)), prop(131098, px(0))])
for rid in [1019, 1025]:
    override(rr[rid]['data'], [prop(131105, pct(100)), prop(131087, pct(100)),
        prop(131097, px(0)), prop(131096, px(0)), prop(131095, pct(100)),
        prop(131094, pct(100)), prop(131084, num(1)), prop(131085, num(1)),
        prop(131074, en('stretch'))])
# All staff identity, contract, context menu and team mappings are unchanged.
for rid, r in refs(original).items():
    if rid not in [1016, 1019, 1025]:
        assert rr[rid] == r, ('unrelated header record changed', rid)
validate_ui(doc, sheet)
for pid, tree in [(HEADER, doc), (sid, sheet)]:
    objects[pid].save_typetree(tree)
    changed[pid] = tree

output = env.file.save(packer='lz4')
check = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(check) == set(objects)
for pid, digest in hashes.items():
    if pid not in changed:
        assert sha(check[pid].get_raw_data()) == digest, ('unrelated asset changed', pid)
for pid, tree in changed.items():
    assert check[pid].read_typetree() == tree, ('roundtrip mismatch', pid)
for pid in [HEADER, 5904429056627683184, 1142760536872937931]:
    tree = check[pid].read_typetree()
    validate_ui(tree, check[tree['inlineSheet']['m_PathID']].read_typetree())
for p, b in before.items():
    assert p.read_bytes() == b
for p, digest in protected.items():
    assert sha(p.read_bytes()) == digest
(OUT / W).write_bytes(output)

report = {'installed': False, 'runtime_verified': False,
    'attributes': attribute_audit, 'numeric_scale': 'native 1-20',
    'portrait': {'reused_player_guid': source['path'], 'path_id': str(PORTRAIT),
        'container': '226px, constrained to header height', 'image_mode': 'scale-to-fit',
        'verified_image_branches': image_branches},
    'changed_objects': [str(i) for i in changed],
    'unchanged_objects_verified': len(hashes) - len(changed),
    'player_pages_and_shared_portrait_unchanged': True,
    'before_sha256': {str(p): sha(b) for p, b in before.items()},
    'after_sha256': {W: sha(output)},
    'protected_sha256': {str(p): h for p, h in protected.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
transaction = {'game': str(GAME), 'skin': str(SKIN), 'files': [W],
    'before': {str(p): str(OUT / ('backup-game' if p.parent == GAME else 'backup-skin') / W) for p in before}}
(OUT / 'transaction.json').write_text(json.dumps(transaction, indent=2), 'utf8')
(OUT / 'installer.py').write_bytes((R / 'install-match-ui-patch.py').read_bytes())
python = Path(sys.executable).as_posix()
for name, flag in [('install.ps1', ''), ('restore.ps1', ' --restore')]:
    (OUT / name).write_text('$ErrorActionPreference = "Stop"\n& \'' + python +
        "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + flag + '\n', 'utf-8-sig')
(OUT / '修改说明.md').write_text('''# Staff Overview：数值评价与完整头像

- 职员属性评价直接显示原生 1–20 数值，保留属性名称、颜色、关键属性标记和各职能分类切换。
- 普通属性行和带图标属性行均已修改；其他复用这两种职员属性行的提示框也会显示数值。
- 职员页头像复用球员大头像的 ReportMiddleSquarePersonPicture，四条图像分支均等比例完整显示。
- 头像框居中，宽高 226px，最大高度受顶部栏限制；不修改球员页和共享头像组件。
- 游戏目录与 tf27-01 皮肤包同步。仅修改一个 bundle 内的四个对象，不更改 catalog、背景及四版球员布局。
- 已通过序列化回读、引用/样式检查及其余对象逐项哈希验证；尚未进行游戏内画面实测。
- 退出游戏后运行 restore.ps1 可回退本次修改。更新游戏后应重新匹配新版原生资源再迁移。
''', 'utf8')
proc = subprocess.run(['powershell', '-NoProfile', '-Command',
    'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],
    capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'waiting_for_game_exit': True, 'output': str(OUT)}))
else:
    result = subprocess.run([sys.executable, str(OUT / 'installer.py'), str(OUT)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    print(result.stdout.strip())
