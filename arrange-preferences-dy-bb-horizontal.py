"""Prepare a minimal, reversible DY-left/BB-right style patch from current resources."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import shutil
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
for filename, wanted in [('build-fc-player-hover-layout.py', 'write'), ('add-card-six-ratings.py', 'validate_ui')]:
    tree = ast.parse((R / filename).read_text('utf8'))
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == wanted]
    exec(compile(ast.Module(body=definitions, type_ignores=[]), filename + ':definitions-only', 'exec'))
TypeTreeHelper.write_value = write

location = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(location['bundle_root']), Path(location['skin_packages'])
assert GAME == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
BG = 'ui-backgrounds_assets_common.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
spec = importlib.util.spec_from_file_location('horizontal_picture_catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog_module)
registry = json.loads((R / 'current-custom-textures.json').read_text('utf8'))
textures = {x['name']: x for x in registry['textures']}
banned = {int(x['path_id']) for x in json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
banned |= {-910000000000001, -910000000000002, -910000000000146}
out = R / ('preferences-dy-bb-horizontal-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
transaction, audits, protected = [], [], {}

for tag, folder in [('game', GAME), ('skin', SKIN)]:
    path = folder / G
    before = path.read_bytes()
    env = UnityPy.load(before)
    assets = env.assets[0]
    objects = assets.objects
    original_raw = {pid: o.get_raw_data() for pid, o in objects.items()}
    document = next(o for o in objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'PreferenceBBDYPictureTile')
    doc = document.read_typetree()
    refs = {r['rid']: r for r in doc['references']['RefIds']}
    sheet = objects[doc['inlineSheet']['m_PathID']]
    style = sheet.read_typetree()
    original_style = copy.deepcopy(style)
    nodes = {}
    for r in refs.values():
        data = r.get('data', {})
        sd = refs.get(data.get('m_SerializedData', {}).get('rid'), {}).get('data', {})
        if sd.get('name') in ['DY', 'BB']:
            assert sd['pickingMode'] == 1
            nodes[sd['name']] = data
    assert set(nodes) == {'DY', 'BB'}
    changed_dimensions = set()
    image_pointers = []
    for name, left in [('DY', 0), ('BB', 52)]:
        rule = style['m_Rules'][nodes[name]['m_RuleIndex']]
        props = {p['m_Id']: p for p in rule['m_Properties']}
        # Only change existing four geometry values; image, fit mode and all bindings stay intact.
        for prop, value in [(131089, left), (131104, 0), (131105, 48), (131087, 100)]:
            handle, = props[prop]['m_Values']
            assert handle['m_ValueType'] == 3
            index = handle['valueIndex']
            uses = sum(h['m_ValueType'] == 3 and h['valueIndex'] == index
                       for r in style['m_Rules'] for p in r['m_Properties'] for h in p['m_Values'])
            assert uses == 1, 'A geometry dimension is shared with another style rule'
            style['dimensions'][index] = {'unit': 2, 'value': float(value)}
            changed_dimensions.add(index)
        image, = props[458753]['m_Values']
        ptr = style['assets'][image['valueIndex']]
        assert ptr['m_PathID'] == int(textures[name]['path_id']) and ptr['m_PathID'] not in banned
        fit, = props[262153]['m_Values']
        assert style['strings'][fit['valueIndex']] == 'scale-to-fit'
        image_pointers.append((name, ptr))
    assert {k: v for k, v in style.items() if k != 'dimensions'} == {k: v for k, v in original_style.items() if k != 'dimensions'}
    assert all(d == original_style['dimensions'][i] for i, d in enumerate(style['dimensions']) if i not in changed_dimensions)
    validate_ui(doc, style)
    sheet.save_typetree(style)
    payload = env.file.save(packer='lz4')
    check = UnityPy.load(payload).assets[0]
    assert set(check.objects) == set(objects)
    changed_objects = [pid for pid, o in check.objects.items() if o.get_raw_data() != original_raw[pid]]
    assert changed_objects == [sheet.path_id], changed_objects
    assert check.objects[sheet.path_id].read_typetree() == style

    # Existing VTA/container/preload registration and cross-bundle image references remain valid.
    metadata = next(o.read_typetree() for o in objects.values() if o.type.name == 'AssetBundle')
    guid = next(k for k, v in metadata['m_Container'] if v['asset'] == {'m_FileID': 0, 'm_PathID': document.path_id})
    catalog_path = (GAME.parent if tag == 'game' else SKIN) / 'catalog.bin'
    cb = catalog_path.read_bytes()
    c = catalog_module.Catalog(cb)
    template_locations = [x for x in c.locations(guid) if c.location(x)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
    assert template_locations and all(x in c.locations('GlobalVisualTreeAssetPreload') for x in template_locations)
    for loc in template_locations:
        deps = c.location(loc)['dependencies']
        assert c.location(deps[0])['internal'].endswith('\\' + G)
        assert any(c.location(d)['internal'].endswith('\\' + BG) for d in deps)
    bg_path = folder / BG
    bg_bytes = bg_path.read_bytes()
    bg = UnityPy.load(bg_bytes).assets[0]
    for name, ptr in image_pointers:
        assert assets.externals[ptr['m_FileID'] - 1].path == f'archive:/{bg.name}/{bg.name}'
        obj = bg.objects[ptr['m_PathID']]
        assert obj.peek_name() == name and sha(obj.get_raw_data()) == textures[name]['texture_sha256']
    protected[str(bg_path)] = sha(bg_bytes)
    protected[str(catalog_path)] = sha(cb)
    protected[str(catalog_path.with_name('catalog.hash'))] = sha(catalog_path.with_name('catalog.hash').read_bytes())
    for filename in ['ui-tileslayouts_assets_all.bundle', 'settings_assets_all.bundle', 'ui-styles_assets_default.bundle',
                     'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',
                     'ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
        p = folder / filename
        if p.exists():
            protected[str(p)] = sha(p.read_bytes())
    output_file, backup_file = out / tag / G, out / ('backup-' + tag) / G
    output_file.parent.mkdir()
    backup_file.parent.mkdir()
    output_file.write_bytes(payload)
    backup_file.write_bytes(before)
    transaction.append({'target': str(path), 'source': str(output_file), 'backup': str(backup_file), 'before': sha(before), 'after': sha(payload)})
    audits.append({'folder': str(folder), 'changed_object_ids': changed_objects,
                   'all_other_objects_byte_identical': True, 'template_guid': guid,
                   'vta_catalog_preload_and_background_dependency_verified': True,
                   'texture_references_and_original_pixels_verified': True})

for filename in ['current-custom-textures.json', 'reserved-texture-ids.json', 'current-sidebar-version.json']:
    p = R / filename
    protected[str(p)] = sha(p.read_bytes())
for item in transaction:
    assert sha(Path(item['target']).read_bytes()) == item['before']
manifest = {'installed': False, 'runtime_verified': False, 'direction': 'horizontal',
            'left': 'DY', 'right': 'BB', 'image_width_percent': 48, 'gap_percent': 4,
            'height_percent': 100, 'preserve_aspect_and_full_image': True,
            'based_on': 'current non-sidebar game and current independent skin resources',
            'only_change': 'PreferenceBBDYPictureTile inline stylesheet geometry',
            'audits': audits, 'protected_sha256': protected}
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(transaction, ensure_ascii=False, indent=2), 'utf8')
shutil.copy2(R / 'install-independent-resource-patch.py', out / 'installer.py')
shutil.copy2(Path(__file__), out / 'build-source.py')
for action, flag in [('install', ''), ('restore', ' --restore')]:
    (out / (action + '.ps1')).write_text("& '" + sys.executable + "' '" + str(out / 'installer.py') + "' '" + str(out) + "'" + flag + '\n', 'utf8')
(out / 'README.md').write_text(
    '# DY / BB 横向排列\n\n偏好设置快速页的右侧图片单元改为 DY 在左、BB 在右，各宽48%、间距4%、高100%，继续等比完整显示。'
    '只修改当前游戏与独立皮肤包中的该单元内联样式；保留 TFWX、原生卡片、网格、目录、图片ID与其他资源。\n\n'
    'backup-game / backup-skin 为修改前完整备份。游戏退出后可执行 restore.ps1 回退；若目标资源已有后续修改，哈希检查会拒绝覆盖。'
    '构建完成并通过对象逐项比对及引用检查；游戏内显示尚未验证。安装状态见 manifest.json。\n', 'utf8')
print(json.dumps({'output': str(out), 'files_prepared': len(transaction), 'installed': False, 'audits': audits}, ensure_ascii=False), flush=True)
