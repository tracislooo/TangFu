"""Raise the card art and live controls inside the existing tactics frame."""
from pathlib import Path
import subprocess


base = Path('apply-tactics-green-pitch-player-card.py').read_text('utf8')
bootstrap = base[base.index('bootstrap = '):base.index('from UnityPy.classes import PPtr')]
bootstrap = bootstrap.replace('tactics-green-pitch-player-card-', 'tactics-card-near-frame-top-')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

parsed = ast.parse(base)
definitions = [node for node in parsed.body if getattr(node, 'name', '') in {'style_value', 'preserve_original_bindings'}]
exec(compile(ast.Module(body=definitions, type_ignores=[]), 'tactics-card-geometry', 'exec'))
index_path = R / 'current-tactics-card-layout.json'
index = json.loads(index_path.read_text('utf8'))
assert index['native_decorative_frame_visible'] is False
previous_patch = Path(index['patch'])
TOP, RAISE = 131104, 7
outputs = {}
checks = []

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    original_bundle = UnityPy.load(str(previous_patch / ('backup-' + tag) / W))
    original_objects = {obj.path_id: obj for obj in original_bundle.objects}

    for template, move_nodes in [('TacticsPositionCombined', (1018, 1026)), ('TacticsPositionDetailed', (1014, 1015))]:
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        for node in move_nodes:
            old_top = style_value(doc, node, TOP)
            assert old_top['unit'] == 1
            doc.st(node, [(TOP, doc.px(old_top['value'] - RAISE))])
        if template == 'TacticsPositionCombined':
            frame = 1027
            assert 'layout-tile-interaction_border_tactics' in doc.a(frame)['m_Classes']
            assert style_value(doc, frame, 458767) == 0
            prior = original_objects[doc.obj.path_id].read_typetree()
            prior_rule = refs(prior)[frame]['data']['m_RuleIndex']
            prior_sheet = original_objects[doc.sid].read_typetree()
            assert doc.s['m_Rules'][prior_rule] == prior_sheet['m_Rules'][prior_rule]
            doc.a(frame)['m_RuleIndex'] = prior_rule
            assert style_value(doc, frame, TOP)['value'] == 0
        preserve_original_bindings(doc, original)
        doc.save()
        checks.append({
            'target': tag, 'template': template, 'content_relative_y': -RAISE,
            'frame_position_preserved': True, 'original_bindings_preserved': True,
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
    '保留原合并卡淡框和框位置，绿盾及卡片内容相对框顶上移7px。'
    '详细卡同步上移内容，维持原淡框状态。保留星级修正及原点击/绑定。'
    '资源回读及安装校验通过，游戏内效果待确认。'
)
previous = (R / 'adjust-tactics-card-left-info-and-rim.py').read_text('utf8')
installer = previous[previous.index('G = W\nmarker = '):previous.index("(R / 'current-tactics-card-layout.json')")]
start = installer.index('description = (')
end = installer.index('start = tail.index', start)
exec(compile(installer[:start] + installer[end:], 'verify-and-install', 'exec'))

index.update({
    'patch': str(OUT), 'installed': manifest['installed'], 'runtime_verified': False,
    'native_decorative_frame_visible': True, 'native_decorative_frame_scope': 'Combined',
    'content_offset_relative_to_frame': -RAISE, 'rating_patch': str(previous_patch),
    'manifest': str(OUT / 'manifest.json'),
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
