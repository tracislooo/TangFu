"""Reflow the live FM27 tactics card templates without replacing shared assets."""
from pathlib import Path
import subprocess


bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
bootstrap = bootstrap.replace('inspect-fitness-backdrop-', 'tactics-green-pitch-player-card-')
exec(compile(bootstrap.replace('hours=-4', 'hours=-7'), 'backup-current-tactics-resources', 'exec'))

from UnityPy.classes import PPtr

for filename, names in [
    ('add-pitch-condition-complexity-columns.py', {'Tree', 'serial'}),
    ('build-fc-player-hover-layout.py', {'Styles'}),
]:
    source = ast.parse((R / filename).read_text('utf-8-sig'))
    definitions = [node for node in source.body if getattr(node, 'name', '') in names]
    exec(compile(ast.Module(body=definitions, type_ignores=[]), filename, 'exec'))

spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog_module)

BACKGROUND_BUNDLE = 'ui-backgrounds_assets_common.bundle'
GREEN = -910000000000154
OLD_BACKGROUND = -910000000000147
BODY, PORTRAIT = 76, 60
PORTRAIT_INSET = (BODY - PORTRAIT) // 2
BAR_Y, BAR_HEIGHT = PORTRAIT_INSET + PORTRAIT - 3, 3
NAME_Y, NAME_HEIGHT = 77, 12
ROLE_Y, ROLE_HEIGHT = 90, 22
LEFT, TOP, WIDTH, HEIGHT = 131089, 131104, 131105, 131087
OVERFLOW, OPACITY = 458768, 458767
outputs = {}
checks = []


def style_value(doc, node, key):
    rule = doc.s['m_Rules'][doc.a(node)['m_RuleIndex']]
    handle, = next(p for p in rule['m_Properties'] if p['m_Id'] == key)['m_Values']
    return doc.s[poolmap[handle['m_ValueType']]][handle['valueIndex']]


def position(doc, node, x, y):
    doc.st(node, [(LEFT, doc.px(x)), (TOP, doc.px(y))])


def absolute_box(doc, node, x, y, width, height):
    doc.size(node, width, height)
    doc.st(node, [
        (131102, doc.enum('absolute')), (LEFT, doc.px(x)), (TOP, doc.px(y)),
        (131103, {'m_ValueType': 1, 'valueIndex': 3}),
        (131080, {'m_ValueType': 1, 'valueIndex': 3}),
    ])


def visibility_for_footer(doc, node):
    # An absolute footer may extend past the card's fixed pitch anchor.
    while node != -2 and node != doc.d['m_VisualTree']['rid']:
        doc.st(node, [(OVERFLOW, doc.enum('visible'))])
        node = doc.a(node)['m_Parent']['rid']


def style_stars_and_name(doc, stars, name):
    # Scale 1.5 around the center of the original 50x8 rating row.
    position(doc, stars, (BODY - 50) / 2, 2)
    absolute_box(doc, name, 0, NAME_Y, BODY, NAME_HEIGHT)
    visibility_for_footer(doc, name)


def style_role_text(doc, node):
    binding = doc.data(node)['TextBinding']['m_visualFunction']
    assert b'tactical_role' in bytes(binding['m_inputs']['m_variable']['m_argumentBytes'])
    doc.st(node, [
        (65552, doc.enum('normal')), (65546, doc.enum('middle-center')),
        (196609, doc.enum('clip')), (OVERFLOW, doc.enum('hidden')),
        (WIDTH, doc.pct(100)), (131097, doc.px(0)),
        (HEIGHT, doc.pct(100)), (131096, doc.px(0)),
        (131099, doc.px(0)), (131100, doc.px(0)),
        (131092, doc.px(0)), (131091, doc.px(0)),
    ])


def style_feet(doc, node, index):
    absolute_box(doc, node, PORTRAIT_INSET + index * 12, 27, 10, 10)


