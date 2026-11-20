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
N = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BG = GAME / 'ui-backgrounds_assets_common.bundle'
OUT = R / ('同步background新CA卡面-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
source = BG.read_bytes()
before = {folder / N: (folder / N).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME / N] == before[SKIN / N], 'Game/skin UI bundle versions differ.'
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    (OUT / ('backup-' + tag + '.bundle')).write_bytes(before[folder / N])
protected = {GAME / name: sha((GAME / name).read_bytes()) for name in [
    'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
    'ui-tileslayouts_assets_all.bundle', 'ui-backgrounds_assets_common.bundle']}
protected[GAME.parent / 'catalog.bin'] = sha((GAME.parent / 'catalog.bin').read_bytes())
be = UnityPy.load(source)
bo = {o.path_id: o for o in be.objects}
env = UnityPy.load(before[GAME / N]); objects = {o.path_id: o for o in env.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
changed = {}; details = []
for pid, name in [(-910000000000003, 'CA000'), (-910000000000004, 'CA120'),
                  (-910000000000005, 'CA140'), (-910000000000006, 'CA160'), (-910000000000007, 'CA180')]:
    src = bo[pid]; dst = objects[pid]
    assert src.type.name == dst.type.name == 'Texture2D'
    original = dst.read_typetree(); replacement = src.read_typetree()
    assert replacement['m_Name'] == original['m_Name'] == name
    assert not replacement['m_StreamData']['size'], 'Texture requires an additional streamed resource.'
    assert set(original) == set(replacement), 'Texture serialization schemas differ.'
    # Decode the source once to verify its compressed texture payload is readable.
    decoded = src.read().image
    assert decoded.size == (replacement['m_Width'], replacement['m_Height'])
    changed[pid] = replacement
    dst.save_typetree(replacement)
    details.append({'name': name, 'path_id': pid, 'old_size': [original['m_Width'], original['m_Height']],
                    'new_size': [replacement['m_Width'], replacement['m_Height']],
                    'source_texture_sha256': sha(src.get_raw_data())})
data = env.file.save(packer='lz4')
(OUT / N).write_bytes(data)
saved = {o.path_id: o for o in UnityPy.load(data).objects}
assert set(saved) == set(objects)
for pid, obj in saved.items():
    if pid in changed:
        assert obj.read_typetree() == changed[pid]
        assert obj.read().image.tobytes() == bo[pid].read().image.tobytes()
    else:
        assert sha(obj.get_raw_data()) == hashes[pid], ('Unrelated asset changed', pid)
for path, old in before.items(): assert path.read_bytes() == old
assert BG.read_bytes() == source
try:
    for path in before:
        path.write_bytes(data)
        assert path.read_bytes() == data
except Exception:
    for path, old in before.items(): path.write_bytes(old)
    raise
for path, expected in protected.items(): assert sha(path.read_bytes()) == expected
report = {'installed': True, 'runtime_verified': False, 'source': str(BG), 'source_sha256': sha(source),
          'textures': details, 'unchanged_objects_verified': len(hashes) - len(changed),
          'layout_and_bindings_preserved': True,
          'before_sha256': {str(p): sha(b) for p, b in before.items()}, 'after_sha256': sha(data)}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), **report}, ensure_ascii=False, indent=2))
