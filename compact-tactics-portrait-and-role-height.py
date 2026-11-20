"""Fit the shield and footer to the smaller portrait and live role text."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-compact-portrait-and-role-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

BODY, PORTRAIT, PORTRAIT_X, PORTRAIT_Y = 76, 60, 8, 14
SHIELD = (0, 9, BODY, 78)
BAR_Y, NAME_Y, ROLE_Y = 71, 75, 88
LEFT, TOP, WIDTH, HEIGHT = 131089, 131104, 131105, 131087
AUTO = {'m_ValueType': 1, 'valueIndex': 2}
NONE = {'m_ValueType': 1, 'valueIndex': 3}
outputs = {}
checks = []

parsed = ast.parse(base)
helpers = {'position', 'absolute_box', 'style_value', 'preserve_original_bindings'}
definitions = [node for node in parsed.body if getattr(node, 'name', '') in helpers]
exec(compile(ast.Module(body=definitions, type_ignores=[]), 'tactics-card-geometry', 'exec'))


def fit_content_height(doc, node):
    doc.st(node, [
        (HEIGHT, AUTO), (131096, doc.px(0)), (131094, NONE),
        (131082, AUTO), (131084, doc.num(0)), (131085, doc.num(0)),
    ])


def use_flow(doc, node):
    doc.st(node, [(131102, doc.enum('relative')), (LEFT, AUTO), (TOP, AUTO)])


def trim_label(doc, node):
    fit_content_height(doc, node)
    doc.st(node, [(key, doc.px(0)) for key in (131090, 131091, 131092, 131093, 131098, 131101)])
    assert style_value(doc, node, 65552) == 'normal'


def tighten_combined_roles(doc):
    row = 1035
    fit_content_height(doc, row)
    doc.st(row, [(131083, doc.enum('row')), (131073, doc.enum('flex-start'))])
    for slot, color, remapper, button, label in ((1055, 1075, 1092, 1105, 1119), (1057, 1078, 1094, 1107, 1122)):
        use_flow(doc, slot)
        for node in (slot, color, remapper, button):
            fit_content_height(doc, node)
        trim_label(doc, label)
        assert style_value(doc, slot, WIDTH)['value'] == 38


def resize_portrait(doc, combined):
    image = doc.named('TacticsPlayerCardBackgroundImage')
    portrait = doc.named('TacticsPlayerPortraitBinding')
    assert style_value(doc, image, 458753)['m_PathID'] == -910000000000154
    assert style_value(doc, portrait, WIDTH)['value'] == 70
    absolute_box(doc, image, *SHIELD)
    absolute_box(doc, portrait, PORTRAIT_X, PORTRAIT_Y, PORTRAIT, PORTRAIT)
    for index, node in enumerate((1029, 1033) if combined else (1024, 1028)):
        position(doc, node, 54, 17 + 11 * index)
    for index, node in enumerate((1032, 1031) if combined else (1027, 1026, 1017)):
        position(doc, node, 52, 36 + 10 * index)

    gate = doc.named('PitchFitnessPlayerVisible')
    backdrop = doc.named('PitchFitnessPercentageBackdrop')
    absolute_box(doc, gate, 0, 0, BODY, PORTRAIT_Y + PORTRAIT)
    position(doc, backdrop, PORTRAIT_X, 16)
    tracks, fills, labels = 0, 0, 0
    for node, record in doc.r.items():
        if 'm_Parent' not in record.get('data', {}):
            continue
        name = doc.data(node).get('name', '')
        if name.endswith('CardFitnessTrack'):
            absolute_box(doc, node, PORTRAIT_X, BAR_Y, PORTRAIT, 3)
            tracks += 1
        elif 'CardFitnessFill' in name:
            suffix = name.split('CardFitnessFill', 1)[1]
            percent = 0 if suffix == 'None' else int(suffix)
            width = struct.unpack('<f', struct.pack('<f', PORTRAIT * percent / 100))[0]
            absolute_box(doc, node, 0, BAR_Y, width, 3)
            fills += 1
        elif name.startswith('PitchFitnessPercent') and node != backdrop:
            absolute_box(doc, node, PORTRAIT_X, 0, PORTRAIT, PORTRAIT_Y + PORTRAIT)
            doc.st(node, [(131099, doc.px(1)), (131101, doc.px(16))])
            labels += 1
    assert (tracks, fills, labels) == (2, 204, 204)


def move_visible_details(doc, stars, name, role, prefix):
    star_top = style_value(doc, stars, TOP)['value']
    assert star_top == 2
    doc.st(stars, [(TOP, doc.px(star_top + 5))])
    position(doc, name, 0, NAME_Y)
    position(doc, role, 0, ROLE_Y)
    for index, side in enumerate(('Left', 'Right')):
        foot = doc.named(f'{prefix}{side}FootednessPlayerVisible')
        position(doc, foot, PORTRAIT_X + index * 12, 27)


for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    for template in (
        'TacticsPositionCombined', 'TacticsPositionDetailed', 'TacticsDetailedCardDetailsDesktop',
        'TacticsDetailedCardDetailsTouch', 'TacticsDetailedCardPositionButton',
    ):
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        if template == 'TacticsPositionCombined':
            resize_portrait(doc, combined=True)
            move_visible_details(doc, 1036, 1037, 1035, 'Combined')
            tighten_combined_roles(doc)
        elif template == 'TacticsPositionDetailed':
            resize_portrait(doc, combined=False)
        elif template == 'TacticsDetailedCardPositionButton':
            for node in (1001, 1002, 1021, 1004, 1006, 1008):
                fit_content_height(doc, node)
            for node in (1006, 1008):
                doc.st(node, [(WIDTH, doc.pct(100)), (131097, doc.px(0)), (131095, NONE)])
            trim_label(doc, 1011)
        else:
            touch = template.endswith('Touch')
            phase = doc.named('DetailedCurrentPhasePositionContext')
            button = doc.named('DetailedCurrentPhasePositionButton')
            move_visible_details(doc, 1027 if touch else 1022, 1061 if touch else 1016, phase, 'Detailed')
            use_flow(doc, button)
            for node in (phase, button):
                fit_content_height(doc, node)
        preserve_original_bindings(doc, original)
        doc.save()
        checks.append({'target': tag, 'template': template, 'bindings_preserved': True})

    data = env[W].file.save(packer='lz4')
    saved = {obj.path_id: obj for obj in UnityPy.load(data).objects}
    assert saved.keys() == original_hashes.keys()
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid]
        else:
            assert sha(obj.get_raw_data()) == original_hashes[pid]
    outputs[folder / W] = data
    (OUT / ('output-' + tag)).mkdir()
    (OUT / ('output-' + tag) / W).write_bytes(data)

description = (
    '战术卡头像70→60px，星级下移5px，绿盾76×78px。体能条/姓名/位置栏上移，'
    '位置栏由固定22px改为内容自适应高度，去除文字上下内外边距，中文保留换行。'
    '序列化回读及无关对象校验通过，实际游戏显示待确认。'
)
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

(R / 'current-tactics-card-layout.json').write_text(json.dumps({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'card_size': [BODY, BODY], 'background_size': list(SHIELD[2:]), 'background_top': SHIELD[1],
    'portrait_size': [PORTRAIT, PORTRAIT], 'portrait_top': PORTRAIT_Y,
    'background': {'name': 'patchplayerbggreen', 'path_id': '-910000000000154'},
    'stars_top': 7, 'name_top': NAME_Y, 'role_top': ROLE_Y, 'role_height': 'auto',
    'combined_role_widths': [38, 38], 'fitness_top': BAR_Y, 'portrait_rim_visible': False,
    'manifest': str(OUT / 'manifest.json'),
}, ensure_ascii=False, indent=2), 'utf8')
