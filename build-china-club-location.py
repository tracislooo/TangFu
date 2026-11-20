from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,uuid,zlib
R=Path(r'G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
OUT=R/('china-club-location-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'templates').mkdir();(OUT/'assets').mkdir()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
def extract(file,names):
 t=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
oldwrite=TypeTreeHelper.write_value
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
rows=json.loads((R/'exports/China-top-two-leagues-2026/club-coordinates.json').read_text('utf8'))['clubs'];rows=[r for r in rows if r['uid']]
assert len(rows)==31
mapfile=OUT/'assets/map_China_ninedash.png';mapfile.write_bytes((R/'exports/China-top-two-leagues-2026/map_China_ninedash.png').read_bytes());guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/club-location/map-china/ninedash-v1').hex
tx=[];audits=[]
def stage(tag,path,before,after):
 for p,b in [(OUT/tag/path.name,after),(OUT/('backup-'+tag)/path.name,before)]:p.parent.mkdir(exist_ok=True);p.write_bytes(b)
 tx.append(dict(target=str(path),source=str(OUT/tag/path.name),backup=str(OUT/('backup-'+tag)/path.name),before=sha(before),after=sha(after)))
def arguments(uid,path):
 def s(x):
  b=x.encode();assert len(b)<128;return bytes([len(b)])+b
 args=[('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',2)),('SI.VisualScripting.Int32VisualArg',struct.pack('<i',uid)),('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+s(path))]
 return list(bytes([3])+b''.join(struct.pack('<I',len(s(t)+v))+s(t)+v for t,v in args))
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 source=(folder/W).read_bytes();e=UnityPy.load(source);env={W:e};objs={W:{o.path_id:o for o in e.objects}};hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()};changes={W:{}};documents=[]
 d=Doc(W,pid=-991100000000030);fit=d.named('TFUKMapWidthAspect');uk=d.named('TFUKMapBackground');donor=d.named('TFClubLocationUID728')
 def clone(i,parent,name,children=False):
  oldchildren=list(d.a(i)['m_Children']);rule=d.a(i)['m_RuleIndex'];n=d.add(d,i,parent,name);d.a(n)['m_RuleIndex']=rule
  if children:
   for ch in oldchildren:clone(ch['rid'],n,d.data(ch['rid']).get('name','')+'Copy',True)
  return n
 gate=clone(donor,fit,'TFMapCountryChina110');d.move(gate,fit,0)
 d.data(gate)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=arguments(110,'club.nation.UniqueId')
 d.move(uk,gate);cn=clone(uk,gate,'TFChinaMapBackground');d.data(cn)['StaticImage']['m_AssetGUID']=guid
 assert d.a(gate)['m_Children']==[{'rid':uk},{'rid':cn}]
 for r in rows:
  uid=r['uid'];g=clone(donor,fit,'TFChinaClubLocationUID'+str(uid),True)
  d.data(g)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=arguments(uid,'club.UniqueId')
  anchor=d.a(g)['m_Children'][1]['rid'];d.st(anchor,[(131089,d.pct(struct.unpack('<f',struct.pack('<f',r['x']/1920*100))[0])),(131104,d.pct(struct.unpack('<f',struct.pack('<f',r['y']/1080*100))[0]))])
 d.save();out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};assert set(check)==set(objs[W])
 for i,h in hashes.items():
  if i not in changes[W]:assert sha(check[i].get_raw_data())==h
 for i,v in changes[W].items():assert check[i].read_typetree()==v
 cp=(folder.parent if tag=='game' else folder)/'catalog.bin';cb=cp.read_bytes();cat=cm.Catalog(cb);keys=dict(cat.keys());assert guid not in keys
 records=list(cat.key_records);kind=next(cat.unpack(k,'2I')[0] for k,v in records if isinstance(cat.object(k),str));tt=next(cat.location(x[0])['raw'][6] for k,ls in keys.items() if isinstance(k,str) for x in cat.array(ls,'I')[:1] if cat.location(x[0])['type'][1]=='UnityEngine.Texture2D')
 ko=cat.add_string(guid);path=mapfile.as_posix();po=cat.add_string(path) if path.isascii() else cat.append(path.encode('utf-16le'),True)|0x80000000
 loc=cat.append(struct.pack('<7I',ko,po,cat.add_string('SI.Core.LocalAssetProvider'),cm.NULL,0,cm.NULL,tt));obj=cat.append(struct.pack('<IHH',ko,0,0));records.append((cat.append(struct.pack('<II',kind,obj)),cat.append(struct.pack('<I',loc),True)));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*x) for x in records),True));new=cm.Catalog(bytes(cat.data));assert Path(new.location(new.locations(guid)[0])['internal'])==mapfile
 stage(tag,folder/W,source,out);stage(tag,cp,cb,bytes(cat.data));hp=cp.with_suffix('.hash');stage(tag,hp,hp.read_bytes(),hashlib.md5(bytes(cat.data)).hexdigest().encode())
 audits.append(dict(target=tag,changed_objects=list(changes[W]),china_uid_count=len(rows),nation_path='club.nation.UniqueId',nation_id=110,unchanged_objects_verified=True))
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps(dict(installed=False,runtime_verified=False,protected_sha256={},audits=audits,china_map_guid=guid,china_map=str(mapfile),uid_unresolved=['宁波俱乐部']),ensure_ascii=False,indent=2),'utf8');(OUT/'uid-coordinates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
(OUT/'restore.ps1').write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot --restore\nif($LASTEXITCODE -ne 0){throw 'Restore failed'}\n",encoding='utf-8-sig')
print('PATCH='+str(OUT),flush=True)

