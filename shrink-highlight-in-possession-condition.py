from pathlib import Path
import json
import re

R = Path(__file__).parent
bootstrap = (R / 'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0]
bootstrap = bootstrap.replace('bench-cards-centered-no-face-number-', 'highlight-in-possession-smaller-condition-')
bootstrap = bootstrap.replace("'NAMES=[W,G]'", "'NAMES=[G]'").replace('bases=(W,G)', 'bases=(G,)')
bootstrap = bootstrap.replace('datetime.timedelta(hours=-6)', 'datetime.timedelta(hours=-7)')
exec(compile(bootstrap, 'load-current-game-and-skin-separately', 'exec'))

size_properties = (131105, 131087, 131097, 131096, 131095, 131094)
ring_name = re.compile(r'MatchCondition_(?:Ring\d+|MissingRing)\Z')
number_name = re.compile(r'MatchCondition_(?:Number\d+|MissingNumber)\Z')
transaction = []
checks = []

for tag, suffix, folder in [('game', '', GAME), ('skin', '::skin', SKIN)]:
    bundle = G + suffix
    doc = Doc(bundle, name='HighlightPhaseSpecificFeetAndCondition')
    original = copy.deepcopy(doc.d)
    original_style = copy.deepcopy(doc.s)
    root = doc.named('MatchCondition_Available')
    gate = doc.named('HighlightInPossessionCondition')
    assert doc.a(root)['m_Parent']['rid'] == gate
    assert doc.data(gate)['Binding']['m_direct']['Path']['m_path'] == 'inpossession'

    def walk(node):
        yield node
        for child in doc.a(node).get('m_Children', []):
            yield from walk(child['rid'])

    def read_px(node, prop):
        rule = doc.s['m_Rules'][doc.a(node)['m_RuleIndex']]
        values = next(p['m_Values'] for p in rule['m_Properties'] if p['m_Id'] == prop)
        assert len(values) == 1 and values[0]['m_ValueType'] == 3
        dimension = doc.s['dimensions'][values[0]['valueIndex']]
        assert dimension['unit'] == 1
        return dimension['value']

    subtree = list(walk(root))
    rings = [node for node in subtree if ring_name.fullmatch(doc.data(node).get('name', ''))]
    numbers = [node for node in subtree if number_name.fullmatch(doc.data(node).get('name', ''))]
    assert len(rings) == len(numbers) == 102
    changed = {root, *rings, *numbers}
    for node in [root, *rings, *numbers]:
        assert all(read_px(node, prop) == 22 for prop in size_properties)
        props = [(prop, doc.px(18)) for prop in size_properties]
        if node in numbers:
            assert read_px(node, 65537) == 8
            props.append((65537, doc.px(7)))
        if node == root:
            # Preserve the centre of the badge while reducing its diameter.
            props.extend((prop, doc.px(read_px(node, prop) + 2)) for prop in (131089, 131104))
        doc.st(node, props)
    expected = copy.deepcopy(original)
    for node, record in refs(expected).items():
        if node in changed:
            record['data']['m_RuleIndex'] = doc.a(node)['m_RuleIndex']
    assert doc.d == expected
    assert doc.s['m_Rules'][:len(original_style['m_Rules'])] == original_style['m_Rules']
    assert all(read_px(node, 131105) == read_px(node, 131087) == 18 for node in changed)
    assert all(read_px(node, 65537) == 7 for node in numbers)
    doc.save()
    raw = env[bundle].file.save(packer='lz4')
    saved = {o.path_id: o for o in UnityPy.load(raw).objects}
    assert set(saved) == set(objs[bundle])
    assert set(changes[bundle]) == {doc.obj.path_id, doc.sid}
    for pid, digest in hashes[bundle].items():
        if pid not in changes[bundle]:
            assert sha(saved[pid].get_raw_data()) == digest
    for pid, tree in changes[bundle].items():
        assert saved[pid].read_typetree() == tree
    validate_ui(saved[doc.obj.path_id].read_typetree(), saved[doc.sid].read_typetree())
    source = OUT / (tag + '-' + G)
    source.write_bytes(raw)
    target = folder / G
    transaction.append({'target': str(target), 'source': str(source), 'backup': str(OUT / ('backup-' + tag) / G), 'before': sha(before[target]), 'after': sha(raw)})
    checks.append({'variant': tag, 'diameter_px': [22, 18], 'font_px': [8, 7], 'ring_and_number_states': len(rings), 'bindings_and_unrelated_objects_unchanged': True})

manifest = {'installed': False, 'runtime_verified': False, 'checks': checks, 'protected_sha256': {}}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transaction, indent=2), 'utf8')
(OUT / 'installer.py').write_bytes((R / 'install-independent-resource-patch.py').read_bytes())
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    command = f"& '{PYTHON}' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot{mode}"
    (OUT / name).write_text("$ErrorActionPreference='Stop'\n" + command + "\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n", 'utf8')
print(OUT)
