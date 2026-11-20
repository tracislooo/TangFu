"""Move the live tactics card and replace its star row with a compact rating badge."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-single-star-raise-card-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

for filename, names in [
    ('apply-tactics-green-pitch-player-card.py', {'position', 'absolute_box', 'style_value'}),
    ('combine-tactics-condition-sharpness.py', {'decode', 'encode'}),
]:
    source = ast.parse((R / filename).read_text('utf8'))
    definitions = [node for node in source.body if getattr(node, 'name', '') in names]
    exec(compile(ast.Module(body=definitions, type_ignores=[]), filename, 'exec'))

catalog_spec = importlib.util.spec_from_file_location('tactics_catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(catalog_spec)
catalog_spec.loader.exec_module(catalog_module)

LEFT, TOP, WIDTH, HEIGHT = 131089, 131104, 131105, 131087
CARD_SHIFT, SIDE_SHIFT = 8, 5
BADGE_X, BADGE_Y, BADGE_W, BADGE_H = 3, 39, 24, 12
RATING_PATH = b'starrating.minvalue'
STAR_CLASSES = ['fm-star-rating-star-no-margin', 'ability-max-potential-level-fullfilled-youth-false']
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FUNCTIONS = 'ui-visualfunctions_assets_all.bundle'
INTEGER_COMPARE = 'f6f314e9db56227459137669d87c44e9'
RANGE_AVAILABLE = '95e40d4306bf4d5428d5c1ffedf071af'
outputs = {}
checks = []


def shift_px(doc, node, prop, delta):
    before_value = style_value(doc, node, prop)
    assert before_value['unit'] == 1
    doc.st(node, [(prop, doc.px(before_value['value'] + delta))])


def hide(doc, node):
    doc.st(node, [(131081, doc.enum('none'))])


def adjust_body(doc, combined):
    draggable = 1016 if combined else 1010
    assert style_value(doc, draggable, 131102) == 'relative'
    assert style_value(doc, draggable, TOP)['value'] == 0
    shift_px(doc, draggable, TOP, -CARD_SHIFT)
    right_icons = (1029, 1033, 1032, 1031) if combined else (1024, 1028, 1027, 1026, 1017)
    for node in right_icons:
        shift_px(doc, node, LEFT, SIDE_SHIFT)
    backdrop = doc.named('PitchFitnessPercentageBackdrop')
    shift_px(doc, backdrop, LEFT, -SIDE_SHIFT)
    tracks = fills = labels = 0
    for node, record in doc.r.items():
        if 'm_Parent' not in record.get('data', {}):
            continue
        name = doc.data(node).get('name', '')
        if name.endswith('CardFitnessTrack'):
            hide(doc, node)
            tracks += 1
        elif 'CardFitnessFill' in name:
            hide(doc, node)
            fills += 1
        elif name.startswith('PitchFitnessPercent') and node != backdrop:
            shift_px(doc, node, LEFT, -SIDE_SHIFT)
            labels += 1
    assert (tracks, fills, labels) == (2, 204, 204)
    return style_value(doc, backdrop, 458752)


def fit_rating_scope(doc, node, width=BADGE_W):
    doc.size(node, width, BADGE_H)
    doc.st(node, [(458768, doc.enum('visible'))])


def move_rating_host(doc, node):
    absolute_box(doc, node, BADGE_X, BADGE_Y, BADGE_W, BADGE_H)
    doc.st(node, [(327681, [doc.num(1), doc.num(1)])])


def style_missing_label(doc, node, backdrop):
    absolute_box(doc, node, 0, 0, 36, BADGE_H)
    doc.st(node, [
        (458752, doc.val(4, backdrop)), (65537, doc.px(8)),
        (65546, doc.enum('middle-center')), (65552, doc.enum('nowrap')),
    ])


def add_rating_tree(doc, parent, donor, backdrop):
    compare_donor = donor.named('LeftFootednessAbove20')
    text_donor = donor.named('LeftFootednessLabel1')
    visual_donor = doc.named('Stars')
    branches, leaves = {}, {}

    def compare(host, threshold):
        node = doc.add(donor, compare_donor, host, f'CompactStarRatingAbove{threshold}')
        absolute_box(doc, node, 0, 0, BADGE_W, BADGE_H)
        fn = doc.data(node)['Binding']['m_visualFunction']
        assert fn['m_target']['m_guid'] == INTEGER_COMPARE
        args = decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
        original_path = b'position.Player.Footedness.LeftFootedness'
        assert args[2].endswith(bytes([len(original_path)]) + original_path)
        assert args[0][-4:] == struct.pack('<i', 4)
        struct.pack_into('<i', args[1], len(args[1]) - 4, threshold)
        args[2][-len(original_path) - 1:] = bytes([len(RATING_PATH)]) + RATING_PATH
        fn['m_inputs']['m_variable']['m_argumentBytes'] = encode(args)
        branches[node] = threshold
        return node

    def leaf(host, value):
        group = doc.add(doc, visual_donor, host, f'CompactStarRatingValue{value}')
        absolute_box(doc, group, 0, 0, BADGE_W, BADGE_H)
        leaves[group] = value
        if value is None:
            return
        doc.st(group, [(458752, doc.val(4, backdrop))])
        label = doc.add(donor, text_donor, group, 'CompactStarNumber')
        label_data = doc.data(label)
        label_data.update(text=f'{value / 2:g}', text_UxmlAttributeFlags=1, TextBinding_UxmlAttributeFlags=0)
        label_data['TextBinding']['m_kind'] = 0
        absolute_box(doc, label, 1, 0, 13, BADGE_H)
        doc.st(label, [
            (65537, doc.px(9)), (65543, doc.enum('bold')), (65546, doc.enum('middle-center')),
            (65536, doc.val(4, {'r': 1., 'g': 1., 'b': 1., 'a': 1.})),
        ])
        icon = doc.add(doc, visual_donor, group, 'CompactNativeGoldStar')
        doc.a(icon)['m_Classes'] = STAR_CLASSES[:]
        absolute_box(doc, icon, 14, 1, 9, 10)

    def build(host, low, high):
        if low == high:
            leaf(host, low)
            return
        mid = (low + high) // 2
        node = compare(host, mid)
        build(node, low, mid)
        build(node, mid + 1, high)

    upper = compare(parent, 10)
    lower = compare(upper, -1)
    leaf(lower, None)
    build(lower, 0, 10)
    leaf(upper, None)
    for value in (None, -1, *range(12)):
        node = upper
        while node in branches:
            fn = doc.data(node)['Binding']['m_visualFunction']
            args = decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
            assert args[2].endswith(bytes([len(RATING_PATH)]) + RATING_PATH)
            threshold = struct.unpack_from('<i', args[1], len(args[1]) - 4)[0]
            assert threshold == branches[node]
            node = doc.a(node)['m_Children'][int(value is not None and value > threshold)]['rid']
        valid = value is not None and 0 <= value <= 10
        assert leaves[node] == (value if valid else None)
        if valid:
            label, icon = (ch['rid'] for ch in doc.a(node)['m_Children'])
            assert doc.data(label)['text'] == f'{value / 2:g}'
            assert doc.a(icon)['m_Classes'] == STAR_CLASSES


def replace_combined_rating(doc, donor, backdrop):
    move_rating_host(doc, 1036)
    for node in (1059, 1080, 1096, 1111, 1112, 1125, 1126):
        fit_rating_scope(doc, node)
    for child in doc.a(1125)['m_Children']:
        hide(doc, child['rid'])
    for node in (1128, 1145):
        style_missing_label(doc, node, backdrop)
    add_rating_tree(doc, 1125, donor, backdrop)
    return 1125


def replace_detailed_rating(doc, donor, native, backdrop, touch):
    stars, color, visible, scope, row = (1027, 1047, 1071, 1097, 1131) if touch else (1022, 1034, 1049, 1064, 1085)
    move_rating_host(doc, stars)
    for node in (color, visible, scope):
        fit_rating_scope(doc, node)
    for child in doc.a(scope)['m_Children']:
        node = child['rid']
        if node == row or doc.data(node).get('name', '').startswith('TacticsStarOutline'):
            hide(doc, node)
    assert native.a(1002)['m_Children'] == [{'rid': 1004}, {'rid': 1005}]
    assert native.data(1004)['MinBinding']['m_path'].encode() == RATING_PATH
    native_gate = doc.add(native, 1002, scope, 'CompactNativeRatingAvailability')
    assert doc.data(native_gate)['Binding'] == native.data(1002)['Binding']
    assert doc.data(native_gate)['Binding']['m_visualFunction']['m_target']['m_guid'] == RANGE_AVAILABLE
    absolute_box(doc, native_gate, 0, 0, BADGE_W, BADGE_H)
    add_rating_tree(doc, native_gate, donor, backdrop)
    unknown = doc.add(native, 1005, native_gate, 'CompactNativeRatingUnknown')
    style_missing_label(doc, unknown, backdrop)
    return scope


def validate_native_dependencies(folder, catalog):
    # The skin packages are an overlay. A missing native bundle comes from the game.
    native_package = folder / FUNCTIONS
    if not native_package.is_file():
        native_package = GAME / FUNCTIONS
    package = UnityPy.load(str(native_package))
    objects = {obj.path_id: obj for obj in package.objects}
    meta = next(obj for obj in objects.values() if obj.type.name == 'AssetBundle').read_typetree()
    containers = dict(meta['m_Container'])
    for guid in (INTEGER_COMPARE, RANGE_AVAILABLE):
        locations = catalog.locations(guid)
        assert locations
        for loc in locations:
            entry = catalog.location(loc)
            assert entry['type'][1] == 'SI.VisualScripting.VisualFunction'
            dependency = catalog.location(entry['dependencies'][0])['internal']
            assert dependency.replace('\\', '/').endswith('/' + FUNCTIONS)
        pointer = containers[guid]['asset']
        assert pointer['m_FileID'] == 0 and pointer['m_PathID'] in objects


def check_existing_nodes(doc, original, append_parent):
    for node, old in refs(original).items():
        updated = copy.deepcopy(doc.r[node])
        if 'm_RuleIndex' in old.get('data', {}):
            updated['data']['m_RuleIndex'] = old['data']['m_RuleIndex']
        if node == append_parent:
            old_children = old['data']['m_Children']
            assert updated['data']['m_Children'][:-1] == old_children
            updated['data']['m_Children'] = old_children
        assert updated == old, (doc.d['m_Name'], node)
    assert doc.d['m_Usings'] == original['m_Usings']


for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    objs[GLOBAL] = {obj.path_id: obj for obj in UnityPy.load(str(folder / GLOBAL)).objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    catalog_path = (GAME.parent if tag == 'game' else SKIN) / 'catalog.bin'
    validate_native_dependencies(folder, catalog_module.Catalog(before[catalog_path]))
    donor = Doc(W, name='TacticsDetailedCardDetailsDesktop')
    native = Doc(GLOBAL, name='stats-star ratings')
    combined = Doc(W, name='TacticsPositionCombined')
    detailed = Doc(W, name='TacticsPositionDetailed')
    for doc, is_combined in [(combined, True), (detailed, False)]:
        original = copy.deepcopy(doc.d)
        backdrop = adjust_body(doc, is_combined)
        append_parent = None
        if is_combined:
            for side in ('Left', 'Right'):
                shift_px(doc, doc.named(f'Combined{side}FootednessPlayerVisible'), LEFT, -SIDE_SHIFT)
            append_parent = replace_combined_rating(doc, donor, backdrop)
        check_existing_nodes(doc, original, append_parent)
        doc.save()
        checks.append({'target': tag, 'template': doc.d['m_Name'], 'native_bindings_and_events_preserved': True})
    for template in ('TacticsDetailedCardDetailsDesktop', 'TacticsDetailedCardDetailsTouch'):
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        for side in ('Left', 'Right'):
            shift_px(doc, doc.named(f'Detailed{side}FootednessPlayerVisible'), LEFT, -SIDE_SHIFT)
        append_parent = replace_detailed_rating(doc, donor, native, backdrop, template.endswith('Touch'))
        check_existing_nodes(doc, original, append_parent)
        doc.save()
        checks.append({'target': tag, 'template': template, 'native_bindings_and_events_preserved': True})

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
    '战术板卡片及点击区域上移8px，体能百分比与左右脚左移5px，右侧图标右移5px。'
    '隐藏体能轨道及填充，原实时百分比保留。星级改为左右脚下的数字加原生金星，'
    '读取原生实心星下界，0–10映射0–5星，原缺失分支保留。回读和安装校验通过，游戏内效果待确认。'
)
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

index_path = R / 'current-tactics-card-layout.json'
index = json.loads(index_path.read_text('utf8'))
index.pop('stars_top', None)
index.pop('fitness_top', None)
index.update({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'card_top_offset': -CARD_SHIFT, 'left_info_shift_x': -SIDE_SHIFT, 'right_icon_shift_x': SIDE_SHIFT,
    'fitness_bar_visible': False, 'rating_badge': [BADGE_X, BADGE_Y, BADGE_W, BADGE_H],
    'rating_source': RATING_PATH.decode(), 'rating_divisor': 2,
    'manifest': str(OUT / 'manifest.json'),
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
