from pathlib import Path

R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

summary = named('CardNativePlayerSummary')
assert dimension(summary, 131089) == 126
override(summary['data'], [prop(131089, px(129))])
footer = named('CardNativeFootFooter')
override(footer['data'], [prop(458768, en('visible'))])
changed_allowed = {summary['rid'], footer['rid']}
native_width = 78
inset = (native_width - native_width * 0.8) / 2
for side, outer, inner in [('Left', 131091, 131092), ('Right', 131092, 131091)]:
    node = named('Card' + side + 'FootNativeStepper')
    assert dimension(node, 131105) == 54
    override(node['data'], [prop(131105, px(native_width)), prop(131097, px(native_width)),
        prop(458768, en('visible')), prop(outer, px(-inset)), prop(inner, px(6 - inset))])
    changed_allowed.add(node['rid'])
for i in range(len(old_sheet['floats']), len(sheet['floats'])):
    sheet['floats'][i] = struct.unpack('<f', struct.pack('<f', sheet['floats'][i]))[0]
for value in sheet['dimensions'][len(old_sheet['dimensions']):]:
    value['value'] = struct.unpack('<f', struct.pack('<f', value['value']))[0]

# Verify the installed game's native minimum step dimensions and spacing.
style_env = UnityPy.load(str(GAME / 'ui-styles_assets_default.bundle'))
native_style = next(o.read_typetree() for o in style_env.objects if o.path_id == -1868520061851585845)
native_steps = next(r for r in native_style['m_Rules'] if any(
    len(s['m_Selectors']) == 1 and s['m_Selectors'][0]['m_Parts'] == [{'m_Value': 'stepper-step', 'm_Type': 3}]
    for s in r['m_ComplexSelectors']))
def native_dimension(pid):
    p = next(p for p in native_steps['m_Properties'] if p['m_Id'] == pid)
    h = p['m_Values'][0]; assert h['m_ValueType'] == 3
    return native_style['dimensions'][h['valueIndex']]['value']
step_min = native_dimension(131097); step_margin = native_dimension(131092)
assert step_min == 10 and step_margin == 3
assert 6 * (step_min + step_margin) <= native_width
assert {i for i in rr if rr[i] != old_refs[i]} == changed_allowed
for i in changed_allowed:
    old = copy.deepcopy(old_refs[i]); old['data']['m_RuleIndex'] = rr[i]['data']['m_RuleIndex']
    assert old == rr[i], ('Non-style change', i)
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
assert all(rr[i] == old_refs[i] for i in rr if 'UxmlSerializedData' in rr[i]['type']['class'])
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
assert property_value(footer, 458768) == 'visible'
assert dimension(footer, 131104) == 219
assert 2 * native_width * 0.8 + 36 + 12 <= dimension(footer, 131105)
for side, inner in [('Left', 131092), ('Right', 131091)]:
    node = named('Card' + side + 'FootNativeStepper')
    scale = next(p for p in sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == 327681)
    assert all(abs(sheet['floats'][h['valueIndex']] - 0.8) < 1e-6 for h in scale['m_Values'])
    assert dimension(node, 131105) == dimension(node, 131097) == 78
    assert property_value(node, 458768) == 'visible'
    assert abs(dimension(node, inner) + inset - 6) < 1e-6
node_count = validate_ui(doc, sheet)
objects[FULL].save_typetree(doc); objects[sid].save_typetree(sheet)
output = env.file.save(packer='lz4')
saved = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(saved) == set(objects)
for i, h in old_hashes.items():
    if i in [FULL, sid]: assert saved[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(saved[i].get_raw_data()) == h, ('Unrelated object changed', i)
validate_ui(saved[FULL].read_typetree(), saved[sid].read_typetree())
for p, data in before.items(): assert p.read_bytes() == data
for p, h in protected.items(): assert sha(p.read_bytes()) == h

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out = R / ('fix-card-foot-stepper-clipping-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'left_summary_left': 129, 'stepper_layout_width': 78, 'stepper_scale': 0.8,
    'stepper_visual_width': 62.4, 'stepper_to_badge_gap': 6,
    'native_step_minimum_width': step_min, 'native_step_margin': step_margin,
    'footer_and_stepper_overflow': 'visible', 'native_bindings_preserved': True,
    'second_version_textures_and_calculations_preserved': True,
    'validated_nodes': node_count, 'unchanged_world_objects_verified': len(old_hashes) - 2,
    'before_sha256': {str(p): sha(data) for p, data in before.items()},
    'after_sha256': {WN: sha(output)}, 'protected_sha256': {str(p): h for p, h in protected.items()}}
manifest = out / 'manifest.json'
manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
if '--install' in sys.argv:
    try:
        for folder in [GAME, SKIN]:
            (folder / WN).write_bytes(output)
            assert (folder / WN).read_bytes() == output
        for p, h in protected.items(): assert sha(p.read_bytes()) == h
    except Exception:
        for p, data in before.items(): p.write_bytes(data)
        raise
    report['installed'] = True
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(out), 'installed': report['installed'], 'after_sha256': report['after_sha256']}, indent=2))
