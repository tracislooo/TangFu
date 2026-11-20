"""Keep the native promo video and add the existing TFWX texture on its right."""
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.helpers import TypeTreeHelper
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
GAME=AA/'StandaloneWindows64';SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
INTRO='ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle';BG='ui-backgrounds_assets_common.bundle'
WORLD='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';GLOBAL='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PID=-910000000000150;RT='073b324505f39d44796109e923324e46'
sha=lambda b:hashlib.sha256(b).hexdigest()
def running():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 return bool(p.stdout.strip())
def install(out,restore=False):
 m=json.loads((out/'manifest.json').read_text('utf8'))
 if running():
  print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(out)}));return
 for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('Related resource changed',p)
 pending={};old={}
 for x in m['install_files']:
  p=Path(x['target']);b=p.read_bytes();assert sha(b)==x['after_sha256' if restore else 'before_sha256'],('Target version changed',p)
  data=(out/x['backup' if restore else 'source']).read_bytes();assert sha(data)==x['before_sha256' if restore else 'after_sha256']
  old[p]=b;pending[p]=data
 try:
  for p,b in pending.items():
   temp=p.with_name(p.name+'.tfwx-tmp');temp.write_bytes(b);temp.replace(p);assert p.read_bytes()==b
  for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('Protected file changed',p)
 except BaseException:
  for p,b in old.items():p.write_bytes(b)
  raise
 m.update(installed=not restore,installed_hash_verified=not restore,installed_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).isoformat())
 (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 print(json.dumps({'installed':not restore,'restored':restore,'output':str(out),'video_size':[520,112],'TFWX_slot':[120,112],'runtime_verified':False},ensure_ascii=False))
if len(sys.argv)>1 and sys.argv[1] in ['--install','--restore']:
 install(Path(sys.argv[2]),sys.argv[1]=='--restore');sys.exit(0)

oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
note=R/'启动页球场覆盖层与横幅动图-更新重做说明.md';agents=R/'AGENTS.md'
before={p:p.read_bytes() for p in [GAME/INTRO,SKIN/INTRO,AA/'catalog.bin',AA/'catalog.hash',SKIN/'catalog.bin',SKIN/'catalog.hash',agents,note]}
assert before[GAME/INTRO]==before[SKIN/INTRO], 'Game and skin intro bundles differ; reconcile current objects before patching.'
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for name in [BG,'ui-backgrounds_assets_.bundle',WORLD,GLOBAL,'ui-visualfunctions_assets_all.bundle','ui-tileslayouts_assets_all.bundle','promobanner_assets_all.bundle'] if (p:=folder/name).exists()}
protected.update({p:sha(p.read_bytes()) for p in [R/'current-custom-textures.json',R/'reserved-texture-ids.json']})
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];banned={int(x['path_id']) for x in reserved};banned_names={x['name'].lower() for x in reserved}
assert PID not in banned
bgb=(GAME/BG).read_bytes();be=UnityPy.load(bgb);ba=be.assets[0]
assert registry['active_custom_texture_count']==len(registry['textures'])
tf=next(x for x in registry['textures'] if x['name']=='TFWX');assert int(tf['path_id'])==PID and tf['texture_format_id']==4
for t in registry['textures']:
 ob=ba.objects[int(t['path_id'])];assert ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256'],t['name']
def retired_absent(af):
 assert banned.isdisjoint(af.objects)
 assert -910000000000146 not in af.objects
 meta=next(o.read_typetree() for o in af.objects.values() if o.type.name=='AssetBundle')
 for ob in af.objects.values():
  if ob.type.name=='Texture2D':assert ob.peek_name().lower() not in banned_names|{'tf patch'}
 for k,v in meta['m_Container']:assert k.lower() not in banned_names|{'tf patch'} and v['asset']['m_PathID'] not in banned|{-910000000000146}
 assert all(p['m_PathID'] not in banned|{-910000000000146} for p in meta['m_PreloadTable'])
