"""Match the taller shield and larger portrait on the current tactics cards."""
from pathlib import Path
import subprocess


source = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = source[source.index('bootstrap = '):source.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-tall-green-shield-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

SHIELD = (0, 9, 76, 88)
PORTRAIT = (3, 14, 70, 70)
NAME_Y, ROLE_Y = 85, 99
BAR_Y = PORTRAIT[1] + PORTRAIT[3] - 3
LEFT, TOP, WIDTH, HEIGHT = 131089, 131104, 131105, 131087
outputs = {}
checks = []

parsed = ast.parse(source)
geometry_helpers = {'position', 'absolute_box', 'style_value', 'preserve_original_bindings'}
definitions = [node for node in parsed.body if getattr(node, 'name', '') in geometry_helpers]
exec(compile(ast.Module(body=definitions, type_ignores=[]), 'tactics-card-geometry', 'exec'))


def resize_portrait_layer(doc):
    image = doc.named('TacticsPlayerCardBackgroundImage')
    portrait = doc.named('TacticsPlayerPortraitBinding')
    texture = style_value(doc, image, 458753)
    assert texture['m_PathID'] == -910000000000154
    absolute_box(doc, image, *SHIELD)
    doc.st(image, [(262153, doc.enum('stretch-to-fill'))])
    absolute_box(doc, portrait, *PORTRAIT)

    combined = doc.d['m_Name'] == 'TacticsPositionCombined'
    for index, node in enumerate((1029, 1033) if combined else (1024, 1028)):
        position(doc, node, 59, 20 + 11 * index)
    for index, node in enumerate((1032, 1031) if combined else (1027, 1026, 1017)):
        position(doc, node, 57, 41 + 10 * index)

    gate = doc.named('PitchFitnessPlayerVisible')
    backdrop = doc.named('PitchFitnessPercentageBackdrop')
    absolute_box(doc, gate, 0, 0, 76, PORTRAIT[1] + PORTRAIT[3])
    position(doc, backdrop, 6, 19)
    counts = {'labels': 0, 'tracks': 0, 'fills': 0}
    for node, record in doc.r.items():
        if 'm_Parent' not in record.get('data', {}):
            continue
        name = doc.data(node).get('name', '')
        if name.endswith('CardFitnessTrack'):
            absolute_box(doc, node, PORTRAIT[0], BAR_Y, PORTRAIT[2], 3)
            counts['tracks'] += 1
        elif 'CardFitnessFill' in name:
            suffix = name.split('CardFitnessFill', 1)[1]
            percent = 0 if suffix == 'None' else int(suffix)
            width = struct.unpack('<f', struct.pack('<f', PORTRAIT[2] * percent / 100))[0]
            absolute_box(doc, node, 0, BAR_Y, width, 3)
            counts['fills'] += 1
        elif name.startswith('PitchFitnessPercent') and node != backdrop:
            absolute_box(doc, node, PORTRAIT[0], 0, PORTRAIT[2], PORTRAIT[1] + PORTRAIT[3])
            doc.st(node, [(131099, doc.px(4)), (131101, doc.px(19))])
            counts['labels'] += 1
    assert counts == {'labels': 204, 'tracks': 2, 'fills': 204}, counts
    return counts


def position_footer_and_feet(doc, prefix, name_node, role_node):
    position(doc, name_node, 0, NAME_Y)
    position(doc, role_node, 0, ROLE_Y)
    for index, side in enumerate(('Left', 'Right')):
        foot = doc.named(f'{prefix}{side}FootednessPlayerVisible')
        position(doc, foot, 6 + index * 12, 32)


for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    for template in (
        'TacticsPositionCombined', 'TacticsPositionDetailed',
        'TacticsDetailedCardDetailsDesktop', 'TacticsDetailedCardDetailsTouch',
    ):
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        audit = {'target': tag, 'template': template}
        if template in ('TacticsPositionCombined', 'TacticsPositionDetailed'):
            audit['fitness'] = resize_portrait_layer(doc)
        if template == 'TacticsPositionCombined':
            position_footer_and_feet(doc, 'Combined', 1037, 1035)
        elif template.startswith('TacticsDetailedCardDetails'):
            name_node = 1061 if template.endswith('Touch') else 1016
            role_node = doc.named('DetailedCurrentPhasePositionContext')
            position_footer_and_feet(doc, 'Detailed', name_node, role_node)
        preserve_original_bindings(doc, original)
        doc.save()
        checks.append(audit)

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
    '战术板绿盾背景76×88px，顶部在y9，头像70×70px，x3/y14。'
    '星级在盾顶，体能百分比和左右脚在左上，位置及状态图标在右上，体能条贴头像底边。'
    '姓名y85叠在盾底，位置栏y99。其余资源和原节点绑定校验通过，游戏内显示待确认。'
)
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

(R / 'current-tactics-card-layout.json').write_text(json.dumps({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'card_size': [76, 76], 'background_size': list(SHIELD[2:]), 'background_top': SHIELD[1],
    'portrait_size': list(PORTRAIT[2:]), 'portrait_top': PORTRAIT[1],
    'background': {'name': 'patchplayerbggreen', 'path_id': '-910000000000154'},
    'name_top': NAME_Y, 'role_top': ROLE_Y, 'combined_role_widths': [38, 38],
    'fitness_top': BAR_Y, 'portrait_rim_visible': False,
    'manifest': str(OUT / 'manifest.json'),
}, ensure_ascii=False, indent=2), 'utf8')
