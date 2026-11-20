"""Keep six round selectors, but use a native persistable tab selection."""
from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-six-page-persistent-selection-').replace('NAMES=[W,G,M,F]','NAMES=[G]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
exec(compile(boot,'backup-installed-six-pages','exec'))
donor=Doc(G,name='PersonSearchConditionFiltersMainBlock')
button_source=None
for ob in objs[G].values():
 if ob.type.name!='MonoBehaviour':continue
 tree=ob.read_typetree()
 for r in tree.get('references',{}).get('RefIds',[]):
  if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIButton':button_source=(ob.path_id,r['rid']);break
 if button_source:break
buttons=Doc(G,pid=button_source[0]);audits=[]
for side in ['Home','Away']:
 doc=Doc(G,name='HighlightLower'+side+'SixPageCarousel')
 before_doc=copy.deepcopy(doc.d);oldroot=1002;parent=doc.a(oldroot)['m_Parent']['rid']
 old_pages=[x['rid'] for x in doc.a(oldroot)['m_Children']]
 assert len(old_pages)==6
 # Explicit Persistent scope prevents loss when the executable is restarted.
 variables=doc.add(donor,1043,parent,'Highlight'+side+'SavedPage')
 doc.data(variables).update(ValueVariables=[{'m_name':'HighlightLowerSelectedPage','m_scopeValue':{'m_serializedData':'Int|0|(Persistent,Explicit,{TF27.Highlight.Lower.'+side+'.SixPages.v2},{selected-page})'}}],ReferenceVariables=[],ValueVariables_UxmlAttributeFlags=1,ReferenceVariables_UxmlAttributeFlags=1)
 tab=doc.add(donor,1006,variables,'tab-group')
 switch=doc.add(donor,1009,tab,'TabsContent')
 group=doc.add(donor,1008,tab,'TabButtons')
 doc.data(tab).update(SelectedTabBinding={'m_path':'HighlightLowerSelectedPage'},SelectedTabBinding_UxmlAttributeFlags=1,DefaultSelection=0,DefaultSelection_UxmlAttributeFlags=1,KeepVisitedTabsBound=0,KeepVisitedTabsBound_UxmlAttributeFlags=1)
 doc.data(group).update(SelectionBinding={'m_path':'HighlightLowerSelectedPage'},SelectionBinding_UxmlAttributeFlags=1,CurrentSelectedIdBinding={'m_path':''},DefaultSelection=0,DefaultSelection_UxmlAttributeFlags=1,SelectedStyle='carousel-indicator-current',SelectedStyle_UxmlAttributeFlags=1,NotifyDefaultSelection=0,NotifyDefaultSelection_UxmlAttributeFlags=1,UsePersistantSelection=0,UsePersistantSelection_UxmlAttributeFlags=1,IgnoredIndex=-1,IgnoredIndex_UxmlAttributeFlags=1)
 for node in [variables,tab,switch]:doc.fill(node);doc.st(node,[(131096,doc.px(0)),(131097,doc.px(0))])
 doc.st(tab,[(131083,doc.enum('column'))])
 doc.st(switch,[(131087,doc.px(0)),(131082,doc.px(0)),(131084,doc.num(1))])
 doc.st(group,[(131083,doc.enum('row')),(131088,doc.enum('center')),(131073,doc.enum('center')),(131087,doc.px(24)),(131096,doc.px(24)),(131094,doc.px(24)),(131085,doc.num(0)),(131084,doc.num(0))])
 doc.a(group)['m_Classes']=[]
 titles=['球队统计','无球阵型','实时积分榜','最新比分','比赛日信息','赛事']
 for index,page in enumerate(old_pages):
  doc.move(page,switch);doc.a(page)['m_Classes']=[]
  button=doc.add(buttons,button_source[1],group,'Highlight'+side+'Page'+str(index))
  value=doc.data(button)
  value.update(StaticText='',StaticText_UxmlAttributeFlags=1,Events={'m_bytes':[]},Events_UxmlAttributeFlags=1,RightClickEvents={'m_bytes':[]},BindTextFunction={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}},BindTextFunction_UxmlAttributeFlags=1,tooltip=titles[index],tooltip_UxmlAttributeFlags=1,focusable=1,focusable_UxmlAttributeFlags=1)
  for key in ['HoverBinding','AuditComponentBinding']:value[key]={'m_path':''}
  value['InputActionRef']={'m_inputActionAsset':{'m_AssetGUID':'','m_SubObjectName':'','m_SubObjectType':''},'m_actionID':''}
  doc.a(button)['m_Classes']=['carousel-indicator']
  doc.size(button,12,12)
  doc.st(button,[(262147,doc.px(6)),(131090,doc.px(3)),(131093,doc.px(3))]+[(p,doc.px(0)) for p in [131098,131099,131100,131101]])
 oldser=doc.a(oldroot)['m_SerializedData']['rid']
 doc.a(parent)['m_Children'].remove({'rid':oldroot})
 doc.d['references']['RefIds']=[r for r in doc.d['references']['RefIds'] if r['rid'] not in [oldroot,oldser]]
 del doc.r[oldroot];del doc.r[oldser]
 assert len(doc.a(switch)['m_Children'])==6 and len(doc.a(group)['m_Children'])==6
 assert [doc.data(x['rid'])['templateId'] for x in doc.a(switch)['m_Children']]==[sd(refs(before_doc),x)['templateId'] for x in old_pages]
 doc.save();audits.append({'side':side,'persistent_variable':doc.data(variables)['ValueVariables'][0],'six_page_assets_and_order_unchanged':True,'native_tab_group':tab,'round_selector_buttons':6,'default_only_when_no_saved_value':True})
outputs={}
for bn in NAMES:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree
 for doc in documents:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/bn;dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for bn in NAMES:
  p=folder/bn;tx.append({'target':str(p),'source':str(outputs[bn]),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(outputs[bn].read_bytes())})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'corrects':'Native BindableCarouselTileRoot SharedPersistenceID uses Session; use explicit Persistent native tab value with round buttons instead.','wrappers':audits,'serialization_roundtrip':True,'all_other_objects_identical':True,'no_new_assets_or_catalog_changes':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('原生圆点轮播内部SharedPersistenceID只使用Session，不能用来承诺重启记忆。本补丁保留六页引用与顺序，改用原生TabGroup/SwitchElement及六个圆形按钮；左右分别绑定原生Persistent变量，默认0且禁止初始化通知覆盖保存值。六页只绑定当前显示页，统计表、无球阵型、数据绑定和其余游戏资源未改。仅改变已登记的两个私有容器及内联样式，不新增资源或改目录。静态回读通过；实际显示、重进和重启保持需要游戏内验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'explicit_persistent':True,'runtime_verified':False},ensure_ascii=False))
