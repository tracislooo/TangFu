"""Adapt Comeback's native kit-image lookup to TF's existing stadium photo overlay."""
from pathlib import Path
import sys,json,ast,copy,hashlib,datetime,struct,importlib.util,xml.etree.ElementTree as ET,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
sys.stdout.reconfigure(encoding='utf8')
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
tree=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='write'],[]),'codec','exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('cm',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
A=R/'analysis/comeback-stadium-20261115';PACK=Path(json.loads((R/'current-club-overview.json').read_text('utf8'))['stadium_image_pack'])
SRC=Path(r'K:\桌面\FM27 Comeback Skin v1.8.3\Skin files')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';F='ui-visualfunctions_assets_all.bundle'
PID=-991100000000030;FGUID='7a35874b5cb0acb4d846df3f46c3a872'
sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
O=R/('club-stadium-comeback-'+stamp);O.mkdir()
clubs={x['id']:x for x in json.loads((A/'clubs-client.json').read_text('utf8'))}
teams=json.loads((A/'teams-server.json').read_text('utf8'));tb=(A/'server-frame-28.bin').read_bytes();sb=(A/'client-frame-22.bin').read_bytes();sn=struct.unpack_from('<I',sb,8)[0]
assert len(teams)==struct.unpack_from('<I',tb,8)[0] and teams[-1]['end']==len(tb)-9
stadiums={i:struct.unpack_from('<I',sb,12+38*i+31)[0] for i in range(sn)}
assert all(struct.unpack_from('<I',sb,12+38*i+27)[0]==i for i in stadiums)
photos={}
for row in ET.parse(PACK/'config.xml').findall('.//record[@to]'):
 m=re.fullmatch(r'graphics/pictures/stadium/(\d+)/background',row.get('to'))
 if not m:continue
 p=(PACK/row.get('from')).resolve();p=next((p.with_suffix(x) for x in ['.jpg','.png'] if p.with_suffix(x).is_file()),None)
 assert p and p.is_relative_to(PACK.resolve());photos[int(m[1])]=p
mapping={};coverage=[]
for t in teams:
 if t['id'] not in clubs or tb[t['start']]!=10 or t['stadium_index'] not in stadiums:continue
 sid=stadiums[t['stadium_index']]
 if sid not in photos:continue
 k=f"kit2d_{t['id']}_fmetstadium";assert k not in mapping;mapping[k]=photos[sid]
 coverage.append(dict(club_id=t['id'],club_name=clubs[t['id']]['names'][0],stadium_id=sid,key=k,image=str(photos[sid])))
