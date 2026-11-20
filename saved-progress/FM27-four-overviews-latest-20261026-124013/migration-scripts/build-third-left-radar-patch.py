from pathlib import Path
src=Path('third-pitch-top-bans-replace-pros.py').read_text('utf8')
head=src.split('doc=objs[W][PAGE]')[0].replace('third-pitch-top-bans-replace-pros-','third-fixed-left-radar-bans-fullwidth-stats-')
body='''doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
# Replace the left scroll view with an ordinary bounded container.
left_sd=rr[1102]['data']['m_SerializedData']['rid']
replacement=copy.deepcopy(serial(old,1291));replacement['rid']=left_sd
replacement['data'].update(uxmlAssetId=rr[1102]['data']['m_Id'],name='ThirdOverviewLeftBoundedNoScroll',name_UxmlAttributeFlags=1)
rr[left_sd].clear();rr[left_sd].update(replacement)
rr[1102]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
override(rr[1102]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),
    prop(458768,en('hidden')),prop(131101,px(0)),prop(131098,px(0))])
override(rr[1114]['data'],[prop(131094,pct(100)),prop(131085,num(1)),prop(458768,en('hidden'))])
# Preserve the native chart and its player binding; only move its container.
rr[1173]['data']['m_Children'].remove({'rid':1026})
rr[1026]['data']['m_Parent']={'rid':6298}
remove_subtree(6230);rr=refs(doc)
rr[6298]['data']['m_Children'].append({'rid':1026})
remove_subtree(6336);rr=refs(doc)
assert rr[6298]['data']['m_Children']==[{'rid':6228},{'rid':1026}]
assert rr[1173]['data']['m_Children']==[{'rid':2242}]
override(rr[1026]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
    prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(160)),
    prop(131096,px(160)),prop(131094,px(160)),prop(131074,en('flex-start'))])
override(rr[1173]['data'],[prop(131083,en('column')),prop(131073,en('stretch'))])
override(rr[2242]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
    prop(131083,en('column')),prop(131073,en('stretch')),prop(131091,px(0)),prop(131092,px(0))])
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
line=add_pair(old[6286],serial(old,6286),2242,'ThirdOverviewFitnessStatsDivider')
rr[line]['data']['m_RuleIndex']=old[6286]['data']['m_RuleIndex']
override(rr[line]['data'],[prop(131087,px(1)),prop(131096,px(1)),prop(131094,px(1)),
    prop(131093,px(3)),prop(131090,px(3)),prop(131105,pct(100)),prop(131084,num(0)),prop(131085,num(0))])
rr[2242]['data']['m_Children']=[{'rid':1186},{'rid':6286},{'rid':2986},{'rid':line},{'rid':6304}]
# Only the scroll wrapper's serialized type and new separator are changed.
for i,r in old.items():
    if i in rr and i!=left_sd and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('unexpected binding change',i)
save(W,PAGE,doc,STYLE,sheet)

'''
tail=src[src.index('outputs={n:e.file.save'):]
a=tail.index("report={'installed':False");b=tail.index("(OUT/'manifest.json')",a)
tail=tail[:a]+'''report={'installed':False,'runtime_verified':False,'third_only':True,
    'left_bounded_no_scroll':True,'tactics_removed':True,'radar_beside_bans':True,
    'bottom_right_report_fitness_stats_full_width':True,'section_separators':True,
    'native_chart_stats_bans_bindings_preserved':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
'''+tail[b:]
tail=tail.replace("'right_height':390,'bans_relocated':True,'pitch_title_removed':True","'left_scroll_removed':True,'radar_relocated':True")
Path('third-fixed-left-radar-bans-fullwidth-stats.py').write_text(head+body+tail,'utf8')
