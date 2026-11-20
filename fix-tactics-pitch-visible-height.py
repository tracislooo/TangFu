from pathlib import Path
import re
import subprocess

bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(compile(bootstrap.replace('inspect-fitness-backdrop-', 'tactics-pitch-visible-height-'), 'bundle-helpers', 'exec'))
source = ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'selector'], type_ignores=[]), 'selectors', 'exec'))
stylesheet_bundle = 'ui-styles_assets_default.bundle'
outputs, checks = {}, []

def update_sheet(sheet):
    def value(pool, kind, entry):
        sheet[pool].append(entry)
        return {'m_ValueType': kind, 'valueIndex': len(sheet[pool])-1}

    def px(n): return value('dimensions', 3, {'unit': 1, 'value': float(n)})
    def pct(n): return value('dimensions', 3, {'unit': 2, 'value': float(n)})
    def number(n): return value('floats', 2, float(n))
    def enum(name): return value('strings', 7, name)

    def rule(selectors, properties):
        for existing_index in range(len(sheet['m_Rules'])-1, -1, -1):
            existing = sheet['m_Rules'][existing_index]
            if existing['m_ComplexSelectors'] == [selector(s, existing_index) for s in selectors]:
                existing['m_Properties'] = [{'m_Id': prop, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [handle]} for prop, handle in properties]
                return
        index = len(sheet['m_Rules'])
        sheet['m_Rules'].append({
            'm_ComplexSelectors': [selector(s, index) for s in selectors],
            'm_Properties': [{'m_Id': prop, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [handle]} for prop, handle in properties],
            'line': -1,
        })

    scopes = ['#CombinedPitchColumn', '#StackedPhasesColumn']
    shell_classes = ['.tf-tactics-pitch-black', '.tf-tactics-pitch-black-dark-header',
                     '.tactics-collapsable-pitch-container', '.tactics-collapsable-pitch-container-with-darker-header']
    rule([f'{scope} {shell}' for scope in scopes for shell in shell_classes], [
        (131105, pct(100)), (131097, px(0)), (131096, px(0)),
        (131074, enum('stretch')), (131073, enum('stretch')), (262151, px(4)),
    ])
    wrappers = ['#pitch-variables', '#pitch-remapper', '#collapse-switch', '#PitchBindableSwitchElement']
    rule([f'{scope} {name}' for scope in scopes for name in wrappers], [
        (131105, pct(100)), (131097, px(0)), (131096, px(0)),
        (131074, enum('stretch')), (131073, enum('stretch')),
    ])
    # Override the native 452px width and 660px max height at the actual renderer.
    rule([f'{scope} .tactics-collapsable-pitch-expanded' for scope in scopes], [
        (131105, pct(100)), (131095, pct(100)), (131097, px(0)),
        (131087, pct(100)), (131094, pct(100)), (131096, px(160)),
        (131082, {'m_ValueType': 1, 'valueIndex': 2}), (131084, number(1)), (131085, number(1)), (131074, enum('stretch')),
    ])
    rule(['#StackedPhasesColumn #TFPitchSwitches'], [
        (131105, pct(100)), (131087, px(24)), (131096, px(24)), (131094, px(24)),
        (131084, number(0)), (131085, number(0)),
    ])
    rule(['#StackedPhasesColumn #TFPitchSwitches SIButton',
          '#StackedPhasesColumn .tactics-collapsable-pitch-header-button'], [
        (131087, px(24)), (131096, px(24)), (131094, px(24)), (262151, px(4)),
        (65537, px(11)),
    ])

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder/W])
    objs[W] = {o.path_id: o for o in env[W].objects}
    changes[W] = {}
    hashes[W] = {pid: sha(o.get_raw_data()) for pid, o in objs[W].items()}
    shape = Doc(W, name='TacticalPlannerTeamShape')
    pitch = Doc(W, name='TacticalPlannerCollapsablePitchesSingle')
    original = copy.deepcopy(shape.d)
    caption_names = ['CombinedPitchTitle', 'BothPhasesTitle', 'InPossessionTitle', 'OutOfPossessionTitle']
    caption_nodes = {shape.named(name) for name in caption_names}
    for node in caption_nodes:
        shape.st(node, [(131087, shape.px(16)), (131096, shape.px(16)), (131094, shape.px(16)), (65537, shape.px(11))])
    first_phase = shape.named('InPossessionSection')
    shape.st(first_phase, [(131090, shape.px(4))])
    overridden = set()
    for name, target_node, orientation in [('CombinedPitch', 1033, 0), ('InPossessionPitch', 1052, 1), ('OutOfPossessionPitch', 1052, 1)]:
        node = shape.named(name)
        target = pitch.a(target_node)
        overrides = shape.a(node)['m_SerializedDataOverride']
        if not overrides:
            serialized = copy.deepcopy(pitch.r[target['m_SerializedData']['rid']])
            serialized['rid'] = shape.nr
            shape.nr += 1
            shape.r[serialized['rid']] = serialized
            shape.d['references']['RefIds'].append(serialized)
            overrides.append({'m_ElementId': target['m_Id'], 'm_ElementIdsPath': [target['m_Id']],
                              'm_SerializedData': {'rid': serialized['rid']}})
        assert len(overrides) == 1
        override = overrides[0]
        assert override['m_ElementIdsPath'] == [target['m_Id']] and override['m_ElementId'] == target['m_Id']
        rid = override['m_SerializedData']['rid']
        data = shape.r[rid]['data']
        assert data['uxmlAssetId'] == target['m_Id']
        assert data['TacticPositionsBinding'] == pitch.data(target_node)['TacticPositionsBinding']
        data.update(FillAllAvailableSpace=1, FillAllAvailableSpace_UxmlAttributeFlags=1,
                    UseParentRectForOutline=0, UseParentRectForOutline_UxmlAttributeFlags=1,
                    Orientation=orientation, Orientation_UxmlAttributeFlags=1)
        overridden.update([node, rid])
    for rid, record in refs(original).items():
        expected = copy.deepcopy(record)
        actual = copy.deepcopy(shape.r[rid])
        if rid in caption_nodes | {first_phase}:
            expected['data']['m_RuleIndex'] = actual['data']['m_RuleIndex']
        if rid not in overridden:
            assert expected == actual, (tag, rid)
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
    checks.append({'target': tag, 'renderer_width': '100% of column interior', 'old_fixed_caps_overridden': True, 'height': '100%', 'min_height': 160, 'native_outline': True,
                   'renderer_orientation': [0, 1, 1], 'title_height': 16, 'middle_button_height': 24,
                   'column_ratios': [25, 35, 40], 'native_table_unchanged': True, 'roundtrip': True})

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
tail = tail[:start] + "(OUT/'修改说明.md').write_text('修正三栏球场及球员卡消失：取消实际球场height0/flex-basis0，改为height100%/flex-basis auto，最小高度160px，恢复原生UseParentRectForOutline=false。保留25/35/40三栏和现有标题、按钮、球员卡及表格，运行效果待游戏验收。','utf8')" + tail[end:]
exec(compile(tail, 'verify-and-install', 'exec'))
