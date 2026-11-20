from pathlib import Path

R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

summary = named('CardNativePlayerSummary')
league = named('CardLeagueStatsScope')
removed = set()

def collect(i):
    if i in removed or i == -2: return
    removed.add(i)
    data = rr[i].get('data', {})
    for child in data.get('m_Children', []): collect(child['rid'])
    serial = data.get('m_SerializedData', {}).get('rid', -2)
    if serial != -2: collect(serial)
    for component in data.get('m_components', []): collect(component['rid'])

collect(league['rid'])
assert removed == {1889, 1890, 1891, 1892, 1895, 1896}
summary['data']['m_Children'] = [c for c in summary['data']['m_Children'] if c['rid'] != league['rid']]
override(summary['data'], [prop(131087, px(116))])
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed: del rr[i]

footer = named('CardNativeFootFooter')
badge = named('CardPreferredFootBadge')
left = named('CardLeftFootNativeStepper')
right = named('CardRightFootNativeStepper')
assert dimension(footer, 131104) == 219
footer['data']['m_Children'] = [{'rid': n['rid']} for n in [left, badge, right]]
inset = (54 - 54 * 0.8) / 2
for node, outer_pid, inner_pid in [(left, 131091, 131092), (right, 131092, 131091)]:
    assert dimension(node, 131105) == 54 and dimension(node, 131087) == 6
    override(node['data'], [prop(131102, en('relative')), prop(131089, auto()), prop(131104, auto()),
        prop(327681, num(0.8), num(0.8)), prop(131074, en('center')),
        prop(outer_pid, px(-inset)), prop(inner_pid, px(6 - inset))])

for i in range(len(old_sheet['floats']), len(sheet['floats'])):
    sheet['floats'][i] = struct.unpack('<f', struct.pack('<f', sheet['floats'][i]))[0]
for value in sheet['dimensions'][len(old_sheet['dimensions']):]:
    value['value'] = struct.unpack('<f', struct.pack('<f', value['value']))[0]

changed_allowed = {summary['rid'], footer['rid'], left['rid'], right['rid']}
assert {i for i in rr if rr[i] != old_refs[i]} == changed_allowed
assert all(rr[i] == old_refs[i] for i in rr if 'UxmlSerializedData' in rr[i]['type']['class'])
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
for label in ['CurrentAbility', 'PotentialAbility', 'BestPosition', 'Height']:
    n = named('Card' + label + 'Value')
    assert n == old_refs[n['rid']]
assert len(summary['data']['m_Children']) == 4
assert dimension(summary, 131087) == 4 * 29
for node in [left, right]:
    props = sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties']
    scale = next(p for p in props if p['m_Id'] == 327681)
    assert all(abs(sheet['floats'][v['valueIndex']] - 0.8) < 1e-6 for v in scale['m_Values'])
    assert property_value(node, 131089) == ('keyword', 2)
    assert property_value(node, 131104) == ('keyword', 2)
assert abs(dimension(left, 131092) + inset - 6) < 1e-6
assert abs(dimension(right, 131091) + inset - 6) < 1e-6
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
out = R / ('compact-foot-bars-remove-league-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'removed_league_records': sorted(removed), 'left_summary_remaining_fields': ['CurrentAbility', 'PotentialAbility', 'BestPosition', 'Height'],
    'foot_stepper_scale': 0.8, 'foot_stepper_visual_size': [43.2, 4.8],
    'stepper_to_badge_gap': 6, 'footer_stage_top_preserved': 219,
    'native_bindings_preserved': True, 'other_layout_textures_calculations_and_second_version_preserved': True,
    'unchanged_world_objects_verified': len(old_hashes) - 2, 'validated_nodes': node_count,
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