assert {r['club_id']:r['stadium_id'] for r in coverage if r['club_id'] in [602,676,680,1708]}=={602:5114336,676:676,680:680,1708:1040}
assert len(mapping)>5000
(O/'photo-mapping.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),'utf8')
donor=UnityPy.load(str(SRC/W));dd=next(o.read_typetree() for o in donor.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='ClubInfoReportBlock')
ds=next(r['data'] for r in dd['references']['RefIds'] if r.get('data',{}).get('name')=='FMETStadiumPic')
binding=copy.deepcopy(ds['Binding']);assert binding['m_visualFunction']['m_target']['m_guid']==FGUID
raw=bytes(binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);pos=1;args=[]
assert raw[0]==6
for _ in range(raw[0]):
 n=struct.unpack_from('<I',raw,pos)[0];pos+=4;a=raw[pos:pos+n];pos+=n
 # Preserve the complete donor argument encoding; TF's active scope is lower-case club.
 a=a.replace(b'Club.MainTeam',b'club.MainTeam');args.append(a)
assert pos==len(raw) and args[4].endswith(struct.pack('<I',7)) and args[5].endswith(b'\x01\x0bfmetstadium')
binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(bytes([6])+b''.join(struct.pack('<I',len(a))+a for a in args))
tx=[];audits=[];protected={}
def stage(tag,p,b,a):
 dst=O/tag/p.name;bak=O/('backup-'+tag)/p.name
 for q,v in [(dst,a),(bak,b)]:q.parent.mkdir(exist_ok=True);q.write_bytes(v)
 tx.append(dict(target=str(p),source=str(dst),backup=str(bak),before=sha(b),after=sha(a)))
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 cp=(folder.parent if tag=='game' else folder)/'catalog.bin';hp=cp.with_suffix('.hash');cb=cp.read_bytes();hb=hp.read_bytes();cat=cm.Catalog(cb);keys=dict(cat.keys())
 original=(folder/W).read_bytes();env=UnityPy.load(original);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
 d=obs[PID].read_typetree();rs={r['rid']:r.get('data',{}) for r in d['references']['RefIds']}
 image=next(r for r in rs.values() if r.get('name')=='ClubOverviewStadiumPackPhoto');old=copy.deepcopy(image)
 image.update(Binding=copy.deepcopy(binding),Binding_UxmlAttributeFlags=1,ScaleMode=1,ScaleMode_UxmlAttributeFlags=1,KeepImageWhileLoading=0,KeepImageWhileLoading_UxmlAttributeFlags=1)
 # The existing picture layer already covers the full stadium module beneath its translucent text.
 assert rs[1010]['m_Children'][0]['rid']==1250 and image['uxmlAssetId']==old['uxmlAssetId']
 obs[PID].save_typetree(d);result=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(result).objects}
 assert set(check)==set(obs) and check[PID].read_typetree()==d
 assert all(sha(check[i].get_raw_data())==h for i,h in hashes.items() if i!=PID)
 meta=next(o.read_typetree() for o in obs.values() if o.type.name=='AssetBundle');vguid=next(k for k,v in meta['m_Container'] if v['asset']==dict(m_FileID=0,m_PathID=PID))
 fe=UnityPy.load(str(folder/F if (folder/F).exists() else Path(cfg['bundle_root'])/F));fm=next(o.read_typetree() for o in fe.objects if o.type.name=='AssetBundle')
 fid=next(v['asset']['m_PathID'] for k,v in fm['m_Container'] if k==FGUID)
 assert next(o for o in fe.objects if o.path_id==fid).read_typetree()['m_Name']=='DatabaseObjectWithColourReplacementFallback'
 for guid,owner,typ in [(FGUID,F,'SI.VisualScripting.VisualFunction'),(vguid,W,'UnityEngine.UIElements.VisualTreeAsset')]:
  loc=cat.location(cat.array(keys[guid],'I')[0][0]);assert loc['internal']==guid and loc['type'][1]==typ
  assert owner in cat.location(loc['dependencies'][0])['internal'],(tag,guid,loc)
 assert any(vguid==cat.location(x[0])['internal'] for x in cat.array(keys['GameWorldVisualTreeAssetPreload'],'I'))
 stage(tag,folder/W,original,result)
 records=list(cat.key_records);kind=next(cat.unpack(k,'2I')[0] for k,v in records if isinstance(cat.object(k),str))
 texture_type=next(cat.location(x[0])['raw'][6] for k,locs in keys.items() if isinstance(k,str) for x in cat.array(locs,'I')[:1] if cat.location(x[0])['type'][1]=='UnityEngine.Texture2D')
 provider=cat.add_string('SI.Core.LocalAssetProvider');added=0;skipped=0;locs_by_path={}
 for k,p in sorted(mapping.items()):
  if k in keys:
   loc=cat.location(cat.array(keys[k],'I')[0][0]);assert Path(loc['internal']).resolve()==p and loc['provider']=='SI.Core.LocalAssetProvider' and loc['type'][1]=='UnityEngine.Texture2D';skipped+=1;continue
  ko=cat.add_string(k)
  if p not in locs_by_path:
   path=p.as_posix();po=cat.add_string(path) if path.isascii() else cat.append(path.encode('utf-16le'),True)|0x80000000
   loc=cat.append(struct.pack('<7I',ko,po,provider,cm.NULL,0,cm.NULL,texture_type));locs_by_path[p]=cat.append(struct.pack('<I',loc),True)
  obj=cat.append(struct.pack('<IHH',ko,0,0));records.append((cat.append(struct.pack('<II',kind,obj)),locs_by_path[p]));added+=1
 struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*row) for row in records),True));after=bytes(cat.data);cc=cm.Catalog(after);kk=dict(cc.keys())
 assert cc.key_records[:len(cat.key_records)]==cat.key_records
 for k,p in mapping.items():
  loc=cc.location(cc.array(kk[k],'I')[0][0]);assert Path(loc['internal']).resolve()==p and loc['provider']=='SI.Core.LocalAssetProvider' and loc['type'][1]=='UnityEngine.Texture2D'
 stage(tag,cp,cb,after);stage(tag,hp,hb,hashlib.md5(after).hexdigest().encode('ascii'))
 for name in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle','ui-backgrounds_assets_.bundle','ui-styles_assets_default.bundle',F]:
  p=folder/name
  if p.is_file():protected[str(p)]=sha(p.read_bytes())
 audits.append(dict(target=tag,changed_objects=[PID],unrelated_objects_byte_identical=True,layout_and_trophies_unchanged=True,photo_keys_added=added,photo_keys_existing=skipped,native_function_guid=FGUID,stadium_template_guid=vguid,catalog_owner_type_preload_verified=True))
manifest=dict(installed=False,runtime_verified=False,request='Use Comeback native kit2d fmetstadium lookup for Club Overview stadium photos',photo_clubs=len(mapping),photo_stadiums=len(set(mapping.values())),source_pack=str(PACK),reference=str(SRC),protected_sha256=protected,audits=audits)
for name,data in [('transaction',tx),('manifest',manifest)]: (O/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (O/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(O/'README.md').write_text(f'''球场图片读取改为 Comeback 的 DatabaseObjectWithColourReplacementFallback，ResourceType=7，KitType=fmetstadium。沿用现有球场照片铺底、资料上层的布局。
原生 ResolveResourceID 已核对为 kit2d_{{club_id}}_fmetstadium；通过当前2700数据库 team表的球场索引关联现有球场ID照片，登记 {len(mapping)} 个俱乐部图片键（{len(set(mapping.values()))} 张不同照片）。图片不复制、不重新压缩。本地图片目录移动后需重建登记。
仅修改两套 gameworld 的 ClubOverviewStadiumStack 对象及各自 catalog/hash。奖杯、其他对象及受保护资源校验保持。游戏运行时不安装；install.ps1 必须正常退出游戏后运行。restore.ps1 受哈希保护，仅撤回本次，后续资源变化不能整包覆盖。
覆盖基于本地初始数据库，存档后新建或更换球场不一定与初始对应；无照片不显示图片。未启动游戏，实际显示待用户确认。
''','utf8')
(R/'current-club-stadium-comeback.json').write_text(json.dumps(dict(patch=str(O),installed=False,runtime_verified=False,photo_clubs=len(mapping),photo_stadiums=len(set(mapping.values())),binding='club.MainTeam.KitHome -> Kit2DFront/fmetstadium -> local stadium JPG/PNG',source_pack=str(PACK)),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(patch=str(O),files=len(tx),photo_clubs=len(mapping),photo_stadiums=len(set(mapping.values())),audits=audits),ensure_ascii=False))
