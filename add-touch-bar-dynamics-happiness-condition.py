from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
HP=5775949770471550939
hd=objects[HP].read_typetree();doc=hd;rr={r['rid']:r for r in doc['references']['RefIds']};oldrefs=copy.deepcopy(rr)
sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree()
m={int(k):v for k,v in json.loads((R/'header-six-native-fitness-metrics-20261018-013417/manifest.json').read_text())['new_node_mapping'].items()}
wrap=named('HeaderFitnessSixMetrics')['rid'];action=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
assert len(rr[wrap]['data']['m_Children'])==11
DYN=3052255369264346086;HAP=3508926604620743622;HT=1835999027414418521;FIT=5108509966786251923
sources={pid:objects[pid].read_typetree() for pid in [DYN,HAP,HT,FIT]}
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
GO=-7625397564865265528;sources[GO]=next(o for o in ge.objects if o.path_id==GO).read_typetree()
src={pid:{r['rid']:r for r in d['references']['RefIds']} for pid,d in sources.items()}
nextid=max(rr)+1;eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
newids=[];binding_copies=[]
def addpair(node,sd,parent,name):
 global nextid,eid
 node=copy.deepcopy(node);sd=copy.deepcopy(sd);nid,did=nextid,nextid+1;nextid+=2
 node['rid']=nid;sd['rid']=did
 node['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':did},m_RuleIndex=-1,m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 sd['data']['uxmlAssetId']=eid;eid+=1
 # Record names are internal identifiers; every display string still uses native localization/binding.
 sd['data'].update(name=name,name_UxmlAttributeFlags=1)
 rr[nid]=node;rr[did]=sd;doc['references']['RefIds'].extend([node,sd]);newids.extend([nid,did])
 rr[parent]['data']['m_Children'].append({'rid':nid})
 return nid
base=rr[m[1028]];basesd=rr[base['data']['m_SerializedData']['rid']]
sep=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='HeaderFitnessSeparator1')
sepsd=rr[sep['data']['m_SerializedData']['rid']]
def plain(parent,name):return addpair(base,basesd,parent,name)
def native(pid,sourceid,parent,name):
 sn=src[pid][sourceid];sd=src[pid][sn['data']['m_SerializedData']['rid']]
 n=addpair(sn,sd,parent,name)
 rr[n]['data']['m_Classes']=[c for c in rr[n]['data']['m_Classes'] if not any(s in c for s in ['margin-','height-','width-','align-self-','overflow-text'])]
 binding_copies.append({'node':n,'serialized':rr[n]['data']['m_SerializedData']['rid'],'source_asset':pid,'source_node':sourceid,'source_serialized':sd['rid']})
 return n
def edit(i,p):override(rr[i]['data'],p)
zero=[prop(262150,px(0)),prop(262151,px(0)),prop(131091,px(0)),prop(131092,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131099,px(0)),prop(131100,px(0)),prop(131101,px(0)),prop(131098,px(0)),prop(131102,en('relative')),prop(131089,auto()),prop(131104,auto()),prop(131105,auto()),prop(131097,px(0)),prop(131095,auto()),prop(131096,px(0)),prop(131094,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(131082,auto()),prop(131074,en('center')),prop(458768,en('visible'))]
def textstyle(i,title=False):edit(i,zero+[prop(131087,px(24)),prop(65537,px(11 if title else 12)),prop(65536,color(173,173,181) if title else color(245,245,247)),prop(65546,en('middle-left')),prop(65552,en('nowrap')),prop(131092,px(4 if title else 0))])
def iconstyle(i):edit(i,zero+[prop(131105,px(14)),prop(131097,px(14)),prop(131095,px(14)),prop(131087,px(14)),prop(131085,num(0)),prop(131092,px(4))])
def pill(name):
 s=addpair(sep,sepsd,wrap,'HeaderStatusSeparator_'+name)
 edit(s,[prop(131105,px(1)),prop(131097,px(1)),prop(131095,px(1)),prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('center')),prop(131091,px(3)),prop(131092,px(3)),prop(458752,color(124,124,132,95))])
 n=plain(wrap,'HeaderStatus_'+name)
 edit(n,zero+[prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('flex-start')),prop(131087,px(26)),prop(131096,px(26)),prop(131094,px(26)),prop(131084,num(1)),prop(131082,auto()),prop(131099,px(5)),prop(131100,px(5)),prop(458752,color(31,31,34)),prop(262147,px(6)),prop(262148,px(1)),prop(262146,color(49,49,53))])
 return n
