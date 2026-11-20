from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<current resources>','exec'))
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';TABLE=-930000000001003
PAGES=[-930000000001001,-930000000001003]
before.update({folder/GN:(folder/GN).read_bytes() for folder in [GAME,SKIN]})
assert before[GAME/GN]==before[SKIN/GN]
protected.pop(GAME/GN);protected.pop(SKIN/GN)
ge=UnityPy.load(before[GAME/GN]);go={o.path_id:o for o in ge.objects};gh={i:sha(o.get_raw_data()) for i,o in go.items()}
table=go[TABLE].read_typetree();table_before=copy.deepcopy(table);gsid=table['inlineSheet']['m_PathID'];gsheet=go[gsid].read_typetree()
gr={r['rid']:r for r in table['references']['RefIds']};gr_before=copy.deepcopy(gr)
srcdoc=objects[PAGES[0]].read_typetree();sr={r['rid']:r for r in srcdoc['references']['RefIds']};srcsheet=objects[srcdoc['inlineSheet']['m_PathID']].read_typetree()
fullsheet=sheet;sheet=gsheet
def apply(refs,i,items):override(refs[i]['data'],[prop(k,v) for k,v in items])
def subtree(refs,i):
 result=[i]
 for c in refs[i]['data'].get('m_Children',[]):result.extend(subtree(refs,c['rid']))
 return result
def remove_tree(d,refs,i):
 nodes=subtree(refs,i);ids=set(nodes)
 for n in nodes:
  sd=refs[n]['data'].get('m_SerializedData',{}).get('rid',-2)
  if sd!=-2:ids.add(sd)
 parent=refs[i]['data']['m_Parent']['rid'];refs[parent]['data']['m_Children'].remove({'rid':i})
 d['references']['RefIds']=[r for r in d['references']['RefIds'] if r['rid'] not in ids]
 for n in ids:del refs[n]
 return sorted(ids)

# The goalkeeper's native three-row technical list moves intact into column one.
assert gr[1063]['data']['m_Parent']=={'rid':1029}
gr[1029]['data']['m_Children'].remove({'rid':1063});gr[1011]['data']['m_Children'].append({'rid':1063});gr[1063]['data']['m_Parent']={'rid':1011}
removed_feet=[]
for i in [1022,1023,1031,1032]:removed_feet.extend(remove_tree(table,gr,i))
table['m_Usings']=[u for u in table['m_Usings'] if u['alias']!='PlayerReportFootednessBlock']

# Keep column widths flexible while stacking their sections in normal flow.
for i in [1007,1008,1009,1011,1012,1013]:
 apply(gr,i,[(131083,en('column')),(131088,en('flex-start')),(131073,en('stretch')),(131097,px(0)),(131087,auto()),(131096,px(0))])
for i in [1025,1063,1020,1021,1029,1030]:
 apply(gr,i,[(131084,num(0)),(131085,num(0)),(131087,auto()),(131096,px(0)),(131074,en('stretch'))])
for i in [1004,1005]:apply(gr,i,[(131083,en('row')),(131073,en('flex-start')),(131087,auto()),(131096,px(0))])
apply(gr,1001,[(131084,num(0)),(131085,num(0)),(131087,auto()),(131096,px(0))])
apply(gr,1002,[(131084,num(0)),(131085,num(0)),(131087,auto()),(131096,px(0))])

