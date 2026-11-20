"""Add the existing stadium texture above the start-screen 3D scene, below its menu."""
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,subprocess,sys
from pathlib import Path

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.helpers import TypeTreeHelper

AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
GAME=AA/'StandaloneWindows64'
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
INTRO='ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle'
BG='ui-backgrounds_assets_common.bundle'
WORLD='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GLOBAL='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PID=-910000000000145
sha=lambda b:hashlib.sha256(b).hexdigest()

def running():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 return bool(p.stdout.strip())

def install(out,restore=False):
 m=json.loads((out/'manifest.json').read_text('utf8'))
 if running():
  print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(out)}));return
 for path,h in m['protected_sha256'].items():assert sha(Path(path).read_bytes())==h,('Related resource changed',path)
 pending={};previous={}
 for item in m['install_files']:
  path=Path(item['target']);old=path.read_bytes() if path.exists() else None
  wanted_hash=item['after_sha256'] if restore else item['before_sha256']
  assert (sha(old) if old is not None else None)==wanted_hash,('Target version changed',path)
  source=item['backup'] if restore else item['source']
  data=(out/source).read_bytes() if source else None
  expected=item['before_sha256'] if restore else item['after_sha256']
  assert (sha(data) if data is not None else None)==expected
  pending[path]=data;previous[path]=old
 try:
  for path,data in pending.items():
   if data is None:path.unlink()
   else:
    temp=path.with_name(path.name+'.kunshan-tmp');temp.write_bytes(data);temp.replace(path)
   assert (path.read_bytes() if path.exists() else None)==data
  for path,h in m['protected_sha256'].items():assert sha(Path(path).read_bytes())==h
 except BaseException:
  for path,data in previous.items():
   if data is None:
    if path.exists():path.unlink()
   else:path.write_bytes(data)
  raise
 m.update(installed=not restore,installed_hash_verified=not restore)
 (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 print(json.dumps({'installed':not restore,'restored':restore,'output':str(out),'texture':'kunshan stadium','path_id':str(PID),'runtime_verified':False},ensure_ascii=False))

if len(sys.argv)>1 and sys.argv[1] in ['--apply','--restore']:
 install(Path(sys.argv[2]),sys.argv[1]=='--restore');sys.exit(0)

oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'ui-validator','exec'))
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)

before={p:p.read_bytes() if p.exists() else None for p in [GAME/INTRO,SKIN/INTRO,AA/'catalog.bin',AA/'catalog.hash',SKIN/'catalog.bin',SKIN/'catalog.hash',R/'AGENTS.md']}
assert before[GAME/INTRO] is not None
assert before[SKIN/INTRO] is None or before[GAME/INTRO]==before[SKIN/INTRO]
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in [folder/BG,folder/WORLD,folder/GLOBAL,folder/'ui-visualfunctions_assets_all.bundle',folder/'ui-tileslayouts_assets_all.bundle'] if p.exists()}
protected.update({p:sha(p.read_bytes()) for p in [R/'reserved-texture-ids.json',R/'current-custom-textures.json']})
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in reserved};banned_names={t['name'].lower() for t in reserved}
assert PID not in banned
bgb=(GAME/BG).read_bytes();be=UnityPy.load(bgb);ba=be.assets[0];bo=ba.objects
assert len(registry['textures'])==176
for t in registry['textures']:
 obj=bo[int(t['path_id'])];assert obj.type.name=='Texture2D' and obj.peek_name()==t['name']
 assert sha(obj.get_raw_data())==t['texture_sha256'],t['name']
assert bo[PID].peek_name()=='kunshan stadium'

def no_retired(af):
 assert banned.isdisjoint(af.objects)
 for obj in af.objects.values():
  if obj.type.name=='Texture2D':assert obj.peek_name().lower() not in banned_names
 meta=next(o.read_typetree() for o in af.objects.values() if o.type.name=='AssetBundle')
 assert all(k.lower() not in banned_names and v['asset']['m_PathID'] not in banned for k,v in meta['m_Container'])
 assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
no_retired(ba)

e=UnityPy.load(before[GAME/INTRO]);a=e.assets[0];hashes={i:sha(o.get_raw_data()) for i,o in a.objects.items()}
obj=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MainMenu')
d=obj.read_typetree();original=copy.deepcopy(d);sid=d['inlineSheet']['m_PathID'];s=a.objects[sid].read_typetree();original_s=copy.deepcopy(s)
rr={r['rid']:r for r in d['references']['RefIds']}
assert not any(r.get('data',{}).get('name')=='KunshanStadiumModelOverlay' for r in rr.values())
assert rr[1001]['data']['m_FullTypeName']=='SI.Bindable.BindingRoot'
ve=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement')
node=copy.deepcopy(ve);data=copy.deepcopy(rr[ve['data']['m_SerializedData']['rid']])
nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
node['rid']=nr;data['rid']=nr+1
node['data'].update(m_Id=ni,m_Parent={'rid':1001},m_Children=[],m_RuleIndex=len(s['m_Rules']),m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SerializedData={'rid':nr+1})
data['data'].update(uxmlAssetId=ni,name='KunshanStadiumModelOverlay',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,focusable=0,focusable_UxmlAttributeFlags=1)
d['references']['RefIds'].extend([node,data]);rr[1001]['data']['m_Children'].insert(0,{'rid':nr})
worlds={n:UnityPy.load(str(GAME/n)).assets[0] for n in [WORLD,GLOBAL]}
matches=[i+1 for i,x in enumerate(a.externals) if x.path==f'archive:/{ba.name}/{ba.name}']
if not matches:
 ext=next(x for x in worlds[WORLD].externals if x.path==f'archive:/{ba.name}/{ba.name}')
 a.externals.append(copy.copy(ext));matches=[len(a.externals)]
