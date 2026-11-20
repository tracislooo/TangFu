"""Hide the old rectangular frame and bind star badges directly to the native rating."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-card-frame-star-visibility-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

for filename, names in [
    ('apply-tactics-green-pitch-player-card.py', {'absolute_box', 'style_value'}),
    ('combine-tactics-condition-sharpness.py', {'decode', 'encode'}),
]:
    source = ast.parse((R / filename).read_text('utf8'))
    definitions = [node for node in source.body if getattr(node, 'name', '') in names]
    exec(compile(ast.Module(body=definitions, type_ignores=[]), filename, 'exec'))

LEFT, TOP, WIDTH, HEIGHT = 131089, 131104, 131105, 131087
BADGE_W, BADGE_H = 24, 12
NATIVE_VISIBLE = 'd52cf0b2ba55c764b9ecda52092aa257'
RATING_PATH = b'starrating.MinValue'
STAR_CLASSES = ['fm-star-rating-star-no-margin', 'ability-max-potential-level-fullfilled-youth-false']
FRAME_CLASS = 'layout-tile-interaction_border_tactics'
outputs = {}
checks = []


def add(doc, donor, source, parent, name):
    node = doc.add(donor, source, parent, name)
    if 'm_ParentId' in doc.a(node):
        doc.a(node)['m_ParentId'] = doc.a(parent)['m_Id']
    return node


def remove_previous_tree(doc, root):
    removed = set()

    def visit(node):
        for child in doc.a(node)['m_Children']:
            visit(child['rid'])
        removed.add(doc.a(node)['m_SerializedData']['rid'])
        removed.add(node)

    visit(root)
    parent = doc.a(root)['m_Parent']['rid']
    doc.a(parent)['m_Children'].remove({'rid': root})
    doc.d['references']['RefIds'] = [r for r in doc.d['references']['RefIds'] if r['rid'] not in removed]
    for node in removed:
        del doc.r[node]
    return parent, removed


def bind_direct_badges(doc, donor, parent, color):
    host = add(doc, donor, 1036, parent, 'DirectTacticsRatingBadges')
    absolute_box(doc, host, 0, 0, BADGE_W, BADGE_H)
    for rating in range(11):
        gate = add(doc, donor, 1126, host, f'DirectTacticsRatingEquals{rating}')
        absolute_box(doc, gate, 0, 0, BADGE_W, BADGE_H)
        doc.st(gate, [(458752, doc.val(4, color))])
        gate_data = doc.data(gate)
        fn = gate_data['Binding']['m_visualFunction']
        assert fn['m_target']['m_guid'] == NATIVE_VISIBLE
        inputs = fn['m_inputs']['m_variable']
        args = decode(inputs['m_argumentBytes'])
        assert len(args) == 4 and args[0][-4:] == struct.pack('<i', 2)
        assert b'NullVisualArg' in args[2]
        old_path = b'starrating.MaxValue'
        assert args[3].endswith(bytes([len(old_path)]) + old_path)
        struct.pack_into('<i', args[1], len(args[1]) - 4, rating)
        args[3][-len(old_path) - 1:] = bytes([len(RATING_PATH)]) + RATING_PATH
        inputs['m_argumentBytes'] = encode(args)

        label = add(doc, donor, donor.named('CompactStarNumber'), gate, 'DirectTacticsRatingNumber')
        data = doc.data(label)
        assert data['TextBinding']['m_kind'] == 0 and data['TextBinding_UxmlAttributeFlags'] == 0
        data['text'] = f'{rating / 2:g}'
        absolute_box(doc, label, 1, 0, 13, BADGE_H)
        doc.st(label, [
            (65537, doc.px(9)), (65543, doc.enum('bold')), (65546, doc.enum('middle-center')),
            (65536, doc.val(4, {'r': 1., 'g': 1., 'b': 1., 'a': 1.})),
        ])
        icon = add(doc, donor, 1036, gate, 'DirectTacticsNativeGoldStar')
        doc.a(icon)['m_Classes'] = STAR_CLASSES[:]
        absolute_box(doc, icon, 14, 1, 9, 10)

    seen = {}
    for child in doc.a(host)['m_Children']:
        gate = child['rid']
        args = decode(doc.data(gate)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        assert args[3].endswith(bytes([len(RATING_PATH)]) + RATING_PATH)
        rating = struct.unpack_from('<i', args[1], len(args[1]) - 4)[0]
        label, icon = (child['rid'] for child in doc.a(gate)['m_Children'])
        seen[rating] = doc.data(label)['text']
        assert doc.a(icon)['m_Classes'] == STAR_CLASSES
    assert seen == {rating: f'{rating / 2:g}' for rating in range(11)}
    return host


def replace_rating_tree(doc, donor, color):
    old_root = doc.named('CompactStarRatingAbove10')
    parent = doc.a(old_root)['m_Parent']['rid']
    previous = doc.a(parent)['m_Children'].index({'rid': old_root})
    _, removed = remove_previous_tree(doc, old_root)
    host = bind_direct_badges(doc, donor, parent, color)
    children = doc.a(parent)['m_Children']
    children.remove({'rid': host})
    children.insert(previous, {'rid': host})
    return parent, removed


def preserve_untouched_nodes(doc, original, parent, removed):
    for node, old in refs(original).items():
        if node in removed:
            assert node not in doc.r
            continue
        actual = copy.deepcopy(doc.r[node])
        if 'm_RuleIndex' in old.get('data', {}):
            actual['data']['m_RuleIndex'] = old['data']['m_RuleIndex']
        if node == parent:
            old_children = old['data']['m_Children']
            children = actual['data']['m_Children']
            assert len(children) == len(old_children)
            assert [ch for ch in children if ch['rid'] in refs(original)] == [ch for ch in old_children if ch['rid'] not in removed]
            actual['data']['m_Children'] = old_children
        assert actual == old, (doc.d['m_Name'], node)
    assert doc.d['m_Usings'] == original['m_Usings']


for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    donor = Doc(W, name='TacticsPositionCombined')
    for name in ('TacticsPositionCombined', 'TacticsDetailedCardDetailsDesktop', 'TacticsDetailedCardDetailsTouch'):
        doc = Doc(W, name=name)
        original = copy.deepcopy(doc.d)
        color = style_value(donor, donor.named('PitchFitnessPercentageBackdrop'), 458752)
        frame_nodes = [
            node for node, record in doc.r.items()
            if FRAME_CLASS in record.get('data', {}).get('m_Classes', [])
        ]
        for node in frame_nodes:
            assert not doc.a(node)['m_Children']
            doc.st(node, [(458767, doc.num(0))])
        parent, removed = replace_rating_tree(doc, donor, color)
        preserve_untouched_nodes(doc, original, parent, removed)
        doc.save()
        checks.append({
            'target': tag, 'template': name, 'hidden_decorative_frames': frame_nodes,
            'direct_exact_rating_gates': 11, 'bindings_and_events_preserved': True,
        })

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
    '隐藏战术卡原矩形装饰框，保留绿盾和卡片偏移。用原生BindIntToVisible直接按'
    'starrating.MinValue显示0–5星徽标，替换旧多层分支。保留原缺失文案、位置点击和其他布局。'
    '资源回读及安装校验通过，游戏内显示待确认。'
)
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

index_path = R / 'current-tactics-card-layout.json'
index = json.loads(index_path.read_text('utf8'))
index.update({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'native_decorative_frame_visible': False, 'rating_source': RATING_PATH.decode(),
    'rating_visibility': 'direct native integer equality',
    'manifest': str(OUT / 'manifest.json'),
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