# Native trait rows already wrap and retain their tooltip/click behaviour.
# Copy the exact list, empty branch, icon and translated heading into each player-type branch.
source_nodes=subtree(sr,1033);assert len(source_nodes)==7
source_ids=source_nodes+[sr[i]['data']['m_SerializedData']['rid'] for i in source_nodes]
next_eid=max(r.get('data',{}).get('m_Id',0) for r in gr.values())+1
imports=[]
for prefix,parent in [('OutfieldAttributes_',1009),('GoalkeeperAttributes_',1013)]:
 start=max(gr)+1;mapping={i:start+k for k,i in enumerate(source_ids)}
 idmap={sr[i]['data']['m_Id']:next_eid+k for k,i in enumerate(source_nodes)};next_eid+=len(source_nodes)
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid'] in mapping:v['rid']=mapping[v['rid']]
   else:
    for k,x in list(v.items()):
     if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in idmap:v[k]=idmap[x]
     else:remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 for i in source_ids:
  r=copy.deepcopy(sr[i]);r['rid']=mapping[i];remap(r['data'])
  if i in source_nodes:
   if i==1033:r['data']['m_Parent']={'rid':parent}
   ridx=r['data'].get('m_RuleIndex',-1)
   if ridx>=0:
    nr=copy.deepcopy(srcsheet['m_Rules'][ridx])
    for p in nr['m_Properties']:
     for h in p['m_Values']:
      if h['m_ValueType']==1:continue
      pool=poolmap[h['m_ValueType']];gsheet[pool].append(copy.deepcopy(srcsheet[pool][h['valueIndex']]));h['valueIndex']=len(gsheet[pool])-1
    r['data']['m_RuleIndex']=len(gsheet['m_Rules']);gsheet['m_Rules'].append(nr)
  elif 'name' in r['data']:
   r['data']['name']=prefix+r['data']['name']
  gr[r['rid']]=r;table['references']['RefIds'].append(r)
 root=mapping[1033];gr[parent]['data']['m_Children'].append({'rid':root})
 for source_node in [1033,1055,1077,1078]:
  apply(gr,mapping[source_node],[(131102,en('relative')),(131084,num(0)),(131085,num(0)),(131087,auto()),(131096,px(0)),(131097,px(0)),(131105,val(3,{'unit':2,'value':100.0})),(131074,en('stretch'))])
 apply(gr,root,[(131093,px(8))])
 listdata=gr[mapping[sr[1078]['data']['m_SerializedData']['rid']]]['data']
 listdata.update(Truncate=0,Truncate_UxmlAttributeFlags=1)
 for i in source_ids:
  if i in source_nodes:continue
  expected=copy.deepcopy(sr[i]['data']);expected['uxmlAssetId']=idmap[expected['uxmlAssetId']];expected['name']=prefix+expected['name']
  if i==sr[1078]['data']['m_SerializedData']['rid']:expected.update(Truncate=0,Truncate_UxmlAttributeFlags=1)
  assert gr[mapping[i]]['data']==expected,('trait binding changed',i)
 imports.append({'prefix':prefix,'parent':parent,'root':root,'mapping':mapping})

known_types={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in go[TABLE].assets_file.ref_types}
for t in objects[PAGES[0]].assets_file.ref_types:
 key=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
 if key not in known_types:go[TABLE].assets_file.ref_types.append(copy.copy(t));known_types.add(key)

# Verify native lists, scores and goalkeeper switching keep their original serialized data.
for i,r in gr_before.items():
 if i in removed_feet:continue
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert gr[i]==r,('original attribute binding changed',i)
assert [c['rid'] for c in gr[1011]['data']['m_Children']]==[1025,1063]
assert [c['rid'] for c in gr[1029]['data']['m_Children']]==[1062]
assert [c['rid'] for c in gr[1009]['data']['m_Children']]==[1020,1021,imports[0]['root']]
assert [c['rid'] for c in gr[1013]['data']['m_Children']]==[1029,1030,imports[1]['root']]
assert not any(r.get('data',{}).get('m_TemplateAlias')=='PlayerReportFootednessBlock' for r in gr.values())
validate_ui(table,gsheet)
go[TABLE].save_typetree(table);go[gsid].save_typetree(gsheet)

# Extend this table's existing preload span with the already registered native trait row.
ab=next(o for o in go.values() if o.type.name=='AssetBundle');gm=ab.read_typetree();gm_before=copy.deepcopy(gm)
tableentry=next(v for k,v in gm['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':TABLE})
traitpid=next(v['asset']['m_PathID'] for k,v in gm['m_Container'] if k=='cf6ecba08a86be0469c39c12907a714e')
span=copy.deepcopy(gm['m_PreloadTable'][tableentry['preloadIndex']:tableentry['preloadIndex']+tableentry['preloadSize']])
for pid in [traitpid,go[traitpid].read_typetree()['inlineSheet']['m_PathID']]:
 ptr={'m_FileID':0,'m_PathID':pid}
 if ptr not in span:span.append(ptr)
tableentry.update(preloadIndex=len(gm['m_PreloadTable']),preloadSize=len(span));gm['m_PreloadTable'].extend(span);ab.save_typetree(gm)
assert gm['m_Dependencies']==gm_before['m_Dependencies']

