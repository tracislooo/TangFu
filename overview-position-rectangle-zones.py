from pathlib import Path
import ast,copy,json,struct,uuid,importlib.util
boot=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0].replace('second-overview-stats-bans-stacked-pitch-','overview-position-rectangle-zones-')
exec(compile(boot,'backups-and-helpers','exec'))
ROW,STYLE=-940000000018000,-940000000018001
KEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-overview-fourteen-rectangle-position-zones-v1').hex
assert ROW not in objs[G] and STYLE not in objs[G]
serial=lambda r,i:r[r[i]['data']['m_SerializedData']['rid']]
native=objs[W][4269476442492208794].read_typetree();nr=refs(native)
selector=objs[G][-940000000005000].read_typetree();sr=refs(selector)
world=objs[W][-930000000001001].read_typetree();wr=refs(world)
switchid=next(i for i,r in wr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement' and serial(wr,i)['data'].get('name','').startswith('OverviewFitness_Condition_Above'))
wrapped=objs[G][-5006547725779349789].read_typetree();lr=refs(wrapped)
listid=next(i for i,r in lr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.WrappedObjectList')
def seven(n):
 out=bytearray()
 while n>=128:out.append((n&127)|128);n>>=7
 out.append(n);return bytes(out)
def string(v):
 b=v.encode();return seven(len(b))+b
def dec(b):
 b=bytes(b);p=1;out=[]
 for _ in range(b[0]):
  n=struct.unpack_from('<I',b,p)[0];p+=4;out.append(b[p:p+n]);p+=n
 assert p==len(b);return out
def enc(a):return list(bytes([len(a)])+b''.join(struct.pack('<I',len(v))+v for v in a))
def replace_path(arg,path):
 end=arg.index(b']')+1;return arg[:end]+b'\x01'+string(path)
def set_event(source,target):
 a=b'\x01\x01'+string(source);b=b'\x01\x01'+string(target)
 payload=struct.pack('<I',0x57e10fd9)+b'\x01'+struct.pack('<I',len(a))+a+struct.pack('<I',len(b))+b+b'\x00\x00'
 return {'m_bytes':list(b'\x01\x01\x01\x01\x01'+struct.pack('<I',len(payload))+payload)}
assert set_event('const.True','InPossession')==serial(sr,1083)['data']['Events']
# PositionMask constants are taken from the current game's metadata enum.
# The pitch is left-to-right; top row is the player's left side.
zones=[('GK',1,0,0,1,3),('DR',4,1,2,1,1),('DL',8,1,0,1,1),('DC',16,1,1,1,1),('WBR',32,2,2,1,1),('WBL',64,2,0,1,1),('DM',128,2,1,1,1),('MR',256,3,2,1,1),('ML',512,3,0,1,1),('MC',1024,3,1,1,1),('AMR',2048,4,2,1,1),('AML',4096,4,0,1,1),('AMC',8192,4,1,1,1),('ST',65536,5,0,1,3)]
assert sum(z[4]*z[5] for z in zones)==18
assert {(x,y) for _,_,xx,yy,ww,hh in zones for x in range(xx,xx+ww) for y in range(yy,yy+hh)}=={(x,y) for x in range(6) for y in range(3)}
doc=copy.deepcopy(native);doc.update(m_Name='OverviewFourteenPositionRectangleRow',inlineSheet={'m_FileID':0,'m_PathID':STYLE},m_Usings=[])
doc['m_Script']=copy.deepcopy(objs[G][-940000000005000].read_typetree()['m_Script'])
doc['references']['RefIds']=[copy.deepcopy(nr[i]) for i in [-2,1000,1001,1003,1002,1005,1004,1007]]
rr=refs(doc);rr[1004]['data']['m_Children']=[]
sheet=copy.deepcopy(objs[W][native['inlineSheet']['m_PathID']].read_typetree());sheet['m_Script']=copy.deepcopy(objs[G][-940000000005001].read_typetree()['m_Script']);sheet['m_Name']='OverviewFourteenPositionRectangleStyles'
sheet.update(m_Rules=[],floats=[],dimensions=[],colors=[],strings=[],assets=[],imports=[],m_FlattenedImportedStyleSheets=[])
next_rid=1100;next_id=1900000000
def add(source,i,parent,name):
 global next_rid,next_id
 a=copy.deepcopy(source[i]);s=copy.deepcopy(serial(source,i));a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 for k in ['m_TemplateAlias','m_AttributeOverrides','m_SerializedDataOverride','m_SlotUsages']:a['data'].pop(k,None)
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1);next_id+=1
 rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
def pickignore(i):sd(i).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
def fill(i):
 override(rr[i]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,pct(100)),prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(262150,px(0)),prop(262151,px(0))]);pickignore(i)
