from pathlib import Path
import re
import subprocess

bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(compile(bootstrap.replace('inspect-fitness-backdrop-', 'tactics-centered-phase-titles-'), 'bundle-helpers', 'exec'))
source = ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'selector'], type_ignores=[]), 'selectors', 'exec'))
stylesheet_bundle = 'ui-styles_assets_default.bundle'
outputs, checks = {}, []

def update_sheet(sheet):
    def px(n):
        sheet['dimensions'].append({'unit': 1, 'value': float(n)})
        return {'m_ValueType': 3, 'valueIndex': len(sheet['dimensions'])-1}

    def number(n):
        sheet['floats'].append(float(n))
        return {'m_ValueType': 2, 'valueIndex': len(sheet['floats'])-1}

    def property_for(selector_text, property_id):
        matches = [p for i, rule in enumerate(sheet['m_Rules'])
                   if rule['m_ComplexSelectors'] == [selector(selector_text, i)]
                   for p in rule['m_Properties'] if p['m_Id'] == property_id]
        assert len(matches) == 1, (selector_text, property_id)
        return matches[0]

    cap = property_for('#StackedPhasesColumn .tactics-collapsable-pitch-expanded', 131094)
    assert sheet['dimensions'][cap['m_Values'][0]['valueIndex']]['value'] == 244
    cap['m_Values'] = [px(288)]
    scale = property_for('#StackedPhasesColumn .tactics-position-layout #radial-shortcut', 327681)
    assert len(scale['m_Values']) == 2
    assert all(abs(sheet['floats'][h['valueIndex']] - .85) < 1e-6 for h in scale['m_Values'])
    scale['m_Values'] = [number(.75), number(.75)]


for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder/W])
    objs[W] = {o.path_id: o for o in env[W].objects}
    hashes[W] = {pid: sha(o.get_raw_data()) for pid, o in objs[W].items()}
    changes[W] = {}
    shape = Doc(W, name='TacticalPlannerTeamShape')
    for name in ['CombinedPitchTitle', 'BothPhasesTitle']:
        shape.st(shape.named(name), [(131081, shape.enum('none'))])
    for name in ['InPossessionTitle', 'OutOfPossessionTitle']:
        shape.st(shape.named(name), [(131105, shape.px(452)),
                                    (131074, shape.enum('center')),
                                    (65546, shape.enum('middle-center'))])
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
        update_sheet(sheet)
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
    checks.append({'target': tag, 'column_ratios': [25, 35, 40], 'mid_card_scale': .75, 'phase_titles_centered_above_pitch': True,
                   'fixed_pitch_width_px': [384,452,452], 'pitch_max_height_px': [620,288,288], 'renderer_uxml_unchanged': True, 'roundtrip': True})

for path, data in outputs.items():
    tag = 'game' if path.parent == GAME else 'skin'
    (OUT/('output-'+tag)).mkdir(exist_ok=True)
    (OUT/('output-'+tag)/path.name).write_bytes(data)

G = W
tail = Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail = "for p,b in before.items():\n if p.name.startswith('catalog.')" + tail
tail = tail.replace("OUT/('backup-'+tag)/G", "OUT/('backup-'+tag)/p.name").replace("OUT/('output-'+tag)/G", "OUT/('output-'+tag)/p.name")
tail = tail.replace(' restore.append("Copy-Item', ' restore.append("if ((Get-FileHash -LiteralPath \'"+str(p)+"\').Hash.ToLower() -ne \'"+sha(outputs[p])+"\') { throw \'Target changed since installation.\' }")\n restore.append("Copy-Item')
start = tail.index("(OUT/'修改说明.md').write_text(")
end = tail.index('\nprint(', start)
tail = tail[:start] + "(OUT/'修改说明.md').write_text('隐藏合并阵型和都包括标题。两阶段标题各自居中于球场正上方。中栏球场最大高度244→288px，球员卡缩至75%。固定球场宽度及绘制参数沿用已确认可见版本，实际效果待游戏验收。','utf8')" + tail[end:]
exec(compile(tail, 'verify-and-install', 'exec'))
