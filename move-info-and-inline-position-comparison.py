from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def pct(x):return val(3,{'unit':2,'value':float(x)})
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def move(i,parent,index=None):
 old=rr[i]['data']['m_Parent']['rid'];rr[old]['data']['m_Children'].remove({'rid':i})
 rr[i]['data']['m_Parent']={'rid':parent}
 if index is None:rr[parent]['data']['m_Children'].append({'rid':i})
 else:rr[parent]['data']['m_Children'].insert(index,{'rid':i})
removed=set()
def remove(i):
 a=rr[i]['data']
 for c in list(a.get('m_Children',[])):remove(c['rid'])
 sd=a.get('m_SerializedData',{}).get('rid')
 if sd in rr:removed.add(sd)
 removed.add(i)
 parent=a.get('m_Parent',{}).get('rid')
 if parent in rr and {'rid':i} in rr[parent]['data'].get('m_Children',[]):rr[parent]['data']['m_Children'].remove({'rid':i})
# Three native title/value rows beside the existing native contract column.
move(1031,1184,0)
st(1184,[(131083,en('row')),(131073,en('flex-start')),(131087,px(60)),(131096,px(60))])
rr[1031]['data']['m_Classes']=[]
st(1031,[(131105,px(150)),(131097,px(150)),(131084,num(0)),(131085,num(0)),(131083,en('column')),(131092,px(12)),(131087,px(60))])
st(1199,[(131105,auto()),(131084,num(1)),(131082,px(0)),(131097,px(0)),(131085,num(1))])
for i in [1049,1050,1051,1072,1087]:
 st(i,[(131083,en('row')),(131073,en('center')),(131087,px(20)),(131096,px(20)),(131084,num(0)),(131085,num(0)),(262150,px(0)),(262151,px(0))])
for i in [1066,1069,1096]:st(i,[(131092,px(6)),(131090,px(0)),(131093,px(0)),(131085,num(0))])
remove(1029);remove(1030);remove(1032)
# Inline the overview's role selector only, leaving every shared/native template intact.
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects}
role=next(o for o in go.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='role_selector-large')
pid=role.path_id;srcdocs={pid:role.read_typetree()};srcsheets={pid:go[srcdocs[pid]['inlineSheet']['m_PathID']].read_typetree()}
next_eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;imports=[]
tree=ast.parse((R/'move-ability-stars-inline-loans-hide-gk-title.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['refs_in','import_native','local_container']],type_ignores=[]),'<inline native helpers>','exec'))
local_container(1007,'OverviewPositionAndComparison')
mp=import_native(pid,1007,'OverviewPosition_')
# Ensure every imported managed type is serializable in this bundle.
af=objects[FULL].assets_file
known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in rr.values()}
for t in role.assets_file.ref_types:
 key=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
 if key in needed and key not in known:af.ref_types.append(copy.copy(t));known.add(key)
source_needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in srcdocs[pid]['references']['RefIds']}
assert (needed-known)<=({(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in old_refs.values()}-known),('new managed type absent',needed-known)
# Keep position/role controls in the left column; put the actual comparison binding/table on its right.
move(mp[1064],mp[1001])
st(mp[1001],[(131083,en('row')),(131073,en('stretch')),(131084,num(1)),(131097,px(0)),(131105,pct(100))])
for i in [1007,1064]:
 st(mp[i],[(131084,num(1)),(131085,num(1)),(131082,px(0)),(131097,px(0)),(131105,auto()),(131074,en('stretch'))])
st(mp[1007],[(131092,px(10))])
st(mp[1064],[(131093,px(0)),(131099,px(8)),(131100,px(0)),(131083,en('column'))])
st(mp[1072],[(131097,px(0)),(131084,num(1)),(131085,num(1)),(131074,en('stretch'))])
# Role list no longer switches away; native condition for selecting a position remains intact.
switch=rr[mp[1055]];sdi=switch['data']['m_SerializedData']['rid']
switch['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
rr[sdi]['type']=copy.deepcopy(rr[1042]['type'])
rr[sdi]['data']=copy.deepcopy(rr[1042]['data']);rr[sdi]['data']['uxmlAssetId']=switch['data']['m_Id']
remove(mp[1020])
# Allocate room for both columns while retaining the attribute table's minimum width.
st(1007,[(131105,px(580)),(131097,px(580)),(131085,num(0))])
settings=rr[1014]['data']['Settings']['m_settings'];assert len(settings)==5
settings[0]['PredefinedSize']=580.0;settings[4]['PredefinedSize']=200.0
for i in [1703,1011]:st(i,[(131095,px(240)),(131097,px(0))])
doc['references']['RefIds']=[rr[r['rid']] for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed:del rr[i]
# Dynamic profile text, contract, card, radar and native comparison-table data remain unchanged.
for i in old_refs:
 if i not in removed and i not in [old_refs[1007]['data']['m_SerializedData']['rid'],1014] and 'UxmlSerializedData' in old_refs[i]['type']['class']:assert rr[i]==old_refs[i],('existing binding changed',i)
for old in [1073,1079]:
 actual=copy.deepcopy(rr[mp[old]]['data']);expected=copy.deepcopy(next(r for r in srcdocs[pid]['references']['RefIds'] if r['rid']==old)['data'])
 actual['uxmlAssetId']=expected['uxmlAssetId'];assert actual==expected,('comparison binding changed',old)
assert rr[1184]['data']['m_Children']==[{'rid':1031},{'rid':1199}]
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('profile-beside-contract-position-comparison-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid],'profile_info_left_of_contract':True,'position_comparison_side_by_side':True,'role_selector_width':580,'native_comparison_binding_unchanged':True,'second_version_unchanged':True,'inline_imports':imports,'removed_records':sorted(removed),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-2}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  (folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output)},ensure_ascii=False))
