"""Resize installed Combined card without replacing bindings or other resources."""
from pathlib import Path

source = Path(__file__).with_name('trial-tactics-combined-layered-card.py').read_text('utf8')
prefix = source.split('# Keep the pitch anchor / footprint')[0]
exec(compile(prefix.replace('tactics-combined-layered-card-trial-', 'tactics-combined-square64-v2-'), 'square64-boot', 'exec'))

def named(name):
    return next(i for i, a in t.r.items()
                if t.r.get(a.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name)

def value(i, key):
    rule = sheet['m_Rules'][t.r[i]['data']['m_RuleIndex']]
    h = next(p for p in rule['m_Properties'] if p['m_Id'] == key)['m_Values'][0]
    return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]

frame, gate, fitness_root = 1165, 1171, 1173
assert value(frame, 131105)['value'] == 80 and value(frame, 131087)['value'] == 86
border = named('CombinedCardNativePositionBackground')
surface = named('CombinedCardInnerSurface')
track = named('CombinedCardFitnessTrack')
transparent = {'r': 0.0, 'g': 0.0, 'b': 0.0, 'a': 0.0}

# Preserve the 80x70 pitch anchor. The 64px card sits 8px in from its sides;
# its bottom stays at the same y=30 as the preceding 80x86 trial.
box(1018, 8, -34, 64, 64)
box(1021, 0, 0, 64, 64)
box(frame, 0, 0, 64, 64)
rounded(frame, 6)
box(border, 0, 0, 64, 64)
rounded(border, 6, True)
box(surface, 2, 2, 60, 60)
rounded(surface, 4, True)
box(1167, 2, 2, 60, 60)
rounded(1167, 4, True)

for node, y in [(1029, 20), (1033, 31)]:
    box(node, 4, y, 10, 10)
for glyph in [1044, 1053]:
    # Native glyph templates use a 16px internal layout. Center a 0.625
    # transform to render at 10px without touching their visibility bindings.
    box(glyph, -3, -3, 16, 16)
    t.edit(glyph, [P(327681, st.num(.625), st.num(.625))])
for node, y in [(1032, 9), (1031, 24)]:
    box(node, 48, y, 16, 16)
    t.edit(node, [P(327681, st.num(.625), st.num(.625))])

# Same decision tree and colours; resize the active leaf and existing fill.
box(gate, 0, 0, 64, 70)
box(track, 0, 67, 64, 3)
rounded(track, 1.5, True)
leaves = {}
for i, a in original.items():
    if a.get('data', {}).get('m_FullTypeName') != 'SI.Bindable.SIText': continue
    name = serial(original, i)['data'].get('name', '')
    if not name.startswith('PitchFitnessPercent'): continue
    suffix = name.removeprefix('PitchFitnessPercent')
    pct = None if suffix == 'None' else int(suffix)
    leaves[i] = pct
    box(i, 0, 0, 64, 70)
    t.edit(i, [P(65537, st.px(9)), P(65543, st.en('bold')),
               P(65546, st.en('upper-left')), P(131099, st.px(4)), P(131101, st.px(9)),
               P(458768, st.en('visible'))])
    fill = named('CombinedCardFitnessFill' + str(pct))
    box(fill, 0, 67, 0 if pct is None else f32(pct * .64), 3)
    rounded(fill, 1.5, True)
assert len(leaves) == 102

# Keep the original FMPitchPosition scope and all descendants in their original
# hierarchy so the two native role buttons retain their context and events.
box(1019, 8, -34, 64, 64)
box(1026, 0, 0, 64, 64)
for node in [1019, 1026]:
    t.edit(node, [P(458768, st.en('visible')), P(458752, st.h(4, transparent))])
    ignore(node)  # Blank layout space passes clicks to the native shirt button.
box(1027, 0, 0, 64, 64)
rounded(1027, 6)

# Overlay the transparent native rating on the top rim, without a header band.
box(1036, 7, -4, 50, 8)
for node in [1036, 1059, 1080, 1096, 1111, 1125, 1126, 1112]:
    t.edit(node, [P(458752, st.h(4, transparent)), P(458768, st.en('visible')),
                  P(262150, st.px(0)), P(262151, st.px(0)),
                  P(131097, st.px(0)), P(131096, st.px(0)),
                  P(131105, st.px(50)), P(131087, st.px(8)),
                  P(131073, st.en('center')), P(131088, st.en('center'))])
box(1143, 0, -1, 50, 10)
t.edit(1143, [P(327681, st.num(.8), st.num(.8)), P(458752, st.h(4, transparent))])
for node in [1145, 1128]:
    t.edit(node, [P(65537, st.px(8)), P(65546, st.en('middle-center')),
                  P(131105, st.px(50)), P(131087, st.px(8)), P(262150, st.px(0)),
                  P(262151, st.px(0)), P(458752, st.h(4, transparent))])

# Name strip sits inside the portrait, above the native two-button footer.
box(1037, 2, 42, 60, 10)
t.edit(1037, [P(458752, st.h(4, {'r': 0.0, 'g': 0.0, 'b': 0.0, 'a': f32(.65)})),
               P(458768, st.en('hidden')), P(262147, st.px(0))])
for node in [1061, 1082, 1098]:
    t.edit(node, [P(131105, st.pct(100)), P(131087, st.px(10)),
                  P(131096, st.px(0)), P(131094, st.px(10)), P(262150, st.px(0)),
                  P(262151, st.px(0)), P(458752, st.h(4, transparent))])
for node in [1115, 1134, 1135, 1151]:
    t.edit(node, [P(131097, st.px(0)), P(131096, st.px(0)), P(131087, st.px(10)),
                  P(131094, st.px(10)), P(262150, st.px(0)), P(262151, st.px(0)),
                  P(65537, st.px(9)), P(65546, st.en('middle-center')),
                  P(65552, st.en('nowrap')), P(196609, st.en('ellipsis'))])
