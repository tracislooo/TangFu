from pathlib import Path

R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

footer = named('CardNativeFootFooter')
badge = named('CardPreferredFootBadge')
assert dimension(footer, 131104) == 229
assert dimension(badge, 131104) == -10
override(footer['data'], [prop(131104, px(219))])
override(badge['data'], [prop(131104, auto())])
assert {i for i in rr if rr[i] != old_refs[i]} == {footer['rid'], badge['rid']}
for i in [footer['rid'], badge['rid']]:
    old = copy.deepcopy(old_refs[i]); old['data']['m_RuleIndex'] = rr[i]['data']['m_RuleIndex']
    assert old == rr[i]
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
assert property_value(badge, 131104) == ('keyword', 2)
for side in ['Left', 'Right']:
    step = named('Card' + side + 'FootNativeStepper')
    assert step == old_refs[step['rid']]
    assert dimension(footer, 131104) + dimension(step, 131104) == 223
assert dimension(footer, 131104) > dimension(named('OverviewCardGoalkeeperSwitch'), 131104) + 44
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
out = R / ('whole-foot-footer-up10-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'footer_stage_top': 219, 'badge_stage_top': 219, 'both_stepper_stage_top': 223,
    'badge_not_shifted_twice': True, 'validated_nodes': node_count,
    'native_bindings_other_layout_textures_calculations_preserved': True,
    'unchanged_world_objects_verified': len(old_hashes) - 2,
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
