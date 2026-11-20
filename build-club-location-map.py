"""Installable, UID-driven club map using native switches and live stadium bindings."""
from pathlib import Path
import ast,base64,copy,datetime,hashlib,importlib.util,json,struct,sys,uuid,zlib
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
F='ui-visualfunctions_assets_all.bundle'
OUT=R/('club-location-map-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();(OUT/'templates').mkdir();(OUT/'assets').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def float32_all(v):
 if isinstance(v,float):return f32(v)
 if isinstance(v,dict):return {k:float32_all(x) for k,x in v.items()}
 if isinstance(v,list):return [float32_all(x) for x in v]
 return v
oldval=Doc.val
Doc.val=lambda self,t,v:oldval(self,t,float32_all(v))

old=R/'exports/UK-premier-league-locations-2026-27'
coordinates=json.loads((old/'club-coordinates.json').read_text('utf8'))
db=json.loads((R/'analysis/comeback-stadium-20261115/clubs-client.json').read_text('utf8'))
mapping=[]
for row in coordinates['clubs']:
 matches=[c for c in db if 600<=c['id']<=750 and row['club'].casefold() in [n.casefold() for n in c['names']]]
 assert len(matches)==1,(row['club'],matches)
 mapping.append(dict(uid=matches[0]['id'],**row))
assert next(x for x in mapping if x['uid']==728)['club']=='Tottenham Hotspur'
(OUT/'uid-coordinates.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),'utf8')
mapuri=ET.parse(old/'map_UK-premier-league-2026-27.svg').getroot().find('{http://www.w3.org/2000/svg}image').attrib['href']
mapbytes=base64.b64decode(mapuri.split(',',1)[1]);assert sha(mapbytes)==coordinates['source_sha256']
mapfile=OUT/'assets/UK_map.png';mapfile.write_bytes(mapbytes)
MAPGUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/club-location/map-uk/source-v1').hex
SWITCH='f6f314e9db56227459137669d87c44e9'
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))
assert 'uk_map' not in {x['name'].casefold() for x in reserved['reserved_textures']}
tx=[];protected={};audits=[]
def stage(tag,path,before,after):
 dest=OUT/tag/path.name;bak=OUT/('backup-'+tag)/path.name
 for p,b in [(dest,after),(bak,before)]:p.parent.mkdir(exist_ok=True);p.write_bytes(b)
 tx.append(dict(target=str(path),source=str(dest),backup=str(bak),before=sha(before),after=sha(after)))
