from pathlib import Path
src=Path('third-fixed-left-radar-bans-fullwidth-stats.py').read_text('utf-8-sig')
head=src.split('doc=objs[W][PAGE]')[0].replace('third-fixed-left-radar-bans-fullwidth-stats-','third-report-fitness-same-row-halves-')
body='''doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
row=add_pair(old[6298],serial(old,6298),2242,'ThirdOverviewScoutFitnessEqualRow')
override(rr[row]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
    prop(131087,auto),prop(131096,px(42)),prop(131094,none),prop(131082,auto),
    prop(131084,num(0)),prop(131085,num(0)),prop(131083,en('row')),
    prop(131073,en('center')),prop(131088,en('flex-start')),prop(262150,px(0)),prop(262151,px(0))])
for i in [1186,2986]:
    rr[2242]['data']['m_Children'].remove({'rid':i})
    rr[i]['data']['m_Parent']={'rid':row}
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
        prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),
        prop(131091,px(0)),prop(131092,px(0))])
rr[row]['data']['m_Children']=[{'rid':1186},{'rid':2986}]
# Report-to-fitness divider no longer separates vertically stacked sections.
remove_subtree(6286);rr=refs(doc)
line=named('ThirdOverviewFitnessStatsDivider')
rr[2242]['data']['m_Children']=[{'rid':row},{'rid':line},{'rid':6304}]
for i,r in old.items():
    if i in rr and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('unexpected binding change',i)
assert rr[row]['data']['m_Children']==[{'rid':1186},{'rid':2986}]
save(W,PAGE,doc,STYLE,sheet)

'''
tail=src[src.index('outputs={n:e.file.save'):]
a=tail.index("report={'installed':False");b=tail.index("(OUT/'manifest.json')",a)
tail=tail[:a]+'''report={'installed':False,'runtime_verified':False,'third_only':True,
    'scout_report_left_fitness_right_same_row':True,'width_ratio':[1,1],
    'stats_below_with_separator':True,'native_bindings_preserved':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
'''+tail[b:]
tail=tail.replace("'left_scroll_removed':True,'radar_relocated':True","'scout_fitness_same_row':True,'width_ratio':'50/50'")
Path('third-report-fitness-same-row-halves.py').write_text(head+body+tail,'utf8')