def fit_fitness(doc):
    gate = doc.named('PitchFitnessPlayerVisible')
    absolute_box(doc, gate, 0, 0, BODY, BODY)
    backdrop = doc.named('PitchFitnessPercentageBackdrop')
    position(doc, backdrop, PORTRAIT_INSET, 14)
    counts = {'labels': 0, 'tracks': 0, 'fills': 0}
    for node, record in doc.r.items():
        if 'm_Parent' not in record.get('data', {}):
            continue
        name = doc.data(node).get('name', '')
        if name.endswith('CardFitnessTrack'):
            absolute_box(doc, node, PORTRAIT_INSET, BAR_Y, PORTRAIT, BAR_HEIGHT)
            counts['tracks'] += 1
        elif 'CardFitnessFill' in name:
            suffix = name.split('CardFitnessFill', 1)[1]
            percent = 0 if suffix == 'None' else int(suffix)
            parent = doc.a(node)['m_Parent']['rid']
            assert doc.data(parent).get('name', '').startswith('PitchFitnessPercent')
            fill_width = struct.unpack('<f', struct.pack('<f', PORTRAIT * percent / 100))[0]
            absolute_box(doc, node, 0, BAR_Y, fill_width, BAR_HEIGHT)
            counts['fills'] += 1
        elif name.startswith('PitchFitnessPercent') and node != backdrop:
            # The text and its absolute progress fill share the original live value.
            absolute_box(doc, node, PORTRAIT_INSET, 0, PORTRAIT, BODY)
            doc.st(node, [(131099, doc.px(1)), (131101, doc.px(14))])
            counts['labels'] += 1
    assert counts == {'labels': 204, 'tracks': 2, 'fills': 204}, counts
    return counts


def copy_feet_to_combined(doc, donor, frame):
    tree = Tree(doc.d, doc.s)
    feet = ('LeftFootedness', 'RightFootedness')
    for index, field in enumerate(feet):
        original = donor.named('Detailed' + field + 'PlayerVisible')
        node = tree.add(donor.r, original, frame, 'Combined' + field + 'PlayerVisible', donor.s, True)
        def check_copy(a, b):
            donor_data, target_data = copy.deepcopy(donor.data(a)), copy.deepcopy(tree.sd(b))
            donor_data.pop('uxmlAssetId')
            target_data.pop('uxmlAssetId')
            if a == original:
                target_data['name'] = donor_data['name']
            assert donor_data == target_data
            old_children = donor.a(a)['m_Children']
            new_children = tree.r[b]['data']['m_Children']
            assert len(old_children) == len(new_children)
            for old, new in zip(old_children, new_children):
                check_copy(old['rid'], new['rid'])
        check_copy(original, node)
        doc.r = tree.r
        style_feet(doc, node, index)
    return len(feet)


def fit_portrait_body(doc, combined):
    frame = doc.named('TacticsPlayerPortraitFrame')
    portrait = doc.named('TacticsPlayerPortraitBinding')
    image = doc.named('TacticsPlayerCardBackgroundImage')
    prefix = 'Combined' if combined else 'Detailed'
    surface = doc.named(prefix + 'CardInnerSurface')
    rim = doc.named(prefix + 'CardNativePositionBackground')
    children = [c['rid'] for c in doc.a(frame)['m_Children']]
    assert children.index(image) < children.index(portrait)
    assert doc.data(image)['pickingMode'] == 1
    old_ref = style_value(doc, image, 458753)
    assert old_ref['m_PathID'] == OLD_BACKGROUND
    texture_ref = dict(old_ref, m_PathID=GREEN)
    doc.st(surface, [(OPACITY, doc.num(0))])
    doc.st(rim, [(OPACITY, doc.num(0))])
    absolute_box(doc, image, 0, 0, BODY, BODY)
    doc.st(image, [(458753, doc.val(6, texture_ref)), (262153, doc.enum('scale-to-fit'))])
    absolute_box(doc, portrait, PORTRAIT_INSET, PORTRAIT_INSET, PORTRAIT, PORTRAIT)
    if combined:
        for outer in (1018, 1019):
            absolute_box(doc, outer, 2, -3, BODY, BODY)
        for inner in (1021, 1026, 1027, frame):
            absolute_box(doc, inner, 0, 0, BODY, BODY)
        movement = ((1029, 1044), (1033, 1053))
        other_icons = (1032, 1031)
    else:
        for outer in (1014, 1015):
            absolute_box(doc, outer, 2, -3, BODY, BODY)
        for inner in (1018, 1030, 1031, frame):
            absolute_box(doc, inner, 0, 0, BODY, BODY)
        movement = ((1024, 1034), (1028, 1043))
        other_icons = (1027, 1026, 1017)
    for index, (icon, glyph) in enumerate(movement):
        absolute_box(doc, icon, 54, 11 + 11 * index, 14, 14)
        absolute_box(doc, glyph, -1, -1, 16, 16)
    for index, icon in enumerate(other_icons):
        position(doc, icon, 52, 32 + 10 * index)
    for node in (frame, *([1015, 1020] if not combined else [])):
        doc.st(node, [(OVERFLOW, doc.enum('visible'))])
    return texture_ref, fit_fitness(doc)