sd(1001)['Parameters']=[p for p in sd(1001)['Parameters'] if p['name']=='position']
sd(1002)['Mappings']=[{'m_serialisedType':0,'from':'player','to':{'m_path':'person'},'type':{'id':1886157170}},{'m_serialisedType':0,'from':'selectedPositionMask','to':{'m_path':'positionmask'},'type':{'id':0}}]
selargs=dec(sd(1004)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']);selargs[2]=replace_path(selargs[2],'position.Position');selargs[3]=selargs[3][:selargs[3].index(b'\x01')+1]+string('fm27-position-is-selected')
sd(1004)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=enc(selargs)
for i in [1001,1002,1004]:fill(i);rr[i]['data']['m_Classes']=[]
leaves={};switches={}
def leaf(parent,z):
 label,mask,x,y,w,h=z
 cell=add(sr,1083,parent,'PositionZone_'+label);rr[cell]['data']['m_Classes']=['fm27-position-block'];s=sd(cell)
 s.update(Events=set_event('position.Position','positionmask'),Events_UxmlAttributeFlags=1,BindTextFunction={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}},BindTextFunction_UxmlAttributeFlags=0,StaticText='',StaticText_UxmlAttributeFlags=1,text='',text_UxmlAttributeFlags=1,tooltip='',tooltip_UxmlAttributeFlags=0,pickingMode=0,pickingMode_UxmlAttributeFlags=1,StopsEventPropagation=1,StopsEventPropagation_UxmlAttributeFlags=1)
 ps=[prop(131102,en('absolute')),prop(131089,pct(x*100/6)),prop(131104,pct(y*100/3)),prop(131105,pct(w*100/6)),prop(131087,pct(h*100/3)),prop(131097,px(0)),prop(131096,px(0)),prop(262150,px(0)),prop(262151,px(0)),prop(262147,px(0)),prop(458752,val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),prop(458753,none),prop(65551,en('visible'))]
 for key in [131076,131077,131078,131079]:ps.append(prop(key,px(.5)))
 for key in [458758,458761,458762,458763]:ps.append(prop(key,val(4,{'r':.8,'g':.86,'b':.9,'a':.65})))
 override(rr[cell]['data'],ps)
 setter=add(nr,1008,cell,'PositionZoneNativeColour_'+label);fill(setter)
 backdrop=add(nr,1006,setter,'PositionZoneColourFill_'+label);fill(backdrop);override(rr[backdrop]['data'],[prop(458767,num(.266))])
 text=add(nr,1020,cell,'PositionZoneValue_'+label);fill(text);s=sd(text);s.update(text='--',text_UxmlAttributeFlags=1,DebugDisplay='',DebugDisplay_UxmlAttributeFlags=0,TextBinding={'m_kind':1,'m_direct':{'Path':{'m_path':'position.PropertyValue'},'Nullable':1},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},TextBinding_UxmlAttributeFlags=1)
 override(rr[text]['data'],[prop(65537,px(12)),prop(65543,en('bold')),prop(65546,en('middle-center')),prop(65536,val(4,{'r':1.,'g':1.,'b':1.,'a':1.})),prop(65552,en('nowrap'))])
 leaves[cell]=mask;return cell