# Use the existing native player context for all ten pills; source pages use both cases.
wsd=rr[rr[wrap]['data']['m_SerializedData']['rid']]['data']
assert wsd['Mappings'][0]['from']=='player'
wsd['Mappings'].append({'m_serialisedType':0,'from':'Player','to':{'m_path':'person'},'type':{'id':1145176065}})
modules=[]
for name,titleid,imageid,valueid in [('Mindset',1058,1047,1059),('Hierarchy',1062,1050,1063)]:
 p=pill(name);modules.append(p)
 textstyle(native(DYN,titleid,p,'Header'+name+'Title'),True)
 iconstyle(native(DYN,imageid,p,'Header'+name+'Icon'))
 textstyle(native(DYN,valueid,p,'Header'+name+'Value'))
p=pill('OverallHappiness');modules.append(p)
textstyle(native(HT,1006,p,'HeaderOverallHappinessTitle'),True)
iconstyle(native(HAP,1014,p,'HeaderOverallHappinessIcon'))
textstyle(native(HAP,1015,p,'HeaderOverallHappinessValue'))
p=pill('OverallCondition');modules.append(p)
# Native injured/non-injured icon visibility and texts are preserved.
for visid,imageid,name in [(1002,1005,'Injured'),(1003,1007,'Normal')]:
 v=native(GO,visid,p,'HeaderCondition'+name+'IconVisible');edit(v,zero+[prop(131087,px(24)),prop(131073,en('center')),prop(131083,en('row'))])
 iconstyle(native(GO,imageid,v,'HeaderCondition'+name+'Icon'))
for visid,textid,name in [(1043,1217,'Normal'),(1044,1158,'Injured')]:
 v=native(FIT,visid,p,'HeaderCondition'+name+'TextVisible');edit(v,zero+[prop(131087,px(24)),prop(131073,en('center')),prop(131083,en('row'))])
 textstyle(native(FIT,textid,v,'HeaderOverallCondition'+name+'Value'))
# Allocate width according to content, rather than ten equal columns.
for i in [1028,1032,1029,1030,1033,1034]:edit(m[i],[prop(131082,auto()),prop(131099,px(5)),prop(131100,px(5))])
for i,r in rr.items():
 sd=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if sd.get('name','').startswith('HeaderFitnessSeparator'):edit(i,[prop(131091,px(3)),prop(131092,px(3))])
# Native display/condition/image functions and their argument byte streams stay identical.
for c in binding_copies:
 a=copy.deepcopy(rr[c['serialized']]['data']);b=copy.deepcopy(src[c['source_asset']][c['source_serialized']]['data'])
 for d in [a,b]:
  for key in ['uxmlAssetId','name','name_UxmlAttributeFlags']:d.pop(key,None)
 assert a==b,('Binding changed',c)
assert rr[action]==oldrefs[action]
assert len([c for c in rr[wrap]['data']['m_Children'] if c['rid'] in modules])==4
assert len(rr[wrap]['data']['m_Children'])==19
count=validate_ui(doc,sheet)
objects[HP].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [HP,sid]:assert saved[i].read_typetree()=={HP:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated changed',i)
validate_ui(saved[HP].read_typetree(),saved[sid].read_typetree())
for p,d in before.items():assert p.read_bytes()==d
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('touch-bar-dynamics-happiness-condition-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'added_metrics':['Mindset','Hierarchy','Overall Happiness','Overall Condition'],'source_assets':{pid:d['m_Name'] for pid,d in sources.items()},'new_module_nodes':modules,'copied_bindings':binding_copies,'header_height':32,'native_source_binding_data_preserved':True,'existing_six_metrics_and_action_preserved':True,'injury_condition_visibility_preserved':True,'all_metrics_before_action':True,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
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
