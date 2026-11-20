from pathlib import Path
import re
import subprocess

bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(compile(bootstrap.replace('inspect-fitness-backdrop-', 'tactics-columns-25-35-40-'), 'bundle-helpers', 'exec'))
source = ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'selector'], type_ignores=[]), 'selectors', 'exec'))
stylesheet_bundle = 'ui-styles_assets_default.bundle'
scale = struct.unpack('<f', struct.pack('<f', .85))[0]
outputs, checks = {}, []

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder/W])
    objs[W] = {o.path_id: o for o in env[W].objects}
    changes[W] = {}
    hashes[W] = {pid: sha(o.get_raw_data()) for pid, o in objs[W].items()}
    shape = Doc(W, name='TacticalPlannerTeamShape')
    proportions = [('PitchesWidthStyleSetter', 60), ('TableAndUnderstandingColumn', 40),
                   ('CombinedPitchColumn', 25), ('StackedPhasesColumn', 35)]
    original = copy.deepcopy(shape.d)
    nodes = set()
    for name, weight in proportions:
        node = shape.named(name)
        shape.st(node, [(131084, shape.num(weight))])
        nodes.add(node)
    for rid, record in refs(original).items():
        expected = copy.deepcopy(record)
        if rid in nodes:
            expected['data']['m_RuleIndex'] = shape.a(rid)['m_RuleIndex']
        assert expected == shape.r[rid]
    shape.save()
    result = env[W].file.save(packer='lz4')
    saved = {o.path_id: o for o in UnityPy.load(result).objects}
    assert saved.keys() == objs[W].keys()
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid]
        else:
            assert sha(obj.get_raw_data()) == hashes[W][pid]
    outputs[folder/W] = result

    # The shortcut element wraps the entire interactive card. The pitch's
    # positioning root keeps its original size and transform.
    detailed = Doc(W, name='TacticsPositionDetailed')
    shortcut = detailed.named('radial-shortcut')
    index = detailed.a(shortcut).get('m_RuleIndex', -1)
    if index >= 0:
        assert all(p['m_Id'] != 327681 for p in detailed.s['m_Rules'][index]['m_Properties'])
    path = folder/stylesheet_bundle
    before[path] = path.read_bytes()
    protected.pop(path, None)
    (OUT/('backup-'+tag)/stylesheet_bundle).write_bytes(before[path])
    style_env = UnityPy.load(before[path])
    style_objects = {o.path_id: o for o in style_env.objects}
    style_hashes = {i: sha(o.get_raw_data()) for i, o in style_objects.items()}
    edited = {}
    for obj in style_objects.values():
        if obj.type.name != 'MonoBehaviour' or obj.peek_name() not in ['AlwaysAppliedStyleSheet', 'FigmaGeneratedStyles']:
            continue
        sheet = obj.read_typetree()
        sheet['floats'].append(scale)
        handle = {'m_ValueType': 2, 'valueIndex': len(sheet['floats'])-1}
        sheet['m_Rules'].append({
            'm_ComplexSelectors': [selector('#StackedPhasesColumn .tactics-position-layout #radial-shortcut', len(sheet['m_Rules']))],
            'm_Properties': [{'m_Id': 327681, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [handle, copy.deepcopy(handle)]}],
            'line': -1,
        })
        obj.save_typetree(sheet)
        edited[obj.path_id] = sheet
    assert len(edited) == 2
    result = style_env.file.save(packer='lz4')
    for obj in UnityPy.load(result).objects:
        if obj.path_id in edited:
            assert obj.read_typetree() == edited[obj.path_id]
        else:
            assert sha(obj.get_raw_data()) == style_hashes[obj.path_id]
    outputs[path] = result
    checks.append({'target': tag, 'column_width_weights': [25, 35, 40], 'middle_card_scale': .85,
                   'middle_card_scope': 'StackedPhasesColumn', 'roundtrip': True})

for p, data in outputs.items():
    tag = 'game' if p.parent == GAME else 'skin'
    (OUT/('output-'+tag)).mkdir(exist_ok=True)
    (OUT/('output-'+tag)/p.name).write_bytes(data)

G = W
tail = Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail = "for p,b in before.items():\n if p.name.startswith('catalog.')" + tail
tail = tail.replace("OUT/('backup-'+tag)/G", "OUT/('backup-'+tag)/p.name").replace("OUT/('output-'+tag)/G", "OUT/('output-'+tag)/p.name")
tail = tail.replace(' restore.append("Copy-Item', ' restore.append("if ((Get-FileHash -LiteralPath \'"+str(p)+"\').Hash.ToLower() -ne \'"+sha(outputs[p])+"\') { throw \'Target changed since installation.\' }")\n restore.append("Copy-Item')
start = tail.index("(OUT/'修改说明.md').write_text(")
end = tail.index('\nprint(', start)
tail = tail[:start] + "(OUT/'修改说明.md').write_text('战术三栏按可用宽度25/35/40分配。仅中间都包括的两块球场球员卡整体缩至85%。游戏及独立皮肤分别安装，资源校验通过，实际显示待确认。','utf8')" + tail[end:]
exec(compile(tail, 'verify-and-install', 'exec'))
