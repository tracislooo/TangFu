from pathlib import Path
import json

R = Path(__file__).parent
bootstrap = (R / 'shrink-highlight-in-possession-condition.py').read_text('utf8')
exec(compile(bootstrap[bootstrap.index('bootstrap ='):bootstrap.index('size_properties =')].replace(
    "'highlight-in-possession-smaller-condition-'", "'highlight-stable-formation-cards-'"
), 'load-current-game-and-skin', 'exec'))

names = [
    'HighlightIntegratedHomeStatsAndFormation',
    'HighlightIntegratedAwayStatsAndFormation',
    'HighlightSixColumnsHomeOutOfPossession',
    'HighlightSixColumnsAwayOutOfPossession',
]
transaction = []
checks = []
for tag, suffix, folder in [('game', '', GAME), ('skin', '::skin', SKIN)]:
    bundle = G + suffix
    for name in names:
        doc = Doc(bundle, name=name)
        original = copy.deepcopy(doc.d)
        saved_refs = refs(original)
        targets = []
        for node, record in doc.r.items():
            if record.get('data', {}).get('m_FullTypeName') != 'FM.UI.FMTacticsPanel':
                continue
            data = doc.data(node)
            assert data['TacticPositionsBinding']['m_path'] in (
                'fixture.PastMatchPlayerTacticData', 'tactic.tacticalpositionsmatchinformation'
            )
            mode, flags = 0, 0
            if 'LayoutMode' not in data:
                assert tag == 'skin' and 'LayoutMode_UxmlAttributeFlags' not in data
                continue
            assert data['LayoutMode'] == 1 and data['LayoutMode_UxmlAttributeFlags'] == 1
            data.update(LayoutMode=mode, LayoutMode_UxmlAttributeFlags=flags)
            serial_id = doc.a(node)['m_SerializedData']['rid']
            saved_refs[serial_id]['data'].update(LayoutMode=mode, LayoutMode_UxmlAttributeFlags=flags)
            targets.append(node)
        if not targets:
            assert tag == 'skin'
            continue
        assert sorted(targets) == [1064, 1065, 1083, 1087]
        assert doc.d == original
        validate_ui(doc.d, doc.s)
        doc.obj.save_typetree(doc.d)
        changes[bundle][doc.obj.path_id] = doc.d
        checks.append({'variant': tag, 'template': name, 'pitch_nodes': targets, 'layout_mode': [1, 0]})

    if not changes[bundle]:
        continue
    raw = env[bundle].file.save(packer='lz4')
    saved = {obj.path_id: obj for obj in UnityPy.load(raw).objects}
    assert set(saved) == set(objs[bundle])
    for pid, digest in hashes[bundle].items():
        if pid not in changes[bundle]:
            assert sha(saved[pid].get_raw_data()) == digest
    for pid, tree in changes[bundle].items():
        assert saved[pid].read_typetree() == tree
    source = OUT / (tag + '-' + G)
    source.write_bytes(raw)
    target = folder / G
    transaction.append({'target': str(target), 'source': str(source), 'backup': str(OUT / ('backup-' + tag) / G), 'before': sha(before[target]), 'after': sha(raw)})

manifest = {'installed': False, 'runtime_verified': False, 'checks': checks, 'protected_sha256': {}}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transaction, indent=2), 'utf8')
(OUT / 'installer.py').write_bytes((R / 'install-independent-resource-patch.py').read_bytes())
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    command = f"& '{PYTHON}' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot{mode}"
    (OUT / name).write_text("$ErrorActionPreference='Stop'\n" + command + "\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n", 'utf8')
print(OUT)