retired_absent(ba)
e=UnityPy.load(before[GAME/INTRO]);a=e.assets[0];hashes={i:sha(o.get_raw_data()) for i,o in a.objects.items()}
obj=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MarketingBannerTile_8x2')
d=obj.read_typetree();old_d=copy.deepcopy(d);sid=d['inlineSheet']['m_PathID'];s=a.objects[sid].read_typetree();old_s=copy.deepcopy(s)
rr={r['rid']:r for r in d['references']['RefIds']};old_rr=copy.deepcopy(rr)
def data(i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
assert rr[1002]['data']['m_Children']==[{'rid':1004}]
assert rr[1004]['data']['m_Children']==[{'rid':1006},{'rid':1007}]
assert data(1006)['name']=='ClickableBannerButton' and data(1007)['name']=='SimpleBanner' and data(1009)['name']=='banner'
assert all(data(i)['RenderTexture']['m_AssetGUID']==RT for i in [1007,1009])
assert not any(r.get('data',{}).get('name')=='StartScreenTFWX' for r in rr.values())
def val(typ,v):
 s[poolmap[typ]].append(v);return {'m_ValueType':typ,'valueIndex':len(s[poolmap[typ]])-1}
def px(v):return val(3,{'unit':1,'value':float(v)})
def en(v):return val(7,v)
def num(v):return val(2,float(v))
def style(i,props):
 nd=rr[i]['data'];ps=copy.deepcopy(s['m_Rules'][nd['m_RuleIndex']]['m_Properties']) if nd.get('m_RuleIndex',-1)>=0 else []
 ids={pid for pid,_ in props};ps=[p for p in ps if p['m_Id'] not in ids]
 ps += [{'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':[v]} for pid,v in props]
 s['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':ps,'line':-1});nd['m_RuleIndex']=len(s['m_Rules'])-1
def size(i,w,h):style(i,[(131105,px(w)),(131097,px(w)),(131095,px(w)),(131087,px(h)),(131096,px(h)),(131094,px(h)),(131084,num(0)),(131085,num(0))])
# Native source stylesheet fixes the video at 640x112; only its presentation width changes.
style(1002,[(131083,en('row')),(131073,en('center')),(131087,px(112)),(131096,px(112))])
for i in [1004,1006,1007,1009]:size(i,520,112)
for i in [1007,1009]:
 style(i,[(262153,en('scale-to-fit'))]);data(i).update(scaleMode=2,scaleMode_UxmlAttributeFlags=1,ScaleMode=2,ScaleMode_UxmlAttributeFlags=1)
nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
n=copy.deepcopy(rr[1002]);sd=copy.deepcopy(rr[rr[1002]['data']['m_SerializedData']['rid']]);n['rid']=nr;sd['rid']=nr+1
n['data'].update(m_Id=ni,m_Parent={'rid':1002},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SerializedData={'rid':nr+1})
sd['data'].update(uxmlAssetId=ni,name='StartScreenTFWX',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,focusable=0,focusable_UxmlAttributeFlags=1)
d['references']['RefIds'].extend([n,sd]);rr[nr]=n;rr[nr+1]=sd;rr[1002]['data']['m_Children'].append({'rid':nr})
matches=[i+1 for i,x in enumerate(a.externals) if x.path==f'archive:/{ba.name}/{ba.name}']
worlds={name:UnityPy.load(str(GAME/name)).assets[0] for name in [WORLD,GLOBAL]}
if not matches:
 ext=next(x for x in worlds[WORLD].externals if x.path==f'archive:/{ba.name}/{ba.name}')
 a.externals.append(copy.copy(ext));matches=[len(a.externals)]
assert len(matches)==1;ptr={'m_FileID':matches[0],'m_PathID':PID}
size(nr,120,112);style(nr,[(458753,val(6,ptr)),(262153,en('scale-to-fit')),(458767,num(1))])
element_count=validate_ui(d,s)
# All original data bindings, click events and switch child indices are preserved.
for rid,old in old_rr.items():
 current=copy.deepcopy(rr[rid]);old_data=old.get('data',{})
 if 'm_RuleIndex' in old_data:current['data']['m_RuleIndex']=old_data['m_RuleIndex']
 if rid==1002:current['data']['m_Children']=old_data['m_Children']
 if rid in [rr[i]['data']['m_SerializedData']['rid'] for i in [1007,1009]]:
  for key in ['scaleMode','scaleMode_UxmlAttributeFlags','ScaleMode','ScaleMode_UxmlAttributeFlags']:current['data'][key]=old_data[key]
 assert current==old,('Unexpected original record edit',rid)
assert rr[1004]['data']['m_Children']==old_rr[1004]['data']['m_Children']
assert s['m_Rules'][:len(old_s['m_Rules'])]==old_s['m_Rules']
assert s['assets'][:-1]==old_s['assets']
obj.save_typetree(d);a.objects[sid].save_typetree(s)
outbytes=e.file.save(packer='lz4');se=UnityPy.load(outbytes);sa=se.assets[0]
assert set(sa.objects)==set(hashes)
for i,h in hashes.items():
 if i in [obj.path_id,sid]:assert sa.objects[i].read_typetree()=={obj.path_id:d,sid:s}[i]
 else:assert sha(sa.objects[i].get_raw_data())==h,('Unrelated object modified',i)
