"""75px Combined card, centered on the native container, with readable footer."""
from pathlib import Path

source = Path(__file__).with_name('trial-tactics-combined-layered-card.py').read_text('utf8')
prefix = source.split('# Keep the pitch anchor / footprint')[0]
exec(compile(prefix.replace('tactics-combined-layered-card-trial-', 'tactics-combined-square75-centered-v3-'), 'square75-boot', 'exec'))
extract('resize-tactics-combined-square64-v2.py', {'named', 'value'})

frame, gate, fitness_root = 1165, 1171, 1173
assert value(frame, 131105)['value'] == value(frame, 131087)['value'] == 64
border = named('CombinedCardNativePositionBackground')
surface = named('CombinedCardInnerSurface')
track = named('CombinedCardFitnessTrack')
transparent = {'r': 0.0, 'g': 0.0, 'b': 0.0, 'a': 0.0}

# Center on the existing 80x70 layout box, instead of holding the old bottom
# edge at y=30. No tactics coordinates, root dimensions or pitch logic change.
for node in [1018, 1019]: box(node, 2.5, -2.5, 75, 75)
for node in [1021, frame, border, 1026, 1027]: box(node, 0, 0, 75, 75)
rounded(frame, 6)
rounded(border, 6, True)
rounded(1027, 6)
for node in [surface, 1167]:
    box(node, 4, 4, 67, 67)
    rounded(node, 2, True)

# Left-hand percentage and role glyph locations remain as in the 64px version.
# Move only native right-hand warnings to follow the wider card's right edge.
for node, y in [(1032, 9), (1031, 24)]:
    box(node, 58, y, 16, 16)
    t.edit(node, [P(327681, st.num(.625), st.num(.625))])
box(1036, 12.5, -4, 50, 8)
box(gate, 0, 0, 75, 81)
box(track, 0, 78, 75, 3)
leaves = {}
for i, a in original.items():
    if a.get('data', {}).get('m_FullTypeName') != 'SI.Bindable.SIText': continue
    name = serial(original, i)['data'].get('name', '')
    if not name.startswith('PitchFitnessPercent'): continue
    suffix = name.removeprefix('PitchFitnessPercent')
    pct = None if suffix == 'None' else int(suffix)
    leaves[i] = pct
    box(i, 0, 0, 75, 81)
    # box() clears padding; reinstate the agreed number position.
    t.edit(i, [P(131099, st.px(4)), P(131101, st.px(9))])
    fill = named('CombinedCardFitnessFill' + str(pct))
    box(fill, 0, 78, 0 if pct is None else pct * .75, 3)
assert len(leaves) == 102

# Name above native roles. The line's entire 12px is reserved independently
# of report glyphs and the native unavailable/selected decoration layers.
box(1037, 4, 47, 67, 12)
t.edit(1037, [P(458752, st.h(4, {'r': 0.0, 'g': 0.0, 'b': 0.0, 'a': f32(.7)})),
               P(458768, st.en('hidden')), P(262147, st.px(0))])
for node in [1061, 1082, 1098]:
    t.edit(node, [P(131105, st.pct(100)), P(131087, st.px(12)),
                  P(131096, st.px(0)), P(131094, st.px(12)), P(262150, st.px(0)),
                  P(262151, st.px(0)), P(458752, st.h(4, transparent))])
for node in [1115, 1134, 1135, 1151]:
    t.edit(node, [P(131097, st.px(0)), P(131096, st.px(0)), P(131087, st.px(12)),
                  P(131094, st.px(12)), P(262150, st.px(0)), P(262151, st.px(0)),
                  P(65537, st.px(10)), P(65546, st.en('middle-center')),
                  P(65552, st.en('nowrap')), P(196609, st.en('ellipsis'))])
t.edit(1115, [P(131105, st.px(0)), P(131082, st.px(0)), P(131084, st.num(1))])
t.edit(1114, [P(131105, st.px(7)), P(131097, st.px(7)), P(131095, st.px(7)),
               P(131087, st.px(12)), P(131085, st.num(0))])
box(1132, 0, 1, 6, 10)
t.edit(1132, [P(131102, st.en('relative')), P(131093, st.px(1))])
t.edit(1158, [P(131096, st.px(0)), P(131087, st.px(10)), P(262151, st.px(0))])

