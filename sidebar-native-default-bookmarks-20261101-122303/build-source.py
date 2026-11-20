"""Prepare a native desktop-club bookmark preset without changing other manager lists."""
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
import winreg

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
tree = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'write'], type_ignores=[]), '<writer-only>', 'exec'))
TypeTreeHelper.write_value = write
location = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(location['bundle_root']), Path(location['skin_packages'])
BUNDLE = 'gamemodules_assets_gameworld.bundle'
path = GAME / BUNDLE
before = path.read_bytes()
env = UnityPy.load(before)
assets = env.assets[0]
objects = assets.objects
original_raw = {pid: o.get_raw_data() for pid, o in objects.items()}
infos = {o.peek_name(): o for o in objects.values() if o.type.name == 'MonoBehaviour'}
original_list = infos['ClubManagerBookmarks']
list_data = original_list.read_typetree()
preset = json.loads((R / 'sidebar-bookmark-defaults-20261101/default-bookmarks.json').read_text('utf8'))
names = ['MessagesBookmark', 'FirstTeamBookmark', 'DynamicsBookmark', 'FirstTeamBookmark',
         'DataHubBookmark', 'ClubStaffBookmark', 'TrainingBookmark', 'MedicalCentreBookmark',
         'FixtureScheduleBookmark', 'CompetitionStatusBookmark', 'PlayerRecommendationsBookmark',
         'ClubSiteBookmark', 'FinancesBookmark', 'YouthSetupBookmark']
