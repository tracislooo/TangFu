"""Sidebar-only frames cleanup; retain the edit widget's existing location."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for file,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),'<definitions>','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';outputs={};before={};reports=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for name in [W,D]:
 path=GAME/name;before[path]=path.read_bytes();env=UnityPy.load(before[path]);obs=env.assets[0].objects;raw={i:o.get_raw_data() for i,o in obs.items()};expected={}
 def save(obj,data):obj.save_typetree(data);expected[obj.path_id]=copy.deepcopy(data)
 def named(label):return next(o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()==label)
 if name==W:
  for label in ['TFReferenceBookmarkSidebar','TFReferenceBookmarkRow']:
   docobj=named(label);doc=docobj.read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};sheetobj=obs[doc['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet)
   def plain(node):
    st.edit(node,[st.p(i,st.px(0)) for i in [131076,131077,131078,131079]]+[st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})),st.p(458753,st.en('none'))])
   if label=='TFReferenceBookmarkSidebar':
    buttons=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','').startswith('TFSidebarFixed_')]
    assert len(buttons)==14
    for n in buttons:plain(n)
    popup=rr[1073];original_popup=copy.deepcopy(popup);st.edit(popup,[st.p(i,st.px(0)) for i in [131076,131077,131078,131079]]+[st.p(131087,st.px(20)),st.p(131096,st.px(20)),st.p(131094,st.px(20)),st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})),st.p(458757,st.px(16),st.px(16))])
    assert popup['data']['m_Parent']==original_popup['data']['m_Parent']
   else:
    for rid in [1001,1006,1009]:plain(rr[rid])
   validate_ui(doc,sheet);save(docobj,doc);save(sheetobj,sheet)
 else:
  obj=named('AlwaysAppliedStyleSheet');sheet=obj.read_typetree();st=Styles(sheet)
  rules=[r for r in sheet['m_Rules'] if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','TFReferenceSidebar'] for sel in r['m_ComplexSelectors'])];assert len(rules)==1
  for prop in rules[0]['m_Properties']:
   if prop['m_Id'] in [131076,131077,131078,131079]:prop['m_Values']=[st.px(0)]
  save(obj,sheet)
 payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0];assert set(check.objects)==set(obs)
 for pid,o in check.objects.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert o.get_raw_data()==raw[pid]
 outputs[path]=payload;reports.append({'file':name,'changed_objects':list(expected),'other_objects_byte_identical':True})
out=R/('sidebar-borderless-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx=[]
for path,data in outputs.items():
 src=out/'packages'/path.name;bak=out/'backup-game'/path.name;src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(data);bak.write_bytes(before[path]);assert path.read_bytes()==before[path]
 tx.append({'target':str(path),'source':str(src),'backup':str(bak),'before':sha(before[path]),'after':sha(data)})
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+[p for p in SKIN.iterdir() if p.is_file()] if p not in outputs}
(out/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'fixed_navigation_borderless':True,'native_bookmarks_borderless':True,'edit_button_height':20,'edit_icon_size':16,'edit_button_location_changed':False,'reports':reports,'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for action,flag in [('install',''),('restore-frames',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+'\n','utf-8-sig')
(out/'README.md').write_text('侧栏分支：取消14固定入口和原生书签的按钮方框、填充背景及侧栏右边框。编辑按钮位置不变，高度20px，三角图标16px。保留文字、事件、侧栏位置、比赛补偿和其他资源；原皮肤工程未改。restore-frames.ps1回退本次外观调整。游戏内效果待确认。\n','utf8')
print(str(out),flush=True)
