"""V3: management content only; restore all shared layer/style settings."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,re,shutil,struct,sys,uuid
V=Path(__file__).resolve().parent;R=V.parent
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 a=ast.parse((R/name).read_text('utf8'));exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in wanted],type_ignores=[]),name,'exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';S='settings_assets_all.bundle'
v2=json.loads((V/'labels-v2/transaction.json').read_text('utf8'))[0]
assert sha((G/W).read_bytes())==v2['after']
env=UnityPy.load(str(V/'baseline'/W));oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};expected={}
def named(name):return next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def sd(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def save(o,d):o.save_typetree(d);expected[o.path_id]=copy.deepcopy(d)
def clone(o,pid,d):
 assert pid not in oo
 c=copy.copy(o);c.path_id=pid;c.data=None;c._read_until=None;c.assets_file.objects[pid]=c;oo[pid]=c;save(c,d);return c
bundle=next(o for o in oo.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree()
byguid={k:oo[x['asset']['m_PathID']] for k,x in meta['m_Container'] if x['asset']['m_PathID'] in oo and oo[x['asset']['m_PathID']].type.name=='MonoBehaviour'}
docs={g:o.read_typetree() for g,o in byguid.items()};docs={g:d for g,d in docs.items() if 'references' in d}

# Exclude every match-owned template and its transitive VTA dependencies.
blocked=set();match_files={}
for bn in ['ui-match_assets_all.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
 raw=(G/bn).read_bytes();match_files[str(G/bn)]=sha(raw)
 for o in UnityPy.load(raw).objects:
  if o.type.name=='MonoBehaviour':blocked.update(re.findall(r'[0-9a-f]{32}',json.dumps(o.read_typetree())))
while True:
 old=len(blocked)
 for guid in list(blocked):
  if guid in docs:blocked.update(re.findall(r'[0-9a-f]{32}',json.dumps(docs[guid])))
 if len(blocked)==old:break
selected={};excluded=[]
for o in UnityPy.load(str(G/'ui-panelids_assets_all.bundle')).objects:
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree();p=d.get('m_panelDescription',{});layer=p.get('layer',{}).get('Name');guid=p.get('uxml',{}).get('m_AssetGUID');name=d['m_Name']
 if layer not in ['MenuBody','ReportBody'] or guid not in docs:continue
 if guid in blocked or re.search('match|onthepitch|teamtalk|shootout|penalt|fullscreenteamselection|fmmenu|draft|store|ige',name,re.I):excluded.append(name)
 else:selected[guid]=name
# Keep nested subtemplates intact; their outer management page provides the sidebar.
nested=set()
for guid,d in docs.items():
 if guid in selected:nested.update(set(re.findall(r'[0-9a-f]{32}',json.dumps(d)))&set(selected)-{guid})
for guid in nested:excluded.append(selected.pop(guid))
assert any(n=='PortalScreen' for n in selected.values()) and any(n=='PlayerReport' for n in selected.values())

# A dedicated row keeps native bookmark buttons and all match UI byte-identical.
current=UnityPy.load(str(G/W));co={o.path_id:o for o in current.objects}
row=next(o for o in co.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='BookmarkButton');rd=row.read_typetree();rs=co[rd['inlineSheet']['m_PathID']].read_typetree()
RID=-980000000031001;SID=-980000000031002
banned={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}|{-910000000000001,-910000000000002,-910000000000146}
assert not ({RID,SID}&banned)
GUID=uuid.uuid5(uuid.NAMESPACE_URL,'TF27/sidebar-content-v3/bookmark-row').hex
rd.update(m_Name='TFManagementSidebarBookmarkRow',inlineSheet={'m_FileID':0,'m_PathID':SID});rs['m_Name']='TFManagementSidebarBookmarkRow_Style'
rr=refs(rd);assert sd(rr,1016)['Binding']['m_direct']['Path']['m_path']=='const.true'
validate_ui(rd,rs);clone(named('BookmarkButton'),RID,rd);clone(oo[named('BookmarkButton').read_typetree()['inlineSheet']['m_PathID']],SID,rs)
span=[{'m_FileID':0,'m_PathID':SID},{'m_FileID':0,'m_PathID':RID}]
meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':RID}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);save(bundle,meta)

title=next(o.read_typetree() for o in co.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='OverviewTitleBar');tr=refs(title)
lst=next(i for i in tr if sd(tr,i).get('name')=='BookmarksList')
popup=next(i for i in tr if sd(tr,i).get('name')=='BookmarksPopupWidget')
rootdonor=named('OverviewTitleBar').read_typetree();rootrefs=refs(rootdonor)
plain=named('BookmarkButton').read_typetree();plainrefs=refs(plain)
auto={'m_ValueType':1,'valueIndex':3}
changes=[]
for guid,name in selected.items():
 obj=byguid[guid];d=copy.deepcopy(docs[guid]);rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
 ridnext=max(rr)+1;used={x.get('data',{}).get('m_Id') for x in rr.values()};idnext=1910313000
 def add(source,sourcerefs,sourceid,parent,label):
  global ridnext,idnext
  while idnext in used:idnext+=1
  el=copy.deepcopy(sourcerefs[sourceid]);ser=copy.deepcopy(sourcerefs[el['data']['m_SerializedData']['rid']]);ei=ridnext;si=ridnext+1;ridnext+=2;eid=idnext;idnext+=1;used.add(eid)
  el['rid']=ei;ser['rid']=si
  el['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_Classes=[],m_RuleIndex=-1,m_Properties=[],m_StylesheetPaths=[],m_Stylesheets=[],m_SerializedData={'rid':si})
  ser['data'].update(uxmlAssetId=eid,name=label,name_UxmlAttributeFlags=1)
  for x in [el,ser]:rr[x['rid']]=x;d['references']['RefIds'].append(x)
  if parent in rr:rr[parent]['data']['m_Children'].append({'rid':ei})
  return ei
 def box(i,left=0,right=0,top=0,bottom=0,width=None):
  props=[st.p(131102,st.en('absolute')),st.p(131089,st.px(left)),st.p(131103,st.px(right) if width is None else auto),st.p(131104,st.px(top)),st.p(131075,st.px(bottom)),st.p(131105,auto if width is None else st.px(width)),st.p(131087,auto),st.p(131097,st.px(0)),st.p(131096,st.px(0))]
  st.edit(rr[i],props)
 oldroots=list(rr[d['m_VisualTree']['rid']]['data']['m_Children']);rr[d['m_VisualTree']['rid']]['data']['m_Children']=[]
 wrapper=add(rootdonor,rootrefs,1001,d['m_VisualTree']['rid'],'TFManagementContentLayout');box(wrapper);sd(rr,wrapper).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 content=add(plain,plainrefs,1012,wrapper,'TFManagementPageContent');box(content,left=100);sd(rr,content).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 rr[content]['data']['m_Children']=oldroots
 for child in oldroots:rr[child['rid']]['data']['m_Parent']={'rid':content}
 sidebar=add(plain,plainrefs,1012,wrapper,'TFManagementSidebar100');box(sidebar,width=100)
 st.edit(rr[sidebar],[st.p(131095,st.px(100)),st.p(131097,st.px(100)),st.p(458752,st.h(4,{'r':0.03125,'g':0.046875,'b':0.0625,'a':1.0}))])
 li=add(title,tr,lst,sidebar,'TFManagementBookmarksList');box(li,bottom=36);sd(rr,li)['RowTemplate']['m_AssetGUID']=GUID
 assert sd(rr,li)['Direction']==0 and sd(rr,li)['Binding']['m_direct']['Path']['m_path']=='gameworldsubtabsandbookmarks.CurrentSelectedBookmarksList'
 pi=add(title,tr,popup,sidebar,'TFManagementBookmarksEdit');box(pi,width=100)
 rr[pi]['data']['m_Classes']=['ui-concepts-chevron-down_small','popupwidget-hover','bookmarks-button']
 st.edit(rr[pi],[st.p(131104,auto),st.p(131087,st.px(32)),st.p(131088,st.en('center'))])
 validate_ui(d,sheet);save(obj,d);save(oo[sid],sheet);changes.append({'page':name,'guid':guid,'path_id':obj.path_id})

# Keep the normal full-width title/tab bars; disable only their management bookmark strip.
obj=named('OverviewTitleBar');d=obj.read_typetree();rr=refs(d)
vs=next(x for x in sd(rr,1002)['ValueVariables'] if x['m_name']=='showbookmarks');assert vs['m_scopeValue']['m_serializedData']=='Bool|1|';vs['m_scopeValue']['m_serializedData']='Bool|0|';save(obj,d)
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catbefore=(G.parent/'catalog.bin').read_bytes();cat=cm.Catalog(catbefore)
source=next(l for l in cat.locations('55c5e407237e29e43a7ee0feb446fea9') if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
catout=cat.add_key_location(GUID,source,source);cat=cm.Catalog(catout)
assert cat.location(cat.location(cat.locations(GUID)[0])['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
assert cat.location(cat.locations(GUID)[0])['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects}
assert set(check)==set(oo)
for pid,o in check.items():
 if pid in expected:assert o.read_typetree()==expected[pid],pid
 else:assert sha(o.get_raw_data())==hashes[pid],pid
assert sha(check[named('BookmarkButton').path_id].get_raw_data())==hashes[named('BookmarkButton').path_id]
assert all(byguid[g].path_id not in expected for g in blocked if g in byguid)
out=V/'content-v3';out.mkdir(exist_ok=False);(out/'packages').mkdir();(out/'backup-game').mkdir()
outputs={G/W:raw,G/D:(V/'baseline'/D).read_bytes(),G/S:(V/'baseline'/S).read_bytes(),G.parent/'catalog.bin':catout,G.parent/'catalog.hash':hashlib.md5(catout).hexdigest().encode('ascii')}
v1=json.loads((V/'manifest.json').read_text('utf8'));protected={p:sha(Path(p).read_bytes()) for p in v1['protected_sha256'] if Path(p) not in outputs}
tx=[]
for target,data in outputs.items():
 before=target.read_bytes();backup=out/'backup-game'/target.name;backup.write_bytes(before);source=out/'packages'/target.name;source.write_bytes(data)
 tx.append({'target':str(target),'source':str(source),'backup':str(backup),'before':sha(before),'after':sha(data)})
record={'version':'V3 management content below native full-width title/tab bars','installed':False,'runtime_verified':False,'width_px':100,'public_settings_and_styles_restored_to_pre_sidebar':True,'match_bundles_unchanged':match_files,'match_reachable_templates_unchanged':True,'native_bookmark_button_unchanged':True,'resolution_configuration_changes':False,'new_row_guid':GUID,'new_path_ids':[RID,SID],'management_pages':changes,'excluded_pages':sorted(excluded),'modified_object_count':len(expected),'protected_sha256':protected}
(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(R/'install-independent-resource-patch.py',out/'installer.py')
for name,flag in [('install',''),('restore-v2',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
full=out/'full-rollback';full.mkdir();fulltx=[]
for row in tx:
 row=copy.deepcopy(row);n=Path(row['target']).name
 if n in [W,D,S]:original=V/'trial-install-001/backup-game'/n
 else:original=out/'backup-game'/n
 row.update(backup=str(original),before=sha(original.read_bytes()));fulltx.append(row)
(full/'transaction.json').write_text(json.dumps(fulltx,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');shutil.copyfile(out/'installer.py',full/'installer.py')
(out/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
(out/'README.md').write_text('V3：顶部原生标题栏/标签栏通栏，100px竖向书签仅在普通管理页内容区左侧显示。公共settings/default styles恢复试装前版本；比赛包及比赛模板依赖保持原始内容。原皮肤工程不修改。\n\nrestore-original.ps1 完整恢复侧栏试装前；restore-v2.ps1 恢复上一试制版。退出游戏后运行。\n\n离线验证通过，游戏内显示与分辨率现象尚需验证。\n','utf8')
print(json.dumps({'output':str(out),'management_pages':len(changes),'excluded_pages':len(excluded),'public_settings_styles_restored':True,'match_templates_unchanged':True,'runtime_verified':False},ensure_ascii=False))
