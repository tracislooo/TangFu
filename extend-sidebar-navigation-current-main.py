"""Extend a freshly rebased sidebar package without installing any resources."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil,struct,sys,zipfile
R=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve();assert OUT.parent==R
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for file,wanted in [('build-fc-player-hover-layout.py',{'write'}),('add-card-six-ratings.py',{'validate_ui'}),('fix-primary-messages-panel-navigation.py',{'payloads','event','string','binding','parameter','open_panel'})]:
 tree=ast.parse((R/file).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),file+':helpers','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
tx=json.loads((OUT/'transaction.json').read_text('utf8'));manifest=json.loads((OUT/'manifest.json').read_text('utf8'));assert not manifest['installed']
for x in tx:assert sha(Path(x['target']).read_bytes())==x['before']
path=OUT/'packages'/W;env=UnityPy.load(str(path));a=env.assets[0];raw={i:o.get_raw_data() for i,o in a.objects.items()};obj=a.objects[-980000000041003];doc=obj.read_typetree();original=copy.deepcopy(doc)
refs=lambda d:{x['rid']:x for x in d['references']['RefIds']};rr=refs(doc)
def serial(rid):return rr[rr[rid]['data']['m_SerializedData']['rid']]['data']
def label(rid):
 for c in rr[rid]['data'].get('m_Children',[]):
  s=serial(c['rid'])
  if s.get('name','').startswith('FixedLabel_'):return s['text']
 return None
buttons={label(x['rid']):x['rid'] for x in rr[1001]['data']['m_Children'] if label(x['rid']) is not None};assert len(buttons)==15
prototype=buttons['一线队'] if '一线队' in buttons else buttons['阵容']
base=payloads(serial(prototype)['Events'])[0];assert len(base)==76
nav=UnityPy.load(str(GAME/'ui-globalnavigation_assets_all.bundle'));trees={o.peek_name():o.read_typetree() for o in nav.objects if o.type.name=='MonoBehaviour'}
panels=UnityPy.load(str(GAME/'ui-panelids_assets_all.bundle')).assets[0];meta=next(o.read_typetree() for o in panels.objects.values() if o.type.name=='AssetBundle');pm=dict(meta['m_Container'])
spec=importlib.util.spec_from_file_location('sidebar_cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);catalog=cm.Catalog((OUT/'packages/catalog.bin').read_bytes())
icon_source=UnityPy.load(str(GAME/'gamemodules_assets_gameworld.bundle'));icons={}
for o in icon_source.objects:
 if o.type.name=='MonoBehaviour':
  d=o.read_typetree()
  if 'm_iconStyle' in d:icons[o.peek_name()]=d['m_iconStyle']
next_rid=max(rr)+1;used={x.get('data',{}).get('m_Id') for x in rr.values()};eid=1911050000;audit=[]
def clone_subtree(oldrid,parent):
 global next_rid,eid
 old=rr[oldrid];oldsd=rr[old['data']['m_SerializedData']['rid']];n=copy.deepcopy(old);s=copy.deepcopy(oldsd)
 rid=next_rid;next_rid+=2
 while eid in used:eid+=1
 uid=eid;eid+=1;used.add(uid)
 n['rid']=rid;s['rid']=rid+1;n['data'].update(m_Id=uid,m_Parent={'rid':parent},m_SerializedData={'rid':rid+1},m_Children=[]);s['data']['uxmlAssetId']=uid
 doc['references']['RefIds'] += [n,s];rr[rid]=n;rr[rid+1]=s
 for c in old['data'].get('m_Children',[]):n['data']['m_Children'].append({'rid':clone_subtree(c['rid'],rid)})
 return rid
def route(tree,name):return next(x['PropertyValue']['m_openEvent'] for x in trees[tree]['m_submenus'] if x['name']==name)
def encode(v):
 assert v['m_panelReference']['kind']==0 and not v['m_anchor']['value']
 return open_panel(v['m_panelReference']['asset']['m_AssetGUID'],[(x['name'],x['path']['m_path'],x['method']) for x in v['m_argumentBindings']],v['m_rebindMethod'],v['m_checkForExistingOpenedPanel'])
additions=[('阵容规划','RecruitmentSubtabs','Overview (Club)','Planner (Club)','SquadPlannerBookmark'),('转会','RecruitmentSubtabs','Overview (Club)','Transfers','TransferActivityBookmark'),('职员招募','RecruitmentSubtabs','Overview (Club)','Staff Recruitment','StaffSearchBookmark'),('俱乐部愿景','ClubSubtabs','Overview','Club Vision','ClubSiteBookmark')]
added={}
for title,tree,root,target,icon in additions:
 rid=clone_subtree(prototype,1001);s=serial(rid);s['name']='TFSidebarExtra_'+title
 rs=[route(tree,root),route(tree,target)];events=[encode(x) for x in rs];s['Events']=event(events);assert payloads(s['Events'])==events
 children=rr[rid]['data']['m_Children'];assert len(children)==2
 ir=children[0]['rid'];lr=children[1]['rid'];rr[ir]['data']['m_Classes']=[icons[icon]];serial(ir)['name']='FixedIcon_'+title;serial(lr).update(name='FixedLabel_'+title,text=title)
 added[title]=rid;routes=[]
 for i,(v,b) in enumerate(zip(rs,events)):
  guid=v['m_panelReference']['asset']['m_AssetGUID'];assert b[30:62]==guid.encode();assert catalog.locations(guid)
  ptr=pm[guid]['asset'];assert ptr['m_FileID']==0;pd=panels.objects[ptr['m_PathID']].read_typetree();layer=pd['m_panelDescription']['layer']['Name'];assert layer==('MenuBody' if i==0 else 'ReportBody')
  routes.append(dict(guid=guid,panel=pd['m_Name'],layer=layer,argument_bindings=v['m_argumentBindings']))
 audit.append(dict(title=title,icon=icons[icon],routes=routes))
sequence=[];first_team='一线队' if '一线队' in buttons else '阵容'
for child in rr[1001]['data']['m_Children']:
 sequence.append(child);title=label(child['rid'])
 for extra in ({first_team:['阵容规划'],'球探':['转会','职员招募'],'俱乐部':['俱乐部愿景']}.get(title,[])):sequence.append({'rid':added[extra]})
rr[1001]['data']['m_Children']=sequence
order=[label(c['rid']) for c in sequence if label(c['rid']) is not None];assert len(order)==19
assert order[order.index(first_team)+1]=='阵容规划';assert order[order.index('球探')+1:order.index('球探')+3]==['转会','职员招募'];assert order[order.index('俱乐部')+1]=='俱乐部愿景'
for x in original['references']['RefIds']:
 expected=copy.deepcopy(x)
 if x['rid']==1001:expected['data']['m_Children']=sequence
 assert rr[x['rid']]==expected,('Existing sidebar record changed',x['rid'])
validate_ui(doc,a.objects[doc['inlineSheet']['m_PathID']].read_typetree());obj.save_typetree(doc);payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
for i,o in check.objects.items():
 if i==obj.path_id:assert o.read_typetree()==doc
 else:assert o.get_raw_data()==raw[i]
path.write_bytes(payload)
# The older archive includes a shared popup repair: preserve the current main object verbatim.
mp=OUT/'packages'/M;me=UnityPy.load(str(mp));ma=me.assets[0];current=UnityPy.load(str(GAME/M)).assets[0];popup=next(o for o in current.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MatchUITacticalOptions');ma.objects[popup.path_id].set_raw_data(popup.get_raw_data());mp.write_bytes(me.file.save(packer='lz4'));assert UnityPy.load(str(mp)).assets[0].objects[popup.path_id].get_raw_data()==popup.get_raw_data()
for entry in manifest['bundle_audits']:
 if entry['bundle']==M:
  entry['changed_objects']=[x for x in entry['changed_objects'] if x['name']!='MatchUITacticalOptions']
for x in tx:x['after']=sha(Path(x['source']).read_bytes())
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
manifest.update(version='Current main plus independent 19-entry sidebar',fixed_navigation_count=19,fixed_navigation_order=order,new_routes=audit,installed=False,runtime_verified=False,current_main_popup_preserved_byte_identical=True,existing_sidebar_labels_events_and_styles_unchanged=True)
aa=OUT/'aa';(aa/'StandaloneWindows64').mkdir(parents=True,exist_ok=True)
for x in tx:
 source=Path(x['source']);dest=aa/('StandaloneWindows64' if source.name.endswith('.bundle') else '')/source.name;shutil.copy2(source,dest)
zipout=R/'exports'/('FM27-sidebar-19-links-current-main-'+OUT.name.rsplit('-',2)[-2]+'-'+OUT.name.rsplit('-',1)[-1]+'-aa.zip')
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in aa.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zipout) as z:
 assert len(z.namelist())==5 and z.testzip() is None
 for p in aa.rglob('*'):
  if p.is_file():assert z.read(p.relative_to(OUT).as_posix())==p.read_bytes()
for x in tx:assert sha(Path(x['target']).read_bytes())==x['before'],('Game changed concurrently',x['target'])
for p,h in list(manifest['protected_sha256'].items()):
 actual=sha(Path(p).read_bytes())
 if actual!=h:
  # Concurrent image maintenance does not affect these five sidebar resources.
  assert Path(p).name in ['ui-backgrounds_assets_common.bundle','current-custom-textures.json'],('Protected file changed',p)
  manifest.setdefault('concurrent_unmodified_image_updates',[]).append(dict(path=p,before=h,after=actual))
  manifest['protected_sha256'][p]=actual
manifest['aa_export']=str(zipout);(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');shutil.copy2(__file__,OUT/'extend-navigation-source.py');shutil.copy2(R/'rebase-latest-approved-sidebar.py',OUT/'migration-driver.py')
(OUT/'README.md').write_text('基于制作时当前游戏主版本资源制作的独立侧栏补丁，未安装。19个固定入口：'+ '、'.join(order)+'。\n\n新增4入口复用原生MenuBody/ReportBody页面事件及参数，同原侧栏图标和尺寸。沿用100px宽、top85px、400px原生书签、顶部编辑三角、深灰蓝底色及医疗白图标。主版本最新Highlight等无关对象保留，共用微调弹窗以当前主版本为准。\n\ninstall-sidebar.ps1安装；restore-non-sidebar.ps1回退到本补丁制作时的主版本，有哈希保护。主版本继续修改后须重新迁移，不可直接覆盖旧aa包。zip内只有aa目录5文件。静态及序列化检查通过，实际点击和显示待游戏验证。\n','utf8')
index=R/'current-sidebar-version.json';state=json.loads(index.read_text('utf8'));state.update(latest_prepared_sidebar_patch=str(OUT),latest_prepared_sidebar_export=str(zipout),latest_prepared_sidebar_fixed_count=19,latest_prepared_sidebar_installed=False,latest_prepared_sidebar_order=order);index.write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(output=str(OUT),zip=str(zipout),fixed_count=19,order=order,installed=False,game_and_main_skin_unchanged=True),ensure_ascii=False),flush=True)
