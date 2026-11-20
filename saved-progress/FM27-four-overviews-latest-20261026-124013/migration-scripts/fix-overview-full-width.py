import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
N = 'ui-tileslayouts_assets_all.bundle'
SAVED = Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
FULL_GUID = '1f6ebbeeaeba50cbbb57ef2d123b47dc'
SIMPLE_GUID = '76cd79feada45acebc482721c1b688da'
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT = R / ('概览上方区域全宽修正-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
before = {(GAME / N): (GAME / N).read_bytes(), (SKIN / N): (SKIN / N).read_bytes()}
assert before[GAME / N] == before[SKIN / N], 'Game and skin layout bundles differ.'
for tag, path in [('game', GAME / N), ('skin', SKIN / N)]:
    (OUT / ('backup-' + tag + '.bundle')).write_bytes(before[path])
saved_before = SAVED.read_bytes() if SAVED.exists() else None
if saved_before is not None:
    before[SAVED] = saved_before
    (OUT / 'backup-saved-layout.json').write_bytes(saved_before)
protected = {n: sha((GAME / n).read_bytes()) for n in [
    'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
    'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',
    'ui-backgrounds_assets_common.bundle']}

env = UnityPy.load(before[GAME / N]); objects = {o.path_id: o for o in env.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
obj = next(o for o in objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'PlayerReportOverviewComposition-Large')
doc = obj.read_typetree(); original = copy.deepcopy(doc)
slot = next(c for c in doc['m_gridComponents'] if c['m_elementID'] == 'PlayerAttributesBlock')
assert slot['m_maxSize'] == {'x': 20, 'y': 7}
assert len(slot['m_gridElementConfigs']) == 1
assert slot['m_gridElementConfigs'][0]['AssetRef']['m_AssetGUID'] == FULL_GUID
slot['m_maxSize']['x'] = 100
expected = copy.deepcopy(original)
next(c for c in expected['m_gridComponents'] if c['m_elementID'] == 'PlayerAttributesBlock')['m_maxSize']['x'] = 100
assert doc == expected
assert doc['m_gridComponents'][1:] == original['m_gridComponents'][1:]
obj.save_typetree(doc)
data = env.file.save(packer='lz4')
(OUT / N).write_bytes(data)
reread = {o.path_id: o for o in UnityPy.load(data).objects}
assert set(reread) == set(objects)
for i, h in hashes.items():
    if i == obj.path_id: assert reread[i].read_typetree() == doc
    else: assert sha(reread[i].get_raw_data()) == h, ('Unrelated asset changed', i)

targets = {GAME / N: data, SKIN / N: data}
if saved_before is not None:
    saved = json.loads(saved_before.decode('utf-8-sig')); old_saved = copy.deepcopy(saved)
    tops = [c for c in saved['m_gridComponents'] if any(
        cfg.get('AssetRef', {}).get('m_AssetGUID') in [FULL_GUID, SIMPLE_GUID] for cfg in c['m_gridElementConfigs'])]
    assert len(tops) == 1
    top = tops[0]
    assert len(top['m_gridElementConfigs']) == len(top['m_configDescriptionKeys']) == 1
    assert top['m_minSize']['x'] == 20 and top['m_maxSize']['y'] == 7
    top['m_maxSize']['x'] = 100
    check = copy.deepcopy(saved)
    next(c for c in check['m_gridComponents'] if c['m_elementID'] == top['m_elementID'])['m_maxSize']['x'] = 20
    assert check == old_saved, 'Saved layout changes exceed the width limit.'
    saved_data = json.dumps(saved, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    (OUT / 'modified-saved-layout.json').write_bytes(saved_data)
    targets[SAVED] = saved_data

for path, old in before.items(): assert path.read_bytes() == old, ('Target changed while building', str(path))
try:
    for path, content in targets.items():
        path.write_bytes(content)
        assert path.read_bytes() == content
except Exception:
    for path, content in before.items(): path.write_bytes(content)
    raise
for name, expected_hash in protected.items(): assert sha((GAME / name).read_bytes()) == expected_hash
report = {
    'installed': True, 'runtime_verified': False,
    'change': 'Restore top overview tile horizontal expansion: max columns 20 -> 100; minimum 20 and height 7 unchanged.',
    'changed_asset': obj.path_id, 'saved_layout_updated': saved_before is not None,
    'native_swap_dropdown_preserved': True, 'bottom_tile_selections_preserved': True,
    'unchanged_layout_objects_verified': len(hashes) - 1,
    'protected_game_sha256': protected,
    'before_sha256': {str(p): sha(b) for p, b in before.items()},
    'after_sha256': {str(p): sha(b) for p, b in targets.items()},
}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), **report}, ensure_ascii=False, indent=2))
