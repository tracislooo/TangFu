"""Move the tactics card's left-side indicators ten pixels farther left."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-left-overlays-')
exec(compile(bootstrap, 'load-current-tactics-resources', 'exec'))

helpers = [node for node in ast.parse(base).body if getattr(node, 'name', '') == 'style_value']
exec(compile(ast.Module(body=helpers, type_ignores=[]), 'read-inline-style', 'exec'))

LEFT = 131089
SHIFT = -10
RATING_HOSTS = {
    'TacticsPositionCombined': ('Combined', 1036),
    'TacticsDetailedCardDetailsDesktop': ('Detailed', 1022),
    'TacticsDetailedCardDetailsTouch': ('Detailed', 1027),
}
TEMPLATES = ('TacticsPositionDetailed', *RATING_HOSTS)
outputs = {}
checks = []


for folder, target in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}

    for template in TEMPLATES:
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        move = set()
        if template in ('TacticsPositionCombined', 'TacticsPositionDetailed'):
            move.update(
                node for node, record in doc.r.items()
                if 'm_Parent' in record.get('data', {})
                and doc.data(node).get('name', '').startswith('PitchFitnessPercent')
            )
            assert len(move) == 205
        if template in RATING_HOSTS:
            prefix, rating_host = RATING_HOSTS[template]
            assert doc.data(rating_host)['name'] == 'Stars'
            assert style_value(doc, rating_host, LEFT)['value'] == 3
            move.add(rating_host)
            move.update(doc.named(f'{prefix}{side}FootednessPlayerVisible') for side in ('Left', 'Right'))

        for node in sorted(move):
            old = style_value(doc, node, LEFT)
            assert old['unit'] == 1
            doc.st(node, [(LEFT, doc.px(old['value'] + SHIFT))])
            assert style_value(doc, node, LEFT) == {'unit': 1, 'value': old['value'] + SHIFT}

        for node, original_record in refs(original).items():
            actual = copy.deepcopy(doc.r[node])
            if node in move:
                actual['data']['m_RuleIndex'] = original_record['data']['m_RuleIndex']
            assert actual == original_record, (template, node)
        doc.save()
        checks.append({'target': target, 'template': template, 'style_nodes': len(move), 'left_delta_px': SHIFT})

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

description = '战术卡体能百分比及其底色、左右脚、灰星及黄星评级徽标在当前坐标基础上再左移10px。'
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

index_path = R / 'current-tactics-card-layout.json'
index = json.loads(index_path.read_text('utf8'))
index.update({
    'patch': str(OUT),
    'installed': manifest['installed'],
    'runtime_verified': False,
    'left_info_shift_x': index['left_info_shift_x'] + SHIFT,
    'rating_badge': [index['rating_badge'][0] + SHIFT, *index['rating_badge'][1:]],
    'manifest': str(OUT / 'manifest.json'),
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
