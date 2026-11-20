from pathlib import Path
src=Path('third-milestones-pitch-inset-right390.py').read_text('utf8')
head=src.split('doc=objs[W][PAGE]')[0].replace('third-milestones-pitch-inset-right390-','third-pitch-top-bans-replace-pros-')
body='''def remove_subtree(i):
    parent=rr[i]['data']['m_Parent']['rid']
    rr[parent]['data']['m_Children'].remove({'rid':i})
    gone=set()
    def walk(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                rid=v['rid']
                if rid in rr and rid not in gone:
                    gone.add(rid);walk(rr[rid])
            else:
                for k,x in v.items():
                    if k!='m_Parent':walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    gone.add(i);walk(rr[i])
    doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in gone]
    return gone

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
remove_subtree(6306)
rr=refs(doc)
rr[6324]['data']['m_Children'].remove({'rid':6228})
rr[6228]['data']['m_Parent']={'rid':6298}
rr[6298]['data']['m_Children'].insert(0,{'rid':6228})
override(rr[6228]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
    prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,auto),
    prop(131096,px(0)),prop(131094,none),prop(131093,px(0)),prop(131092,px(4)),
    prop(131073,en('stretch')),prop(131074,en('stretch'))])
for i in [1035,6230]:assert rr[i]==old[i]
assert rr[6298]['data']['m_Children']==[{'rid':6228},{'rid':6230}]
assert {'rid':6228} not in rr[6324]['data']['m_Children']
doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias']!='OverviewTitledProsConsIcons']
save(W,PAGE,doc,STYLE,sheet)

doc=objs[G][SELECTOR].read_typetree();rr=refs(doc);sheet=objs[G][SELECTOR_STYLE].read_typetree()
remove_subtree(1009);rr=refs(doc)
override(rr[2000]['data'],[prop(131093,px(0)),prop(131101,px(0)),prop(131088,en('flex-start'))])
override(rr[1010]['data'],[prop(131093,px(0)),prop(131101,px(0)),prop(131088,en('flex-start'))])
inset=named('ThirdOverviewPitchSafeInset')
override(rr[inset]['data'],[prop(131104,px(0)),prop(131088,en('flex-start'))])
fitter=named('ThirdOverviewPortraitPitchRatio')
override(rr[fitter]['data'],[prop(131074,en('flex-start')),prop(131093,px(0)),prop(131104,px(0))])
assert sd(1023)['Orientation']==1
save(G,SELECTOR,doc,SELECTOR_STYLE,sheet)

'''
tail=src[src.index('outputs={n:e.file.save'):]
start=tail.index("report={'installed':False")
end=tail.index("(OUT/'manifest.json')",start)
tail=tail[:start]+'''report={'installed':False,'runtime_verified':False,'third_only':True,
    'pitch_position_header_removed':True,'pitch_top_inset':0,
    'pros_cons_removed':True,'bans_moved_from_left_to_right_upper_left_half':True,
    'tactics_right_half_preserved':True,'right_upper_height':390,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
'''+tail[end:]
tail=tail.replace("'right_height':390,'pitch_safe_inset':8","'right_height':390,'bans_relocated':True,'pitch_title_removed':True")
Path('third-pitch-top-bans-replace-pros.py').write_text(head+body+tail,'utf8')
