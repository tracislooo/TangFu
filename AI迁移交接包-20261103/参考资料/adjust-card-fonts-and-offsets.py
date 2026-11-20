from pathlib import Path

# Reuse the established read-only loader and serialization helpers, stopping before any layout edits.
R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

summary = named('CardNativePlayerSummary')
assert dimension(summary, 131104) == 28
override(summary['data'], [prop(131104, px(38))])
changed_allowed = {summary['rid']}
fonts = {}
for label, previous_size in [('CurrentAbility', 13), ('PotentialAbility', 11),
                              ('BestPosition', 10), ('Height', 11), ('LeagueRating', 11)]:
    node = named('Card' + label + 'Value')
    assert dimension(node, 65537) == previous_size
    props = [prop(65537, px(previous_size + 5))]
    if label in ['CurrentAbility', 'PotentialAbility']:
        props.append(prop(65543, en('bold')))
    override(node['data'], props)
    fonts[label] = previous_size + 5
    changed_allowed.add(node['rid'])

ratings = named('OverviewCardGoalkeeperSwitch')
assert dimension(ratings, 131104) == 179
override(ratings['data'], [prop(131104, px(174))])
changed_allowed.add(ratings['rid'])
badge = named('CardPreferredFootBadge')
assert property_value(badge, 131104) == ('keyword', 2)
# Relative positioning offsets only the preferred-foot badge, retaining the native left/right bars.
override(badge['data'], [prop(131104, px(-10))])
changed_allowed.add(badge['rid'])

assert set(rr) == set(old_refs)
changed = {i for i in rr if rr[i] != old_refs[i]}
assert changed == changed_allowed
for i in changed:
    old_node = copy.deepcopy(old_refs[i])
    old_node['data']['m_RuleIndex'] = rr[i]['data']['m_RuleIndex']
    assert old_node == rr[i], ('Non-style change', i)
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
assert all(rr[i] == old_refs[i] for i in rr if 'UxmlSerializedData' in rr[i]['type']['class'])
for label in ['CurrentAbility', 'PotentialAbility']:
    assert property_value(named('Card' + label + 'Value'), 65543) == 'bold'
for side in ['Left', 'Right']:
    node = named('Card' + side + 'FootNativeStepper')
    assert node == old_refs[node['rid']]
footer = named('CardNativeFootFooter')
badge_top = dimension(footer, 131104) + dimension(badge, 131104)
assert badge_top == 219
assert badge_top > dimension(ratings, 131104) + dimension(ratings, 131087)
assert badge_top + dimension(footer, 131087) < 263
assert dimension(summary, 131104) + dimension(summary, 131087) < 263
node_count = validate_ui(doc, sheet)

objects[FULL].save_typetree(doc); objects[sid].save_typetree(sheet)
output = env.file.save(packer='lz4')
saved = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(saved) == set(objects)
for i, h in old_hashes.items():
    if i in [FULL, sid]: assert saved[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(saved[i].get_raw_data()) == h, ('Unrelated object changed', i)
validate_ui(saved[FULL].read_typetree(), saved[sid].read_typetree())
for p, data in before.items(): assert p.read_bytes() == data, ('Source changed', str(p))
for p, h in protected.items(): assert sha(p.read_bytes()) == h

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out = R / ('card-fonts-offsets-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'changed_asset_ids': [FULL, sid], 'summary_top': 38, 'summary_fonts_px': fonts,
    'current_and_potential_ability_bold': True, 'six_ratings_top': 174,
    'preferred_foot_relative_top': -10, 'preferred_foot_stage_top': badge_top,
    'left_right_foot_bars_preserved': True, 'native_bindings_preserved': True,
    'second_version_card_textures_and_calculations_preserved': True,
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
print(json.dumps({'output': str(out), 'installed': report['installed'], 'fonts': fonts,
    'unchanged_world_objects_verified': report['unchanged_world_objects_verified'],
    'after_sha256': report['after_sha256']}, ensure_ascii=False, indent=2))
