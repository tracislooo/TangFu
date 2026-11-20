from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
HP=5775949770471550939;SP=5108509966786251923
doc=objects[HP].read_typetree();oldheader=copy.deepcopy(doc)
sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};headerrefs=copy.deepcopy(rr)
st=objects[SP].read_typetree();sr={r['rid']:r for r in st['references']['RefIds']};ss=objects[st['inlineSheet']['m_PathID']].read_typetree()
row=named('FrameActions')['rid'];action=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
assert rr[row]['data']['m_Children']==[{'rid':action}]
# Compact copies from the actual six report-fitness modules. Bindings stay native.
childmap={1028:[1174,1053],1053:[1176,1178],1029:[1107,1056],1056:[1109,1110],1030:[1113,1060],1060:[1115,1116],1032:[1119,1065],1065:[1121,1123],1033:[1126,1068],1068:[1128],1128:[1191,1192],1034:[1131,1072],1072:[1133,1134]}
roots=[1028,1029,1030,1032,1033,1034];titles=[1174,1107,1113,1119,1126,1131];values=[1178,1109,1115,1123,1191,1133];steppers=[1110,1116,1192,1134];images=[1176,1121]
nodeids=[]
def walk(i):
 nodeids.append(i)
 for c in childmap.get(i,[]):walk(c)
for i in roots:walk(i)
assert len(set(nodeids))==len(nodeids)
allids=nodeids+[sr[i]['data']['m_SerializedData']['rid'] for i in nodeids]
start=max(rr)+1;wrapid,wrapsdid=start,start+1
mapping={i:start+2+k for k,i in enumerate(allids)}
eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
eids={i:eid+1+k for k,i in enumerate(nodeids)}
wrap=copy.deepcopy(rr[1002]);wrapsd=copy.deepcopy(rr[rr[1002]['data']['m_SerializedData']['rid']])
wrap['rid']=wrapid;wrapsd['rid']=wrapsdid
wrap['data'].update(m_Id=eid,m_Parent={'rid':row},m_Children=[{'rid':mapping[i]} for i in roots],m_SerializedData={'rid':wrapsdid},m_Classes=[],m_Properties=[],m_RuleIndex=-1)
wrapsd['data'].update(uxmlAssetId=eid,name='HeaderFitnessSixMetrics',name_UxmlAttributeFlags=1,Mappings=[{'m_serialisedType':0,'from':'player','to':{'m_path':'person'},'type':{'id':1145176065}},{'m_serialisedType':0,'from':'team','to':{'m_path':'person.Team'},'type':{'id':1145176088}}],Mappings_UxmlAttributeFlags=1)
rr[wrapid]=wrap;rr[wrapsdid]=wrapsd;doc['references']['RefIds'].extend([wrap,wrapsd])
parentmap={c:p for p,children in childmap.items() for c in children}
for i in allids:
 r=copy.deepcopy(sr[i]);r['rid']=mapping[i]
 if i in nodeids:
  d=r['data'];d.update(m_Id=eids[i],m_Parent={'rid':wrapid if i in roots else mapping[parentmap[i]]},m_Children=[{'rid':mapping[c]} for c in childmap.get(i,[])],m_SerializedData={'rid':mapping[sr[i]['data']['m_SerializedData']['rid']]})
  ix=d['m_RuleIndex']
  if ix>=0:
   rulecopy=copy.deepcopy(ss['m_Rules'][ix])
   for p in rulecopy['m_Properties']:
    for h in p['m_Values']:
     if h['m_ValueType']==1:continue
     pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]))
     h['valueIndex']=len(sheet[pool])-1
   d['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(rulecopy)
 else:
  n=next(n for n in nodeids if sr[n]['data']['m_SerializedData']['rid']==i);r['data']['uxmlAssetId']=eids[n]
 rr[r['rid']]=r;doc['references']['RefIds'].append(r)
rr[row]['data']['m_Children']=[{'rid':wrapid},{'rid':action}]
def edit(i,ps):override(rr[i]['data'],ps)
def styled(i,ps):edit(mapping[i],ps)
def pct(n):return val(3,{'unit':2,'value':float(n)})
common=[prop(262150,px(0)),prop(262151,px(0)),prop(131091,px(0)),prop(131092,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131099,px(0)),prop(131100,px(0)),prop(131101,px(0)),prop(131098,px(0)),prop(131102,en('relative')),prop(131089,auto()),prop(131104,auto()),prop(131087,auto()),prop(131096,px(0)),prop(131094,auto()),prop(131105,auto()),prop(131097,px(0)),prop(131095,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(458768,en('visible'))]
for i in nodeids:
 # Replace inherited tile sizing classes with header-only sizing; preserve text/stepper colors.
 d=rr[mapping[i]]['data']
 if i in roots or i in childmap:d['m_Classes']=[]
 styled(i,common)
edit(wrapid,[prop(131083,en('row')),prop(131073,en('center')),prop(131087,px(32)),prop(131096,px(32)),prop(131094,px(32)),prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),prop(131097,px(0)),prop(131092,px(12)),prop(262151,px(0)),prop(458768,en('visible'))])
for i in roots:
 styled(i,[prop(131083,en('column')),prop(131087,px(32)),prop(131084,num(1)),prop(131082,px(0)),prop(131100,px(8)),prop(131088,en('center'))])
for i in titles:styled(i,[prop(65537,px(11)),prop(131087,px(14)),prop(131085,num(0)),prop(65546,en('middle-left'))])
for i in values:styled(i,[prop(65537,px(12)),prop(131087,px(18)),prop(131084,num(1)),prop(131082,px(0)),prop(65546,en('middle-left'))])
for i in [1053,1056,1060,1065,1128,1072]:styled(i,[prop(131083,en('row')),prop(131073,en('center')),prop(131087,px(18)),prop(131105,pct(100))])
styled(1068,[prop(131087,px(18)),prop(131105,pct(100))])
for i in steppers:styled(i,[prop(131105,px(78)),prop(131097,px(78)),prop(131087,px(4)),prop(131085,num(0)),prop(131091,px(4))])
for i in images:styled(i,[prop(131105,px(14)),prop(131097,px(14)),prop(131087,px(14)),prop(131085,num(0)),prop(131092,px(4))])
# Verify every imported serialized binding and visual-function argument is unchanged.
for i in nodeids:
 originalsd=copy.deepcopy(sr[sr[i]['data']['m_SerializedData']['rid']]['data']);originalsd['uxmlAssetId']=eids[i]
 assert rr[mapping[sr[i]['data']['m_SerializedData']['rid']]]['data']==originalsd
for i in headerrefs:
 if i!=row:assert rr[i]==headerrefs[i],('Existing header node changed',i)
assert not any('m_TemplateAlias' in rr[mapping[i]]['data'] for i in nodeids)
count=validate_ui(doc,sheet)
objects[HP].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for i,h in old_hashes.items():
 if i in [HP,sid]:assert saved[i].read_typetree()=={HP:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated changed',i)
validate_ui(saved[HP].read_typetree(),saved[sid].read_typetree())
for p,d in before.items():assert p.read_bytes()==d
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('header-six-native-fitness-metrics-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'header_height':32,'source_asset':SP,'metrics':['Match Sharpness','Match Load','Injury Susceptibility','Energy','Training Load','Injury Risk'],'native_bindings_unchanged':True,'action_unchanged':True,'original_fitness_page_unchanged':True,'new_node_mapping':mapping,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except Exception:
  for p,d in before.items():p.write_bytes(d)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':report['installed'],'sha256':sha(output),'validated_nodes':count},ensure_ascii=False,indent=2))
