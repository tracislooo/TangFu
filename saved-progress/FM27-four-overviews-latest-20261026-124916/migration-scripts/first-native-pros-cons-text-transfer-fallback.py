from pathlib import Path
import ast,copy,json,struct,uuid,importlib.util
bootstrap=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0].replace('second-overview-stats-bans-stacked-pitch-','first-native-pros-cons-text-transfer-fallback-')
exec(compile(bootstrap,'backup-and-helpers','exec'))
PAGE,STYLE=-930000000001001,-930000000001000
SOURCE=-940000000006002;MODULE,MS=-940000000015000,-940000000015001;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-first-native-pros-cons-icon-text-two-columns-v1').hex
FUNCTION=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-fourth-has-pros-cons-or-valid-tactics-switch-v1').hex

def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
# Clone the existing conditional headings, but restore the game's full icon-and-description row.
native=objs[G][7391060340652509499].read_typetree();nr=refs(native)
doc=copy.deepcopy(objs[G][SOURCE].read_typetree());oldstyle=doc['inlineSheet']['m_PathID'];sheet=copy.deepcopy(objs[G][oldstyle].read_typetree());doc.update(m_Name='FirstOverviewNativeProsConsIconTextTwoColumns',inlineSheet={'m_FileID':0,'m_PathID':MS});sheet['m_Name']='FirstOverviewNativeProsConsIconTextTwoColumns_Style'
rr=refs(doc);old=copy.deepcopy(rr)
for i in [1001,1002]:
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('stretch'))])
override(rr[1002]['data'],[prop(131083,en('row'))])
for i in [1004,1005]:
 # Both columns keep their half-width even when their own list is empty.
 sid=rr[i]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(serial(nr,i));replacement['rid']=sid;replacement['data'].update(uxmlAssetId=rr[i]['data']['m_Id'],name='FirstOverviewProsColumn' if i==1004 else 'FirstOverviewConsColumn',name_UxmlAttributeFlags=1)
 rr[sid].clear();rr[sid].update(replacement);rr[i]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
 override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131083,en('column')),prop(131073,en('stretch')),prop(131090,px(0)),prop(131099,px(4)),prop(131100,px(4))])
for i in [1008,1011]:
 native_sd=serial(nr,i)['data']
 for k in ['RowTemplate','RowParamName','Direction','ScrollViewMode','DynamicElements','FixedElementSize','ClampSizeToPage','Truncate']:
  if k in native_sd:sd(i)[k]=copy.deepcopy(native_sd[k]);sd(i)[k+'_UxmlAttributeFlags']=1
 for k in ['HorizontalScrollerVisibility','VerticalScrollerVisibility']:sd(i)[k]=2;sd(i)[k+'_UxmlAttributeFlags']=1
 rr[i]['data']['m_Classes']=[]
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0))])
 assert sd(i)['Binding']==serial(old,i)['data']['Binding']
validate_ui(doc,sheet)
for source,pid,data in [(oldstyle,MS,sheet),(SOURCE,MODULE,doc)]:
 assert pid not in objs[G];obj=copy.copy(objs[G][source]);obj.path_id=pid;obj.assets_file.objects[pid]=obj;objs[G][pid]=obj;obj.save_typetree(data);changed[G][pid]=data
metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();sourcekey=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':SOURCE});entry=next(v for k,v in meta['m_Container'] if k==sourcekey and v['asset']['m_PathID']==SOURCE);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for ptr in span:
 if ptr['m_FileID']==0:
  if ptr['m_PathID']==SOURCE:ptr['m_PathID']=MODULE
  elif ptr['m_PathID']==oldstyle:ptr['m_PathID']=MS
meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':MODULE}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);changed[G][metaobj.path_id]=meta

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
# Remove the tactical template and its serialized record from the first version only.
parent=rr[6230]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':6230});removed={6230,rr[6230]['data']['m_SerializedData']['rid']};doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed];rr=refs(doc)
td=objs[W][-940000000003000].read_typetree();tr=refs(td)
switch=add_pair(tr[1012],serial(tr,1012),6298,'FirstOverviewProsConsOrTransferSwitch')
def seven(n):
 b=bytearray()
 while n>=128:b.append((n&127)|128);n>>=7
 b.append(n);return b
paths=['person.PlayerReportForContextTeam.ScoutedProConsList.ProsList','person.PlayerReportForContextTeam.ScoutedProConsList.ConsList','const.NullRef'];raw=bytearray([3]);typ=b'>SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
for p in paths:
 b=typ+bytes([1])+seven(len(p.encode()))+p.encode();raw+=struct.pack('<I',len(b))+b
sd(switch).update(Binding={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':FUNCTION},'m_inputs':{'m_variable':{'m_argumentBytes':list(raw)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},Binding_UxmlAttributeFlags=1,AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1,Preview={'Mask':1},Preview_UxmlAttributeFlags=1)
map=add_pair(old[6306],serial(old,6306),switch,'FirstOverviewTransferPlayerMapping');sd(map).update(Mappings=[{'m_serialisedType':0,'from':'player','to':{'m_path':'person'},'type':{'id':1145176065}}],Mappings_UxmlAttributeFlags=1)
transfer=add_pair(old[6308],serial(old,6308),map,'FirstOverviewNativeTransferStatusFallback')
metaW=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle');transferkey=next(k for k,v in metaW['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':5482864726752486163});alias='FirstOverviewNativeTransferStatus';rr[transfer]['data'].update(m_TemplateAlias=alias,m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[]);sd(transfer).update(templateId=alias,templateId_UxmlAttributeFlags=1);doc['m_Usings'].append({'alias':alias,'path':transferkey,'asset':{'m_FileID':0,'m_PathID':0}})
rr[6298]['data']['m_Children'].remove({'rid':6306});rr[6306]['data']['m_Parent']={'rid':switch};rr[switch]['data']['m_Children'].append({'rid':6306})
for i in [6298,switch,6306,6308]:
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131083,en('column')),prop(131073,en('stretch')),prop(131091,px(0)),prop(131092,px(0))])
for i in [map,transfer]:
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,px(260)),prop(131096,px(260)),prop(131094,px(260)),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131091,px(0)),prop(131092,px(0))])
for u in doc['m_Usings']:
 if u['alias']=='OverviewTitledProsConsIcons':u.update(path=KEY,asset={'m_FileID':0,'m_PathID':0})
doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias']!='RightMiddleTacticalEffectiveness']
assert rr[6298]['data']['m_Children']==[{'rid':switch}];assert rr[switch]['data']['m_Children']==[{'rid':map},{'rid':6306}];assert 6230 not in rr
validate_ui(doc,sheet);objs[W][PAGE].save_typetree(doc);objs[W][STYLE].save_typetree(sheet);changed[W][PAGE]=doc;changed[W][STYLE]=sheet
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);assert cat.locations(FUNCTION) and cat.locations(transferkey);loc=cat.locations(sourcekey)[0];cat=cm.Catalog(cat.add_key_location(KEY,loc,loc));label='GlobalVisualTreeAssetPreload';idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)==label);ko,ls=cat.key_records[idx];locations=[x[0] for x in cat.array(ls,'I')]+cat.locations(KEY);newset=cat.append(b''.join(struct.pack('<I',x) for x in locations),True);records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);hashout=__import__('hashlib').md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'first_only':True,
    'tactics_removed':True,'pros_cons_columns':[50,50],'native_icon_and_description_row':True,
    'fallback':'native Personal Overview Transfer Status only when both pros and cons are empty',
    'conditional_function_guid':FUNCTION,'private_module_guid':KEY,'native_transfer_guid':transferkey,
    'other_three_versions_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
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
print(json.dumps({'installed':True,'output':str(OUT),'first_pros_cons_text':True,'transfer_fallback':True}))
