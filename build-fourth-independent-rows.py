from pathlib import Path
src=Path('fourth-transfer-fallback-radar250.py').read_text('utf-8-sig')
head=src[:src.index('PAGE,STYLE=')].replace('fourth-transfer-fallback-radar250-','fourth-bans-tactics-radar-pros-rows-')
body=r'''
PAGE,STYLE=-940000000012000,-940000000012001
FUNC=-940000000013010;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-fourth-report-or-tactics-has-content-to-visible-v1').hex
F='ui-visualfunctions_assets_all.bundle';fe=UnityPy.load(str(GAME/F));native=next(o.read_typetree() for o in fe.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='BindListHasItemsToVisible')
show_template=next(r for r in native['references']['RefIds'] if r.get('type',{}).get('class')=='IBindableVisible_Show')
graph=copy.deepcopy(objs[G][-940000000013000].read_typetree());graph.update(m_Name='FourthOverviewReportOrTacticsToVisible',m_name='FourthOverviewReportOrTacticsToVisible')
graph['m_inputs'][1]['m_type']=copy.deepcopy(native['m_inputs'][1]['m_type'])
# Retain the already validated null-safe data test, changing only its output operation.
for r in graph['references']['RefIds']:
 if r.get('type',{}).get('class')=='BindableSwitchElement_SetVisibleIndex':
  old=r['data'];new=copy.deepcopy(show_template);new['rid']=r['rid']
  for k in ['m_id','m_parentID','m_execInExecInput','m_execOutExecOutput','m_target']:new['data'][k]=copy.deepcopy(old[k])
  new['data']['m_name']='Show when content available' if old['m_dataInIndex']['m_defaultSocketValue']['m_value'] else 'Hide empty content'
  new['data']['m_dataInShouldShow']=copy.deepcopy(old['m_dataInIndex']);new['data']['m_dataInShouldShow']['m_name']='should Show'
  r.clear();r.update(new)
helper=ast.parse(Path('add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['gid','check_graph']],type_ignores=[]),'graph-validator','exec'));check_graph(graph)
af=env[G].assets[0];known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
for t in fe.assets[0].ref_types:
 if (t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)==('IBindableVisible_Show','SI.Bindable','SI.Bindable') and (t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) not in known:af.ref_types.append(copy.copy(t))
obj=copy.copy(objs[G][-940000000013000]);obj.path_id=FUNC;af.objects[FUNC]=obj;objs[G][FUNC]=obj;obj.save_typetree(graph);changed[G][FUNC]=graph
metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':FUNC}}));meta['m_PreloadTable'].extend([graph['m_Script'],{'m_FileID':0,'m_PathID':FUNC}]);meta['m_Container'].sort(key=lambda kv:kv[0]);metaobj.save_typetree(meta);changed[G][metaobj.path_id]=meta

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1

def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def move(i,parent):
 a=rr[i]['data'];rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});a['m_Parent']={'rid':parent};rr[parent]['data']['m_Children'].append({'rid':i})
def remove_tree(i):
 global rr
 parent=rr[i]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':i});gone=set()
 def walk(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    j=v['rid']
    if j in rr and j not in gone:gone.add(j);walk(rr[j])
   else:
    for k,x in v.items():
     if k!='m_Parent':walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 gone.add(i);walk(rr[i]);doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in gone];rr=refs(doc)
def fixed(i,h):override(rr[i]['data'],[prop(131087,px(h)),prop(131096,px(h)),prop(131094,px(h)),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0))])
def binding(paths):
 raw=bytearray([len(paths)]);typ=b'>SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
 for path in paths:
  p=path.encode();length=bytearray();size=len(p)
  while size>=128:length.append((size&127)|128);size>>=7
  length.append(size);v=typ+bytes([1])+length+p;raw+=struct.pack('<I',len(v))+v
 return {'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':KEY},'m_inputs':{'m_variable':{'m_argumentBytes':list(raw)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
# Separate independent availability gates; no whole-row fallback can hide the other module.
prosd=objs[G][-940000000006002].read_typetree();pr=refs(prosd);visible=pr[1004];visiblesd=serial(pr,1004)
tactical=add_pair(visible,visiblesd,6298,'FourthOverviewConditionalTacticalHalf')
sd(tactical).update(Binding=binding(['const.NullRef','const.NullRef','team.Tactic.TacticalEffectiveness.StatusFlags.NoTacticError']),Binding_UxmlAttributeFlags=1,AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1)
pros=add_pair(visible,visiblesd,1173,'FourthOverviewConditionalProsCons30Percent')
sd(pros).update(Binding=binding(['person.PlayerReportForContextTeam.ScoutedProConsList.ProsList','person.PlayerReportForContextTeam.ScoutedProConsList.ConsList','const.NullRef']),Binding_UxmlAttributeFlags=1,AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1)
move(6416,tactical);move(6420,pros);move(1026,1173)
switch=named('FourthOverviewContentOrTransferSwitch');remove_tree(switch)
move(6298,6322)
line=add_pair(old[6334],serial(old,6334),6322,'FourthOverviewSecondThirdRowDivider');rr[line]['data']['m_RuleIndex']=old[6334]['data']['m_RuleIndex']
rr[6322]['data']['m_Children']=[{'rid':1703},{'rid':6334},{'rid':6298},{'rid':line},{'rid':1173}]
rr[6298]['data']['m_Children']=[{'rid':6228},{'rid':tactical}]
rr[1173]['data']['m_Children']=[{'rid':1026},{'rid':pros}]
# Use normal flow for the first row so it occupies only its actual report/statistics height.
firstsd=rr[1703]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(serial(old,1011));replacement['rid']=firstsd;replacement['data'].update(uxmlAssetId=rr[1703]['data']['m_Id'],name='FourthOverviewScoutFitnessStatsFirstRow',name_UxmlAttributeFlags=1);rr[firstsd].clear();rr[firstsd].update(replacement);rr[1703]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
override(rr[1703]['data'],[prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(0))])
fixed(6298,150);fixed(6228,150);fixed(tactical,150)
for i in [6228,tactical]:override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131091,px(0)),prop(131092,px(0))])
override(rr[6416]['data'],[prop(131105,pct(100)),prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131084,num(1)),prop(131085,num(1))])
for i,grow in [(1026,7),(pros,3)]:
 override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(grow)),prop(131085,num(1)),prop(131087,px(250)),prop(131096,px(250)),prop(131094,px(250)),prop(131091,px(0)),prop(131092,px(0)),prop(131073,en('stretch')),prop(131074,en('flex-start'))])
fixed(1043,250)
override(rr[1173]['data'],[prop(131083,en('row')),prop(131087,px(0)),prop(131096,px(250)),prop(131094,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131073,en('flex-start')),prop(131088,en('flex-start'))])
override(rr[6420]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131082,auto),prop(131084,num(0)),prop(131085,num(1))])
doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias']!='FourthOverviewNativeTransferStatus']
validate_ui(doc,sheet);objs[W][PAGE].save_typetree(doc);objs[W][STYLE].save_typetree(sheet);changed[W][PAGE]=doc;changed[W][STYLE]=sheet
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);oldkey=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-fourth-has-pros-cons-or-valid-tactics-switch-v1').hex;loc=cat.locations(oldkey)[0];catout=cat.add_key_location(KEY,loc,loc)
'''
tail=src[src.index('outputs={n:e.file.save'):]
a=tail.index("report={'installed':False");b=tail.index("(OUT/'manifest.json')",a)
tail=tail[:a]+'''report={'installed':False,'runtime_verified':False,'fourth_only':True,'transfer_fallback_removed':True,
    'second_row_height':150,'second_row':'bans 100% without tactics; bans/tactics 50:50 with tactics',
    'third_row_height':250,'third_row':'radar 100% without report icons; radar/pros-cons icons 70:30 with icons',
    'availability_checks_independent':True,'conditional_function_guid':KEY,'first_three_pages_unchanged':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
'''+tail[b:]
tail=tail.replace("'fallback_cases_verified':36,'radar_width':250,'row_height':250,'upper_height':450","'second_row_height':150,'third_row_ratio':'70:30 or 100:0'")
Path('fourth-bans-tactics-radar-pros-rows.py').write_text(head+body+tail,'utf8')
