"""Adjust the current Combined and Detailed pitch cards in both installations."""
from pathlib import Path
import subprocess


bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
bootstrap = bootstrap.replace('inspect-fitness-backdrop-', 'tactics-card-left-info-rim-')
bootstrap = bootstrap.replace('hours=-4', 'hours=-7')
exec(compile(bootstrap, 'backup-current-tactics-resources', 'exec'))

LEFT, TOP, WIDTH, HEIGHT = 131089, 131104, 131105, 131087
MAX_WIDTH, PADDING_TOP, OPACITY = 131095, 131101, 458767
NAME_TOP = 76
ROLE_WIDTH = 36
DOWN = 6
outputs = {}
checks = []


def pixel_value(doc, node, key):
    rule = doc.s['m_Rules'][doc.a(node)['m_RuleIndex']]
    handle = next(p for p in rule['m_Properties'] if p['m_Id'] == key)['m_Values'][0]
    value = doc.s['dimensions'][handle['valueIndex']]
    assert handle['m_ValueType'] == 3 and value['unit'] == 1
    return value['value']


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

        def place(node, key, value):
            edits.setdefault(node, {})[key] = doc.px(value)

        if name_node is not None:
            assert pixel_value(doc, name_node, TOP) == 73
            place(name_node, TOP, NAME_TOP)

        if template in ('TacticsPositionCombined', 'TacticsPositionDetailed'):
            prefix = 'Combined' if template.endswith('Combined') else 'Detailed'
            rim = doc.named(prefix + 'CardNativePositionBackground')
            portrait = doc.named('TacticsPlayerPortraitBinding')
            frame = doc.named('TacticsPlayerPortraitFrame')
            children = doc.a(frame)['m_Children']
            assert children.index({'rid': rim}) < children.index({'rid': portrait})
            assert pixel_value(doc, portrait, WIDTH) == pixel_value(doc, portrait, HEIGHT) == 67
            assert pixel_value(doc, rim, WIDTH) == pixel_value(doc, rim, HEIGHT) == 67
            for key in (WIDTH, HEIGHT, 131097, 131096, MAX_WIDTH, 131094):
                place(rim, key, 73)
            place(rim, LEFT, 1)
            place(rim, TOP, 1)
            edits[rim][OPACITY] = doc.num(0.625)

            backdrop = doc.named('PitchFitnessPercentageBackdrop')
            old_top = pixel_value(doc, backdrop, TOP)
            place(backdrop, TOP, old_top + DOWN)
            fitness_labels = 0
            bars = 0
            for node, record in doc.r.items():
                if 'm_Parent' not in record.get('data', {}):
                    continue
                name = doc.data(node).get('name', '')
                if name.startswith('PitchFitnessPercent') and name != 'PitchFitnessPercentageBackdrop':
                    assert pixel_value(doc, node, PADDING_TOP) == old_top
                    place(node, PADDING_TOP, old_top + DOWN)
                    fitness_labels += 1
                elif 'CardFitnessFill' in name or name.endswith('CardFitnessTrack'):
                    assert pixel_value(doc, node, TOP) == 68
                    assert pixel_value(doc, node, HEIGHT) == 3
                    bars += 1
            assert fitness_labels == 204 and bars == 206

        if template == 'TacticsPositionCombined':
            place(1035, TOP, pixel_value(doc, 1035, TOP) + DOWN)
            for node in (1035, 1055, 1057):
                place(node, WIDTH, ROLE_WIDTH)
            for node in (1075, 1078, 1092, 1094, 1105, 1107):
                place(node, MAX_WIDTH, ROLE_WIDTH)
        elif template in ('TacticsDetailedCardDetailsDesktop', 'TacticsDetailedCardDetailsTouch'):
            context = doc.named('DetailedCurrentPhasePositionContext')
            for node in (
                context,
                doc.named('DetailedLeftFootednessPlayerVisible'),
                doc.named('DetailedRightFootednessPlayerVisible'),
            ):
                place(node, TOP, pixel_value(doc, node, TOP) + DOWN)
            for node in (context, doc.named('DetailedCurrentPhasePositionButton')):
                place(node, WIDTH, ROLE_WIDTH)
        elif template == 'TacticsDetailedCardPositionButton':
            for node in (1001, 1002, 1004, 1006, 1008):
                place(node, WIDTH, ROLE_WIDTH)
                place(node, MAX_WIDTH, ROLE_WIDTH)

        for node, properties in edits.items():
            doc.st(node, list(properties.items()))
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

# Reuse the local install/verify workflow and guard both rollback files before copying.
G = W
marker = "for p,b in before.items():\n if p.name.startswith('catalog.')"
tail = marker + Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split(marker)[1]
description = (
    '战术板合并与详细卡左侧位置、左右脚、体能数字下移6px，位置标签底板28→36px。'
    '恢复头像下的73×73px半透明位置色底框（x1/y1，62.5%不透明），姓名位于框外y76，'
    '体能横条位于头像内区底部y68–71。仅修改样式，序列化回读及无关对象校验通过。'
)
start = tail.index("(OUT/'修改说明.md').write_text(")
end = tail.index('\nprint(', start)
tail = tail[:start] + f"(OUT/'修改说明.md').write_text({description!r},'utf8')" + tail[end:]
needle = "for p in outputs:\n tag='game' if p.parent==GAME else 'skin'\n install.append"
guard = (
    "for p in outputs:\n"
    " restore.append(\"if ((Get-FileHash -LiteralPath '\"+str(p)+\"').Hash.ToLower() -ne '\""
    "+sha(outputs[p])+\"') { throw 'Target changed after this patch; merge rollback required.' }\")\n"
)
assert needle in tail
exec(compile(tail.replace(needle, guard + needle), 'verify-and-install', 'exec'))

(R / 'current-tactics-card-layout.json').write_text(json.dumps({
    'patch': str(OUT),
    'installed': manifest['installed'],
    'runtime_verified': False,
    'left_offset_y': DOWN,
    'role_width': ROLE_WIDTH,
    'portrait_rim': {'x': 1, 'y': 1, 'width': 73, 'height': 73, 'opacity': 0.625},
    'name_top': NAME_TOP,
    'fitness_top': 68,
    'manifest': str(OUT / 'manifest.json'),
}, ensure_ascii=False, indent=2), 'utf8')
