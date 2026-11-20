"""Rebase the live map module into the AI club page, retaining native page scopes."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
previous=json.loads((R/'current-club-location-map.json').read_text('utf8'));previous_patch=Path(previous['patch'])
OUT=R/('ai-club-location-map-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();(OUT/'templates').mkdir()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
F='ui-visualfunctions_assets_all.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
oldwrite=TypeTreeHelper.write_value
def extract(file,names):
 t=ast.parse((R/file).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
tx=[];protected={};audits=[]
def stage(tag,path,before,after):
 dest=OUT/tag/path.name;backup=OUT/('backup-'+tag)/path.name
 for p,b in [(dest,after),(backup,before)]:p.parent.mkdir(exist_ok=True);p.write_bytes(b)
 tx.append(dict(target=str(path),source=str(dest),backup=str(backup),before=sha(before),after=sha(after)))
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 source=(folder/W).read_bytes();e=UnityPy.load(source)
 env={W:e};objs={W:{o.path_id:o for o in e.objects}};hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()};changes={W:{}};documents=[]
 body=Doc(W,name='ClubSiteBlock');player=Doc(W,pid=-991100000000060);stadium=Doc(W,pid=-991100000000030)
 before_body=copy.deepcopy(body.d);before_stadium=copy.deepcopy(stadium.d)
 # Keep the native club -> current-page team remapper. No human-manager context is added.
 mapping_before=copy.deepcopy(body.data(1007))
 # Suppress original About and News columns and their dividers.
 for i in [1015,1016,1017,1019,1020]:body.st(i,[(131081,body.enum('none'))])
 body.st(1007,[(131083,body.enum('row')),(131087,body.pct(100)),(131096,body.px(0)),(131097,body.px(0)),(131105,body.pct(100)),(131084,body.num(1)),(131085,body.num(1)),(262151,body.px(0)),(458768,body.enum('hidden'))])
 module=body.add(player,1201,1007,'AIClubCurrentLocationAndStadium');body.using(player,'ClubOverviewStadiumStack');body.move(module,1007,0)
 body.st(module,[(131102,body.enum('relative')),(131105,body.pct(50)),(131087,body.pct(100)),(131096,body.px(0)),(131097,body.px(0)),(131084,body.num(0)),(131085,body.num(0)),(458768,body.enum('hidden'))])
 right=body.add(body,1014,1007,'AIClubRightSquadAndTransfers');body.a(right)['m_Classes']=[]
 body.st(right,[(131083,body.enum('row')),(131105,body.pct(50)),(131087,body.pct(100)),(131096,body.px(0)),(131097,body.px(0)),(131084,body.num(0)),(131085,body.num(1)),(458768,body.enum('hidden'))])
 body.move(1014,right)
 divider=body.add(body,1015,right,'AIClubSquadTransferDivider');body.using(body,'layout-divider-solid-vertical')
 body.st(divider,[(131105,body.px(1)),(131087,body.pct(100)),(131084,body.num(0)),(131085,body.num(0)),(131093,body.px(8)),(131090,body.px(8))])
 body.move(1018,right)
 for i in [1014,1018]:
  body.st(i,[(131105,body.px(0)),(131087,body.pct(100)),(131096,body.px(0)),(131097,body.px(0)),(131084,body.num(1)),(131085,body.num(1)),(458768,body.enum('hidden'))])
 assert body.data(1007)==mapping_before
 # Verify every pre-existing serialized binding remains byte-for-byte equivalent.
 original_refs={r['rid']:r.get('data',{}) for r in before_body['references']['RefIds']}
 for i,r in body.r.items():
  if i in original_refs and 'uxmlAssetId' in original_refs[i]:assert r.get('data',{})==original_refs[i],('Original AI serialized data changed',i)
 body.save()

 gates=[]
 for i,r in stadium.r.items():
  a=r.get('data',{})
  if 'm_SerializedData' not in a:continue
  sd0=stadium.data(i);name=sd0.get('name','')
  if not name.startswith('TFClubLocationUID'):continue
  uid=int(name.removeprefix('TFClubLocationUID'));raw=bytes(sd0['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
  assert raw.endswith(b'club.UniqueId') and sd0['Binding']['m_visualFunction']['m_target']['m_guid']=='f6f314e9db56227459137669d87c44e9'
  p=1;args=[]
  for _ in range(raw[0]):n=struct.unpack_from('<I',raw,p)[0];p+=4;args.append(raw[p:p+n]);p+=n
  assert struct.unpack('<i',args[0][-4:])[0]==2 and struct.unpack('<i',args[1][-4:])[0]==uid
  children=stadium.a(i)['m_Children'];assert len(children)==2
  assert stadium.data(children[0]['rid'])['name']=='TFLocationOtherClub'+str(uid)
  assert stadium.data(children[1]['rid'])['name']=='TFLocationAnchor'+str(uid)
  # Default to the empty false branch and instantiate only the selected branch.
  sd0.update(AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1,Preview={'Mask':1},Preview_UxmlAttributeFlags=1,BindDirectAsMask=0,BindDirectAsMask_UxmlAttributeFlags=1,InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1)
  gates.append(dict(uid=uid,gate=i,empty=children[0]['rid'],point=children[1]['rid']))
 assert len(gates)==20
 oldrs={r['rid']:r.get('data',{}) for r in before_stadium['references']['RefIds']}
 changed_gate_sd={stadium.a(g['gate'])['m_SerializedData']['rid'] for g in gates}
 for i,r in stadium.r.items():
  if i not in changed_gate_sd:assert r.get('data',{})==oldrs[i],('Unexpected stadium data change',i)
 stadium.save()

 cp=(folder.parent if tag=='game' else folder)/'catalog.bin';cb=cp.read_bytes();cat=cm.Catalog(cb)
 meta=next(o.read_typetree() for o in objs[W].values() if o.type.name=='AssetBundle')
 key=lambda pid:next(k for k,v in meta['m_Container'] if v['asset']==dict(m_FileID=0,m_PathID=pid))
 stadium_guid=key(stadium.obj.path_id);body_guid=key(body.obj.path_id)
 assert next(u for u in body.d['m_Usings'] if u['alias']=='ClubOverviewStadiumStack')['path']==stadium_guid
 dependencies=cat.location(cat.locations(stadium_guid)[0])['dependencies']
 for loc in cat.locations(body_guid):
  deps=list(cat.location(loc)['dependencies'])
  for dep in dependencies:
   if dep not in deps:deps.append(dep)
  data=b''.join(struct.pack('<I',d) for d in deps);struct.pack_into('<II',cat.data,loc+12,cat.append(data,True),zlib.crc32(data))
 for guid in [stadium_guid,body_guid]:
  loc=cat.location(cat.locations(guid)[0]);assert loc['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and W in cat.location(loc['dependencies'][0])['internal']
 preload=[cat.location(x[0])['internal'] for x in cat.array(dict(cat.keys())['GameWorldVisualTreeAssetPreload'],'I')]
 assert stadium_guid in preload and body_guid in preload
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};assert set(check)==set(objs[W])
 for i,h in hashes.items():
  if i not in changes[W]:assert sha(check[i].get_raw_data())==h,(tag,i)
 for i,d in changes[W].items():assert check[i].read_typetree()==d,(tag,i)
 # All existing map keys, photos and function locations remain in this catalog.
 oldcat=cm.Catalog(cb);oldkeys=dict(oldcat.keys());newkeys=dict(cat.keys());assert set(oldkeys)==set(newkeys)
 assert cat.locations(previous['map_guid'])==oldcat.locations(previous['map_guid'])
 for uid in [667,728,602,680]:assert 'kit2d_'+str(uid)+'_fmetstadium' in newkeys
 stage(tag,folder/W,source,out);stage(tag,cp,cb,bytes(cat.data));hp=cp.with_suffix('.hash');stage(tag,hp,hp.read_bytes(),hashlib.md5(bytes(cat.data)).hexdigest().encode())
 for n in [F,'ui-backgrounds_assets_.bundle','ui-styles_assets_default.bundle','ui-tileslayouts_assets_all.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
  p=folder/n
  if p.is_file():protected[str(p)]=sha(p.read_bytes())
 cases={str(uid):[g['uid'] for g in gates if uid==g['uid']] for uid in [667,728,602,99999999]}
 assert cases=={'667':[667],'728':[728],'602':[602],'99999999':[]}
 audits.append(dict(target=tag,changed_objects=list(changes[W]),ai_native_bindings_preserved=True,player_page_structure_unchanged=True,shared_marker_defaults_empty=True,always_instantiate=False,uid_cases=cases,gates=gates,unrelated_objects_byte_identical=True,ai_body_guid=body_guid,stadium_guid=stadium_guid))

for p in [R/'reserved-texture-ids.json',R/'current-custom-textures.json',Path(json.loads((previous_patch/'manifest.json').read_text('utf8'))['map_asset'])]:protected[str(p)]=sha(p.read_bytes())
manifest=dict(installed=False,runtime_verified=False,request='AI club page: left half live club map/stadium, right half native squad+transfers; About/News removed. Shared map shows only current UID marker.',protected_sha256=protected,audits=audits,map_dependency=str(previous_patch),coordinate_clubs=20,native_stadium_bindings=True,limitations='Only UK map and existing 20-club coordinate table are available; other clubs have no marker; photo mapping follows existing club UID library.')
for name,data in [('transaction',tx),('manifest',manifest)]: (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (OUT/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(OUT/'README.md').write_text('AI球队原生ClubSiteBlock改为左半地图+球场、右半原生阵容和转会各半；取消关于俱乐部及新闻。原生club→team映射和阵容/转会绑定不变。左侧复用已有ClubOverviewStadiumStack，所有球场值及图库读取继续以当前页面club为上下文，没有固定热刺/玩家球队数据。共用定位开关改为默认空分支、AlwaysInstantiate=0，20队UID逐个匹配，仅当前UID圆圈可见；未匹配时无圆圈。位置表已自动对应UID，不需手工配对。地图资源保留于上一轮补丁assets目录，不可删除。游戏与独立皮肤分别基于当前文件增量修改；restore.ps1仅撤销本轮并保留上一轮玩家页地图。未启动游戏，切页及刷新结果待用户确认。','utf8')
(OUT/'previous-state.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8')
(R/'current-ai-club-location-map.json').write_text(json.dumps(dict(patch=str(OUT),installed=False,runtime_verified=False),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(patch=str(OUT),files=len(tx),audits=[{k:v for k,v in a.items() if k!='gates'} for a in audits]),ensure_ascii=False),flush=True)
