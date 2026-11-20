from pathlib import Path
import json,collections

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-fixed-comparison-no-titles-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-match-template-and-load-codecs','exec'))

d=Doc(G,name='MatchViewer_12x4')
old=copy.deepcopy(d.d);old_refs=refs(old);old_style=copy.deepcopy(d.s)
native=Doc(G,pid=d.obj.path_id,tree=old,style=old_style)
allowed_assets=set();graph_audit=[]
def subtree(doc,i):
 yield i
 for child in doc.a(i).get('m_Children',[]):yield from subtree(doc,child['rid'])
def one(nodes,predicate,description):
 found=[i for i in nodes if predicate(i)]
 assert len(found)==1,(description,found)
 return found[0]
def edit(i,props):d.st(i,props);allowed_assets.add(i)
def fill_remaining(i):
 edit(i,[(131105,d.pct(100)),(131087,d.px(0)),(131082,d.px(0)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])

for home,side in [(True,'Home'),(False,'Away')]:
 for kind in ['Heat','Pass']:
  card=d.named('HighlightNative'+side+kind+'Card');nodes=list(subtree(d,card))
  title_frame=one(nodes,lambda i:d.data(i).get('name')=='title area frame','whole native title bar')
  edit(title_frame,[(131081,d.enum('none'))])
  content=one(nodes,lambda i:d.data(i).get('name')=='states-templates-tile-content','native content area')
  frame=one(nodes,lambda i:d.data(i).get('name')==('heat_map-frame' if kind=='Heat' else 'pass-map-frame'),'pitch and legends area')
  slot=d.named('HighlightNative'+side+kind+'PlotSlot')
  fill_remaining(content);fill_remaining(frame);fill_remaining(slot)
  gps=None;legend=None;direction_row=None
  if kind=='Heat':
   gps=one(nodes,lambda i:d.data(i).get('name')=='heat-map-description-frame','GPS description row')
   edit(gps,[(131081,d.enum('none'))])
   legend=one(nodes,lambda i:d.data(i).get('name')=='heat-maps-visuals-keys-frame','whole heatmap scale legend')
   edit(legend,[(327681,[d.num(.5),d.num(.5)])])
   arrow=one(nodes,lambda i:d.data(i).get('name')=='game-concepts-sort-arrow-up_small','direction arrow')
   direction_row=d.a(arrow)['m_Parent']['rid']
   children=d.a(direction_row)['m_Children']
   assert len(children)==2 and children[0]['rid']==arrow
   if home:
    d.a(direction_row)['m_Children']=[children[1],children[0]];allowed_assets.add(direction_row)
    assert 'margin-right-global-gap-regular' in d.a(arrow)['m_Classes']
    d.a(arrow)['m_Classes']=['margin-left-global-gap-regular' if c=='margin-right-global-gap-regular' else c for c in d.a(arrow)['m_Classes']]
    allowed_assets.add(arrow)
   else:
    for rid in subtree(d,direction_row):
     assert d.r[rid]==old_refs[rid]
     assert d.data(rid)==sd(old_refs,rid),'Away direction row changed'
  plot=one(nodes,lambda i:d.r.get(d.a(i).get('m_SerializedData',{}).get('rid'),{}).get('type',{}).get('class') in ['FMHeatMap/UxmlSerializedData','FMPassMapPanel/UxmlSerializedData'],'pitch renderer')
  assert d.r[plot]==old_refs[plot] and d.data(plot)==sd(old_refs,plot),'Plot orientation or live data changed'
  graph_audit.append({'side':side,'kind':kind,'card':card,'hidden_title_bar':title_frame,'hidden_gps_row':gps,'legend':legend,'legend_scale':.5 if legend else None,'direction_row':direction_row,'home_order':'text_then_arrow' if home and kind=='Heat' else None,'away_direction_unchanged':not home,'content_uses_released_title_space':True,'pitch_renderer_unchanged':plot})

lower=d.named('HighlightDataLowerHalf')
assert d.a(lower)['m_Children']==[{'rid':1011}]
assert d.data(1016)['name']=='statsOnlyView'
assert d.a(1011)['m_Children']==[{'rid':1015},{'rid':1016},{'rid':1017}]
legacy=d.add(native,1015,lower,'HighlightInactiveLegacyViews')
d.a(legacy)['m_Classes']=[];d.st(legacy,[(131081,d.enum('none'))])
d.move(1011,legacy);allowed_assets|={1011,lower}

# Duplicate the complete native page, preserving every text, event and binding record.
page_map={}
def clone_page(src,parent):
 original_data=native.data(src)
 new=d.add(native,src,parent,original_data.get('name',''))
 page_map[src]=new
 a=d.a(new)
 a['m_Classes']=copy.deepcopy(native.a(src).get('m_Classes',[]))
 a['m_Properties']=copy.deepcopy(native.a(src).get('m_Properties',[]))
 a['m_RuleIndex']=native.a(src).get('m_RuleIndex',-1)
 for key in ['name_UxmlAttributeFlags','pickingMode','pickingMode_UxmlAttributeFlags']:
  if key in original_data:d.data(new)[key]=original_data[key]
 alias=native.a(src).get('m_TemplateAlias')
 if alias:d.using(native,alias)
 for child in native.a(src).get('m_Children',[]):clone_page(child['rid'],new)
 return new
fixed=clone_page(1016,lower)
d.data(fixed).update(name='HighlightFixedStatsOnlyView',name_UxmlAttributeFlags=1)
# The native header retains its natural height; the three-column comparison takes the remaining height.
d.st(page_map[1026],[(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])

def selected_tab_dependency(value):
 if isinstance(value,dict):
  for key,item in value.items():
   if key=='m_argumentBytes' and isinstance(item,list) and b'selectedtab' in bytes(item).lower():return True
   if selected_tab_dependency(item):return True
 elif isinstance(value,list):return any(selected_tab_dependency(v) for v in value)
 elif isinstance(value,str):return value.lower() in ['selectedtab','highlightstatsonlydefaultv3']
 return False
native_counts=collections.Counter()
for src,new in page_map.items():
 expected=copy.deepcopy(native.data(src));expected['uxmlAssetId']=d.data(new)['uxmlAssetId']
 if src==1016:expected.update(name='HighlightFixedStatsOnlyView',name_UxmlAttributeFlags=1)
 assert d.data(new)==expected,('Native comparison content or binding changed',src)
 assert d.a(new)['m_Classes']==native.a(src).get('m_Classes',[])
 assert not selected_tab_dependency(d.data(new)),('Independent page still depends on old selector',src)
 expected_children=[{'rid':page_map[c['rid']]} for c in native.a(src).get('m_Children',[])]
 assert d.a(new)['m_Children']==expected_children,('Native data item order changed',src)
 serial=native.r[native.a(src)['m_SerializedData']['rid']]
 native_counts[serial['type']['class']]+=1
assert native_counts['SIProgressBar/UxmlSerializedData']==15
assert len(page_map)==len(list(subtree(native,1016)))
assert d.a(lower)['m_Children']==[{'rid':legacy},{'rid':fixed}]
assert d.a(legacy)['m_Children']==[{'rid':1011}]
assert d.a(1011)['m_Children']==native.a(1011)['m_Children']

for rid,record in old_refs.items():
 if rid not in allowed_assets:assert d.r[rid]==record,('Unrequested existing record changed',rid)
 else:
  expected=copy.deepcopy(record)
  for key in ['m_RuleIndex','m_Classes','m_Children','m_Parent']:expected['data'][key]=copy.deepcopy(d.r[rid]['data'][key])
  assert d.r[rid]==expected,('Unrequested serialized content changed',rid)
for i in [1001,1002,1004,1006,1008,1009,1013,1022,d.named('HighlightPitchUpperHalf'),d.named('HighlightHomeAnalysisColumn'),d.named('HighlightAwayAnalysisColumn')]:
 assert d.r[i]==old_refs[i] and d.data(i)==sd(old_refs,i),('Main layout or selector changed',i)
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value,('Existing stylesheet data changed',key)
 else:assert d.s[key]==value
d.save()

output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected,('Serialization roundtrip failed',pid)
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'passed':True,'graph_changes':graph_audit,'fixed_comparison':{'root':fixed,'source':'statsOnlyView','source_record':1016,'native_ui_nodes':len(page_map),'native_element_types':dict(native_counts),'native_text_events_data_bindings_and_order_preserved':True,'old_views_hidden_behind_unbound_container':legacy,'no_selected_tab_dependencies':True,'original_selector_options_structurally_cannot_control_this_page':[0,1,2]},'upper_lower_60_40_and_columns_25_50_25_unchanged':True,'main_pitch_and_chart_drawing_records_unchanged':True,'selector_position_style_options_and_binding_unchanged':True,'background_and_hidden_fixture_date_rows_preserved':True,'native_styles_and_unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 图表内容区及固定“仅数据”对比

- 隐藏四个图表的完整标题栏，隐藏两个热点图 GPS 说明行；容器改为使用剩余空间，传球图绘图区使用原标题占位。
- 主队方向行顺序改为文字、向右箭头，并将原右间距移到箭头左侧；客队方向行保持原样。
- 两个色阶图例组由 30% 改为 50%，不改变热点球场或其他字号。
- 下方独立复制完整原生 statsOnlyView：323 个 UI 节点、75 个文字节点、15 个比较条目，内容、顺序、事件和数据绑定逐条比较一致。
- 原三模式开关及其页面保持内部结构，整体放入新的无绑定隐藏容器。固定数据对比页是其兄弟节点，不受选择器选项 0/1/2 或历史选择影响。
- 原选择器的位置、外观、选项和绑定不变，其操作仅影响已隐藏的旧页面。
- 保持上下 60%/40%、横向 25%/50%/25%、区域高度、背景透明、原来已隐藏的对阵时间行、球场绘图和其方向。

控制资源：ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle 内 MatchViewer_12x4 及内联样式。
已通过原生页面内容和绑定一致性、层级/样式、序列化回读及无关对象校验。尚未在游戏里检查实际渲染和实时刷新。
退出游戏后运行 install.ps1 安装；restore.ps1 仅恢复本次修改。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'hidden_title_bars':4,'hidden_gps_rows':2,'legend_scale':.5,'independent_native_comparison_nodes':len(page_map),'comparison_items':15},ensure_ascii=False))
