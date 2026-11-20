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
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BG = GAME / 'ui-backgrounds_assets_common.bundle'
PID = -910000000000003
sha = lambda data: hashlib.sha256(data).hexdigest()
source_bytes = BG.read_bytes()
before = {folder / WN: (folder / WN).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME / WN] == before[SKIN / WN], 'Game/skin UI versions differ'
protected_paths = [GAME / n for n in ['ui-backgrounds_assets_common.bundle',
    'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle', 'ui-visualfunctions_assets_all.bundle',
    'ui-tileslayouts_assets_all.bundle']]
protected_paths += [GAME.parent / 'catalog.bin']
protected = {p: sha(p.read_bytes()) for p in protected_paths}
bg_env = UnityPy.load(source_bytes)
src = next(o for o in bg_env.objects if o.path_id == PID)
env = UnityPy.load(before[GAME / WN]); objects = {o.path_id: o for o in env.objects}
dst = objects[PID]
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
replacement, original = src.read_typetree(), dst.read_typetree()
assert src.type.name == dst.type.name == 'Texture2D'
assert replacement['m_Name'] == original['m_Name'] == 'CA000'
assert set(original) == set(replacement)
assert replacement['m_StreamData']['size'] == 0
assert src.get_raw_data() != dst.get_raw_data(), 'CA000 already synchronized'
pixels = src.read().image
assert pixels.size == (replacement['m_Width'], replacement['m_Height'])
dst.save_typetree(replacement)
output = env.file.save(packer='lz4')
saved = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(saved) == set(objects)
for i, obj in saved.items():
    if i == PID:
        assert obj.read_typetree() == replacement
        assert obj.read().image.tobytes() == pixels.tobytes()
    else: assert sha(obj.get_raw_data()) == hashes[i], ('Unrelated asset changed', i)
for p, data in before.items(): assert p.read_bytes() == data
for p, h in protected.items(): assert sha(p.read_bytes()) == h

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out = R / ('relink-CA000-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'source': str(BG),
    'source_sha256': sha(source_bytes), 'changed_bundle': WN, 'changed_texture': 'CA000',
    'changed_path_id': PID, 'source_texture_sha256': sha(src.get_raw_data()),
    'old_texture_sha256': hashes[PID], 'size': list(pixels.size),
    'unchanged_objects_verified': len(hashes) - 1, 'other_CA_tiers_layout_and_bindings_preserved': True,
    'before_sha256': {str(p): sha(data) for p, data in before.items()}, 'after_sha256': sha(output),
    'protected_sha256': {str(p): h for p, h in protected.items()}}
manifest = out / 'manifest.json'
manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
if '--install' in sys.argv:
    try:
        for folder in [GAME, SKIN]:
            (folder / WN).write_bytes(output)
            assert (folder / WN).read_bytes() == output
        for p, h in protected.items(): assert sha(p.read_bytes()) == h
    except Exception:
        for p, data in before.items(): p.write_bytes(data)
        raise
    report['installed'] = True
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(out), 'installed': report['installed'],
    'unchanged_objects_verified': report['unchanged_objects_verified'], 'after_sha256': report['after_sha256']}, indent=2))
