from pathlib import Path

R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

def pct(value): return val(3, {'unit': 2, 'value': float(value)})
def edit(node_id, properties): override(rr[node_id]['data'], properties)

# Value, wage/expiry, and agreed playing time occupy three successive rows.
assert dimension(rr[1199], 131087) == 56
edit(1295, [prop(131096, px(64))])
edit(1199, [prop(131087, px(72))])
edit(1215, [prop(131087, px(44)), prop(131096, px(44))])
edit(1237, [prop(131083, en('column')), prop(131073, en('stretch')),
    prop(131088, en('flex-start')), prop(131087, px(44))])
edit(1260, [prop(131087, px(20)), prop(131090, px(4)), prop(131092, px(0)),
    prop(131085, num(0)), prop(131074, en('flex-start'))])
edit(1261, [prop(131087, px(20)), prop(131085, num(0)), prop(131074, en('stretch'))])

frame = named('FrameActions')
assert frame['rid'] == 1102
menu = rr[1103]
old_parent = rr[menu['data']['m_Parent']['rid']]
assert old_parent['rid'] == 1186
old_parent['data']['m_Children'].remove({'rid': menu['rid']})
edit(1186, [prop(131101, px(0))])
# Remove the previous local alias; the scout panel retains its original team mapping.
rr[1218]['data']['Mappings'] = [m for m in rr[1218]['data']['Mappings'] if m['from'] != 'Person']

node, serialized = copy.deepcopy(rr[1116]), copy.deepcopy(rr[1117])
rid = max(rr) + 1
eid = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
node['rid'], serialized['rid'] = rid, rid + 1
node['data'].update(m_Id=eid, m_Parent={'rid': frame['rid']}, m_Children=[{'rid': menu['rid']}],
    m_SerializedData={'rid': serialized['rid']}, m_Classes=[], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[])
serialized['data'].update(uxmlAssetId=eid, name='OverviewActionsForegroundContext', name_UxmlAttributeFlags=1,
    pickingMode=1, pickingMode_UxmlAttributeFlags=1,
    Mappings=[{'m_serialisedType': 0, 'from': 'overviewactionperson',
        'to': {'m_path': 'person'}, 'type': {'id': 1145176065}}], Mappings_UxmlAttributeFlags=1)
rr[node['rid']] = node; rr[serialized['rid']] = serialized
doc['references']['RefIds'].extend([node, serialized])
frame['data']['m_Children'].append({'rid': node['rid']})
menu['data']['m_Parent'] = {'rid': node['rid']}
edit(frame['rid'], [prop(131102, en('relative'))])
edit(node['rid'], [prop(131102, en('absolute')), prop(131089, auto()), prop(131103, px(24)),
    prop(131104, px(48)), prop(131105, px(160)), prop(131097, px(160)), prop(131095, px(160)),
    prop(131087, px(32)), prop(131096, px(32)), prop(131094, px(32)),
    prop(131084, num(0)), prop(131085, num(0)), prop(458768, en('visible')),
    prop(262150, px(0)), prop(262151, px(0))])
edit(menu['rid'], [prop(131102, en('relative')), prop(131089, px(0)), prop(131104, px(0)),
    prop(131105, pct(100)), prop(131087, px(32))])
rr[1109]['data']['BindingPaths'] = [{'m_path': 'overviewactionperson'}]
rr[1109]['data']['BindingPaths_UxmlAttributeFlags'] = 1

allowed = {1295, 1199, 1215, 1237, 1260, 1261, 1186, 1218, 1102, 1103, 1109}
assert {i for i in old_refs if rr[i] != old_refs[i]} == allowed
assert set(rr) == set(old_refs) | {node['rid'], serialized['rid']}
for i in old_refs:
    if 'UxmlSerializedData' in rr[i]['type']['class'] and i not in [1109, 1218]:
        assert rr[i] == old_refs[i], ('Unrelated binding changed', i)
for key in old_refs[1109]['data']:
    if key not in ['BindingPaths', 'BindingPaths_UxmlAttributeFlags']:
        assert rr[1109]['data'][key] == old_refs[1109]['data'][key]
assert any(p['name'] == 'person' and p['type']['id'] == 1145176065 for p in rr[1015]['data']['Parameters'])
assert serialized['data']['Mappings'][0]['from'] == rr[1109]['data']['BindingPaths'][0]['m_path']
assert node['data']['m_Parent'] == {'rid': frame['rid']}
assert frame['data']['m_Children'][-1] == {'rid': node['rid']}
assert old_parent['data']['m_Children'] == [{'rid': 1202}, {'rid': 1203}]
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
for i in [1234, 1276, 1277, 1278, 1283, 1284]: assert rr[i] == old_refs[i]
assert property_value(rr[1237], 131083) == 'column'
assert dimension(rr[1214], 131087) + dimension(rr[1214], 131090) + dimension(rr[1215], 131087) == 72
assert dimension(rr[1260], 131087) + dimension(rr[1260], 131090) + dimension(rr[1261], 131087) == 44
assert 30 + 2 + 48 + 24 + dimension(rr[1295], 131096) + 4 + 72 + 2 <= 250
assert dimension(node, 131104) + dimension(node, 131087) <= 250
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
out = R / ('contract-three-rows-action-foreground-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'contract_rows': ['transfer value', 'wage / expiry', 'agreed playing time'],
    'contract_height': 72, 'nation_club_min_height': 64,
    'action_foreground_parent': 'FrameActions', 'action_parent_draws_last': True,
    'action_current_player_alias': 'overviewactionperson -> person',
    'action_bounds': {'right': 24, 'top': 48, 'width': 160, 'height': 32},
    'native_context_menu_payload_preserved_except_binding_alias': True,
    'new_reference_ids': [node['rid'], serialized['rid']], 'validated_nodes': node_count,
    'second_version_textures_calculations_and_other_assets_preserved': True,
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
