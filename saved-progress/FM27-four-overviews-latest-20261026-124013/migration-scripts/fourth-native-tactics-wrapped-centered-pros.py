from pathlib import Path
import ast,copy,json,struct,uuid,importlib.util
s=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0].replace('second-overview-stats-bans-stacked-pitch-','fourth-native-tactics-wrapped-centered-pros-')
exec(compile(s,'backup-and-helpers','exec'))
PAGE,STYLE=-940000000012000,-940000000012001
MODULE,MS=-940000000014000,-940000000014001;SOURCE=-940000000006002;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-fourth-centered-auto-wrapped-pros-cons-v1').hex

def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def save(n,pid,doc,sid,sheet):
 validate_ui(doc,sheet);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(sheet);changed[n][pid]=doc;changed[n][sid]=sheet
# Private clone: preserve native report headings, rows, tooltips and conditional titles.
doc=copy.deepcopy(objs[G][SOURCE].read_typetree());oldstyle=doc['inlineSheet']['m_PathID'];sheet=copy.deepcopy(objs[G][oldstyle].read_typetree());doc.update(m_Name='FourthOverviewWrappedProsConsIcons',inlineSheet={'m_FileID':0,'m_PathID':MS});sheet['m_Name']='FourthOverviewWrappedProsConsIcons_Style'
rr=refs(doc);original=copy.deepcopy(rr)
for i in [1001,1002,1004,1005,1008,1011]:
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0))])
for i in [1008,1011]:
 rr[i]['data']['m_Classes']=list(dict.fromkeys(rr[i]['data']['m_Classes']+['fourth_wrapped_icons']))
 for k,v in {'Direction':1,'ScrollViewMode':0,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':2,'DynamicElements':1,'FixedElementSize':24.0,'ClampSizeToPage':0,'Truncate':0}.items():sd(i)[k]=v;sd(i)[k+'_UxmlAttributeFlags']=1
 for k in ['Binding','RowTemplate','RowParamName']:assert sd(i)[k]==serial(original,i)['data'][k]
# Constrain the virtual list's row width, allow natural multi-line height, and prohibit growing cells.
for child in ['virtualised-list__view','unity-scroll-view__content-container']:
 ri=rule([prop(131083,en('row')),prop(131086,en('wrap')),prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('flex-start')),prop(131088,en('flex-start'))])
 sheet['m_Rules'][ri]['m_ComplexSelectors']=[{'m_Specificity':21,'m_Selectors':[{'m_Parts':[{'m_Value':'fourth_wrapped_icons','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':child,'m_Type':3}],'m_PreviousRelationship':2}],'ruleIndex':ri}]
validate_ui(doc,sheet)
for source,pid,data in [(oldstyle,MS,sheet),(SOURCE,MODULE,doc)]:
 assert pid not in objs[G];obj=copy.copy(objs[G][source]);obj.path_id=pid;obj.assets_file.objects[pid]=obj;objs[G][pid]=obj;obj.save_typetree(data);changed[G][pid]=data
metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();sourcekey=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':SOURCE});entry=next(v for k,v in meta['m_Container'] if k==sourcekey and v['asset']['m_PathID']==SOURCE);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for ptr in span:
 if ptr['m_FileID']==0:
  if ptr['m_PathID']==SOURCE:ptr['m_PathID']=MODULE
  elif ptr['m_PathID']==oldstyle:ptr['m_PathID']=MS
meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':MODULE}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);changed[G][metaobj.path_id]=meta

doc=objs[W][PAGE].read_typetree();rr=refs(doc);original=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
tactic=named('FourthOverviewConditionalTacticalHalf');pros=named('FourthOverviewConditionalProsCons30Percent')
# SIVisible's native direct binding accepts numeric flags as well as booleans.
sd(tactic).update(Binding={'m_kind':1,'m_direct':{'Path':{'m_path':'localteam.Tactic.TacticalEffectiveness.StatusFlags.NoTacticError'},'Nullable':1},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},Binding_UxmlAttributeFlags=1,InvertDirectBinding=1,InvertDirectBinding_UxmlAttributeFlags=1,AcceptNumbers=1,AcceptNumbers_UxmlAttributeFlags=1,AlwaysInstantiate=1,AlwaysInstantiate_UxmlAttributeFlags=1)
team=add_pair(original[6312],serial(original,6312),tactic,'FourthOverviewTacticsSelectedPlayerAndTeam')
sd(team).update(Mappings=[{'m_serialisedType':0,'from':'team','to':{'m_path':'localteam'},'type':{'id':1145176088}},{'m_serialisedType':0,'from':'player','to':{'m_path':'person'},'type':{'id':1145176065}}],Mappings_UxmlAttributeFlags=1)
rr[tactic]['data']['m_Children'].remove({'rid':6416});rr[6416]['data']['m_Parent']={'rid':team};rr[team]['data']['m_Children']=[{'rid':6416}]
for i in [team,6416]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
# Center the whole block, allowing its two icon lists to determine their natural height.
override(rr[pros]['data'],[prop(131083,en('column')),prop(131088,en('center')),prop(131073,en('stretch'))])
for i in [6420,6422]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('stretch'))])
for u in doc['m_Usings']:
 if u['alias']=='OverviewTitledProsConsIcons':u.update(path=KEY,asset={'m_FileID':0,'m_PathID':0})
assert serial(rr,6416)==serial(original,6416)
assert rr[6298]['data']['m_Children']==original[6298]['data']['m_Children']
assert rr[1173]['data']['m_Children']==original[1173]['data']['m_Children']
save(W,PAGE,doc,STYLE,sheet)
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=cat.locations(sourcekey)[0];cat=cm.Catalog(cat.add_key_location(KEY,loc,loc))
label='GlobalVisualTreeAssetPreload';idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)==label);ko,ls=cat.key_records[idx];locations=[x[0] for x in cat.array(ls,'I')]+cat.locations(KEY);newset=cat.append(b''.join(struct.pack('<I',x) for x in locations),True);records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);hashout=__import__('hashlib').md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'fourth_only':True,
    'tactical_visibility':'native inverse error flag, numeric values accepted, explicitly selected player team',
    'tactics_internal_bindings_unchanged':True,'pros_icons_wrap':True,'pros_block_vertical_alignment':'center',
    'private_pros_module_guid':KEY,'second_row_height':150,'radar_pros_ratio':[70,30],
    'first_three_pages_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
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
print(json.dumps({'installed':True,'output':str(OUT),'native_tactics_gate':True,'wrapped_pros_centered':True}))