assert len(matches)==1
ptr={'m_FileID':matches[0],'m_PathID':PID}
def value(typ,v):
 s[poolmap[typ]].append(v);return {'m_ValueType':typ,'valueIndex':len(s[poolmap[typ]])-1}
def px(v):return value(3,{'unit':1,'value':float(v)})
def en(v):return value(7,v)
props=[(131102,en('absolute')),(131089,px(0)),(131103,px(0)),(131104,px(0)),(131080,px(0)),(458753,value(6,ptr)),(262153,en('scale-and-crop')),(458767,value(2,1.0))]
s['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':[{'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':[v]} for pid,v in props],'line':-1})
element_count=validate_ui(d,s)
oldrr={r['rid']:r for r in original['references']['RefIds']}
for rid,old in oldrr.items():
 actual=copy.deepcopy(rr[rid])
 if rid==1001:actual['data']['m_Children']=actual['data']['m_Children'][1:]
 assert actual==old,('Original menu record changed',rid)
assert s['m_Rules'][:-1]==original_s['m_Rules']
for key,v in original_s.items():
 if isinstance(v,list):assert s[key][:len(v)]==v
 else:assert s[key]==v
obj.save_typetree(d);a.objects[sid].save_typetree(s)
outbytes=e.file.save(packer='lz4');saved=UnityPy.load(outbytes);sa=saved.assets[0]
assert set(sa.objects)==set(a.objects)
for i,h in hashes.items():
 if i in [obj.path_id,sid]:assert sa.objects[i].read_typetree()=={obj.path_id:d,sid:s}[i]
 else:assert sha(sa.objects[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(sa.objects[obj.path_id].read_typetree(),sa.objects[sid].read_typetree());no_retired(sa)
linked=UnityPy.load(outbytes,bgb);la=next(x for x in linked.assets if x.name==sa.name)
resolved=PPtr(m_FileID=ptr['m_FileID'],m_PathID=PID,assetsfile=la).deref()
assert resolved.peek_name()=='kunshan stadium' and sha(resolved.get_raw_data())==sha(bo[PID].get_raw_data())

outputs={GAME/INTRO:outbytes,SKIN/INTRO:outbytes};catalog_reports=[]
for folder in [AA,SKIN]:
 path=folder/'catalog.bin';raw=before[path];c=cm.Catalog(raw);keys=c.keys();locs={loc for _,p in keys for (loc,) in c.array(p,'I')}
 def bundleloc(name):
  found=[loc for loc in locs if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+name)]
  assert len(found)==1,(name,found);return found[0]
 own=bundleloc(INTRO);bg=bundleloc(BG);fixes=[];arrays={}
 for loc in sorted(locs):
  fields=c.unpack(loc,'7I');deps=c.location(loc)['dependencies']
  if own not in deps or bg in deps:continue
  if fields[3] not in arrays:arrays[fields[3]]=c.append(struct.pack('<'+'I'*(len(deps)+1),*(deps+[bg])),True)
  struct.pack_into('<I',c.data,loc+12,arrays[fields[3]]);fixes.append(loc)
 cb=bytes(c.data);cc=cm.Catalog(cb);oc=cm.Catalog(raw);assert cc.keys()==keys
 for loc in locs:
  old=oc.location(loc);new=cc.location(loc)
  assert all(new[k]==old[k] for k in ['primary','internal','provider','type'])
  assert new['dependencies']==old['dependencies']+([bg] if loc in fixes else [])
 meta=next(o.read_typetree() for o in sa.objects.values() if o.type.name=='AssetBundle')
 main_guid=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':obj.path_id})
 assert any(cc.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' for loc in cc.locations(main_guid))
 for loc in cc.locations(main_guid):
  v=cc.location(loc);assert v['dependencies'][0]==own and bg in v['dependencies']
 # Verify every existing custom VTA and VisualFunction against actual current objects.
 audit=[]
 for name,wa in worlds.items():
  own_world=bundleloc(name);meta=next(o.read_typetree() for o in wa.objects.values() if o.type.name=='AssetBundle')
  for key,entry in meta['m_Container']:
   if not re.fullmatch('[0-9a-f]{32}',key) or entry['asset']['m_FileID']!=0:continue
   wo=wa.objects.get(entry['asset']['m_PathID'])
   if wo is None or not (-1000000000000000<wo.path_id<-900000000000000) or wo.type.name!='MonoBehaviour':continue
   tree=wo.read_typetree();typ='SI.VisualScripting.VisualFunction' if 'm_nodes' in tree else ('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in tree else None)
   if not typ:continue
   for loc in cc.locations(key):
    v=cc.location(loc);assert v['type'][1]==typ and v['dependencies'][0]==own_world and bg in v['dependencies'],(key,v)
   audit.append({'guid':key,'name':wo.peek_name(),'type':typ,'bundle':name,'path_id':str(wo.path_id)})
 assert len(audit)>=82
 if cb!=raw:
  outputs[path]=cb;outputs[folder/'catalog.hash']=hashlib.md5(cb).hexdigest().encode('ascii')
 catalog_reports.append({'catalog':str(path),'dependency_locations_updated':len(fixes),'main_menu_guid':main_guid,'main_menu_type_and_background_dependency_verified':True,'custom_resources_checked':audit})

instructions=before[R/'AGENTS.md'].decode('utf8')
assert '仅入 backgrounds，未绑定界面。' in instructions
outputs[R/'AGENTS.md']=instructions.replace('仅入 backgrounds，未绑定界面。','保留在 backgrounds；Start screen 的 MainMenu 已引用该纹理，新增全屏图片层覆盖人物模型，菜单保留在图片上层。').encode('utf8')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('start-screen-kunshan-overlay-'+stamp);out.mkdir();(out/'templates').mkdir()
(out/'templates/MainMenu.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
(out/'templates/MainMenu-style.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
items=[]
for path,content in outputs.items():
 tag='workspace' if path.parent==R else ('game' if path.parent in [AA,GAME] else 'skin')
 source=Path(tag)/path.name;(out/source).parent.mkdir(exist_ok=True);(out/source).write_bytes(content)
 backup=Path('backup-'+tag)/path.name if before[path] is not None else None
 if backup:(out/backup).parent.mkdir(exist_ok=True);(out/backup).write_bytes(before[path])
 items.append({'target':str(path),'source':source.as_posix(),'backup':backup.as_posix() if backup else None,'before_sha256':sha(before[path]) if before[path] is not None else None,'after_sha256':sha(content)})
for path,b in before.items():assert (path.read_bytes() if path.exists() else None)==b
for path,h in protected.items():assert sha(path.read_bytes())==h
for path,b in before.items():
 if path not in outputs and b is not None:protected[path]=sha(b)
report={'installed':False,'runtime_verified':False,'template':'MainMenu','template_path_id':str(obj.path_id),'style_path_id':str(sid),'texture':'kunshan stadium','texture_path_id':str(PID),'texture_pointer':ptr,'layer':'3D scene < KunshanStadiumModelOverlay < all original MainMenu children','size':'absolute fill (all four insets 0), scale-and-crop','picking_mode':'Ignore','new_assets_or_texture_ids':0,'all_original_menu_records_preserved':True,'unrelated_bundle_objects_unchanged':len(hashes)-2,'active_176_textures_hash_verified':True,'retired_70_absent_from_objects_container_preload':True,'catalog_audits':catalog_reports,'install_files':items,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps({'passed':True,'serialization_roundtrip':True,'menu_element_count':element_count,'menu_bindings_and_styles_preserved':True,'background_reference_resolves_to_latest_bundle':True,'addressables_main_menu_and_existing_82_custom_resources_verified':True,'all_176_textures_unchanged':True,'reserved_70_absent':True,'runtime_verified':False},indent=2),'utf8')
for action,flag in [('install','--apply'),('restore','--restore')]:
 script="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(Path(__file__).resolve())+"' '"+flag+"' $PSScriptRoot\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n"
 (out/(action+'.ps1')).write_text(script,'utf-8-sig')
(out/'说明.txt').write_text('Start screen：新增 KunshanStadiumModelOverlay 全屏图片层，位于人物模型之上、原生菜单之下。\n直接引用当前 backgrounds 内 kunshan stadium (-910000000000145)，等比裁切铺满，忽略鼠标拾取。\n保留全部菜单节点、事件、绑定、可见条件和样式；不修改背景包、卡面、评分公式或禁用清单。\n游戏与皮肤包同步安装；catalog 按实际情况补齐依赖，本次所需 backgrounds 依赖已存在，两份 catalog 均未修改。\ninstall.ps1 安装；restore.ps1 校验版本后回退。需退出游戏；实际游戏显示待重启确认。\n','utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'catalog_dependency_updates':[x['dependency_locations_updated'] for x in catalog_reports],'existing_custom_resources_checked':[len(x['custom_resources_checked']) for x in catalog_reports]},ensure_ascii=False),flush=True)
install(out)
