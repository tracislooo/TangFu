from pathlib import Path
import json
root=Path(__file__).resolve().parent
state=json.loads((root/'current-sidebar-version.json').read_text('utf8'))
archive=Path(state['latest_saved_sidebar_archive'])
script=(root/'rebase-approved-sidebar-current.py').read_text('utf8')
script=script.replace("ARCHIVE = R / 'saved-progress/FM27-sidebar-approved-20261101'","ARCHIVE = archive")
script=script.replace('non-sidebar-baseline','non-sidebar-backup')
script=script.replace("sidebar-approved-rebased-","sidebar-updated-replacement-")
script=script.replace("for name in [W, D, M]:","for name in [W, D, M, 'ui-tileslayouts_assets_all.bundle']:")
script=script.replace("'sidebar_left_top_width': [0, 0, 100]","'sidebar_left_top_width': [0, 85, 100], 'fixed_navigation_count': 19")
script=script.replace("current five target files","current six target files")
helpers=(root/'build-match-ui-avatars-layout.py').read_text('utf8')
script=script.replace('# Verify archive integrity',helpers[helpers.index('def import_types('):helpers.index('class Doc:')]+'\n# Verify archive integrity')
script=script.replace('        if added:\n', "        if 'm_VisualTree' in approved_data:\n            import_types(approved, current, approved_data['references']['RefIds'])\n        if added:\n")
script=script.replace("            assert obj.read_typetree() == expected[pid], (name, pid)", "            print(name,pid,expected[pid].get('m_Name'),flush=True)\n            assert obj.read_typetree() == expected[pid], (name, pid)")
script=script.replace('obj.set_raw_data(archived_object.get_raw_data())','obj.serialized_type = current.types[obj.type_id]\n            obj.save_typetree(approved_data)')
script=script.replace("            obj.serialized_type = current.types[obj.type_id]", """            if pid == SIDE:
                list_type = 'StreamedObjectList/UxmlSerializedData'
                donor = next(o for o in current.objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'SquadRewardsTile_2x1')
                prototype = next(x['data'] for x in donor.read_typetree()['references']['RefIds'] if x['type']['class'] == list_type)
                fields = ('RowEnabledProperty', 'SharedPersistenceIDScope', 'InvertRowEnabled')
                defaults = {k: copy.deepcopy(prototype[k]) for f in fields for k in (f, f+'_UxmlAttributeFlags')}
                assert defaults == {'RowEnabledProperty': {'id': 0}, 'SharedPersistenceIDScope': 0, 'InvertRowEnabled': 0, **{k+'_UxmlAttributeFlags': 0 for k in fields}}
                for ref in approved_data['references']['RefIds']:
                    if ref['type']['class'] == list_type:
                        ref['data'].update({k:v for k,v in defaults.items() if k not in ref['data']})
            obj.serialized_type = current.types[obj.type_id]""")
start=script.index("(out / 'README.md').write_text(")
end=script.index("print(json.dumps",start)
script=script[:start]+script[end:]
exec(compile(script,str(root/'rebase-approved-sidebar-current.py'),'exec'),dict(__file__=__file__,archive=archive))




