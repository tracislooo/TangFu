"""Narrow the pitch card role labels and hide the portrait rim."""
from pathlib import Path
import subprocess


previous = Path('adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
bootstrap = previous[previous.index('bootstrap = '):previous.index('LEFT, TOP,')]
bootstrap = bootstrap.replace('tactics-card-left-info-rim-', 'tactics-card-narrow-role-no-rim-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

LEFT, TOP, WIDTH, MAX_WIDTH, OPACITY = 131089, 131104, 131105, 131095, 458767
ROLE_WIDTH, ROLE_LEFT, NAME_TOP = 26, -12, 73
outputs = {}
checks = []

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}

    for template, name_node in [
        ('TacticsPositionCombined', 1037),
        ('TacticsPositionDetailed', None),
        ('TacticsDetailedCardDetailsDesktop', 1016),
        ('TacticsDetailedCardDetailsTouch', 1061),
        ('TacticsDetailedCardPositionButton', None),
    ]:
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        edits = {}

        if name_node is not None:
            edits[name_node] = [(TOP, doc.px(NAME_TOP))]

        if template in ('TacticsPositionCombined', 'TacticsPositionDetailed'):
            prefix = 'Combined' if template.endswith('Combined') else 'Detailed'
            rim = doc.named(prefix + 'CardNativePositionBackground')
            assert doc.data(rim)['pickingMode'] == 1
            edits[rim] = [(OPACITY, doc.num(0))]

        if template == 'TacticsPositionCombined':
            edits[1035] = [(LEFT, doc.px(ROLE_LEFT)), (WIDTH, doc.px(ROLE_WIDTH))]
            for node in (1055, 1057):
                edits[node] = [(WIDTH, doc.px(ROLE_WIDTH))]
            for node in (1075, 1078, 1092, 1094, 1105, 1107):
                edits[node] = [(MAX_WIDTH, doc.px(ROLE_WIDTH))]
        elif template in ('TacticsDetailedCardDetailsDesktop', 'TacticsDetailedCardDetailsTouch'):
            context = doc.named('DetailedCurrentPhasePositionContext')
            edits[context] = [(LEFT, doc.px(ROLE_LEFT)), (WIDTH, doc.px(ROLE_WIDTH))]
            edits[doc.named('DetailedCurrentPhasePositionButton')] = [(WIDTH, doc.px(ROLE_WIDTH))]
        elif template == 'TacticsDetailedCardPositionButton':
            for node in (1001, 1002, 1004, 1006, 1008):
                edits[node] = [(WIDTH, doc.px(ROLE_WIDTH)), (MAX_WIDTH, doc.px(ROLE_WIDTH))]

        for node, properties in edits.items():
            doc.st(node, properties)
        for node, original_record in refs(original).items():
            new_record = copy.deepcopy(doc.r[node])
            if node in edits:
                new_record['data']['m_RuleIndex'] = original_record['data']['m_RuleIndex']
            assert new_record == original_record, (template, node)
        doc.save()
        checks.append({'target': tag, 'template': template, 'style_nodes': len(edits), 'bindings_preserved': True})

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
    '两种战术板卡片隐藏头像半透明底框，位置标签宽36→26px，左移4px（x−8→−12）。'
    '姓名恢复y73，体能条在头像底部y68–71。资源回读及无关对象校验通过。'
)
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

(R / 'current-tactics-card-layout.json').write_text(json.dumps({
    'patch': str(OUT),
    'installed': manifest['installed'],
    'runtime_verified': False,
    'left_offset_y': 6,
    'role_width': ROLE_WIDTH,
    'role_left': ROLE_LEFT,
    'portrait_rim_visible': False,
    'name_top': NAME_TOP,
    'fitness_top': 68,
    'manifest': str(OUT / 'manifest.json'),
}, ensure_ascii=False, indent=2), 'utf8')
