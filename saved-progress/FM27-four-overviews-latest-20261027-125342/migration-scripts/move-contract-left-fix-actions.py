from pathlib import Path

R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

def pct(value): return val(3, {'unit': 2, 'value': float(value)})

def edit(node_id, properties): override(rr[node_id]['data'], properties)

contract = rr[1184]
old_parent = rr[contract['data']['m_Parent']['rid']]
identity = named('ReportIdentityOffsetContent')
assert old_parent['rid'] == 1349 and identity['rid'] == 1297
assert identity['data']['m_Children'] == [{'rid': 1171}, {'rid': 1295}]
old_parent['data']['m_Children'].remove({'rid': contract['rid']})
identity['data']['m_Children'].append({'rid': contract['rid']})
contract['data']['m_Parent'] = {'rid': identity['rid']}
contract['data']['m_Classes'] = []
edit(1184, [prop(131093, px(4)), prop(131105, pct(100)), prop(131085, num(0)),
    prop(458768, en('visible'))])
edit(1199, [prop(131087, px(56)), prop(131085, num(0)), prop(131083, en('column')),
    prop(458768, en('visible'))])
edit(1215, [prop(131087, px(28)), prop(131096, px(28)), prop(131085, num(0))])
edit(1237, [prop(131083, en('row')), prop(131073, en('center')), prop(131087, px(28)),
    prop(131097, px(0)), prop(131105, pct(100)), prop(458768, en('visible'))])
salary = rr[1260]
salary['data']['m_Classes'] = [c for c in salary['data']['m_Classes'] if c != 'margin-bottom-global-gap-regular']
edit(1260, [prop(131090, px(0)), prop(131092, px(12)), prop(131097, px(0)),
    prop(131085, num(1)), prop(131074, en('center'))])
edit(1261, [prop(131097, px(0)), prop(131085, num(1)), prop(131074, en('center'))])

# Preserve the native menu payload and explicitly map its expected Person to the current player's scope.
action_parent = rr[1186]
remapper = rr[1218]['data']
assert remapper['Mappings'] == [{'m_serialisedType': 0, 'from': 'team',
    'to': {'m_path': 'localteam'}, 'type': {'id': 1145176088}}]
remapper['Mappings'].append({'m_serialisedType': 0, 'from': 'Person',
    'to': {'m_path': 'person'}, 'type': {'id': 1145176065}})
remapper['Mappings_UxmlAttributeFlags'] = 1
menu, menu_sd = rr[1103], rr[1109]['data']
assert menu_sd['BindingPaths'] == [{'m_path': 'Person'}]
assert menu['data']['m_Parent']['rid'] == action_parent['rid']
assert action_parent['data']['m_Children'] == [{'rid': 1202}, {'rid': 1103}, {'rid': 1203}]
# Keep the action above the scout content while painting/picking it last within its panel.
action_parent['data']['m_Children'] = [{'rid': 1202}, {'rid': 1203}, {'rid': 1103}]
edit(1186, [prop(131101, px(40)), prop(458768, en('visible'))])
edit(1103, [prop(131102, en('absolute')), prop(131089, px(0)), prop(131104, px(0)),
    prop(131105, pct(100)), prop(131097, px(0)), prop(131087, px(32)),
    prop(131096, px(32)), prop(131094, px(32)), prop(131074, en('stretch')),
    prop(131073, en('center')), prop(131083, en('row')), prop(458768, en('visible')),
    prop(262150, px(0)), prop(131090, px(0))])
menu_sd.update(pickingMode=0, pickingMode_UxmlAttributeFlags=1,
    enabledSelf=1, enabledSelf_UxmlAttributeFlags=1, MouseButton=0, MouseButton_UxmlAttributeFlags=1)
for child in menu['data']['m_Children']:
    sd = rr[rr[child['rid']]['data']['m_SerializedData']['rid']]['data']
    sd['pickingMode'] = 1; sd['pickingMode_UxmlAttributeFlags'] = 1

allowed = {1349, 1297, 1184, 1199, 1215, 1237, 1260, 1261, 1186, 1218, 1103, 1109}
changed = {i for i in rr if rr[i] != old_refs[i]}
assert changed <= allowed and {1184, 1218, 1109} <= changed
assert set(rr) == set(old_refs)
for i in rr:
    if 'UxmlSerializedData' in rr[i]['type']['class'] and i not in [1218, 1109]:
        assert rr[i] == old_refs[i], ('Unrelated binding changed', i)
assert menu_sd['BindingPaths'] == old_refs[1109]['data']['BindingPaths']
for key in old_refs[1109]['data']:
    if key not in ['pickingMode', 'pickingMode_UxmlAttributeFlags', 'enabledSelf',
                   'enabledSelf_UxmlAttributeFlags', 'MouseButton', 'MouseButton_UxmlAttributeFlags']:
        assert menu_sd[key] == old_refs[1109]['data'][key], ('Menu behavior changed', key)
for i in [1234, 1276, 1277, 1278, 1283, 1284]:
    assert rr[i] == old_refs[i], ('Contract binding changed', i)
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
assert identity['data']['m_Children'][-1] == {'rid': 1184}
assert not any(c['rid'] == 1184 for c in old_parent['data']['m_Children'])
# Both locations retain their existing person/localteam/hasContract source at their common ancestor.
def ancestors(i):
    result = []
    while 'm_Parent' in rr.get(i, {}).get('data', {}):
        i = rr[i]['data']['m_Parent']['rid']; result.append(i)
    return result
assert 1167 in ancestors(1184) and 1167 in ancestors(1103)
assert dimension(identity, 131093) + 2 + 48 + 24 + 72 + 4 + 56 <= 250
assert dimension(rr[1214], 131087) + dimension(rr[1214], 131090) + dimension(rr[1215], 131087) == 56
assert dimension(rr[1103], 131087) == 32
assert dimension(rr[1186], 131101) >= dimension(rr[1103], 131087) + 8
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
out = R / ('contract-left-actions-repair-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'contract_parent': 'ReportIdentityOffsetContent', 'contract_below': 'ReportNationClubRow',
    'transfer_value_wage_expiry_agreed_playing_time_bindings_preserved': True,
    'contract_section_height': 56, 'contract_second_row': 'wage / expiry + agreed playing time',
    'action_person_remap': {'Person': 'person'}, 'action_click_surface_height': 32,
    'action_explicitly_enabled': True, 'action_decorations_ignore_picking': True,
    'action_painted_last_in_panel': True, 'native_menu_actions_and_shortcut_preserved': True,
    'changed_reference_ids': sorted(changed), 'validated_nodes': node_count,
    'second_version_card_textures_calculations_and_other_assets_preserved': True,
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
print(json.dumps({'output': str(out), 'installed': report['installed'],
    'changed_reference_ids': report['changed_reference_ids'], 'after_sha256': report['after_sha256']}, indent=2))
