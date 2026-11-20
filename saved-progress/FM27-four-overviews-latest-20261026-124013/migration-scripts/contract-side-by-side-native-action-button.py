from pathlib import Path

R = Path(__file__).parent
source = (R / 'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<card bundle loader>', 'exec'))

def pct(value): return val(3, {'unit': 2, 'value': float(value)})
def edit(i, properties): override(rr[i]['data'], properties)

# Match the reference: value on the left; wage/expiry over playing time on the right.
assert dimension(rr[1199], 131087) == 72
edit(1199, [prop(131083, en('row')), prop(131073, en('center')), prop(131087, px(44))])
edit(1214, [prop(131090, px(0)), prop(131092, px(12)), prop(131085, num(0)),
    prop(131074, en('center'))])
edit(1215, [prop(131105, auto()), prop(131082, px(0)), prop(131084, num(1)),
    prop(131085, num(1)), prop(131097, px(0)), prop(131074, en('center'))])
assert rr[1237]['data']['m_Children'] == [{'rid': 1260}, {'rid': 1261}]

# Use the existing SIButton class (as used by the working value button) as the real click target.
# The native menu remains an ancestor, receiving the bubbling mouse event with its existing player context.
menu = rr[1103]
menu_sd = rr[1109]['data']
assert menu_sd['BindingPaths'] == [{'m_path': 'overviewactionperson'}]
assert menu['data']['m_Parent']['rid'] == 1907
node = copy.deepcopy(rr[1214])
sd = copy.deepcopy(rr[rr[1214]['data']['m_SerializedData']['rid']])
new_rid = max(rr) + 1
new_id = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
node['rid'], sd['rid'] = new_rid, new_rid + 1
children = copy.deepcopy(menu['data']['m_Children'])
node['data'].update(m_Id=new_id, m_Parent={'rid': menu['rid']}, m_Children=children,
    m_SerializedData={'rid': sd['rid']}, m_Classes=[c for c in menu['data']['m_Classes']
        if c != 'plugin-context-menu-bindings-overlay'], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[])
sd['data'].update(uxmlAssetId=new_id, name='OverviewActionsNativeClickTarget', name_UxmlAttributeFlags=1,
    pickingMode=0, pickingMode_UxmlAttributeFlags=1, enabledSelf=1, enabledSelf_UxmlAttributeFlags=1,
    text='', text_UxmlAttributeFlags=1, Events={'m_bytes': []}, Events_UxmlAttributeFlags=1,
    RightClickEvents={'m_bytes': []}, RightClickEvents_UxmlAttributeFlags=1,
    StopsEventPropagation=0, StopsEventPropagation_UxmlAttributeFlags=1,
    OnlyAcceptsClickEvents=1, OnlyAcceptsClickEvents_UxmlAttributeFlags=1,
    OnlyAcceptsSubmitEvents=0, OnlyAcceptsSubmitEvents_UxmlAttributeFlags=1)
rr[node['rid']], rr[sd['rid']] = node, sd
doc['references']['RefIds'].extend([node, sd])
menu['data']['m_Children'] = [{'rid': node['rid']}]
menu['data']['m_Classes'] = ['row-direction-normal', 'plugin-context-menu-bindings-overlay', 'no-padding']
for child in children:
    rr[child['rid']]['data']['m_Parent'] = {'rid': node['rid']}
    deco = rr[rr[child['rid']]['data']['m_SerializedData']['rid']]['data']
    assert deco['pickingMode'] == 1 and deco['pickingMode_UxmlAttributeFlags'] == 1
edit(node['rid'], [prop(131102, en('relative')), prop(131089, px(0)), prop(131104, px(0)),
    prop(131105, pct(100)), prop(131097, px(0)), prop(131087, px(32)),
    prop(131096, px(32)), prop(131094, px(32)), prop(131084, num(0)), prop(131085, num(0)),
    prop(131083, en('row')), prop(131073, en('center')), prop(131074, en('stretch')),
    prop(262150, px(0)), prop(262151, px(0)), prop(131091, px(0)), prop(131092, px(0)),
    prop(131090, px(0)), prop(131093, px(0)), prop(458768, en('visible'))])

allowed = {1199, 1214, 1215, 1103, 1104, 1105, 1106, 1107}
assert {i for i in old_refs if rr[i] != old_refs[i]} == allowed
assert set(rr) == set(old_refs) | {node['rid'], sd['rid']}
for i in old_refs:
    if 'UxmlSerializedData' in rr[i]['type']['class']: assert rr[i] == old_refs[i]
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
assert node['data']['m_FullTypeName'] == 'SI.Bindable.SIButton'
assert sd['data']['Events']['m_bytes'] == sd['data']['RightClickEvents']['m_bytes'] == []
assert sd['data']['StopsEventPropagation'] == 0
assert rr[1109] == old_refs[1109]
assert rr[1908] == old_refs[1908]
assert property_value(rr[1199], 131083) == 'row'
assert property_value(rr[1237], 131083) == 'column'
assert dimension(rr[1260], 131087) + dimension(rr[1260], 131090) + dimension(rr[1261], 131087) == 44
node_count = validate_ui(doc, sheet)
objects[FULL].save_typetree(doc); objects[sid].save_typetree(sheet)
output = env.file.save(packer='lz4')
saved = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(saved) == set(objects)
for i, h in old_hashes.items():
    if i in [FULL, sid]: assert saved[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(saved[i].get_raw_data()) == h, ('Unrelated asset changed', i)
validate_ui(saved[FULL].read_typetree(), saved[sid].read_typetree())
for p, data in before.items(): assert p.read_bytes() == data
for p, h in protected.items(): assert sha(p.read_bytes()) == h

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out = R / ('contract-reference-native-action-click-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False, 'changed_bundle': WN,
    'contract_layout': 'value left; wage and expiry upper right; agreed playing time lower right',
    'contract_height': 44, 'new_action_click_target': 'SI.Bindable.SIButton',
    'native_click_target_reference_ids': [node['rid'], sd['rid']],
    'native_menu_and_current_player_context_preserved': True,
    'button_has_no_navigation_events_and_allows_mouse_event_bubbling': True,
    'all_existing_dynamic_bindings_preserved': True,
    'textures_calculations_second_version_and_other_assets_preserved': True,
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