validate_ui(sa.objects[obj.path_id].read_typetree(),sa.objects[sid].read_typetree());retired_absent(sa)
linked=UnityPy.load(outbytes,bgb);la=next(x for x in linked.assets if x.name==a.name)
resolved=PPtr(m_FileID=ptr['m_FileID'],m_PathID=PID,assetsfile=la).deref()
assert resolved.peek_name()=='TFWX' and sha(resolved.get_raw_data())==tf['texture_sha256']
def styled(i,pid):
 p=next(p for p in s['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==pid);h=p['m_Values'][0];return s[poolmap[h['m_ValueType']]][h['valueIndex']]
assert styled(1004,131105)['value']+styled(nr,131105)['value']==640
assert 640-styled(1004,131105)['value']==120
assert all(styled(i,131087)['value']==112 for i in [1004,1006,1007,1009,nr])
assert styled(nr,262153)=='scale-to-fit' and sd['data']['pickingMode']==1

outputs={GAME/INTRO:outbytes,SKIN/INTRO:outbytes};audits=[]
meta=next(o.read_typetree() for o in sa.objects.values() if o.type.name=='AssetBundle')
guid=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':obj.path_id})
for folder in [AA,SKIN]:
 path=folder/'catalog.bin';raw=before[path];c=cm.Catalog(raw);keys=c.keys();locs={l for _,p in keys for (l,) in c.array(p,'I')}
 def bundleloc(name):
  found=[loc for loc in locs if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+name)]
  assert len(found)==1;return found[0]
 own=bundleloc(INTRO);bg=bundleloc(BG);fixed=[];arrays={}
 for loc in sorted(locs):
  fields=c.unpack(loc,'7I');deps=c.location(loc)['dependencies']
  if own not in deps or bg in deps:continue
  if fields[3] not in arrays:arrays[fields[3]]=c.append(struct.pack('<'+'I'*(len(deps)+1),*(deps+[bg])),True)
  struct.pack_into('<I',c.data,loc+12,arrays[fields[3]]);fixed.append(loc)
 cb=bytes(c.data);cc=cm.Catalog(cb);oc=cm.Catalog(raw);assert cc.keys()==keys
 for loc in locs:
  old=oc.location(loc);new=cc.location(loc)
  assert all(old[k]==new[k] for k in ['primary','internal','provider','type'])
  assert new['dependencies']==old['dependencies']+([bg] if loc in fixed else [])
 assert any(cc.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' for loc in cc.locations(guid))
 for loc in cc.locations(guid):
  v=cc.location(loc);assert v['dependencies'][0]==own and bg in v['dependencies']
 rtloc=cc.locations(RT);assert len(rtloc)==1
 rtval=cc.location(rtloc[0]);assert rtval['type'][1]=='UnityEngine.RenderTexture' and rtval['dependencies'][0]==bundleloc('promobanner_assets_all.bundle')
 checked=[]
 for name,wa in worlds.items():
  own_world=bundleloc(name);wm=next(o.read_typetree() for o in wa.objects.values() if o.type.name=='AssetBundle')
  for key,entry in wm['m_Container']:
   if not re.fullmatch('[0-9a-f]{32}',key) or entry['asset']['m_FileID']!=0:continue
   wo=wa.objects.get(entry['asset']['m_PathID'])
   if wo is None or not (-1000000000000000<wo.path_id<-900000000000000) or wo.type.name!='MonoBehaviour':continue
   tree=wo.read_typetree();typ='SI.VisualScripting.VisualFunction' if 'm_nodes' in tree else ('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in tree else None)
   if not typ:continue
   for loc in cc.locations(key):
    v=cc.location(loc);assert v['type'][1]==typ and v['dependencies'][0]==own_world and bg in v['dependencies'],(key,v)
   checked.append({'guid':key,'name':wo.peek_name(),'type':typ,'path_id':str(wo.path_id),'bundle':name})
 if cb!=raw:
  outputs[path]=cb;outputs[folder/'catalog.hash']=hashlib.md5(cb).hexdigest().encode('ascii')
 audits.append({'catalog':str(path),'banner_guid':guid,'background_dependency_added_locations':len(fixed),'video_rendertexture_registration_valid':True,'custom_resources_checked':checked})

agents_text=before[agents].decode('utf8')
old_line='- V70 新增纹理 `TFWX`，Path ID `-910000000000150`，须沿用；本次仅加入 backgrounds，未设置界面关联。'
assert old_line in agents_text
new_line='- V70 新增纹理 `TFWX`，Path ID `-910000000000150`，须沿用；开始页 `MarketingBannerTile_8x2` 已关联：原生视频显示宽度由640减至520px，高112px；右侧120×112px区域等比完整显示TFWX；保留原生循环视频、链接和分支绑定。'
outputs[agents]=agents_text.replace(old_line,new_line).encode('utf8')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('start-banner-video520-tfwx120-'+stamp)
addition='''

## 8. 2026-10-29 最新：视频横幅缩窄并在右侧放置 TFWX

本节补充／覆盖第 5 节关于横幅未修改的历史状态。等待置顶“1.添加图片”完成 V70 后实施，直接复用已打包 TFWX，不重新导入图片。

- `MarketingBannerTile_8x2` 原视频显示尺寸640×112px，最新为520×112px，宽度减少120px；右侧新增120×112px图片槽，整行内容仍640×112px。
- 图片为当前 backgrounds 中 `TFWX`，固定 Path ID `-910000000000150`，原图1221×1221，RGBA32。以 `scale-to-fit` 完整显示，槽内实际图片112×112px、左右各4px留空；不裁剪赞赏码或文字。
- 原container改横排，原视频switch保持两个分支的顺序。可点击视频按钮、SimpleBanner及内部banner均520×112px，视频按比例完整显示；新 `StartScreenTFWX` VisualElement 与switch为同级兄弟，宽120px、忽略拾取，未添加跳转链接。
- 视频、VideoPlayer、RenderTexture、语言选择、循环播放和原视频点击事件保留；没有改视频编码、帧率、时长或播放器输出分辨率。
- 本次改动局限于intro包的横幅模板及其inlineStyle；背景包和180张有效自定义图片保持原样。资源总数未来以最新清单为准，保留原生背景覆盖规则、70张永久禁用规则和V65删除TF patch的规则。
- 更新后在新版模板上重新实现上述左右布局；按实际CAB和外部引用序号链接TFWX，验证横幅GUID与backgrounds依赖，保留当前其他页面和开始页背景。不要覆盖旧整包或重跑旧176张基线脚本。
- 实施脚本 `start-banner-video520-tfwx120.py`；本次安装／回退和校验记录见下列目录。运行时显示需启动游戏确认。
'''
addition+='\n本次记录：`'+out.name+'`。\n'
outputs[note]=(before[note].decode('utf8')+addition).encode('utf8')
out.mkdir();(out/'templates').mkdir()
(out/'templates/MarketingBannerTile_8x2.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
(out/'templates/MarketingBannerTile_8x2-style.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
items=[]
for p,b in outputs.items():
 tag='workspace' if p.parent==R else ('game' if p.parent in [AA,GAME] else 'skin')
 source=Path(tag)/p.name;backup=Path('backup-'+tag)/p.name
 for rel,data_b in [(source,b),(backup,before[p])]:
  (out/rel).parent.mkdir(exist_ok=True);(out/rel).write_bytes(data_b)
 items.append({'target':str(p),'source':source.as_posix(),'backup':backup.as_posix(),'before_sha256':sha(before[p]),'after_sha256':sha(b)})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p not in outputs:protected[p]=sha(b)
verify={'passed':True,'serialization_roundtrip':True,'video_display_size':[520,112],'tfwx_slot_size':[120,112],'total_width_unchanged':640,'video_width_reduction':120,'all_original_bindings_click_events_and_switch_order_preserved':True,'video_files_player_and_rendertexture_unchanged':True,'tfwx_latest_bundle_pointer_verified':True,'all_current_custom_texture_hashes_verified':len(registry['textures']),'reserved_70_and_deleted_TF_patch_absent':True,'unrelated_intro_objects_unchanged':len(hashes)-2,'runtime_verified':False}
report={'installed':False,'runtime_verified':False,'template':d['m_Name'],'template_path_id':str(obj.path_id),'style_path_id':str(sid),'texture':'TFWX','texture_path_id':str(PID),'texture_pointer':ptr,'video_width_before':640,'video_width_after':520,'video_height':112,'tfwx_slot':[120,112],'element_rid':nr,'picking_mode':'Ignore','new_asset_path_ids':0,'waited_for_image_task_completion':{'thread_id':'01a130f8-0796-7b71-bc75-f93524dc3703','turn_id':'01a18727-2a83-7b00-80c7-8eacf612094d','status':'completed'},'verification':verify,'catalog_audits':audits,'install_files':items,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(out/'verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install','--install'),('restore','--restore')]:
 script="$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(Path(__file__).resolve())+"' '"+flag+"' $PSScriptRoot\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n"
 (out/(action+'.ps1')).write_text(script,'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'verification':verify,'catalog_dependency_updates':[x['background_dependency_added_locations'] for x in audits],'custom_resources_checked':[len(x['custom_resources_checked']) for x in audits]},ensure_ascii=False),flush=True)
install(out)
