from pathlib import Path
import ast,copy,json,struct,uuid,itertools,importlib.util
source=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0]
source=source.replace("'second-overview-stats-bans-stacked-pitch-'","'fourth-transfer-fallback-radar250-'")
exec(compile(source,'backup-and-helpers','exec'))
PAGE,STYLE=-940000000012000,-940000000012001
FUNC=-940000000013000;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-fourth-has-pros-cons-or-valid-tactics-switch-v1').hex
F='ui-visualfunctions_assets_all.bundle';fe=UnityPy.load(str(GAME/F));fo={o.path_id:o for o in fe.objects}
funcs={o.peek_name():o for o in fo.values() if o.type.name=='MonoBehaviour'}
templates={}
for o in funcs.values():
 for r in o.read_typetree().get('references',{}).get('RefIds',[]):
  if r.get('type',{}).get('class'):templates.setdefault(r['type']['class'],r)
helper=ast.parse(Path('add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['guid','gid','link','socket_source','constant','check_graph']],type_ignores=[]),'graph-helpers','exec'))
base=funcs['BindListHasItemsToSwitch'].read_typetree();root=guid();graph=copy.deepcopy(objs[G][-940000000000100].read_typetree())
graph.update(m_Name='FourthOverviewContentOrTransferSwitch',m_name='FourthOverviewContentOrTransferSwitch',m_id=root,m_description='Show native pros/cons and tactics when either list has items or NoTacticError is explicitly false. Otherwise show transfer status.',m_inputs=[],m_outputs=[],m_variables=[],m_nodes=[])
for name,p in [('BindingBag',base['m_inputs'][0]),('Switch',base['m_inputs'][1]),('Pros',base['m_inputs'][2]),('Cons',base['m_inputs'][2]),('NoTacticError',base['m_inputs'][2])]:
 p=copy.deepcopy(p);p.update(m_name=name,m_id=guid(),m_parentID=copy.deepcopy(root));graph['m_inputs'].append(p)
grefs=[]
def clone(cls,name):
 r=copy.deepcopy(templates[cls]);r['rid']=194000000000000000+len(grefs);d=r['data'];d.update(m_name=name,m_id=guid(),m_parentID=copy.deepcopy(root))
 def reset(v):
  if isinstance(v,dict):
   for k,x in list(v.items()):
    if k=='m_id' and isinstance(x,dict) and 'm_idBytes' in x:v[k]=guid()
    elif k in ['m_sourceID','m_destinationID']:v[k]={'m_idBytes':[0]*16}
    else:reset(x)
  elif isinstance(v,list):
   for x in v:reset(x)
 for k,v in d.items():
  if k not in ['m_id','m_parentID']:reset(v)
 grefs.append(r);return d
entry=clone('EntryNode','Entry');entry['m_dataSockets']=[{'m_id':guid(),'m_name':p['m_name'],'m_dataID':copy.deepcopy(p['m_id'])} for p in graph['m_inputs']];ports={p['m_name']:p['m_id'] for p in entry['m_dataSockets']}
bind=clone('BindNode','Observe current report lists and tactical data')
socket_source(bind,'m_bindingBagDataInputSocket',ports['BindingBag']);socket_source(bind,'m_componentDataInputSocket',ports['Switch'])
di=copy.deepcopy(bind['m_dynamicDataInputSockets'][0]);do=copy.deepcopy(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0]);bind['m_dynamicDataInputSockets']=[];bind['m_outputAsyncExecSocket']['m_dataOutputSockets']=[]
for p in graph['m_inputs'][2:]:
 a,b=copy.deepcopy(di),copy.deepcopy(do);a.update(m_id=guid(),m_name=p['m_name'],m_sourceID=ports[p['m_name']],m_dataID=p['m_id']);b.update(m_id=guid(),m_name=p['m_name'],m_dataID=p['m_id']);bind['m_dynamicDataInputSockets'].append(a);bind['m_outputAsyncExecSocket']['m_dataOutputSockets'].append(b)
bound=bind['m_outputAsyncExecSocket']['m_dataOutputSockets'];has=[]
for j,name in enumerate(['Pros','Cons']):
 get=clone('TypedValueVisualFunctionLibrary_GetIList','Get '+name+' list');socket_source(get,'m_dataInValue',bound[j]['m_id'])
 node=clone('GeneralVisualFunction_HasItems',name+' list has items');socket_source(node,'m_dataInList',get['m_dataOutIList']['m_id']);has.append(node['m_dataOutBoolean']['m_id'])
valid=clone('TypedValueVisualFunctionLibrary_TryGetBool','NoTacticError is an available boolean');socket_source(valid,'m_dataInValue',bound[2]['m_id'])
noterror=clone('VisualFunctionLibrary_XOR_bool_bool_bool','No tactical error');socket_source(noterror,'m_dataInA',valid['m_dataOutBoolValue']['m_id']);constant(noterror,'m_dataInB',1)
andnode=clone('GeneralVisualFunction_AND','Tactical data available and no error');socket_source(andnode,'m_dataInA',valid['m_dataOutBoolean']['m_id']);socket_source(andnode,'m_dataInB',noterror['m_dataOutBoolean']['m_id'])
listor=clone('GeneralVisualFunction_OR','Any pros or cons');socket_source(listor,'m_dataInA',has[0]);socket_source(listor,'m_dataInB',has[1])
anycontent=clone('GeneralVisualFunction_OR','Any report or tactics content');socket_source(anycontent,'m_dataInA',listor['m_dataOutBoolean']['m_id']);socket_source(anycontent,'m_dataInB',andnode['m_dataOutBoolean']['m_id'])
branch=clone('GeneralVisualFunction_Branch','Choose content or transfer status');socket_source(branch,'m_dataInCondition',anycontent['m_dataOutBoolean']['m_id'])
show=clone('BindableSwitchElement_SetVisibleIndex','Show pros cons and tactics');socket_source(show,'m_target',ports['Switch']);constant(show,'m_dataInIndex',1)
fallback=clone('BindableSwitchElement_SetVisibleIndex','Show native transfer status');socket_source(fallback,'m_target',ports['Switch']);constant(fallback,'m_dataInIndex',0)
link(entry,'m_outputExecSocket',bind,'m_inputExecSocket');link(bind,'m_outputAsyncExecSocket',valid)
chain=[valid,andnode,listor,anycontent,branch]
for a,b in zip(chain,chain[1:]):link(a,'m_execOutExecOutput',b)
link(branch,'m_execOutTrue',show);link(branch,'m_execOutFalse',fallback)
graph['m_nodes']=[{'rid':r['rid']} for r in grefs];graph['references']={'version':2,'RefIds':grefs};check_graph(graph)
# Evaluate the actual generated graph across available, empty, and missing data.
def evaluate(pros,cons,noerror):
 memo={gid(bound[0]['m_id']):pros,gid(bound[1]['m_id']):cons,gid(bound[2]['m_id']):noerror};outputs={};execs={}
 for r in grefs:
  d=r['data']
  for k,v in d.items():
   if isinstance(v,dict) and 'm_id' in v and (k.startswith('m_dataOut') or k=='m_target'):outputs[gid(v['m_id'])]=(r,k)
  if 'm_execInExecInput' in d:execs[gid(d['m_execInExecInput']['m_id'])]=r
 def val(d,k):
  s=d[k];ident=gid(s['m_sourceID']);return resolve(ident) if any(ident) else s.get('m_defaultSocketValue',{}).get('m_value')
 def resolve(ident):
  if ident in memo:return memo[ident]
  r,k=outputs[ident];d=r['data'];c=r['type']['class']
  if c=='TypedValueVisualFunctionLibrary_GetIList':v=val(d,'m_dataInValue');result=v if isinstance(v,list) else None
  elif c=='GeneralVisualFunction_HasItems':result=bool(val(d,'m_dataInList'))
  elif c=='VisualFunctionLibrary_XOR_bool_bool_bool':result=bool(val(d,'m_dataInA'))!=bool(val(d,'m_dataInB'))
  elif c=='GeneralVisualFunction_OR':result=bool(val(d,'m_dataInA')) or bool(val(d,'m_dataInB'))
  elif c=='GeneralVisualFunction_AND':result=bool(val(d,'m_dataInA')) and bool(val(d,'m_dataInB'))
  else:raise AssertionError(c)
  memo[ident]=result;return result
 target=gid(bind['m_outputAsyncExecSocket']['m_destinationID'])
 for _ in range(12):
  r=execs[target];d=r['data'];c=r['type']['class']
  if c=='TypedValueVisualFunctionLibrary_TryGetBool':
   v=val(d,'m_dataInValue');memo[gid(d['m_dataOutBoolean']['m_id'])]=type(v) is bool;memo[gid(d['m_dataOutBoolValue']['m_id'])]=v if type(v) is bool else False
  elif c in ['GeneralVisualFunction_AND','GeneralVisualFunction_OR']:resolve(gid(d['m_dataOutBoolean']['m_id']))
  elif c=='GeneralVisualFunction_Branch':target=gid(d['m_execOutTrue' if val(d,'m_dataInCondition') else 'm_execOutFalse']['m_destinationID']);continue
  elif c=='BindableSwitchElement_SetVisibleIndex':return val(d,'m_dataInIndex')
  else:raise AssertionError(c)
  target=gid(d['m_execOutExecOutput']['m_destinationID'])
 raise AssertionError('no final switch')
for pros,cons,err in itertools.product([None,[],[1]],[None,[],[1]],[None,True,False,0]):assert evaluate(pros,cons,err)==int(bool(pros) or bool(cons) or (type(err) is bool and not err))
af=env[G].assets[0];known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types};needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in grefs}
for t in fe.assets[0].ref_types:
 k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
 if k in needed and k not in known:af.ref_types.append(copy.copy(t));known.add(k)
