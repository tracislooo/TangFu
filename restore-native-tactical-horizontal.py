from pathlib import Path
import subprocess

helper_path = Path(__file__).with_name('inspect-fitness-backdrop.py')
helpers = helper_path.read_text('utf-8-sig').split('for name in [')[0]
helpers = helpers.replace('inspect-fitness-backdrop-', 'tactical-native-horizontal-').replace('hours=-4', 'hours=-7')
exec(compile(helpers, 'bundle-helpers', 'exec'))

first_patch = R / 'tactical-percent-gauges-20261108-133140'
current_index = R / 'current-tactical-percent-gauges.json'
previous_patch = Path(json.loads(current_index.read_text('utf8'))['patch'])
name = 'TacticalEffectivenessGauge'
outputs = {}
checks = []

def read_patch_bundle(patch, target, role):
    row = next(row for row in json.loads((patch / 'transaction.json').read_text('utf8'))
               if Path(row['target']) == target)
    data = Path(row[role]).read_bytes()
    assert sha(data) == row['before' if role == 'backup' else 'after'], (patch, target)
    return {obj.path_id: obj for obj in UnityPy.load(data).objects}

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    target = folder / W
    env[W] = UnityPy.load(before[target])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    current = Doc(W, name=name)
    pid, sid = current.obj.path_id, current.sid

    previous = read_patch_bundle(previous_patch, target, 'source')
    donor = read_patch_bundle(first_patch, target, 'source')
    native = read_patch_bundle(first_patch, target, 'backup')
    for object_id in (pid, sid):
        assert objs[W][object_id].get_raw_data() == previous[object_id].get_raw_data(), ('Target template changed', tag, object_id)
        source_externals = donor[object_id].assets_file.externals
        target_externals = objs[W][object_id].assets_file.externals
        assert [ext.name for ext in source_externals] == [ext.name for ext in target_externals[:len(source_externals)]]

    restored = Doc(W, pid=pid, tree=donor[pid].read_typetree(), style=donor[sid].read_typetree())
    assert restored.sid == sid
    native_refs = refs(native[pid].read_typetree())
    assert [c['rid'] for c in restored.a(1010)['m_Children']][:2] == [1012, 1021]
    for node in (1012, 1016, 1017, 1023, 1024, 1026, 1027):
        assert restored.r[node] == native_refs[node]
        assert restored.data(node) == sd(native_refs, node)
    for node, width in [(1030, 27), (1031, 78)]:
        assert restored.data(node)['TextBinding'] == current.data(node)['TextBinding']
        restored.size(node, width, 24)
        restored.st(node, [(65546, restored.enum('middle-right')),
                           (131090, restored.px(4)), (131093, restored.px(0))])
    restored.save()
    assert set(changes[W]) == {pid, sid}
    data = env[W].file.save(packer='lz4')
    saved = {obj.path_id: obj for obj in UnityPy.load(data).objects}
    assert saved.keys() == objs[W].keys()
    for object_id, obj in saved.items():
        if object_id in changes[W]:
            assert obj.read_typetree() == changes[W][object_id]
        else:
            assert obj.get_raw_data() == objs[W][object_id].get_raw_data(), (tag, object_id)
    outputs[target] = data
    destination = OUT / ('output-' + tag)
    destination.mkdir()
    (destination / W).write_bytes(data)
    checks.append({'target': tag, 'native_steppers': 4, 'percent_and_range_bindings_preserved': True})

for target, original in before.items():
    assert target.read_bytes() == original, ('Concurrent change', target)
protected.update({target: sha(data) for target, data in before.items() if target not in outputs})
transaction = []
for target, data in outputs.items():
    tag = 'game' if target.parent == GAME else 'skin'
    transaction.append({'target': str(target), 'backup': str(OUT / ('backup-' + tag) / W),
                        'source': str(OUT / ('output-' + tag) / W),
                        'before': sha(before[target]), 'after': sha(data)})

manifest = {'installed': False, 'runtime_verified': False, 'checks': checks,
            'scope': 'Native horizontal tactical effectiveness gauges with percentage labels',
            'protected_sha256': {str(path): digest for path, digest in protected.items()}}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transaction, indent=2), 'utf8')
installer = R / 'install-independent-resource-patch.py'
for filename, flag in [('install.ps1', ''), ('restore.ps1', ' --restore')]:
    (OUT / filename).write_text(f"& '{PYTHON}' '{installer}' $PSScriptRoot{flag}\n", 'utf8')
print(OUT, flush=True)
subprocess.run([str(PYTHON), str(installer), str(OUT)], check=True)
current_index.write_text(json.dumps({'patch': str(OUT), 'installed': True, 'runtime_verified': False,
                                     'manifest': str(OUT / 'manifest.json')}, indent=2), 'utf8')
