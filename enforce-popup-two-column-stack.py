from pathlib import Path
import sys,json,copy,ast,struct,datetime,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
oldwrite=TypeTreeHelper.write_value;h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in h.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<helpers>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']};sha=lambda b:hashlib.sha256(b).hexdigest()
before={p/W:(p/W).read_bytes() for p in [GAME,SKIN]};protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name!=W}
for folder in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:
  p=folder/n
  if p.exists():protected[p]=sha(p.read_bytes())
outputs={};audits=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={}
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988]:
  o=oo[pid];d=o.read_typetree();old=copy.deepcopy(d);rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
  def named(name):
   a=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name];assert len(a)==1,(name,len(a));return a[0]
  assert not any(r.get('data',{}).get('name')=='PopupStackedLeftColumn' for r in rr.values()),'Already installed; inspect instead of duplicating columns.'
  bg=named('RightPanelBackground');body=rr[bg['data']['m_Parent']['rid']];proto=copy.deepcopy(bg);psd=copy.deepcopy(rr[bg['data']['m_SerializedData']['rid']]);nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
  def addcolumn(name,x,y,w,h):
   global nr,ni
   n=copy.deepcopy(proto);sd=copy.deepcopy(psd);n['rid']=nr;sd['rid']=nr+1;nr+=2
   n['data'].update(m_Id=ni,m_Parent={'rid':body['rid']},m_Children=[],m_SerializedData={'rid':sd['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
   sd['data'].update(uxmlAssetId=ni,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,focusable=0,focusable_UxmlAttributeFlags=1);ni+=1
   st.box(n,x,y,w,h);st.edit(n,[st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})),st.p(65551,st.en('visible'))]);d['references']['RefIds'].extend([n,sd]);rr[n['rid']]=n;rr[sd['rid']]=sd
   body['data']['m_Children'].append({'rid':n['rid']});return n
  left=addcolumn('PopupStackedLeftColumn',12,12,400,808);right=addcolumn('PopupAttributesRightColumn',426,12,694,808)
  for col,regions in [(left,[('Fixed_FCPlayerCard',0,0,400,596),('Fixed_VerticalPositionPitch',0,608,400,200),('PopupPanelOutline_Pitch',0,608,400,200)]),(right,[('Fixed_PlayerHeader',0,0,694,64),('Fixed_SmallAttributes',0,76,694,592),('Fixed_CoachScoutReport',0,680,272,128),('Fixed_PlayerMood',284,680,136,128),('Fixed_PlayerPosition',432,680,262,128)])]:
   for name,x,y,w,h in regions:
    n=named(name);parent=rr[n['data']['m_Parent']['rid']];parent['data']['m_Children'].remove({'rid':n['rid']});n['data']['m_Parent']={'rid':col['rid']};col['data']['m_Children'].append({'rid':n['rid']});st.box(n,x,y,w,h)
  st.box(bg,12,12,1118,808);st.edit(bg,[st.p(458752,st.h(4,{'r':.0625,'g':.09375,'b':.125,'a':1.}))]);st.box(named('PopupPanelOutline_Attributes'),12,12,1118,808)
  # Background first, content columns next, entire-popup outline last.
  outline=named('PopupPanelOutline_Attributes');kids=body['data']['m_Children'];body['data']['m_Children']=[{'rid':bg['rid']}]+[c for c in kids if c['rid'] not in [bg['rid'],outline['rid']]]+[{'rid':outline['rid']}]
  visited=set();ids=set()
  def walk(i):
   assert i not in visited;visited.add(i);a=rr[i]['data'];assert a['m_Id'] not in ids;ids.add(a['m_Id'])
   sd=a.get('m_SerializedData',{}).get('rid',-2)
   if sd!=-2:assert rr[sd]['data']['uxmlAssetId']==a['m_Id']
   for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']=={'rid':i};walk(c['rid'])
  walk(d['m_VisualTree']['rid']);assert all(r['rid'] in visited for r in rr.values() if 'm_Parent' in r.get('data',{}))
  for rid,r in refs(old).items():
   check=copy.deepcopy(rr[rid]);a=check.get('data',{})
   for k in ['m_Children','m_Parent','m_RuleIndex']:
    if k in r.get('data',{}):a[k]=r['data'][k]
   assert check==r,('Original binding/serialized data changed',rid)
  for ob,data in [(o,d),(so,s)]:ob.save_typetree(data);changed[ob.path_id]=data
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 # Confirm horizontal private row retains its 14 native hover tooltip bindings.
 ge=UnityPy.load(str(folder/G));go={o.path_id:o for o in ge.objects};row=go[-960000000003040].read_typetree();assert sum(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.Tooltip' for r in refs(row).values())==14
 outputs[folder/W]=b;audits.append({'folder':str(folder),'modified_objects':list(changed),'unrelated_objects_unchanged':len(oo)-len(changed),'private_pitch_native_tooltips':14})
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('popup-two-column-stack-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'layout':'Explicit left column FC above horizontal pitch; explicit right column attributes above three bottom modules','design_size':[1142,832],'display_size':[970.7,707.2],'card_design_size_preserved':[400,596],'pitch_display_size':[340,170],'background':'single opaque deep dark panel covering both columns','audits':audits,'other_bundles_and_catalogs_unchanged':True}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
note='\n\n## 2026-11-01 已确认示意图：独立左右栏\n\n本节覆盖之前的平铺子节点方案。左栏 `PopupStackedLeftColumn` 设计(12,12,400,808)：FC卡面(0,0,400,596)，横向球场(0,608,400,200)，保持原卡面大小；右栏 `PopupAttributesRightColumn` (426,12,694,808)：头部(0,0,694,64)，Small区域(0,76,694,592)，三个底部模块Y=680、各高128，底端与球场对齐。统一背景与外框(12,12,1118,808)，背景使用不透明深色，覆盖全部左右栏。三种入口均建立这两个明确容器，保留一层85%缩放及14个原生左右侧偏好悬停提示。设计总尺寸1142×832，悬浮显示970.7×707.2，含标题栏点击框970.7×754.8。恢复P06直接建立最终两栏，不重复追加容器。实现 `enforce-popup-two-column-stack.py`；记录 `'+out.name+'/manifest.json`。文件及布局树回读通过，游戏内视觉与点击待确认。\n'
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md','球员位置模块统一恢复顺序.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+note,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));current={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=current[a['path_id_reference_only']].read_typetree();a['tree']=t;s=t['inlineSheet'];a['inline_style']=current[s['m_PathID']].read_typetree() if s['m_PathID'] and not s['m_FileID'] else None
snap['bundles'][W]=sha(outputs[GAME/W]);snap.update(revision='Approved mockup implemented using explicit left card-above-pitch and right attributes columns; full opaque dark background; 85% scale',runtime_verified=False);p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True))