desired, expected, selected = [], {}, []
banned = {int(x['path_id']) for x in json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
banned |= {-910000000000001, -910000000000002, -910000000000146}

# Native top-nav translation IDs for Tactics and Club; keep native BookmarkInfo labels elsewhere.
world = UnityPy.load(str(GAME / 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).assets[0]
menu = next(o.read_typetree() for o in world.objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'MenuBar')
refs = {r['rid']: r for r in menu['references']['RefIds']}
def primary_label(button):
    node = next(r for r in refs.values() if refs.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == button)
    data = next(refs[v['m_SerializedData']['rid']]['data'] for v in node['data']['m_SerializedDataOverride']
                if 'TextBinding' in refs[v['m_SerializedData']['rid']]['data'])
    payload = bytes(data['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    arg = payload[5:]
    assert arg[0] < 128
    return struct.unpack_from('<i', arg, 1 + arg[0])[0]

def clone_info(source, data, ordinal):
    pid = -980000000042000 - ordinal
    assert pid not in objects and pid not in banned
    obj = copy.copy(source)
    obj.path_id, obj.assets_file = pid, assets
    obj.data, obj._read_until = None, None
    obj.set_raw_data(source.get_raw_data())
    objects[pid] = obj
    obj.save_typetree(data)
    expected[pid] = copy.deepcopy(data)
    return {'m_FileID': 0, 'm_PathID': pid}

for i, (entry, name) in enumerate(zip(preset['entries'], names), 1):
    source = infos[name]
    data = source.read_typetree()
    native = entry['native_property_value']
    # Use the native navigation route only when the existing bookmark has a different destination.
    # Matching native bookmarks retain their original arguments, indicators and navigation contexts.
    if data['m_panelIDRef'] != native['m_panelIDRef']:
        data['m_panelIDRef'] = copy.deepcopy(native['m_panelIDRef'])
        data['m_panelUID'] = native['m_panelUID']
        data['m_openEvent'] = copy.deepcopy(native['m_openEvent'])
    if entry['label_zh'] == '战术':
        data['m_mainPanelIDRef'] = copy.deepcopy(native['m_panelIDRef'])
        data['m_displayValue'] = {'GameID': primary_label('ClubTacticsButton')}
        data['m_iconStyle'] = 'game-concepts-tactics_medium'
        data['m_indicatorType'] = 0
    elif entry['label_zh'] == '球探':
        data['m_displayValue'] = copy.deepcopy(native['m_displayValue'])
    elif entry['label_zh'] == '俱乐部':
        data['m_displayValue'] = {'GameID': primary_label('ClubButton')}
    data['m_Name'] = 'TFSidebarDefault_' + str(i) + '_' + entry['label_zh']
    data['m_isDefaultSelection'] = -1
    desired.append(clone_info(source, data, i))
    selected.append(data['m_panelUID'])
    entry['actual_bookmark_path_id'] = desired[-1]['m_PathID']
    entry['actual_panel_uid'] = data['m_panelUID']
    entry['actual_label_game_id'] = data['m_displayValue']['GameID']

# Keep every original optional bookmark available for editing, without changing shared originals.
for old_pointer in list_data['m_bookmarks']:
    source = objects[old_pointer['m_PathID']]
    data = source.read_typetree()
    if data['m_panelUID'] in selected:
        continue
    data['m_Name'] = 'TFSidebarOptional_' + data['m_Name']
    data['m_isDefaultSelection'] = 0
    desired.append(clone_info(source, data, len(desired) + 1))
list_data['m_bookmarks'] = desired
original_list.save_typetree(list_data)
expected[original_list.path_id] = list_data
assert len(selected) == len(set(selected)) == 14
assert [expected[p['m_PathID']]['m_panelUID'] for p in desired[:14]] == selected
assert sum(expected[p['m_PathID']]['m_isDefaultSelection'] != 0 for p in desired) == 14

# Preserve every existing preload span; extend only exports that depend on the club list.
metadata_object = next(o for o in objects.values() if o.type.name == 'AssetBundle')
metadata = metadata_object.read_typetree()
preload_changes = []
for key, value in metadata['m_Container']:
    span = metadata['m_PreloadTable'][value['preloadIndex']:value['preloadIndex'] + value['preloadSize']]
    if any(p == {'m_FileID': 0, 'm_PathID': original_list.path_id} for p in span):
        new_span = span + [p for p in desired if p not in span]
        value['preloadIndex'], value['preloadSize'] = len(metadata['m_PreloadTable']), len(new_span)
        metadata['m_PreloadTable'].extend(new_span)
        preload_changes.append({'guid': key, 'asset': value['asset'], 'before_size': len(span), 'after_size': len(new_span)})
assert preload_changes
metadata_object.save_typetree(metadata)
expected[metadata_object.path_id] = metadata
payload = env.file.save(packer='lz4')
checked = UnityPy.load(payload).assets[0]
assert set(checked.objects) == set(objects)
for pid, obj in checked.objects.items():
    if pid in expected:
        assert obj.read_typetree() == expected[pid], pid
    else:
        assert obj.get_raw_data() == original_raw[pid], pid

# Validate actual native PanelID addresses and module ownership using the current catalog.
spec = importlib.util.spec_from_file_location('bookmark_catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
catalog = cm.Catalog((GAME.parent / 'catalog.bin').read_bytes())
panels_env = UnityPy.load(str(GAME / 'ui-panelids_assets_all.bundle')).assets[0]
panel_metadata = next(o.read_typetree() for o in panels_env.objects.values() if o.type.name == 'AssetBundle')
panel_container = dict(panel_metadata['m_Container'])
for p in desired[:14]:
    d = expected[p['m_PathID']]
    for key in ['m_panelIDRef', 'm_mainPanelIDRef']:
        guid = d[key]['m_AssetGUID']
        assert catalog.locations(guid) and guid in panel_container
        ref = panel_container[guid]['asset']
        assert ref['m_FileID'] == 0 and ref['m_PathID'] in panels_env.objects
for change in preload_changes:
    assert catalog.locations(change['guid'])
    assert any(catalog.location(catalog.location(loc)['dependencies'][0])['internal'].replace('\\', '/').endswith('/' + BUNDLE)
               for loc in catalog.locations(change['guid']))

out = R / ('sidebar-native-default-bookmarks-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
source, backup = out / 'packages' / BUNDLE, out / 'backup-game' / BUNDLE
source.parent.mkdir()
backup.parent.mkdir()
source.write_bytes(payload)
backup.write_bytes(before)
KEY, NAME = r'Software\Sports Interactive\Football Manager 27', 'SelectedBookmarksKey_h3185478356'
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY) as key:
    preference, kind = winreg.QueryValueEx(key, NAME)
assert kind == winreg.REG_BINARY and isinstance(preference, bytes)
new_preference = (','.join(map(str, selected)) + ',').encode('ascii') + b'\0'
prefs = {'key': KEY, 'name': NAME, 'kind': kind, 'before_hex': preference.hex(), 'after_hex': new_preference.hex()}
(out / 'bookmark-preference.json').write_text(json.dumps(prefs, ensure_ascii=False, indent=2), 'utf8')
protected = {str(p): sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle')) + list(GAME.glob('settings*.bundle')) + [p for p in SKIN.iterdir() if p.is_file()]}
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', R / 'current-custom-textures.json', R / 'reserved-texture-ids.json']:
    protected[str(p)] = sha(p.read_bytes())
assert path.read_bytes() == before
tx = [{'target': str(path), 'source': str(source), 'backup': str(backup), 'before': sha(before), 'after': sha(payload)}]
m = {'installed': False, 'runtime_verified': False, 'default_bookmark_count': 14,
     'default_order': [x['label_zh'] for x in preset['entries']], 'selected_panel_uids': selected,
     'scope': 'desktop club manager native bookmarks', 'original_other_manager_lists_and_shared_bookmarks_unchanged': True,
     'original_optional_bookmarks_retained': True, 'catalog_modified': False, 'new_standalone_addressable_assets': False,
     'all_unrelated_objects_byte_identical': True, 'preload_audits': preload_changes,
     'saved_club_bookmark_preference_updated_on_install': True, 'protected_sha256': protected}
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
(out / 'integrated-bookmarks.json').write_text(json.dumps(preset, ensure_ascii=False, indent=2), 'utf8')
shutil.copy2(R / 'install-sidebar-bookmark-defaults.py', out / 'installer.py')
shutil.copy2(__file__, out / 'build-source.py')
for action, flag in [('install', ''), ('restore-bookmarks', ' --restore')]:
    (out / (action + '.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable + "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + flag + "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n", 'utf-8-sig')
(out / 'README.md').write_text(
    '# 原生默认书签14项\n\n默认顺序：' + ' → '.join(m['default_order']) + '。\n\n'
    '接入桌面俱乐部经理原生ClubManagerBookmarks列表，并同步当前用户的SelectedBookmarksKey单项偏好。'
    '保留原生点击、消息提示、编辑和其他可选书签；普通版动态和战术使用原生导航参数。其他模式书签、分辨率、存档和独立皮肤工程不改。\n\n'
    'backup-game与bookmark-preference.json保存安装前资源和该项偏好。退出游戏后restore-bookmarks.ps1撤销本次书签修改；后续版本变化时哈希检查会拒绝覆盖。'
    '实际显示与跳转尚需游戏内确认。\n', 'utf8')
print(json.dumps({'output': str(out), 'default_count': 14, 'available_count': len(desired), 'selected_uids': selected,
                  'original_objects_changed': [original_list.path_id, metadata_object.path_id], 'installed': False}, ensure_ascii=False))