t.edit(1115, [P(131105, st.px(0)), P(131082, st.px(0)), P(131084, st.num(1))])
box(1132, 0, 1, 6, 8)
t.edit(1132, [P(131102, st.en('relative')), P(131093, st.px(1))])
t.edit(1158, [P(131097, st.px(0)), P(131105, st.px(6)), P(131087, st.px(8)),
               P(262151, st.px(0)), P(327681, st.num(.625), st.num(.625))])
for key in ['DisplayTooltipWhenElided', 'displayTooltipWhenElided']:
    assert key in t.sd(1135)
    t.sd(1135).update({key: 1, key + '_UxmlAttributeFlags': 1})

box(1035, 2, 52, 60, 10)
rounded(1035, 2, True)
for node in [1055, 1057, 1075, 1078, 1092, 1094, 1105, 1107]:
    t.edit(node, [P(131097, st.px(0)), P(131096, st.px(0)), P(131087, st.px(10)),
                  P(131094, st.px(10)), P(131085, st.num(1)), P(262150, st.px(0)),
                  P(262151, st.px(0))])
for node in [1055, 1057]: t.edit(node, [P(131082, st.pct(50)), P(131105, st.pct(50))])
for node in [1119, 1122]:
    t.edit(node, [P(65537, st.px(8)), P(65546, st.en('middle-center')),
                  P(131087, st.px(10)), P(131097, st.px(0)), P(131096, st.px(0)),
                  P(262150, st.px(0)), P(262151, st.px(0)), P(65552, st.en('nowrap')),
                  P(196609, st.en('ellipsis')), P(458768, st.en('hidden'))])

# Ratings paint last so transparent wrappers never place the stars underneath
# portrait overlays. IDs, parents and every button event remain the same.
children = t.r[1026]['data']['m_Children']
t.r[1026]['data']['m_Children'] = [a for a in children if a['rid'] != 1036] + [{'rid': 1036}]
for dim in sheet['dimensions']: dim['value'] = f32(dim['value'])

# Check serialized data changes are limited to documented presentation flags.
allowed_sd = {t.r[i]['data']['m_SerializedData']['rid']: {'pickingMode', 'pickingMode_UxmlAttributeFlags'}
              for i in [1019, 1026]}
allowed_sd[t.r[1135]['data']['m_SerializedData']['rid']] = {
    'DisplayTooltipWhenElided', 'DisplayTooltipWhenElided_UxmlAttributeFlags',
    'displayTooltipWhenElided', 'displayTooltipWhenElided_UxmlAttributeFlags'}
for i, old in original.items():
    if 'UxmlSerializedData' not in old.get('type', {}).get('class', ''): continue
    a, b = copy.deepcopy(old), copy.deepcopy(t.r[i])
    for key in allowed_sd.get(i, set()): a['data'].pop(key, None); b['data'].pop(key, None)
    assert a == b, ('Binding/event change', i)
assert set(t.r) == set(original), 'No new nodes expected'
assert d['m_Usings'] == objs[PID].read_typetree()['m_Usings']
assert value(frame, 131105)['value'] == value(frame, 131087)['value'] == 64
assert value(1036, 131104)['value'] == -4
assert all(value(i, 458752)['a'] == 0 for i in [1036, 1059, 1080, 1096, 1111, 1125, 1126, 1112])
assert value(1018, 131089)['value'] + 32 == 40  # unchanged horizontal center
assert value(1018, 131104)['value'] + 64 == 30  # unchanged bottom alignment
assert value(1035, 131104)['value'] == value(1037, 131104)['value'] + 10
assert 31 + 10 < 42 and -4 + 8 < 9  # glyph/name and star/percentage separation
checked = []
for pct in [None, -2147483648, -1] + list(range(111)):
    node = fitness_root
    while node not in leaves:
        args = decode(t.sd(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        assert args[2].endswith(b'position.Player.Condition')
        limit = struct.unpack_from('<i', args[1], len(args[1])-4)[0]
        node = t.r[node]['data']['m_Children'][int(pct is not None and pct > limit)]['rid']
    expected = None if pct is None or pct < 0 else min(pct, 100)
    assert leaves[node] == expected
    assert t.sd(node)['text'] == ('--' if expected is None else str(expected) + '%')
    fill = named('CombinedCardFitnessFill' + str(expected))
    assert value(fill, 131105)['value'] == f32(0 if expected is None else expected * .64)
    assert value(fill, 458752) == colour(expected)
    if pct in [None, 0, 1, 50, 68, 99, 100]: checked.append(pct)

# Reuse the first trial's non-mutating registry/catalog audit and its guarded
# save/backup/install code; no obsolete first-trial layout is executed.
audit = source.split("reserved = json.loads((R/'reserved-texture-ids.json')")[1]
audit = "reserved = json.loads((R/'reserved-texture-ids.json')" + audit
audit = audit.replace("'card_size': [80, 86], 'portrait_inset': 3", "'card_size': [64, 64], 'portrait_inset': 2")
audit = audit.replace("'native_role_icons_vertical': [19, 37]", "'native_role_icons_vertical': [20, 31]")
audit = audit.replace("'all_original_serialized_bindings_and_events_unchanged': True,",
                      "'all_original_serialized_bindings_and_events_unchanged': True, 'presentation_only_sd_changes': [1019, 1026, 1135], 'stars': 'transparent, top border centered 50x8', 'name': 'inside, y42 60x10, font9', 'role_buttons': 'inside, y52 60x10, font8', 'progress': 'outside, y67 64x3',")
exec(compile(audit, 'square64-audit-install', 'exec'))
