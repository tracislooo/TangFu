from pathlib import Path
import re
import subprocess

bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(compile(bootstrap.replace('inspect-fitness-backdrop-', 'tactics-fixed-measurement-'), 'bundle-helpers', 'exec'))
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
        index = len(sheet['m_Rules'])
        sheet['m_Rules'].append({
            'm_ComplexSelectors': [selector(s, index) for s in selectors],
            'm_Properties': [{'m_Id': prop, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [handle]} for prop, handle in properties],
            'line': -1,
        })


    scopes = ['#CombinedPitchColumn', '#StackedPhasesColumn']
    shell = ['.tf-tactics-pitch-black', '.tf-tactics-pitch-black-dark-header']
    wrappers = ['#pitch-variables', '#pitch-remapper', '#collapse-switch', '#PitchBindableSwitchElement']
    previous_selectors = [
        [f'{scope} {part}' for scope in scopes for part in parts]
        for parts in [shell, wrappers, ['.tactics-collapsable-pitch-expanded']]
    ]
    # Disable exactly the last patch's three rules without moving rule indices.
    for names in previous_selectors:
        matches = [r for i, r in enumerate(sheet['m_Rules'])
                   if r['m_ComplexSelectors'] == [selector(s, i) for s in names]]
        assert len(matches) == 1, names
        matches[0]['m_Properties'] = []

    # Keep the native renderer's fixed-width measurement and auto height.
    for scope, width, cap in [(scopes[0], 384, 620), (scopes[1], 452, 244)]:
        rule([f'{scope} {part}' for part in shell], [
            (131105, px(width)), (131095, px(width)), (131097, px(width)),
            (131074, enum('center')), (262151, px(0)),
        ])
        rule([f'{scope} .tactics-collapsable-pitch-expanded'], [
            (131105, px(width)), (131095, px(width)), (131097, px(width)),
            (131094, px(cap)),
        ])

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
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
    checks.append({'target': tag, 'column_ratios': [25, 35, 40], 'mid_card_scale': .85,
                   'fixed_pitch_width_px': [384,452,452], 'pitch_max_height_px': [620,244,244], 'renderer_uxml_unchanged': True, 'roundtrip': True})

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
tail = tail[:start] + "(OUT/'修改说明.md').write_text('撤销百分比宽度。黑底与球场使用一致的像素宽度，合并384px、中间452px。以620/244px限制球场最大高度来减少页面溢出，保留原生高度计算和渲染参数。显示和滚动待游戏验证。','utf8')" + tail[end:]
exec(compile(tail, 'verify-and-install', 'exec'))
