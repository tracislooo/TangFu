from pathlib import Path
src=Path('third-left-fc-hidden-overview.py').read_text('utf8')
head=src[:src.index('# Independent three-column selector')]
head=head.replace("'third-left-fc-hidden-overview-'","'fourth-left-large-portrait-no-hidden-'")
head=head.replace('PAGE,PS=-940000000010000,-940000000010001','PAGE,PS=-940000000012000,-940000000012001')
head=head.replace('DESCRIPTION=-940000000010030','DESCRIPTION=-940000000012030')
head=head.replace("'fm27-third-left-fc-card-hidden-overview-v1'","'fm27-fourth-left-large-portrait-no-hidden-overview-v1'")
head=head.replace("TITLE='左边版FC卡面+隐藏';IDENT='PlayerOverviewLeftFC';TITLE_KEY='OverviewLeftFCVariantTitle'","TITLE='左边版大头像+非隐藏';IDENT='PlayerOverviewLeftPortrait';TITLE_KEY='OverviewLeftPortraitVariantTitle'")
body=r'''
# Work only on a private copy of the current third version.
doc,sheet,old_sid=clone(W,-940000000010000,PAGE,PS,PAGE_GUID,'OverviewFourthLeftLargePortraitNoHidden')
rr=refs(doc);original=copy.deepcopy(rr)
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1

def subtree_refs(source,root):
    found=set()
    def visit(i):
        if i not in source or i in found or i==-2:return
        found.add(i)
        def walk(v):
            if isinstance(v,dict):
                if set(v)=={'rid'}:visit(v['rid'])
                else:
                    for k,x in v.items():
                        if k!='m_Parent':walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(source[i].get('data',{}))
    visit(root);return found

def remove_tree(i):
    global rr
    parent=rr[i]['data']['m_Parent']['rid']
    rr[parent]['data']['m_Children'].remove({'rid':i})
    gone=subtree_refs(rr,i)
    doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in gone]
    rr=refs(doc)
    return gone

def import_subtree(source_pid,root,parent):
    global next_rid,next_id
    donor=objs[W][source_pid].read_typetree();sr=refs(donor)
    ss=objs[W][donor['inlineSheet']['m_PathID']].read_typetree()
    found=subtree_refs(sr,root);mapping={i:next_rid+j for j,i in enumerate(sorted(found))};next_rid+=len(found)
    nodes=[i for i in found if 'm_Id' in sr[i].get('data',{})]
    uidmap={sr[i]['data']['m_Id']:next_id+j for j,i in enumerate(sorted(nodes))};next_id+=len(nodes)
    rulemap={}
    def remap(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                if v['rid'] in mapping:v['rid']=mapping[v['rid']]
            else:
                for k,x in v.items():
                    if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in uidmap:v[k]=uidmap[x]
                    else:remap(x)
        elif isinstance(v,list):
            for x in v:remap(x)
    for i in sorted(found):
        r=copy.deepcopy(sr[i]);r['rid']=mapping[i];remap(r['data'])
        if i in nodes:
            ix=r['data'].get('m_RuleIndex',-1)
            if ix>=0:
                if ix not in rulemap:
                    ruledata=copy.deepcopy(ss['m_Rules'][ix])
                    for p in ruledata['m_Properties']:
                        for h in p['m_Values']:
                            if h['m_ValueType'] in poolmap:
                                pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
                    rulemap[ix]=len(sheet['m_Rules']);sheet['m_Rules'].append(ruledata)
                r['data']['m_RuleIndex']=rulemap[ix]
            alias=r['data'].get('m_TemplateAlias')
            if alias:
                use=next(u for u in donor['m_Usings'] if u['alias']==alias)
                current=next((u for u in doc['m_Usings'] if u['alias']==alias),None)
                if current:assert current==use,('template alias conflict',alias)
                else:doc['m_Usings'].append(copy.deepcopy(use))
        if i==root:r['data']['m_Parent']={'rid':parent}
        rr[r['rid']]=r;doc['references']['RefIds'].append(r)
    rr[parent]['data']['m_Children'].append({'rid':mapping[root]})
    return mapping

remove_tree(1293)
portrait=import_subtree(-930000000001003,1293,1169)
rr[1169]['data']['m_Children']=[{'rid':portrait[1293]},{'rid':6324}]
for i in [portrait[1293],portrait[1299]]:
    override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
        prop(131087,px(310)),prop(131096,px(310)),prop(131094,px(310)),
        prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0)),prop(262151,px(0)),
        prop(131093,px(0)),prop(131073,en('center')),prop(131088,en('flex-start'))])
override(rr[portrait[1285]]['data'],[prop(131105,px(286)),prop(131087,px(286)),
    prop(131096,px(286)),prop(131094,px(286)),prop(131085,num(0)),prop(131093,px(2))])
# The second version's status/foot/footer and all photo bindings stay intact.
remove_tree(5852)
move(2242,1011)
rr[1011]['data']['m_Children']=[{'rid':2242},{'rid':6298}]
override(rr[2242]['data'],[prop(131087,auto),prop(131096,px(0)),prop(131094,none),
    prop(131084,num(0)),prop(131085,num(0)),prop(131082,auto),prop(131090,px(6))])
# Restore the native report mapping, automatic icon wrapping, and content-only tactics.
restored=import_subtree(-930000000001001,6298,1173)
row=restored[6298];pros=restored[6306];tactic=restored[6230]
override(rr[row]['data'],[prop(131105,pct(100)),prop(131087,pct(100)),prop(131096,px(160)),
    prop(131094,none),prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),
    prop(131083,en('row')),prop(131093,px(0)),prop(131090,px(0))])
for i in [pros,tactic]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
        prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,auto),
        prop(131091,px(0)),prop(131092,px(0))])
assert rr[1173]['data']['m_Children']==[{'rid':row}]
assert rr[6298]['data']['m_Children']==[{'rid':6228},{'rid':1026}]
assert 5852 not in rr and 1301 not in rr and 1819 not in rr and 1863 not in rr
assert rr[1007]==original[1007] and rr[1040]==original[1040]
# All retained native serialized fields must remain identical.
for i,r in original.items():
    if i in rr and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('retained binding changed',i)
commit_clone(W,-940000000010000,PAGE,PS,old_sid,doc,sheet)

'''
tail=src[src.index('# Add a third native tile choice'):]
tail=tail.replace("desc.update(m_Name='OverviewThirdLeftFCDescription')","desc.update(m_Name='OverviewFourthLeftPortraitDescription')")
tail=tail.replace("desc=copy.deepcopy(objs[L][-930000000001004].read_typetree())","desc=copy.deepcopy(objs[L][-940000000010030].read_typetree())")
a=tail.index("report={'installed':False");b=tail.index("(OUT/'manifest.json')",a)
tail=tail[:a]+'''report={'installed':False,'runtime_verified':False,'new_version':TITLE,'guid':PAGE_GUID,
    'first_three_pages_and_styles_byte_identical':True,'left_width':300,'middle_right_ratio':[2,1],
    'attributes_height':390,'right_upper_height':390,'portrait_size':286,
    'status_and_feet_from_second':True,'hidden_panel_removed':True,
    'right_upper_order':['scout report / fitness 50:50','four rows of native season stats','bans / radar 50:50'],
    'right_lower_order':['pros and cons 50%','tactics 50%'],
    'native_retained_bindings_unchanged':True,'saved_active_selection_unchanged':True,
    'new_assets':[{'bundle':c['bundle'],'guid':c['key'],'pid':c['pid']} for c in clones],
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
'''+tail[b:]
tail=tail.replace("'third_guid':PAGE_GUID","'fourth_guid':PAGE_GUID")
Path('fourth-left-large-portrait-no-hidden.py').write_text(head+body+tail,'utf8')
