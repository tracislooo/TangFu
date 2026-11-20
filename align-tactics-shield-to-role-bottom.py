"""Give the shield a fixed width and anchor it to the measured role footer."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-shield-role-bottom-')
exec(compile(bootstrap, 'load-current-tactics-resources', 'exec'))

helpers = {'style_value', 'preserve_original_bindings'}
definitions = [node for node in ast.parse(base).body if getattr(node, 'name', '') in helpers]
exec(compile(ast.Module(body=definitions, type_ignores=[]), 'tactics-layout-helpers', 'exec'))

LEFT, TOP, BOTTOM = 131089, 131104, 131080
WIDTH, HEIGHT, MIN_HEIGHT, MAX_HEIGHT = 131105, 131087, 131096, 131094
POSITION, DIRECTION, MARGIN_TOP = 131102, 131083, 131093
AUTO = {'m_ValueType': 1, 'valueIndex': 2}
NONE = {'m_ValueType': 1, 'valueIndex': 3}
SHIELD_ID = -910000000000154
SHIELD_WIDTH = 76
ROLE_TOP = 88
DETAIL_TEMPLATES = {
    'TacticsDetailedCardDetailsDesktop': (-970000000009000, 1005),
    'TacticsDetailedCardDetailsTouch': (-970000000010000, 1005),
}
outputs = {}
checks = []


def art_geometry(folder):
    bundle = 'ui-backgrounds_assets_common.bundle'
    texture = next(obj for obj in UnityPy.load(str(folder / bundle)).objects if obj.path_id == SHIELD_ID)
    assert texture.peek_name() == 'patchplayerbggreen'
    pixels = texture.read().image.getchannel('A')
    width, height = pixels.size
    # Align the visible shield edge, accounting for the soft transparent border in the PNG.
    visible_bottom = pixels.point(lambda alpha: 255 if alpha >= 128 else 0).getbbox()[3]
    natural_height = SHIELD_WIDTH * height / width
    inset = SHIELD_WIDTH * (height - visible_bottom) / width
    # Unity stores inline lengths as single-precision floats.
    natural_height, inset = struct.unpack('<ff', struct.pack('<ff', natural_height, inset))
    return width, height, natural_height, inset


def content_height(doc, node, positioning, column=True):
    properties = [
        (POSITION, doc.enum(positioning)), (HEIGHT, AUTO),
        (MIN_HEIGHT, doc.px(0)), (MAX_HEIGHT, NONE),
        (131082, AUTO), (131084, doc.num(0)), (131085, doc.num(0)),
        (458768, doc.enum('visible')),
    ]
    if column:
        properties.append((DIRECTION, doc.enum('column')))
    doc.st(node, properties)


def enter_flow(doc, node, column=True):
    content_height(doc, node, 'relative', column)
    doc.st(node, [(LEFT, AUTO), (TOP, AUTO), (BOTTOM, AUTO)])


def measure_role(doc, node, combined=False):
    assert style_value(doc, node, TOP) == {'unit': 1, 'value': ROLE_TOP}
    enter_flow(doc, node, column=not combined)
    doc.st(node, [(MARGIN_TOP, doc.px(ROLE_TOP))])


def move(doc, node, parent):
    doc.move(node, parent)
    if 'm_ParentId' in doc.a(node):
        doc.a(node)['m_ParentId'] = doc.a(parent)['m_Id']


def make_shield_layer(doc, draggable, shirt, details, natural_height, inset):
    image = doc.named('TacticsPlayerCardBackgroundImage')
    assert doc.data(image)['pickingMode'] == 1
    assert style_value(doc, image, 458753)['m_PathID'] == SHIELD_ID
    assert style_value(doc, image, WIDTH)['value'] == SHIELD_WIDTH
    assert style_value(doc, image, HEIGHT)['value'] == 78
    origin = [(key, style_value(doc, shirt, key)['value']) for key in (LEFT, TOP)]

    layer = doc.add(doc, image, draggable, 'TacticsShieldAndRoleLayout')
    assert doc.a(layer)['m_FullTypeName'] == 'UnityEngine.UIElements.VisualElement'
    if 'm_ParentId' in doc.a(layer):
        doc.a(layer)['m_ParentId'] = doc.a(draggable)['m_Id']
    content_height(doc, layer, 'absolute')
    doc.st(layer, [(WIDTH, doc.px(SHIELD_WIDTH)), *((key, doc.px(value)) for key, value in origin)])
    for node in (image, shirt, details):
        move(doc, node, layer)

    doc.st(image, [
        (TOP, AUTO), (BOTTOM, doc.px(-inset)), (HEIGHT, doc.px(natural_height)),
        (MIN_HEIGHT, doc.px(0)), (MAX_HEIGHT, doc.pct(100)),
        (262153, doc.enum('stretch-to-fill')),
    ])
    doc.st(shirt, [(LEFT, doc.px(0)), (TOP, doc.px(0))])
    enter_flow(doc, details)
    assert doc.a(layer)['m_Children'] == [{'rid': node} for node in (image, shirt, details)]
    return layer, image


def check_reparenting(doc, original, layer, image, draggable, shirt, details):
    old_refs = refs(original)
    assert set(doc.r) - set(old_refs) == {layer, doc.a(layer)['m_SerializedData']['rid']}
    old_image_parent = old_refs[image]['data']['m_Parent']['rid']
    for node, before_record in old_refs.items():
        actual = copy.deepcopy(doc.r[node])
        old = before_record.get('data', {})
        if 'm_RuleIndex' in old:
            actual['data']['m_RuleIndex'] = old['m_RuleIndex']
        if node in (image, shirt, details):
            assert actual['data']['m_Parent']['rid'] == layer
            actual['data']['m_Parent'] = old['m_Parent']
            if 'm_ParentId' in old:
                actual['data']['m_ParentId'] = old['m_ParentId']
        if node in (old_image_parent, draggable):
            expected = [{'rid': layer}] if node == draggable else [c for c in old['m_Children'] if c['rid'] != image]
            assert actual['data']['m_Children'] == expected
            actual['data']['m_Children'] = old['m_Children']
        assert actual == before_record, (doc.d['m_Name'], node)
    assert doc.d['m_Usings'] == original['m_Usings']


for folder, target in [(GAME, 'game'), (SKIN, 'skin')]:
    width, height, natural_height, inset = art_geometry(folder)
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}

    for name, draggable, shirt, details in (
        ('TacticsPositionCombined', 1016, 1018, 1019),
        ('TacticsPositionDetailed', 1010, 1014, 1015),
    ):
        doc = Doc(W, name=name)
        original = copy.deepcopy(doc.d)
        if name.endswith('Combined'):
            frame_top = style_value(doc, details, TOP)['value'] - style_value(doc, shirt, TOP)['value']
            assert frame_top == 7 and style_value(doc, 1027, TOP)['value'] == 0
            doc.st(1027, [(TOP, doc.px(frame_top))])
            enter_flow(doc, 1026)
            measure_role(doc, 1035, combined=True)
        else:
            for node in (1020, 1030, 1031):
                enter_flow(doc, node)
        layer, image = make_shield_layer(doc, draggable, shirt, details, natural_height, inset)
        check_reparenting(doc, original, layer, image, draggable, shirt, details)
        doc.save()
        checks.append({'target': target, 'template': name, 'art_dimensions': [width, height],
                       'width': SHIELD_WIDTH, 'natural_height': natural_height,
                       'height_cap': '100% of measured card height', 'visible_bottom_inset': inset})

    for name, (pid, pitch) in DETAIL_TEMPLATES.items():
        doc = Doc(W, pid=pid)
        assert doc.d['m_Name'] == name
        original = copy.deepcopy(doc.d)
        for node in (1001, pitch):
            enter_flow(doc, node)
        if name.endswith('Desktop'):
            # The hidden decorative frame must not contribute to the content measurement.
            assert style_value(doc, 1008, 458767) == 0
            doc.st(1008, [(POSITION, doc.enum('absolute'))])
        measure_role(doc, doc.named('DetailedCurrentPhasePositionContext'))
        preserve_original_bindings(doc, original)
        doc.save()
        checks.append({'target': target, 'template': name, 'role_start': ROLE_TOP, 'role_height': 'auto'})

    data = env[W].file.save(packer='lz4')
    saved = {obj.path_id: obj for obj in UnityPy.load(data).objects}
    assert saved.keys() == original_hashes.keys()
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid]
        else:
            assert sha(obj.get_raw_data()) == original_hashes[pid]
    outputs[folder / W] = data
    (OUT / ('output-' + target)).mkdir()
    (OUT / ('output-' + target) / W).write_bytes(data)

description = '绿盾固定宽度76px，原图等比高度约101px，仅在卡片更短时限高。背景可见底边跟随位置区实测高度。'
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

index_path = R / 'current-tactics-card-layout.json'
index = json.loads(index_path.read_text('utf8'))
index.pop('background_top', None)
index.update({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'background_size': [SHIELD_WIDTH, 'role-measured, capped at source aspect ratio'],
    'background_natural_height': round(natural_height, 3), 'background_anchor': 'role-footer bottom',
    'manifest': str(OUT / 'manifest.json'),
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