def build(parent,zz):
 if len(zz)==1:return leaf(parent,zz[0])
 n=len(zz)//2;limit=zz[n-1][1];i=add(wr,switchid,parent,'PositionZoneMaskAbove'+str(limit));fill(i)
 a=dec(sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);a[1]=a[1][:-4]+struct.pack('<i',limit);a[2]=replace_path(a[2],'position.Position');sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=enc(a);switches[i]=limit
 build(i,zz[:n]);build(i,zz[n:]);return i
tree=build(1004,sorted(zones,key=lambda z:z[1]));rr[tree]['data']['m_Classes']=['fm27-position-selection-scope']
for z in zones:
 i=tree
 while i in switches:i=rr[i]['data']['m_Children'][int(z[1]>switches[i])]['rid']
 assert leaves[i]==z[1]
# The repeater's generated item roots fill the pitch but do not obscure other cells.
def css(parts,properties):
 selectors=[{'m_Parts':[{'m_Value':v,'m_Type':3} for v in names],'m_PreviousRelationship':rel} for names,rel in parts]
 idx=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':10*sum(len(x[0]) for x in parts),'m_Selectors':selectors,'ruleIndex':idx}],'m_Properties':properties,'line':-1})
css([(['fm27-position-item-root'],0)],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,pct(100)),prop(131087,pct(100)),prop(65551,en('hidden'))])
css([(['fm27-position-selection-scope','fm27-position-is-selected'],0),(['fm27-position-block'],2)],[*[prop(k,px(2)) for k in [131076,131077,131078,131079]],*[prop(k,val(4,{'r':1.,'g':1.,'b':1.,'a':1.})) for k in [458758,458761,458762,458763]]])
borderkeys={131076,131077,131078,131079,458758,458761,458762,458763};baseborder=None
for i in leaves:
 rule0=sheet['m_Rules'][rr[i]['data']['m_RuleIndex']];baseborder=baseborder or [p for p in rule0['m_Properties'] if p['m_Id'] in borderkeys];rule0['m_Properties']=[p for p in rule0['m_Properties'] if p['m_Id'] not in borderkeys]
css([(['fm27-position-block'],0)],baseborder)
def f32all(v):
 if isinstance(v,float):return struct.unpack('<f',struct.pack('<f',v))[0]
 if isinstance(v,list):return [f32all(x) for x in v]
 if isinstance(v,dict):return {k:f32all(x) for k,x in v.items()}
 return v
sheet=f32all(sheet);doc=f32all(doc);validate_ui(doc,sheet)
for source,pid,data in [(-940000000005001,STYLE,sheet),(-940000000005000,ROW,doc)]:
 o=copy.copy(objs[G][source]);o.path_id=pid;o.assets_file.objects[pid]=o;objs[G][pid]=o;o.save_typetree(data);changed[G][pid]=data