# Both overview variants retain only the native bans component on the right.
# Give the central table its own native vertical scroll view for long trait lists.
page_outputs={};page_audit=[]
sheet=fullsheet
for pid in PAGES:
 d=objects[pid].read_typetree();old=copy.deepcopy(d);refs={r['rid']:r for r in d['references']['RefIds']};ss=objects[d['inlineSheet']['m_PathID']].read_typetree();sheet=ss
 oldrefs=copy.deepcopy(refs);right=1011;bans=1035
 removed=[]
 for c in list(refs[right]['data']['m_Children']):
  if c['rid']!=bans:removed.extend(remove_tree(d,refs,c['rid']))
 assert refs[right]['data']['m_Children']==[{'rid':bans}]
 assert refs[bans]==oldrefs[bans]
 apply(refs,right,[(131088,en('flex-start')),(131093,px(0)),(131090,px(0))])
 source=refs[1703];source_sd=refs[source['data']['m_SerializedData']['rid']]
 rid=max(refs)+1;sdid=rid+1;eid=max(r.get('data',{}).get('m_Id',0) for r in refs.values())+1
 node=copy.deepcopy(source);serial=copy.deepcopy(source_sd);node['rid']=rid;serial['rid']=sdid
 parent=refs[1040]['data']['m_Parent']['rid'];assert parent==1025
 node['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[{'rid':1040}],m_SerializedData={'rid':sdid},m_RuleIndex=-1,m_Classes=['flex-grow-class','align-self-stretch'])
 serial['data'].update(uxmlAssetId=eid,name='OverviewAttributesContentScroll',name_UxmlAttributeFlags=1,mode=0,mode_UxmlAttributeFlags=1,horizontalScrollerVisibility=2,horizontalScrollerVisibility_UxmlAttributeFlags=1,verticalScrollerVisibility=0,verticalScrollerVisibility_UxmlAttributeFlags=1)
 refs[rid]=node;refs[sdid]=serial;d['references']['RefIds'].extend([node,serial])
 position=refs[parent]['data']['m_Children'].index({'rid':1040});refs[parent]['data']['m_Children'][position]={'rid':rid};refs[1040]['data']['m_Parent']={'rid':rid}
 apply(refs,rid,[(131105,val(3,{'unit':2,'value':100.0})),(131097,px(0)),(131095,{'m_ValueType':1,'valueIndex':3}),(131087,auto()),(131096,px(0)),(131084,num(1)),(131085,num(1)),(262150,px(0)),(262151,px(0))])
 apply(refs,parent,[(131096,px(0)),(131097,px(0)),(131084,num(1)),(131085,num(1))])
 for i,r in oldrefs.items():
  if i in removed:continue
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert refs[i]==r,('page binding changed',pid,i)
 assert next(u for u in d['m_Usings'] if u['alias']=='AttributesTableTemplate')['path']=='3bc158458fec50bf9230826edbc62cd1'
 validate_ui(d,ss);objects[pid].save_typetree(d);objects[d['inlineSheet']['m_PathID']].save_typetree(ss)
 page_outputs[pid]=d;page_outputs[d['inlineSheet']['m_PathID']]=ss
 page_audit.append({'page_id':pid,'page_name':d['m_Name'],'right_children':[bans],'removed_right_records':removed,'attribute_scroll_id':rid})

outputs={WN:env.file.save(packer='lz4'),GN:ge.file.save(packer='lz4')}
savedworld={o.path_id:o for o in UnityPy.load(outputs[WN]).objects};savedglobal={o.path_id:o for o in UnityPy.load(outputs[GN]).objects}
assert set(savedworld)==set(objects) and set(savedglobal)==set(go)
global_changes={TABLE:table,gsid:gsheet,ab.path_id:gm}
for pid,h in old_hashes.items():
 if pid in page_outputs:assert savedworld[pid].read_typetree()==page_outputs[pid]
 else:assert sha(savedworld[pid].get_raw_data())==h,('unrelated world asset changed',pid)
for pid,h in gh.items():
 if pid in global_changes:assert savedglobal[pid].read_typetree()==global_changes[pid]
 else:assert sha(savedglobal[pid].get_raw_data())==h,('unrelated global asset changed',pid)
validate_ui(savedglobal[TABLE].read_typetree(),savedglobal[gsid].read_typetree())
for pid in PAGES:validate_ui(savedworld[pid].read_typetree(),savedworld[page_outputs[pid]['inlineSheet']['m_PathID']].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h

stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('attributes-traits-bans-restructure-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir()
 for name in outputs:(backup/name).write_bytes(before[folder/name])
for name,data in outputs.items():(out/name).write_bytes(data)
report={'installed':False,'runtime_verified':False,'output':str(out),'pages':page_audit,'table_id':TABLE,'goalkeeper_technical_parent':1011,'goalkeeper_third_column':[1029,1030,imports[1]['root']],'outfield_third_column':[1020,1021,imports[0]['root']],'traits_imports':imports,'footedness_records_removed':removed_feet,'trait_lists_untruncated':True,'trait_rows_native_wrap_and_tooltips_preserved':True,'original_attribute_rating_and_bans_bindings_preserved':True,'native_vertical_scroll_added_to_both_pages':True,'changed_world_assets':list(page_outputs),'changed_global_assets':list(global_changes),'unchanged_world_asset_count':len(old_hashes)-len(page_outputs),'unchanged_global_asset_count':len(gh)-len(global_changes),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()}}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  for name,data in outputs.items():(folder/name).write_bytes(data);assert sha((folder/name).read_bytes())==sha(data)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'pages':len(page_audit),'traits_copies':len(imports),'table_branches':2,'footedness_records_removed':len(removed_feet)},ensure_ascii=True))