def fit_combined_footer(doc):
    style_stars_and_name(doc, 1036, 1037)
    absolute_box(doc, 1035, 0, ROLE_Y, BODY, ROLE_HEIGHT)
    visibility_for_footer(doc, 1035)
    for index, nodes in enumerate(((1055, 1075, 1092, 1105, 1119), (1057, 1078, 1094, 1107, 1122))):
        slot, color, remapper, button, label = nodes
        width = BODY // 2
        absolute_box(doc, slot, index * width, 0, width, ROLE_HEIGHT)
        for inner in (color, remapper, button):
            doc.size(inner, width, ROLE_HEIGHT)
        style_role_text(doc, label)


def fit_detailed_footer(doc, touch):
    body_nodes = (1001, 1005, 1007, 1008, 1009, 1015, 1018, 1037) if touch else (1001, 1005, 1007, 1009, 1014)
    for node in body_nodes:
        absolute_box(doc, node, 0, 0, BODY, BODY)
    style_stars_and_name(doc, 1027 if touch else 1022, 1061 if touch else 1016)
    phase = doc.named('DetailedCurrentPhasePositionContext')
    button = doc.named('DetailedCurrentPhasePositionButton')
    absolute_box(doc, phase, 0, ROLE_Y, BODY, ROLE_HEIGHT)
    absolute_box(doc, button, 0, 0, BODY, ROLE_HEIGHT)
    visibility_for_footer(doc, phase)
    for index, field in enumerate(('LeftFootedness', 'RightFootedness')):
        style_feet(doc, doc.named('Detailed' + field + 'PlayerVisible'), index)


def preserve_original_bindings(doc, original, extended_parent=None):
    for node, record in refs(original).items():
        actual = copy.deepcopy(doc.r[node])
        original_data = record.get('data', {})
        if 'm_RuleIndex' in original_data:
            actual['data']['m_RuleIndex'] = original_data['m_RuleIndex']
        if node == extended_parent:
            assert actual['data']['m_Children'][:len(original_data['m_Children'])] == original_data['m_Children']
            actual['data']['m_Children'] = original_data['m_Children']
        assert actual == record, (doc.d['m_Name'], node)
    assert doc.d['m_Usings'] == original['m_Usings']