# Keep the original native panel bound for its initial best-position selection; only its visuals/input are hidden.
selector_checks=[]
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 doc=objs[G][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 assert sd(1023)['PositionTemplateAsset']['m_AssetGUID']=='d6b3b3e4fa729864cbe89c7957538b2c'
 assert sd(1023)['TacticPositionsBinding']['m_path']=='person.positionaptitudelist'
 sd(1023).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 override(rr[1023]['data'],[prop(65551,en('hidden')),prop(458767,num(0))])
 pitch_parent=rr[1022]['data']['m_Parent']['rid']
 overlay=add(lr,listid,pitch_parent,'OverviewFourteenPositionZones');fill(overlay);s=sd(overlay);s.update(ItemTemplate={'m_AssetGUID':KEY,'m_SubObjectName':'','m_SubObjectType':''},ItemTemplate_UxmlAttributeFlags=1,ItemParamName='position',ItemParamName_UxmlAttributeFlags=1,ItemUssClassName='fm27-position-item-root',ItemUssClassName_UxmlAttributeFlags=1,GridPlacement=0,GridPlacement_UxmlAttributeFlags=1,NumPreviewElements=14,NumPreviewElements_UxmlAttributeFlags=1)
 # Native identity list binding preserves list-item contexts and player-change refresh.
 v=s['VisualFuncBinding'];v['m_target']['m_guid']='36a81e80154fa1d4e9a3b0cdea217c5b'
 a=dec(v['m_inputs']['m_variable']['m_argumentBytes']);a=a[:2];a[1]=replace_path(a[1],'person.positionaptitudelist');v['m_inputs']['m_variable']['m_argumentBytes']=enc(a)
 rr[1010]['data']['m_Stylesheets'].append({'m_FileID':0,'m_PathID':STYLE})
 # The original role, comparison, phase, position-mask and report mappings remain unchanged.
 for i,r in old.items():
  if i not in [1023,serial(old,1023)['rid'],1010,pitch_parent]:assert rr[i]==r,('unrelated selector record changed',pid,i)
 sheet=f32all(sheet);validate_ui(doc,sheet);objs[G][pid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][pid]=doc;changed[G][sid]=sheet
 selector_checks.append({'selector':str(pid),'inlineStyle':str(sid),'native_selection_binding_preserved':True,'overlay':overlay})
# New row uses an existing Global provider and is eagerly registered alongside the private selectors.
metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();sourcekey=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':-940000000005000})
span=[copy.deepcopy(objs[G][ROW].read_typetree()['m_Script']),copy.deepcopy(objs[G][STYLE].read_typetree()['m_Script']),{'m_FileID':0,'m_PathID':STYLE},{'m_FileID':0,'m_PathID':ROW}]
meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':ROW}}));meta['m_PreloadTable'].extend(span)
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 entry=next(v for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid});span0=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for ptr in span:
  if ptr not in span0:span0.append(ptr)
 entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span0));meta['m_PreloadTable'].extend(span0)
meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);changed[G][metaobj.path_id]=meta
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=next(x for x in cat.locations(sourcekey) if cat.location(x)['type'][1].endswith('VisualTreeAsset'));cat=cm.Catalog(cat.add_key_location(KEY,loc,loc))
idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];locs=[x[0] for x in cat.array(ls,'I')]+cat.locations(KEY);newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data);hashout=hashlib.md5(catout).hexdigest().encode('ascii')
output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==objs[G].keys()
for i,h in hashes[G].items():
 if i not in changed[G]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
for i,d in changed[G].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
# Resolve each overview through its actual imported private selector.
meta_map={v['asset']['m_PathID']:k for k,v in meta['m_Container']};selector_keys={meta_map[x['selector'] and int(x['selector'])] for x in selector_checks}
for pid in [-930000000001001,-930000000001003,-940000000010000,-940000000012000]:assert any(u['path'] in selector_keys for u in objs[W][pid].read_typetree()['m_Usings'])
(OUT/G).write_bytes(output);(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'versions':4,'selectors':selector_checks,'zones':[{'name':n,'mask':m,'grid':[x,y,w,h]} for n,m,x,y,w,h in zones],'value_path':'position.PropertyValue','click':'native SetBinding event position.Position -> positionmask','list':'person.positionaptitudelist','native_background_colour':True,'new_row':str(ROW),'new_style':str(STYLE),'new_guid':KEY,'world_pages_backgrounds_tilelayouts_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
pending=[(folder/G,output) for folder in [GAME,SKIN]]+[(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout),(SKIN/'catalog.hash',hashout)]
for p,b in pending:
 if p not in before:
  before[p]=p.read_bytes() if p.exists() else None
  if before[p] is not None:(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name).write_bytes(before[p])
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first.' }"]
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
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'zones':14,'versions':4}))
