"""Insert fourteen direct native page links before the editable bookmarks."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, shutil, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for file,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'}),('fix-primary-messages-panel-navigation.py',{'payloads','event','string','binding','parameter','open_panel'})]:
 tree=ast.parse((R/file).read_text('utf8'))
 definitions=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted]
 exec(compile(ast.Module(body=definitions,type_ignores=[]),file+':definitions-only','exec'))
TypeTreeHelper.write_value=write
location=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(location['bundle_root']);SKIN=Path(location['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';path=GAME/W;before=path.read_bytes();env=UnityPy.load(before);objects=env.assets[0].objects
sha=lambda b:hashlib.sha256(b).hexdigest()
hashes={pid:sha(o.get_raw_data()) for pid,o in objects.items()}
named=lambda name:next(o for o in objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
serial=lambda rr,i:rr.get(rr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
sidebar=named('TFReferenceBookmarkSidebar');doc=sidebar.read_typetree();original=copy.deepcopy(doc);rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();st=Styles(sheet)
menu=named('MenuBar').read_typetree();mr=refs(menu)
proto=next(r for i,r in mr.items() if 'm_SerializedData' in r.get('data',{}) and serial(mr,i).get('name')=='PrimaryNavMessagesButton')
proto_sd=mr[proto['data']['m_SerializedData']['rid']]
base=payloads(proto_sd['data']['Events'])[0];assert len(base)==76
navigation=UnityPy.load(str(GAME/'ui-globalnavigation_assets_all.bundle'))
trees={o.peek_name():o.read_typetree() for o in navigation.objects if o.type.name=='MonoBehaviour'}
preset=json.loads((R/'sidebar-bookmark-defaults-20261101/default-bookmarks.json').read_text('utf8'))
parents=[('PortalSubtabs','Overview'),('SquadSubtabs','Overview (Club)'),('SquadSubtabs','Overview (Club)'),('TacticsSubtabs','Overview'),('TacticsSubtabs','Overview'),('ClubSubtabs','Overview'),('TrainingSubtabs','Overview'),('TrainingSubtabs','Overview'),('PortalSubtabs','Overview'),('PortalSubtabs','Overview'),('RecruitmentSubtabs','Overview (Club)'),('ClubSubtabs','Overview'),('ClubSubtabs','Overview'),('SquadSubtabs','Overview (Club)')]
panels=UnityPy.load(str(GAME/'ui-panelids_assets_all.bundle')).assets[0];panelmeta=next(o.read_typetree() for o in panels.objects.values() if o.type.name=='AssetBundle');panelmap=dict(panelmeta['m_Container'])
spec=importlib.util.spec_from_file_location('fixed_nav_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);catalog=cm.Catalog((GAME.parent/'catalog.bin').read_bytes())
assert rr[1001]['data']['m_Children']==[{'rid':1046}]
rid=max(rr)+1;used={r.get('data',{}).get('m_Id') for r in rr.values()};buttons=[];audits=[]
for index,(entry,(tree_name,parent_name)) in enumerate(zip(preset['entries'],parents)):
 label=entry['label_zh'];root=next(v for v in trees[tree_name]['m_submenus'] if v['name']==parent_name)['PropertyValue']['m_openEvent'];target=entry['native_property_value']['m_openEvent']
 routes=[root] if root['m_panelReference']['asset']['m_AssetGUID']==target['m_panelReference']['asset']['m_AssetGUID'] else [root,target]
 def encode(route):
  assert route['m_panelReference']['kind']==0 and not route['m_anchor']['value']
  return open_panel(route['m_panelReference']['asset']['m_AssetGUID'],[(a['name'],a['path']['m_path'],a['method']) for a in route['m_argumentBindings']],route['m_rebindMethod'],route['m_checkForExistingOpenedPanel'])
 events=[encode(route) for route in routes]
 audit=[]
 for route,encoded in zip(routes,events):
  guid=route['m_panelReference']['asset']['m_AssetGUID'];assert encoded[30:62]==guid.encode('ascii')
  pointer=panelmap[guid]['asset'];assert pointer['m_FileID']==0
  pd=panels.objects[pointer['m_PathID']].read_typetree();assert catalog.locations(guid)
  audit.append({'name':pd['m_Name'],'guid':guid,'layer':pd['m_panelDescription']['layer']['Name']})
 assert audit[0]['layer']=='MenuBody',(label,audit)
 if len(audit)>1:assert audit[-1]['layer']=='ReportBody',(label,audit)
 n,sd=copy.deepcopy(proto),copy.deepcopy(proto_sd);eid=1911016000+index;assert eid not in used;used.add(eid)
 n['rid'],sd['rid']=rid,rid+1
 n['data'].update(m_Id=eid,m_Parent={'rid':1001},m_Children=[],m_Classes=['sibutton','bookmarks-button'],m_Properties=[],m_RuleIndex=-1,m_StylesheetPaths=[],m_Stylesheets=[],m_SerializedData={'rid':rid+1})
 sd['data'].update(uxmlAssetId=eid,name='TFSidebarFixed_'+str(index+1),name_UxmlAttributeFlags=1,text=label,text_UxmlAttributeFlags=1,pickingMode=0,pickingMode_UxmlAttributeFlags=1,Events=event(events),Events_UxmlAttributeFlags=1,RightClickEvents={'m_bytes':[]},RightClickEvents_UxmlAttributeFlags=1)
 assert payloads(sd['data']['Events'])==events
 doc['references']['RefIds'] += [n,sd];rr[rid]=n;rr[rid+1]=sd
 st.edit(n,[st.p(131105,st.px(100)),st.p(131097,st.px(100)),st.p(131095,st.px(100)),st.p(131087,st.px(30)),st.p(131096,st.px(30)),st.p(131094,st.px(30)),st.p(131085,st.num(0)),st.p(262150,st.px(0)),st.p(262151,st.px(0)),st.p(65537,st.px(12)),st.p(65546,st.en('middle-center')),st.p(65536,st.h(4,{'r':1.,'g':1.,'b':1.,'a':1.})),st.p(458752,st.h(4,{'r':0.0625,'g':0.0625,'b':0.125,'a':1.})),st.p(458753,st.en('none')),st.p(131076,st.px(1)),st.p(458758,st.h(4,{'r':0.5,'g':0.5,'b':0.5,'a':0.5}))],reset=True)
 buttons.append({'rid':rid});audits.append({'label':label,'height':30,'routes':audit});rid+=2
rr[1001]['data']['m_Children']=buttons+[{'rid':1046}]
# Four editable bookmark rows remain visible below the fixed entries, with native scrolling.
st.edit(rr[1229],[st.p(131087,st.px(160))])
validate_ui(doc,sheet)
for i,record in refs(original).items():
 expected=copy.deepcopy(record)
 if i==1001:expected['data']['m_Children']=rr[i]['data']['m_Children']
 if i==1229:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
 assert rr[i]==expected,('Native bookmark record changed',i)
sidebar.save_typetree(doc);objects[sid].save_typetree(sheet);payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
assert set(check.objects)==set(objects)
for pid,obj in check.objects.items():
 if pid==sidebar.path_id:assert obj.read_typetree()==doc
 elif pid==sid:assert obj.read_typetree()==sheet
 else:assert sha(obj.get_raw_data())==hashes[pid],pid
out=R/('sidebar-fixed-navigation-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();source=out/'packages'/W;backup=out/'backup-game'/W;source.parent.mkdir();backup.parent.mkdir();source.write_bytes(payload);backup.write_bytes(before)
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle'))+list(GAME.glob('settings*.bundle'))+[GAME/'gamemodules_assets_gameworld.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+[p for p in SKIN.iterdir() if p.is_file()] if p!=path}
assert path.read_bytes()==before
tx=[{'target':str(path),'source':str(source),'backup':str(backup),'before':sha(before),'after':sha(payload)}]
manifest={'installed':False,'runtime_verified':False,'fixed_navigation_count':14,'position':'before original editable bookmarks','width_px':100,'button_height_px':30,'native_bookmark_view_height_px':160,'direct_native_panel_events':True,'routes':audits,'unrelated_objects_byte_identical':True,'protected_sha256':protected}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for action,flag in [('install',''),('restore-fixed-navigation',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+'\n','utf-8-sig')
(out/'README.md').write_text('14项固定导航按指定顺序位于原生可编辑书签上方，宽100px、每项高30px。标题直接显示中文文字，通过原生MenuBody根页面及ReportBody目标页面事件跳转。下方保留原生书签与编辑入口，书签列表高160px并可滚动。仅修改TFReferenceBookmarkSidebar及其内联样式，其他资源对象保持字节一致。游戏内显示与点击尚未验证。restore-fixed-navigation.ps1撤销本次固定导航。\n','utf8')
print(json.dumps({'output':str(out),'fixed_links':len(audits),'changed_objects':[sidebar.path_id,sid],'installed':False},ensure_ascii=False),flush=True)