box(1035, 4, 59, 67, 12)
for node in [1055, 1057, 1075, 1078, 1092, 1094, 1105, 1107]:
    t.edit(node, [P(131097, st.px(0)), P(131096, st.px(0)), P(131087, st.px(12)),
                  P(131094, st.px(12)), P(262150, st.px(0)), P(262151, st.px(0))])
for node in [1119, 1122]:
    t.edit(node, [P(65537, st.px(9)), P(131087, st.px(12)), P(131096, st.px(0)),
                  P(262150, st.px(0)), P(262151, st.px(0))])

# Paint every native selection frame first. Name and role controls then paint
# above the decorations, while their exact existing parents/scopes stay intact.
children = t.r[1026]['data']['m_Children']
assert {a['rid'] for a in children} == {1035, 1036, 1037, 1038}
t.r[1026]['data']['m_Children'] = [{'rid': i} for i in [1038, 1035, 1037, 1036]]
children = t.r[1019]['data']['m_Children']
assert {a['rid'] for a in children} == {1023, 1024, 1025, 1026, 1027}
t.r[1019]['data']['m_Children'] = [{'rid': i} for i in [1023, 1024, 1025, 1027, 1026]]
decorations = [1027, 1038, 1063, 1084, 1100]
for node in decorations: ignore(node)
for dim in sheet['dimensions']: dim['value'] = f32(dim['value'])

# All existing serialized binding/event payloads remain unchanged; the only
# serialized differences are Ignore picking flags on non-interactive frames.
allowed = {t.r[i]['data']['m_SerializedData']['rid'] for i in decorations}
for i, old in original.items():
    if 'UxmlSerializedData' not in old.get('type', {}).get('class', ''): continue
    a, b = copy.deepcopy(old), copy.deepcopy(t.r[i])
    if i in allowed:
        for key in ['pickingMode', 'pickingMode_UxmlAttributeFlags']:
            a['data'].pop(key, None); b['data'].pop(key, None)
    assert a == b, ('Native serialized data changed', i)
assert set(t.r) == set(original)
assert value(1001, 131105)['value'] == 80 and value(1001, 131087)['value'] == 70
assert value(frame, 131105)['value'] == value(frame, 131087)['value'] == 75
assert value(1018, 131089)['value'] + 37.5 == 40
assert value(1018, 131104)['value'] + 37.5 == 35
assert value(1018, 131089) == value(1019, 131089) and value(1018, 131104) == value(1019, 131104)
assert value(1167, 131089)['value'] == value(1167, 131104)['value'] == 4
assert value(1167, 131105)['value'] == value(1167, 131087)['value'] == 67
assert value(1037, 131104)['value'] + value(1037, 131087)['value'] == value(1035, 131104)['value']
assert value(1035, 131104)['value'] + value(1035, 131087)['value'] == 71
assert value(1036, 458752)['a'] == value(1059, 458752)['a'] == 0
for node in [1105, 1107, 1135, 1143]:
    assert t.r[node]['data']['m_Parent'] == original[node]['data']['m_Parent']
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
    assert value(fill, 131105)['value'] == f32(0 if expected is None else expected * .75)
    assert value(fill, 458752) == colour(expected)
    if pct in [None, 0, 1, 50, 68, 99, 100]: checked.append(pct)

audit = source.split("reserved = json.loads((R/'reserved-texture-ids.json')")[1]
audit = "reserved = json.loads((R/'reserved-texture-ids.json')" + audit
audit = audit.replace("'card_size': [80, 86], 'portrait_inset': 3", "'card_size': [75, 75], 'portrait_inset': 4")
audit = audit.replace("'native_role_icons_vertical': [19, 37]", "'native_role_icons_vertical': [20, 31]")
audit = audit.replace("'all_original_serialized_bindings_and_events_unchanged': True,",
                      "'all_original_serialized_bindings_and_events_unchanged': True, 'presentation_only_ignore_picking_nodes': decorations, 'card_offset': [2.5, -2.5], 'card_center_in_native_container': [40, 35], 'border_width': 4, 'stars': 'transparent, top border centered 50x8', 'name': 'inside, y47 67x12, font10, above decorations', 'role_buttons': 'inside, y59 67x12, font9', 'progress': 'outside, y78 75x3',")
exec(compile(audit, 'square75-audit-install', 'exec'))
