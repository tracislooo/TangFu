"""Migrate only the approved sidebar delta onto current game files; do not install."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import shutil
import struct
import sys

R = Path(__file__).resolve().parent
ARCHIVE = R / 'saved-progress/FM27-sidebar-approved-20261101'
location = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(location['bundle_root']), Path(location['skin_packages'])
assert GAME == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
for file, wanted in [('build-fc-player-hover-layout.py', {'write', 'Styles'}), ('add-card-six-ratings.py', {'validate_ui'})]:
    tree = ast.parse((R / file).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in wanted], type_ignores=[]), file + ':definitions-only', 'exec'))
TypeTreeHelper.write_value = write
sha = lambda b: hashlib.sha256(b).hexdigest()
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
D = 'ui-styles_assets_default.bundle'
M = 'ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
ROW, ROWSTYLE, SIDE, SIDESTYLE = -980000000041001, -980000000041002, -980000000041003, -980000000041004
ROWGUID, SIDEGUID = '2f7f33f147615f32bb80061b0ecda1bf', '2384a857dfa15051ac87a35445fa03ab'
out = R / ('sidebar-approved-rebased-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
outputs, before, reports, checks = {}, {}, [], []

def merge(base, approved, current, path=''):
    """Preserve fields outside the approved delta; reject overlapping scalar edits."""
    if base == approved:
        return copy.deepcopy(current)
    if current == base or current == approved:
        return copy.deepcopy(approved)
    if isinstance(base, dict) and isinstance(approved, dict) and isinstance(current, dict):
        assert base.keys() <= approved.keys() and base.keys() <= current.keys(), path
        result = copy.deepcopy(current)
        for k in approved:
            if k not in base:
                assert k not in current or current[k] == approved[k], (path, k)
                result[k] = copy.deepcopy(approved[k])
            else:
                result[k] = merge(base[k], approved[k], current[k], path + '/' + k)
        return result
    if isinstance(base, list) and isinstance(approved, list) and isinstance(current, list):
        if path.endswith('/RefIds'):
            bm, am, cm = ({v['rid']: v for v in seq} for seq in [base, approved, current])
            result = copy.deepcopy(current)
            for i, item in enumerate(result):
                rid = item['rid']
                if rid in bm:
                    result[i] = merge(bm[rid], am[rid], item, path + '/' + str(rid))
            for item in approved:
                if item['rid'] not in bm:
                    assert item['rid'] not in cm, ('Reference ID collision', path, item['rid'])
                    result.append(copy.deepcopy(item))
            return result
        assert approved[:len(base)] == base, ('Non-additive list conflict', path)
        return copy.deepcopy(current) + [copy.deepcopy(x) for x in approved[len(base):] if x not in current]
    raise AssertionError(('Overlapping edit needs resolution', path, base, approved, current))

def import_style_delta(base, approved, current):
    """Append eight approved rules, resolving pool indices against the current sheet."""
    count = len(base['m_Rules'])
    assert approved['m_Rules'][:count] == base['m_Rules']
    assert len(approved['m_Rules']) - count == 8
    result = copy.deepcopy(current)
    style = Styles(result)
    for rule in approved['m_Rules'][count:]:
        imported = copy.deepcopy(rule)
        for selector in imported['m_ComplexSelectors']:
            selector['ruleIndex'] = len(result['m_Rules'])
        for prop in imported['m_Properties']:
            for h in prop['m_Values']:
                t = h['m_ValueType']
                if t in poolmap:
                    h.update(style.h(t, copy.deepcopy(approved[poolmap[t]][h['valueIndex']])))
        result['m_Rules'].append(imported)
    for key, value in current.items():
        if key == 'm_Rules' or key in set(poolmap.values()):
            assert result[key][:len(value)] == value, ('Existing stylesheet data overwritten', key)
        else:
            assert result[key] == value
    return result

# Verify archive integrity before extracting its delta.
for entry in json.loads((ARCHIVE / 'transaction.json').read_text('utf8')):
    name = Path(entry['target']).name
    assert sha((ARCHIVE / 'packages' / name).read_bytes()) == entry['after']
    assert sha((ARCHIVE / 'non-sidebar-baseline' / name).read_bytes()) == entry['before']

world_objects = None
for name in [W, D, M]:
    target = GAME / name
    before[target] = target.read_bytes()
    old = UnityPy.load(str(ARCHIVE / 'non-sidebar-baseline' / name)).assets[0]
    approved = UnityPy.load(str(ARCHIVE / 'packages' / name)).assets[0]
    env = UnityPy.load(before[target])
    current = env.assets[0]
    assert old.externals == approved.externals == current.externals
    original_raw = {pid: o.get_raw_data() for pid, o in current.objects.items()}
    expected, merged_later_changes = {}, []
    for pid, archived_object in approved.objects.items():
        if pid in old.objects and old.objects[pid].get_raw_data() == archived_object.get_raw_data():
            continue
        if archived_object.type.name == 'AssetBundle':
            continue
        added = pid not in old.objects
        approved_data = archived_object.read_typetree()
        if added:
            assert pid in [ROW, ROWSTYLE, SIDE, SIDESTYLE] and pid not in current.objects
            obj = copy.copy(archived_object)
            obj.assets_file = current
            obj.data = None
            obj._read_until = None
            obj.set_raw_data(archived_object.get_raw_data())
            current.objects[pid] = obj
            expected[pid] = approved_data
        else:
            obj = current.objects[pid]
            base_data, current_data = old.objects[pid].read_typetree(), obj.read_typetree()
            if current_data != base_data:
                merged_later_changes.append({'path_id': pid, 'name': current_data.get('m_Name')})
            if name == D:
                result = import_style_delta(base_data, approved_data, current_data)
            else:
                result = merge(base_data, approved_data, current_data, name + ':' + str(pid))
            obj.save_typetree(result)
            expected[pid] = result

    if name == W:
        ab = next(o for o in current.objects.values() if o.type.name == 'AssetBundle')
        meta = ab.read_typetree()
        previous_meta = copy.deepcopy(meta)
        for guid, pid, sid in [(ROWGUID, ROW, ROWSTYLE), (SIDEGUID, SIDE, SIDESTYLE)]:
            assert all(k != guid for k, _ in meta['m_Container'])
            span = [{'m_FileID': 0, 'm_PathID': sid}, {'m_FileID': 0, 'm_PathID': pid}]
            meta['m_Container'].append((guid, {'preloadIndex': len(meta['m_PreloadTable']), 'preloadSize': 2, 'asset': {'m_FileID': 0, 'm_PathID': pid}}))
            meta['m_PreloadTable'].extend(span)
        meta['m_Container'].sort(key=lambda x: x[0])
        assert meta['m_PreloadTable'][:len(previous_meta['m_PreloadTable'])] == previous_meta['m_PreloadTable']
        # Native containers may contain repeated keys; preserve every entry, including duplicates.
        assert [x for x in meta['m_Container'] if x[0] not in [ROWGUID, SIDEGUID]] == sorted(previous_meta['m_Container'], key=lambda x: x[0])
        ab.save_typetree(meta)
        expected[ab.path_id] = meta

    # Validate every affected template and all untouched object bytes after serialization.
    for pid, doc in expected.items():
        if 'm_VisualTree' in doc:
            sheet_id = doc['inlineSheet']['m_PathID']
            sheet = expected[sheet_id] if sheet_id in expected else current.objects[sheet_id].read_typetree()
            try:
                validate_ui(doc, sheet)
            except AssertionError as error:
                raise AssertionError(('Template validation failed', name, pid, doc.get('m_Name'), len(sheet['m_Rules']))) from error
    payload = env.file.save(packer='lz4')
    checked = UnityPy.load(payload).assets[0]
    assert set(checked.objects) == set(current.objects)
    for pid, obj in checked.objects.items():
        if pid in expected:
            assert obj.read_typetree() == expected[pid], (name, pid)
        else:
            assert obj.get_raw_data() == original_raw[pid], (name, pid)
    outputs[target] = payload
    reports.append({'bundle': name, 'changed_objects': [{'path_id': pid, 'name': doc.get('m_Name')} for pid, doc in expected.items()],
                    'later_changes_merged_in_affected_objects': merged_later_changes, 'all_other_objects_byte_identical': True})
    if name == W:
        world_objects = checked.objects

# Add new template locations to the CURRENT catalog; keep all existing locations and keys.
spec = importlib.util.spec_from_file_location('sidebar_catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog_module)
cp = GAME.parent / 'catalog.bin'
before[cp] = cp.read_bytes()
c = catalog_module.Catalog(before[cp])
original_keys = c.keys()
for guid, source_guid in [(ROWGUID, '55c5e407237e29e43a7ee0feb446fea9'), (SIDEGUID, 'f7baf58db4dbb2940be4a343961ba9ea')]:
    candidates = [x for x in c.locations(source_guid) if c.location(x)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
    assert len(candidates) == 1
    c = catalog_module.Catalog(c.add_key_location(guid, candidates[0], candidates[0]))
label = 'GameWorldVisualTreeAssetPreload'
index = next(i for i, (key, _) in enumerate(c.keys()) if key == label)
key_object, pointer = c.key_records[index]
label_locations = [x[0] for x in c.array(pointer, 'I')] + c.locations(ROWGUID) + c.locations(SIDEGUID)
records = list(c.key_records)
records[index] = (key_object, c.append(b''.join(struct.pack('<I', x) for x in label_locations), True))
struct.pack_into('<I', c.data, 8, c.append(b''.join(struct.pack('<2I', *x) for x in records), True))
cat_bytes = bytes(c.data)
assert cat_bytes[:8] == before[cp][:8] and cat_bytes[12:len(before[cp])] == before[cp][12:]
new_catalog = catalog_module.Catalog(cat_bytes)
new_keys = dict(new_catalog.keys())
old_catalog = catalog_module.Catalog(before[cp])
for key, pointer in original_keys:
    old_locs = [x[0] for x in old_catalog.array(pointer, 'I')]
    actual = [x[0] for x in new_catalog.array(new_keys[key], 'I')]
    assert actual == (label_locations if key == label else old_locs)

for guid, pid in [(ROWGUID, ROW), (SIDEGUID, SIDE)]:
    loc, = new_catalog.locations(guid)
    value = new_catalog.location(loc)
    assert value['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset' and loc in new_catalog.locations(label)
    assert new_catalog.location(value['dependencies'][0])['internal'].replace('\\', '/').endswith('/' + W)
    assert world_objects[pid].type.name == 'MonoBehaviour'
    checks.append({'guid': guid, 'actual_object': world_objects[pid].peek_name(), 'own_bundle_first': True, 'preload_membership': True})
function_guid = '678bbaf2a5da6f54ab4aa7b453f7d150'
function_locations = new_catalog.locations(function_guid)
assert function_locations and all('VisualFunction' in new_catalog.location(x)['type'][1] for x in function_locations)
for loc in function_locations:
    dependency = new_catalog.location(new_catalog.location(loc)['dependencies'][0])['internal'].replace('\\', '/').rsplit('/', 1)[-1]
    functions = UnityPy.load(str(GAME / dependency)).assets[0]
    metadata = next(o.read_typetree() for o in functions.objects.values() if o.type.name == 'AssetBundle')
    pointer = dict(metadata['m_Container'])[function_guid]['asset']
    assert pointer['m_FileID'] == 0 and pointer['m_PathID'] in functions.objects
outputs[cp] = cat_bytes
hp = GAME.parent / 'catalog.hash'
before[hp] = hp.read_bytes()
outputs[hp] = hashlib.md5(cat_bytes).hexdigest().encode('ascii')

# Original skin, fonts, images, settings and other UI files are protected from installation.
protected = {}
for path in list(GAME.glob('ui-*.bundle')) + list(GAME.glob('settings*.bundle')) + [p for p in SKIN.iterdir() if p.is_file()]:
    if path not in outputs:
        protected[str(path)] = sha(path.read_bytes())
for file in ['current-game-location.json', 'current-custom-textures.json', 'reserved-texture-ids.json']:
    protected[str(R / file)] = sha((R / file).read_bytes())
for path in ARCHIVE.rglob('*'):
    if path.is_file():
        protected[str(path)] = sha(path.read_bytes())
tx = []
for target, payload in outputs.items():
    assert target.read_bytes() == before[target], ('Target changed during preparation', target)
    source, backup = out / 'packages' / target.name, out / 'non-sidebar-backup' / target.name
    source.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    source.write_bytes(payload)
    backup.write_bytes(before[target])
    tx.append({'target': str(target), 'source': str(source), 'backup': str(backup), 'before': sha(before[target]), 'after': sha(payload)})
manifest = {'version': 'user-approved V5 sidebar rebased onto current resources', 'installed': False,
            'approved_design_user_confirmed': True, 'rebased_build_runtime_verified': False,
            'sidebar_left_top_width': [0, 0, 100], 'bookmark_source': 'native CurrentSelectedBookmarksList',
            'bookmark_default_preset_installed': False, 'independent_skin_modified': False,
            'settings_and_resolution_config_modified': False, 'global_bundle_modified': False,
            'preserves_latest_game_bugfixes_and_fonts': True, 'bundle_audits': reports, 'catalog_audits': checks,
            'protected_sha256': protected, 'backup_scope': 'current five target files immediately before sidebar installation',
            'source_approved_archive': str(ARCHIVE)}
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
shutil.copy2(R / 'install-independent-resource-patch.py', out / 'installer.py')
shutil.copy2(__file__, out / 'migration-source.py')
for action, flag in [('install-sidebar', ''), ('restore-non-sidebar', ' --restore')]:
    (out / (action + '.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable + "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + flag + "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n", 'utf-8-sig')
(out / 'README.md').write_text(
    '# 认可侧栏迁移到当前资源\n\n以当前游戏资源为基础，仅迁移已认可的 V5 + tactics-header-arrow-fix 侧栏增量。100px竖排原生书签从左上角贯穿到底部，导航和正文位于右侧；保留文字、前进后退留位及16×16编辑箭头。'
    '比赛逆向补偿沿用认可版；比赛模板除补偿标记外保留最新内容，共用战术页仅比赛状态补偿。\n\n'
    '未覆盖旧整包；当前Global包、字体、图片、分辨率设置及原皮肤工程保持不变。14项默认书签仍为未接入的独立源配置，本次沿用原生已保存书签。\n\n'
    'non-sidebar-backup保存本次安装前的5份目标文件，含最新修复。退出游戏后执行restore-non-sidebar.ps1可回退；若后续资源发生变化，哈希检查会拒绝覆盖。安装状态见manifest.json。\n\n'
    '离线对象逐项、目录与预加载检查通过；迁移后游戏内显示尚未验证。\n', 'utf8')
print(json.dumps({'output': str(out), 'prepared_files': len(tx), 'bundle_audits': reports, 'catalog_audits': checks, 'installed': False}, ensure_ascii=False), flush=True)