assert needed<=known
obj=copy.copy(objs[G][-940000000000100]);obj.path_id=FUNC;af.objects[FUNC]=obj;objs[G][FUNC]=obj;obj.save_typetree(graph);changed[G][FUNC]=graph
metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':FUNC}}));meta['m_PreloadTable'].extend([graph['m_Script'],{'m_FileID':0,'m_PathID':FUNC}]);meta['m_Container'].sort(key=lambda kv:kv[0]);metaobj.save_typetree(meta);changed[G][metaobj.path_id]=meta
# Native template is referenced directly, preserving all transfer details and bindings.
doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def fixed(i,h):override(rr[i]['data'],[prop(131087,px(h)),prop(131096,px(h)),prop(131094,px(h)),prop(131084,num(0)),prop(131085,num(0))])
fixed(1703,450);fixed(6298,250);fixed(1026,250);fixed(1043,250);fixed(6228,250)
override(rr[1026]['data'],[prop(131105,px(250)),prop(131097,px(250)),prop(131095,px(250)),prop(131082,px(250)),prop(131084,num(0)),prop(131085,num(0))])
override(rr[6228]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
# Force the bans table to scroll within its fixed-height region, using a fourth-only scroll wrapper.
scrollsource=old[1703];scrollsd=serial(old,1703)
ban_sd=rr[6228]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(scrollsd);replacement['rid']=ban_sd;replacement['data'].update(uxmlAssetId=rr[6228]['data']['m_Id'],name='FourthOverviewBans250Scroll',name_UxmlAttributeFlags=1)
rr[ban_sd].clear();rr[ban_sd].update(replacement);rr[6228]['data']['m_FullTypeName']='SI.UI.SIScrollView'
tacticdoc=objs[W][-940000000003000].read_typetree();tr=refs(tacticdoc)
switch=add_pair(tr[1012],serial(tr,1012),1173,'FourthOverviewContentOrTransferSwitch')
paths=['person.PlayerReportForContextTeam.ScoutedProConsList.ProsList','person.PlayerReportForContextTeam.ScoutedProConsList.ConsList','team.Tactic.TacticalEffectiveness.StatusFlags.NoTacticError']
def seven(n):
 out=bytearray()
 while n>=128:out.append((n&127)|128);n>>=7
 out.append(n);return out
raw=bytearray([3]);typ='>SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'.encode()
for path in paths:
 b=typ+bytes([1])+seven(len(path.encode()))+path.encode();raw+=struct.pack('<I',len(b))+b
sd(switch).update(Binding={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':KEY},'m_inputs':{'m_variable':{'m_argumentBytes':list(raw)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},Binding_UxmlAttributeFlags=1,AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1,Preview={'Mask':1},Preview_UxmlAttributeFlags=1)
override(rr[switch]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,pct(100)),prop(131096,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
transfer=add_pair(old[6416],serial(old,6416),switch,'FourthOverviewTransferStatusFallback')
metaW=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle');transferkey=next(k for k,v in metaW['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':5482864726752486163})
alias='FourthOverviewNativeTransferStatus';rr[transfer]['data'].update(m_TemplateAlias=alias,m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[]);sd(transfer).update(templateId=alias,templateId_UxmlAttributeFlags=1)
doc['m_Usings'].append({'alias':alias,'path':transferkey,'asset':{'m_FileID':0,'m_PathID':0}})
override(rr[transfer]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,pct(100)),prop(131096,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
rr[1173]['data']['m_Children'].remove({'rid':6418});rr[6418]['data']['m_Parent']={'rid':switch};rr[switch]['data']['m_Children'].append({'rid':6418})
assert rr[1173]['data']['m_Children']==[{'rid':switch}]
assert rr[switch]['data']['m_Children']==[{'rid':transfer},{'rid':6418}]
validate_ui(doc,sheet);objs[W][PAGE].save_typetree(doc);objs[W][STYLE].save_typetree(sheet);changed[W][PAGE]=doc;changed[W][STYLE]=sheet
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin'])
oldkey=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':-940000000000100});loc=cat.locations(oldkey)[0];catout=cat.add_key_location(KEY,loc,loc);cat=cm.Catalog(catout);assert cat.locations(transferkey)
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);hashout=__import__('hashlib').md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'fourth_only':True,'fallback':'transfer only when both pros/cons lists empty and no valid tactics','conditional_function_guid':KEY,'truth_table_cases':36,'radar_width':250,'bans_and_radar_height':250,'right_upper_height':450,'native_transfer_guid':transferkey,'first_three_pages_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
pending=[(folder/n,b) for n,b in outputs.items() for folder in [GAME,SKIN]]+[(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout),(SKIN/'catalog.hash',hashout)]
for p,b in pending:
 if p not in before:
  before[p]=p.read_bytes() if p.exists() else None
  if before[p] is not None:(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name).write_bytes(before[p])
restore=['$ErrorActionPreference = "Stop"']
for p,b in before.items():
 if b is not None:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in pending:p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():
  if b is not None:p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'fallback_cases_verified':36,'radar_width':250,'row_height':250,'upper_height':450}))