def string(s):
 b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def arguments(uid):
 args=[('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',2)),('SI.VisualScripting.Int32VisualArg',struct.pack('<i',uid)),('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+string('club.UniqueId'))]
 return list(bytes([3])+b''.join(struct.pack('<I',len(string(t)+v))+string(t)+v for t,v in args))

for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 source=(folder/W).read_bytes();e=UnityPy.load(source)
 env={W:e};objs={W:{o.path_id:o for o in e.objects}};hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 changes={W:{}};documents=[]
 stadium=Doc(W,pid=-991100000000030);body=Doc(W,pid=-991100000000060)
 ratio_donor=Doc(W,name='ClubInfoReportBlock')
 gate_donor=Doc(W,name='TacticsConditionPercentageCell')
 gate_id=next(i for i,r in gate_donor.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement')
 original_stadium=copy.deepcopy(stadium.d);original_body=copy.deepcopy(body.d)
 original_text={i:copy.deepcopy(stadium.data(i)) for i,r in stadium.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText'}
 original_photo_binding=copy.deepcopy(stadium.data(1250)['Binding'])
 def ve(d,parent,name):
  return d.add(stadium,1004,parent,name)
 def box(d,i):
  d.a(i)['m_Classes']=[]
  d.st(i,[(131097,d.px(0)),(131096,d.px(0)),(262151,d.px(0)),(262148,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(458768,d.enum('visible'))])
 def absbox(d,i,left,top,width,height):
  box(d,i);d.st(i,[(131102,d.enum('absolute')),(131089,d.pct(left)),(131104,d.pct(top)),(131105,d.pct(width)),(131087,d.pct(height))])
 def colour(d,r,g,b,a=1):return d.val(4,dict(r=r,g=g,b=b,a=a))
 def aspect(d,parent,name):
  fit=d.add(ratio_donor,1261,parent,name);box(d,fit)
  d.data(fit).update(AspectMode=0,AspectMode_UxmlAttributeFlags=1,AspectRatio=f32(1080/1920),AspectRatio_UxmlAttributeFlags=1)
  d.st(fit,[(131102,d.enum('relative')),(131105,d.pct(100)),(131087,{'m_ValueType':1,'valueIndex':2}),(131074,d.enum('flex-start'))])
  return fit

 # The left panel spans both rows; the remaining right-side content keeps its ratios.
 body.st(1007,[(131102,body.enum('relative'))])
 for i in [1014,1015,1016,1017,1185,1187,1189,1191]:body.st(i,[(131081,body.enum('none'))])
 for i in [1177,1179,1183]:body.st(i,[(131105,body.pct(50)),(131074,body.enum('flex-end'))])
 body.move(1201,1007,0)
 body.st(1201,[(131102,body.enum('absolute')),(131089,body.px(0)),(131104,body.px(0)),(131105,body.pct(50)),(131087,body.pct(100)),(131097,body.px(0)),(131096,body.px(0)),(131084,body.num(0)),(131085,body.num(0))])
 body.save()

 # Native stadium context (club -> team -> selectedstadium) and all value bindings survive.
 for i in [1001,1004,1006,1010]:
  stadium.a(i)['m_Classes']=[]
  stadium.fill(i);stadium.st(i,[(262151,stadium.px(0)),(262148,stadium.px(0)),(131083,stadium.enum('column')),(458768,stadium.enum('hidden'))])
 stadium.st(1010,[(131102,stadium.enum('relative')),(458752,colour(stadium,0,0,0))])
 fit=aspect(stadium,1010,'TFUKMapWidthAspect')
 stadium.move(fit,1010,0)
 image=stadium.add(stadium,1250,fit,'TFUKMapBackground');absbox(stadium,image,0,0,100,100)
 no_binding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
 stadium.data(image).update(Binding=copy.deepcopy(no_binding),Binding_UxmlAttributeFlags=1,StaticImage={'m_AssetGUID':MAPGUID,'m_SubObjectName':'','m_SubObjectType':''},StaticImage_UxmlAttributeFlags=1,ScaleMode=2,ScaleMode_UxmlAttributeFlags=1,scaleMode=2,scaleMode_UxmlAttributeFlags=1,KeepImageWhileLoading=0,KeepImageWhileLoading_UxmlAttributeFlags=1)
 stadium.st(image,[(262153,stadium.enum('stretch-to-fill'))])
 markers=[]
 for row in mapping:
  uid=row['uid'];gate=stadium.add(gate_donor,gate_id,fit,'TFClubLocationUID'+str(uid));absbox(stadium,gate,0,0,100,100)
  stadium.data(gate).update(Binding={'m_kind':2,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':SWITCH},'m_inputs':{'m_variable':{'m_argumentBytes':arguments(uid)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},Binding_UxmlAttributeFlags=1,Preview={'Mask':1},Preview_UxmlAttributeFlags=1,AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1,BindDirectAsMask=0,BindDirectAsMask_UxmlAttributeFlags=1,InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1)
  empty=ve(stadium,gate,'TFLocationOtherClub'+str(uid));box(stadium,empty);stadium.size(empty,0,0)
  anchor=ve(stadium,gate,'TFLocationAnchor'+str(uid));absbox(stadium,anchor,row['x']/1920*100,row['y']/1080*100,0,0)
  ring=ve(stadium,anchor,'TFLocationCircle'+str(uid));box(stadium,ring);stadium.size(ring,14,14)
  stadium.st(ring,[(131102,stadium.enum('absolute')),(131089,stadium.px(-7)),(131104,stadium.px(-7)),(262147,stadium.px(100)),(458752,colour(stadium,.192,.847,.933))])
  hole=ve(stadium,ring,'TFLocationCircleInner'+str(uid));box(stadium,hole);stadium.size(hole,10,10)
  stadium.st(hole,[(131102,stadium.enum('absolute')),(131089,stadium.px(2)),(131104,stadium.px(2)),(262147,stadium.px(100)),(458752,colour(stadium,.02,.07,.09))])
  dot=ve(stadium,hole,'TFLocationCentre'+str(uid));box(stadium,dot);stadium.size(dot,4,4)
  stadium.st(dot,[(131102,stadium.enum('absolute')),(131089,stadium.px(3)),(131104,stadium.px(3)),(262147,stadium.px(100)),(458752,colour(stadium,1,1,1))])
  assert stadium.a(gate)['m_Children']==[{'rid':empty},{'rid':anchor}]
  markers.append(dict(uid=uid,gate=gate,anchor=anchor,x_percent=f32(row['x']/1920*100),y_percent=f32(row['y']/1080*100)))

 right=ve(stadium,1010,'TFClubLocationStadiumRight');absbox(stadium,right,55.37,3,42.4,94)
 stadium.st(right,[(131083,stadium.enum('column')),(458768,stadium.enum('hidden'))])
 title=stadium.add(stadium,1154,right,'TFClubLocationStadiumTitle');box(stadium,title)
 stadium.st(title,[(131105,stadium.pct(100)),(131087,stadium.px(28)),(65537,stadium.px(18)),(65536,colour(stadium,1,1,1)),(65546,stadium.enum('middle-left'))])
 photo_fit=aspect(stadium,right,'TFClubLocationPhotoAspect')
 stadium.move(1250,photo_fit);absbox(stadium,1250,0,0,100,100)
 stadium.data(1250).update(ScaleMode=2,ScaleMode_UxmlAttributeFlags=1,scaleMode=2,scaleMode_UxmlAttributeFlags=1,KeepImageWhileLoading=0,KeepImageWhileLoading_UxmlAttributeFlags=1)
 stadium.st(1250,[(262153,stadium.enum('scale-to-fit'))])
 stadium.move(1012,right)
 stadium.st(1012,[(131105,stadium.pct(100)),(131087,stadium.px(0)),(131096,stadium.px(0)),(131084,stadium.num(1)),(131085,stadium.num(1)),(131083,stadium.enum('column')),(262151,stadium.px(0)),(131098,stadium.px(12)),(458752,colour(stadium,0,0,0,0))])
 stadium.st(1016,[(131084,stadium.num(1)),(131085,stadium.num(1)),(131087,stadium.pct(100)),(131096,stadium.px(0)),(131083,stadium.enum('column')),(262151,stadium.px(0))])
 for i in [1023,1025,1027,1028,1033,1034]:
  stadium.st(i,[(131087,stadium.px(0)),(131096,stadium.px(20)),(131084,stadium.num(1)),(131085,stadium.num(1)),(131105,stadium.pct(100)),(131083,stadium.enum('row')),(262151,stadium.px(0)),(458752,colour(stadium,0,0,0,0))])
  children=stadium.a(i)['m_Children'];assert len(children)==2
  for j,ch in enumerate(children):
   stadium.st(ch['rid'],[(131105,stadium.pct(33 if j==0 else 67)),(131097,stadium.px(0)),(131084,stadium.num(0)),(131085,stadium.num(1))])
 for i in original_text:
  # Typography changes only; value and translation bindings are untouched.
  stadium.st(i,[(65537,stadium.px(14)),(65536,colour(stadium,1,1,1))])
  assert stadium.data(i)==original_text[i],('Native text changed',i)
 assert stadium.data(1250)['Binding']==original_photo_binding
 assert stadium.data(title)['TextBinding']['m_direct']['Path']['m_path']=='selectedstadium.Name'
 stadium.save()

 # Register the one external source map; native marker switches need no new textures.
 cp=(folder.parent if tag=='game' else folder)/'catalog.bin';cb=cp.read_bytes();cat=cm.Catalog(cb);keys=dict(cat.keys())
 assert MAPGUID not in keys
 records=list(cat.key_records);kind=next(cat.unpack(k,'2I')[0] for k,v in records if isinstance(cat.object(k),str))
 texture_type=next(cat.location(x[0])['raw'][6] for k,ls in keys.items() if isinstance(k,str) for x in cat.array(ls,'I')[:1] if cat.location(x[0])['type'][1]=='UnityEngine.Texture2D')
 ko=cat.add_string(MAPGUID);path=mapfile.as_posix();po=cat.add_string(path) if path.isascii() else cat.append(path.encode('utf-16le'),True)|0x80000000
 loc=cat.append(struct.pack('<7I',ko,po,cat.add_string('SI.Core.LocalAssetProvider'),cm.NULL,0,cm.NULL,texture_type))
 obj=cat.append(struct.pack('<IHH',ko,0,0));records.append((cat.append(struct.pack('<II',kind,obj)),cat.append(struct.pack('<I',loc),True)))
 struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*x) for x in records),True))
 cat=cm.Catalog(bytes(cat.data));meta=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle')
 guid_for=lambda pid:next(k for k,v in meta['m_Container'] if v['asset']==dict(m_FileID=0,m_PathID=pid))
 function_deps=cat.location(cat.locations(SWITCH)[0])['dependencies']
 for pid in [stadium.obj.path_id,body.obj.path_id,find(W,'ClubScreenOverviewBlock').path_id]:
  for loc in cat.locations(guid_for(pid)):
   deps=list(cat.location(loc)['dependencies'])
   for dep in function_deps:
    if dep not in deps:deps.append(dep)
   raw=b''.join(struct.pack('<I',d) for d in deps)
   struct.pack_into('<II',cat.data,loc+12,cat.append(raw,True),zlib.crc32(raw))
 # Validate function actual type, owning object and first dependency, plus map provider.
 function_path=folder/F if (folder/F).is_file() else Path(cfg['bundle_root'])/F
 fe=UnityPy.load(str(function_path));fo={o.path_id:o for o in fe.objects};fm=next(o.read_typetree() for o in fo.values() if o.type.name=='AssetBundle')
 fl=cat.location(cat.locations(SWITCH)[0]);assert fl['type'][1]=='SI.VisualScripting.VisualFunction' and F in cat.location(fl['dependencies'][0])['internal']
 fp=next(v['asset']['m_PathID'] for k,v in fm['m_Container'] if k==SWITCH);assert fo[fp].peek_name()=='BindIntComparisonToSwitch'
 # True comparison selects child 1; false selects child 0 (empty), including unmapped UID.
 ft=fo[fp].read_typetree();rr=[r for r in ft['references']['RefIds'] if r.get('data')];branch=next(r['data'] for r in rr if r['type']['class']=='GeneralVisualFunction_Branch')
 targets={tuple(r['data']['m_execInExecInput']['m_id']['m_idBytes']):r['data']['m_dataInIndex']['m_defaultSocketValue']['m_value'] for r in rr if r['type']['class']=='BindableSwitchElement_SetVisibleIndex'}
 assert targets[tuple(branch['m_execOutTrue']['m_destinationID']['m_idBytes'])]==1 and targets[tuple(branch['m_execOutFalse']['m_destinationID']['m_idBytes'])]==0
 cl=cat.location(cat.locations(MAPGUID)[0]);assert Path(cl['internal'])==mapfile and cl['type'][1]=='UnityEngine.Texture2D' and cl['provider']=='SI.Core.LocalAssetProvider'
 preload=[cat.location(x[0])['internal'] for x in cat.array(dict(cat.keys())['GameWorldVisualTreeAssetPreload'],'I')]
 for doc in [stadium,body]:
  guid=guid_for(doc.obj.path_id);assert guid in preload,(tag,guid,'missing preload')
  loc=cat.location(cat.locations(guid)[0]);assert W in cat.location(loc['dependencies'][0])['internal']
 # No objects added: reserved IDs and every unrelated object are preserved byte-for-byte.
 result=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(result).objects}
 assert set(check)==set(objs[W])
 for pid,h in hashes.items():
  if pid not in changes[W]:assert sha(check[pid].get_raw_data())==h,(tag,pid)
 for pid,d in changes[W].items():assert check[pid].read_typetree()==d,(tag,pid)
 after=bytes(cat.data)
 stage(tag,folder/W,source,result);stage(tag,cp,cb,after);hp=cp.with_suffix('.hash');stage(tag,hp,hp.read_bytes(),hashlib.md5(after).hexdigest().encode())
 for n in [F,'ui-backgrounds_assets_.bundle','ui-styles_assets_default.bundle','ui-tileslayouts_assets_all.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
  p=folder/n
  if p.is_file():protected[str(p)]=sha(p.read_bytes())
 audits.append(dict(target=tag,changed_objects=list(changes[W]),new_objects=0,unrelated_objects_byte_identical=True,markers=markers,live_stadium_text_bindings_unchanged=True,photo_binding_unchanged=True,static_stadium_values_added=False,marker_function_actual_type_owner_preload_verified=True,map_source_sha256=sha(mapbytes)))
 (OUT/(tag+'-stadium.json')).write_text(json.dumps(stadium.d,ensure_ascii=False,indent=2),'utf8')

protected[str(R/'reserved-texture-ids.json')]=sha((R/'reserved-texture-ids.json').read_bytes())
protected[str(R/'current-custom-textures.json')]=sha((R/'current-custom-textures.json').read_bytes())
protected[str(mapfile)]=sha(mapbytes)
manifest=dict(installed=False,runtime_verified=False,request='Club overview left half: UK map, UID-driven circle without name/leader, live native stadium photo and info',map_asset=str(mapfile),map_guid=MAPGUID,coordinate_clubs=20,coordinate_precision=coordinates['precision'],native_stadium_scope='club.MainTeam -> selectedstadium',photo_scope='club.MainTeam.KitHome -> kit2d_<clubid>_fmetstadium',limitations='Map coordinates cover supplied 20 clubs; others have no circle. Photos use existing initial-database club/stadium mapping; rebuilt or moved stadiums may need refreshed photo mapping.',protected_sha256=protected,audits=audits)
for name,data in [('transaction',tx),('manifest',manifest)]: (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (OUT/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'README.md').write_text('英国位置地图：一张1920×1080共用底图，左上对齐，原生WidthControlsHeight比例控件；20个UID原生整数比较开关选择圆圈，只有圆圈、无队名及横线。球队UID不匹配时全部圆圈隐藏。球场名称、城市、容量、年份、草皮、尺寸均沿用游戏原生selectedstadium绑定，无固定热刺值。球场照片沿用现有按当前club UID读取的图库绑定，存档里换新球场不保证照片与新球场同步。游戏与独立皮肤分别增量制作，保留右侧转会/新闻/荣誉/统计和其他对象。只改gameworld及catalog/hash；不新增包内纹理、不占用禁用ID。assets目录必须保留，catalog指向其中UK_map.png。退出游戏后install.ps1安装，restore.ps1带哈希保护，仅撤销本次改动。未启动游戏，显示与切队刷新待用户验证。','utf8')
(R/'current-club-location-map.json').write_text(json.dumps(dict(patch=str(OUT),installed=False,runtime_verified=False,uid_table=str(OUT/'uid-coordinates.json'),native_stadium_bindings=True,map_guid=MAPGUID),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(patch=str(OUT),files=len(tx),map_bytes=len(mapbytes),coordinate_clubs=20),ensure_ascii=False),flush=True)
