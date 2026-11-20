"""Decode both native star bands on the current tactics cards."""
from pathlib import Path
import subprocess


previous_patch = Path('fix-tactics-overlays-and-rating-selector.py').read_text('utf8')
bootstrap = previous_patch[:previous_patch.index('index_path=')]
bootstrap = bootstrap.replace('tactics-overlays-down-rating-switch-', 'tactics-grey-gold-rating-')
exec(compile(bootstrap, 'load-current-tactics-resources', 'exec'))

RATING_PATH = b'starrating.minvalue'
STAR_CLASS = 'ability-max-potential-level-fullfilled-youth-'
TEMPLATES = (
    'TacticsPositionCombined',
    'TacticsDetailedCardDetailsDesktop',
    'TacticsDetailedCardDetailsTouch',
)
outputs = {}
checks = []


def clone_badge(doc, source, parent, name):
    node = doc.add(doc, source, parent, name)
    old, new = doc.a(source), doc.a(node)
    new['m_Classes'] = old['m_Classes'][:]
    new['m_RuleIndex'] = old['m_RuleIndex']
    if 'm_ParentId' in new:
        new['m_ParentId'] = doc.a(parent)['m_Id']
    return node


def badge_arguments(doc, selector):
    function = doc.data(selector)['Binding']['m_visualFunction']
    assert function['m_target']['m_guid'] == 'f6f314e9db56227459137669d87c44e9'
    inputs = function['m_inputs']['m_variable']
    args = decode(inputs['m_argumentBytes'])
    assert len(args) == 3 and struct.unpack('<i', args[0][-4:])[0] == 2
    assert args[2].endswith(bytes([len(RATING_PATH)]) + RATING_PATH)
    return inputs, args


def update_badges(doc):
    host = doc.named('DirectTacticsRatingBadges')
    zero, *grey = (child['rid'] for child in doc.a(host)['m_Children'])
    assert len(grey) == 10
    _, zero_value = (child['rid'] for child in doc.a(zero)['m_Children'])
    # A native zero rating draws no filled stars.
    doc.st(zero_value, [(131081, doc.enum('none'))])

    for half_stars, selector in enumerate(grey, 1):
        blank, value = (child['rid'] for child in doc.a(selector)['m_Children'])
        number, star = (child['rid'] for child in doc.a(value)['m_Children'])
        assert doc.data(number)['text'] == f'{half_stars / 2:g}'
        assert doc.a(star)['m_Classes'] == ['fm-star-rating-star-no-margin', STAR_CLASS + 'false']

        gold_code = half_stars + 10
        gold = clone_badge(doc, selector, host, f'TacticsRatingSelector{gold_code}')
        inputs, args = badge_arguments(doc, gold)
        assert struct.unpack('<i', args[1][-4:])[0] == half_stars
        struct.pack_into('<i', args[1], len(args[1]) - 4, gold_code)
        inputs['m_argumentBytes'] = encode(args)

        clone_badge(doc, blank, gold, 'RatingNotMatched')
        gold_value = clone_badge(doc, value, gold, f'TacticsRatingValue{gold_code}')
        clone_badge(doc, number, gold_value, 'DirectTacticsRatingNumber')
        clone_badge(doc, star, gold_value, 'DirectTacticsNativeGoldStar')

        doc.a(star)['m_Classes'][-1] = STAR_CLASS + 'true'
        doc.data(star)['name'] = 'DirectTacticsNativeGreyStar'

    labels = {}
    for child in doc.a(host)['m_Children'][1:]:
        selector = child['rid']
        _, args = badge_arguments(doc, selector)
        code = struct.unpack('<i', args[1][-4:])[0]
        _, value = (branch['rid'] for branch in doc.a(selector)['m_Children'])
        number, star = (element['rid'] for element in doc.a(value)['m_Children'])
        labels[code] = (doc.data(number)['text'], doc.a(star)['m_Classes'][-1])
    assert labels == {
        code: (f'{(code - 10 if code > 10 else code) / 2:g}', STAR_CLASS + ('false' if code > 10 else 'true'))
        for code in range(1, 21)
    }
    return host


for folder, target in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}

    for template in TEMPLATES:
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        host = update_badges(doc)
        original_refs = refs(original)
        # Changes to preexisting nodes are confined to the badge and its descendants.
        descendants = {host}
        pending = [host]
        while pending:
            element = original_refs[pending.pop()]['data']
            descendants.add(element['m_SerializedData']['rid'])
            children = [child['rid'] for child in element['m_Children']]
            descendants.update(children)
            pending.extend(children)
        assert all(doc.r[node] == record for node, record in original_refs.items() if node not in descendants)
        doc.save()
        checks.append({'target': target, 'template': template, 'grey_levels': 10, 'gold_levels': 10})

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

description = (
    '战术卡星级分两段读取原生实星数。原始值1–10显示灰星和原值÷2，'
    '11–20显示黄星和(原值−10)÷2。两段各显示0.5至5星。'
    '零级不显示星标，原生评分缺失分支保留。实际游戏显示待确认。'
)
installer = previous_patch[previous_patch.index('previous = (R /'):previous_patch.index('index.update(')]
exec(compile(installer, 'verify-and-install', 'exec'))

index_path = R / 'current-tactics-card-layout.json'
index = json.loads(index_path.read_text('utf8'))
index.update({
    'patch': str(OUT),
    'installed': manifest['installed'],
    'runtime_verified': False,
    'rating_patch': str(OUT),
    'rating_source': RATING_PATH.decode(),
    'rating_visibility': 'exact native half-star code in either palette',
    'rating_bands': {'grey': [1, 10], 'gold': [11, 20], 'gold_offset': 10},
    'manifest': str(OUT / 'manifest.json'),
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
