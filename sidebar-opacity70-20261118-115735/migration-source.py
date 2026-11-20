from pathlib import Path
import json
root=Path(__file__).resolve().parent
state=json.loads((root/'current-sidebar-version.json').read_text('utf8'))
archive=root/'sidebar-recorded-delta-source-20261112'
script=(root/'rebase-approved-sidebar-current.py').read_text('utf8')
script=script.replace("ARCHIVE = R / 'saved-progress/FM27-sidebar-approved-20261101'","ARCHIVE = archive")
script=script.replace('non-sidebar-baseline','non-sidebar-backup')
script=script.replace("sidebar-approved-rebased-","sidebar-after-total-")
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
script=script.replace("sidebar-after-total-", "sidebar-opacity70-")
script=script.replace("                result = merge(base_data, approved_data, current_data, name + ':' + str(pid))", """                if pid == -3741644877788538029:
                    result=copy.deepcopy(current_data)
                    rr={x['rid']:x for x in result['references']['RefIds']}
                    fm=copy.deepcopy(rr[1030]['data'])
                    proto=copy.deepcopy(rr[1031])
                    proto['rid']=1030
                    for k in proto['data']:
                        if k in fm:proto['data'][k]=copy.deepcopy(fm[k])
                    for entry in proto['data']['GridCompositionSets']:
                        entry['m_gridCompositionSetBindings']=copy.deepcopy(fm['Bindings'])
                    rr[1030].clear();rr[1030].update(proto)
                    rr[1025]['data']['m_FullTypeName']='SI.Bindable.MultiGridLayoutElement'
                else:
                    result = merge(base_data, approved_data, current_data, name + ':' + str(pid))""")
script=script.replace("            expected[pid] = result", """            if name == D:
                rules=[rule for rule in result['m_Rules'] if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','TFReferenceSidebar'] for sel in rule['m_ComplexSelectors'])]
                assert len(rules)==1
                prop=next(p for p in rules[0]['m_Properties'] if p['m_Id']==458752)
                color=copy.deepcopy(result['colors'][prop['m_Values'][0]['valueIndex']])
                color['a']=struct.unpack('<f',struct.pack('<f',.7))[0]
                result['colors'].append(color)
                prop['m_Values']=[dict(m_ValueType=4,valueIndex=len(result['colors'])-1)]
                obj.save_typetree(result)
            expected[pid] = result""")
script=script.replace("            obj.save_typetree(approved_data)", """            defaults_by_type={
                'SIButton/UxmlSerializedData':dict(RepeatDelay=0,RepeatInterval=0,RepeatDelay_UxmlAttributeFlags=0,RepeatInterval_UxmlAttributeFlags=0),
                'SIText/UxmlSerializedData':dict(SquashToFit=0,SquashToFit_UxmlAttributeFlags=0),
                'SIImage/UxmlSerializedData':dict(ResampleToSize=0,ResampleToSize_UxmlAttributeFlags=0),
                'StreamedObjectList/UxmlSerializedData':dict(EventID='',EventID_UxmlAttributeFlags=0,ResortBinding={'m_path':''},ResortBinding_UxmlAttributeFlags=0,DigBlockedBinding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},DigBlockedBinding_UxmlAttributeFlags=0)
            }
            for ref in approved_data.get('references',{}).get('RefIds',[]):
                for k,v in defaults_by_type.get(ref['type']['class'],{}).items():
                    ref['data'].setdefault(k,copy.deepcopy(v))
            obj.save_typetree(approved_data)""")
helper="""
def import_inline_delta(base, side, current):
    count=len(base['m_Rules'])
    assert side['m_Rules'][:count]==base['m_Rules']
    result=copy.deepcopy(current);st=Styles(result);mapping={}
    for old_index,rule in enumerate(side['m_Rules'][count:],count):
        mapping[old_index]=len(result['m_Rules'])
        rule=copy.deepcopy(rule)
        for selector in rule['m_ComplexSelectors']:selector['ruleIndex']=len(result['m_Rules'])
        for prop in rule['m_Properties']:
            for handle in prop['m_Values']:
                kind=handle['m_ValueType']
                if kind in poolmap:handle.update(st.h(kind,copy.deepcopy(side[poolmap[kind]][handle['valueIndex']])))
        result['m_Rules'].append(rule)
    return result,mapping
"""
script=script.replace("# Verify archive integrity",helper+"\n# Verify archive integrity")
script=script.replace("    expected, merged_later_changes = {}, []","    expected, merged_later_changes = {}, []\n    inline_mappings={}")
script=script.replace("                if pid == -3741644877788538029:","""                if 'm_Rules' in base_data and 'm_Rules' in approved_data:
                    result,mapping=import_inline_delta(base_data,approved_data,current_data)
                    inline_mappings[pid]=mapping
                elif pid == -3741644877788538029:""")
script=script.replace("    # Validate every affected template", """    for pid,doc in expected.items():
        if 'm_VisualTree' not in doc:continue
        sid=doc['inlineSheet']['m_PathID']
        if sid not in inline_mappings:continue
        source_refs={x['rid']:x for x in approved.objects[pid].read_typetree()['references']['RefIds']}
        base_refs={x['rid']:x for x in old.objects[pid].read_typetree()['references']['RefIds']}
        mapping=inline_mappings[sid]
        for ref in doc['references']['RefIds']:
            rid=ref['rid'];node=ref.get('data',{})
            original=base_refs.get(rid,{}).get('data',{}).get('m_RuleIndex',-1)
            side_index=source_refs.get(rid,{}).get('data',{}).get('m_RuleIndex',-1)
            if side_index!=original and side_index in mapping:node['m_RuleIndex']=mapping[side_index]
        current.objects[pid].save_typetree(doc)
    # Validate every affected template""")
exec(compile(script,str(root/'rebase-approved-sidebar-current.py'),'exec'),dict(__file__=__file__,archive=archive))