def register_texture_preloads(bundle_meta, refs_by_asset, catalog):
    tree = bundle_meta.read_typetree()
    updated = set()
    preload = tree['m_PreloadTable']
    new_spans = {}
    for key, entry in tree['m_Container']:
        asset = entry['asset']
        if asset['m_FileID'] != 0 or asset['m_PathID'] not in refs_by_asset:
            continue
        locations = catalog.locations(key)
        assert locations, key
        for location in locations:
            dependencies = catalog.location(location)['dependencies']
            bundles = [catalog.location(dep)['internal'].replace('\\', '/').rsplit('/', 1)[-1] for dep in dependencies]
            assert bundles[0] == W and BACKGROUND_BUNDLE in bundles, (key, bundles)
        texture_ref = refs_by_asset[asset['m_PathID']]
        index, size = entry['preloadIndex'], entry['preloadSize']
        span = copy.deepcopy(preload[index:index + size])
        if texture_ref not in span:
            if (index, size) not in new_spans:
                span = [texture_ref if p == dict(texture_ref, m_PathID=OLD_BACKGROUND) else p for p in span]
                if texture_ref not in span:
                    span.append(texture_ref)
                new_spans[index, size] = (len(preload), len(span))
                preload.extend(span)
            entry['preloadIndex'], entry['preloadSize'] = new_spans[index, size]
        assert texture_ref in preload[entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']]
        updated.add(asset['m_PathID'])
    assert updated == refs_by_asset.keys()
    bundle_meta.save_typetree(tree)
    return tree


for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    gameworld = UnityPy.load(before[folder / W])
    env[W] = gameworld
    objs[W] = {obj.path_id: obj for obj in gameworld.objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    catalog_path = (GAME.parent if tag == 'game' else SKIN) / 'catalog.bin'
    catalog = catalog_module.Catalog(before[catalog_path])
    donor = Doc(W, name='TacticsDetailedCardDetailsDesktop')
    refs_by_asset = {}
    branch_checks = {'target': tag, 'templates': [], 'fitness': {}}
    for name in (
        'TacticsPositionCombined', 'TacticsPositionDetailed',
        'TacticsDetailedCardDetailsDesktop', 'TacticsDetailedCardDetailsTouch',
        'TacticsDetailedCardPositionButton',
    ):
        doc = Doc(W, name=name)
        original = copy.deepcopy(doc.d)
        extended_parent = None
        if name in ('TacticsPositionCombined', 'TacticsPositionDetailed'):
            combined = name == 'TacticsPositionCombined'
            texture_ref, counts = fit_portrait_body(doc, combined)
            refs_by_asset[doc.obj.path_id] = texture_ref
            refs_by_asset[doc.sid] = texture_ref
            branch_checks['fitness'][name] = counts
            if combined:
                fit_combined_footer(doc)
                extended_parent = doc.named('TacticsPlayerPortraitFrame')
                branch_checks['combined_live_foot_indicators'] = copy_feet_to_combined(doc, donor, extended_parent)
        elif name == 'TacticsDetailedCardPositionButton':
            for node in (1001, 1002, 1021, 1004, 1006, 1008):
                doc.size(node, BODY, ROLE_HEIGHT)
            style_role_text(doc, 1011)
        else:
            fit_detailed_footer(doc, touch=name.endswith('Touch'))
        preserve_original_bindings(doc, original, extended_parent)
        doc.save()
        branch_checks['templates'].append(name)
    bundle_meta = next(obj for obj in objs[W].values() if obj.type.name == 'AssetBundle')
    changes[W][bundle_meta.path_id] = register_texture_preloads(bundle_meta, refs_by_asset, catalog)

    data = gameworld.file.save(packer='lz4')
    combined_env = UnityPy.load(data, str(folder / BACKGROUND_BUNDLE))
    saved = {obj.path_id: obj for obj in combined_env.objects if obj.assets_file.name == bundle_meta.assets_file.name}
    assert saved.keys() == original_hashes.keys()
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid], pid
        else:
            assert sha(obj.get_raw_data()) == original_hashes[pid], pid
    for pid, texture_ref in refs_by_asset.items():
        texture = PPtr(**texture_ref, assetsfile=saved[pid].assets_file).deref()
        assert texture.peek_name() == 'patchplayerbggreen'
    branch_checks['background_resolved'] = str(GREEN)
    branch_checks['catalog_and_preload_verified'] = True
    branch_checks['original_serialized_bindings_preserved'] = True
    checks.append(branch_checks)
    outputs[folder / W] = data
    (OUT / ('output-' + tag)).mkdir()
    (OUT / ('output-' + tag) / W).write_bytes(data)

description = (
    '战术板主体76×76，等比显示patchplayerbggreen，头像60×60居中；星级顶部，'
    '原生体能/左右脚/位置与状态图标位于头像上层，体能条贴头像底边。'
    '框外姓名下接位置，有球/无球各一项，合并左右38px等宽，中文短名允许两行。'
    '已检查本地及跨包引用、原生绑定、目录预加载和无关对象，实际游戏显示待确认。'
)
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

(R / 'current-tactics-card-layout.json').write_text(json.dumps({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'card_size': [BODY, BODY], 'portrait_size': [PORTRAIT, PORTRAIT],
    'background': {'name': 'patchplayerbggreen', 'path_id': str(GREEN)},
    'name_top': NAME_Y, 'role_top': ROLE_Y, 'combined_role_widths': [BODY // 2] * 2,
    'fitness_top': BAR_Y, 'portrait_rim_visible': False,
    'manifest': str(OUT / 'manifest.json'),
}, ensure_ascii=False, indent=2), 'utf8')
