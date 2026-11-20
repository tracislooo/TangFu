from pathlib import Path
import json

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-chart-details-only-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-live-resource-and-load-codecs','exec'))

d=Doc(G,name='MatchViewer_12x4')
old=copy.deepcopy(d.d);old_refs=refs(old);old_sheet=copy.deepcopy(d.s)
allowed_assets=set();allowed_serials=set();audit=[]
ROTATE=327680;SCALE=327681
f32=lambda value:struct.unpack('<f',struct.pack('<f',value))[0]
empty_function={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
background_classes={'layout-tile-interaction-button-background','layout-tile-interaction-button-background-highlighted','heat-map-tile-background','pass-map-block-inlay-background'}
background_names={'layout-tile-base-container','BackgroundStyleSetter','layout-tile-interaction-button','Border_TIle','states-templates-tile-content','heat_maps-large','pass-maps-large','heat_map-frame','pass-map-frame'}

def subtree(i):
 yield i
 for child in d.a(i).get('m_Children',[]):yield from subtree(child['rid'])
def one(nodes,predicate,label):
 result=[i for i in nodes if predicate(i)]
 assert len(result)==1,(label,result)
 return result[0]
def rule_properties(i):
 idx=d.a(i).get('m_RuleIndex',-1)
 return d.s['m_Rules'][idx]['m_Properties'] if idx>=0 else []
def edit(i,props):
 d.st(i,props);allowed_assets.add(i)

for home,side in [(True,'Home'),(False,'Away')]:
 for kind in ['Heat','Pass']:
  card=d.named('HighlightNative'+side+kind+'Card');nodes=list(subtree(card))
  caption=one(nodes,lambda i:d.data(i).get('name')=='title-text','module title')
  assert not any(p['m_Id']==65537 for p in rule_properties(caption)), 'Title already has a local font override; refusing a repeated subtraction'
  edit(caption,[(65537,d.px(9))])
  assert d.data(caption)==sd(old_refs,caption),'Native title text or formatting changed'

  if kind=='Heat':
   fixture=one(nodes,lambda i:d.data(i).get('name')=='teams-and-dates-frame','heat fixture/date row')
  else:
   fixture=one(nodes,lambda i:d.a(i).get('m_TemplateAlias')=='PassMapsFixtureTeamsAndDateTemplate','pass fixture/date row')
  edit(fixture,[(131081,d.enum('none'))])

  legend=None;arrow=None
  if kind=='Heat':
   legend=one(nodes,lambda i:d.data(i).get('name')=='heat-maps-visuals-keys-frame','heat scale legend')
   edit(legend,[(SCALE,[d.num(f32(.3)),d.num(f32(.3))])])
   arrow=one(nodes,lambda i:d.data(i).get('name')=='game-concepts-sort-arrow-up_small','direction arrow')
   edit(arrow,[(ROTATE,d.val(3,{'unit':5,'value':90.0 if home else -90.0}))])

  writer=one(nodes,lambda i:d.data(i).get('name')=='BackgroundStyleSetter','background class writer')
  writer_data=d.data(writer)
  assert writer_data['BindFunction']['m_target']['m_guid']=='d47d9f6bfe419344692270d5af16c5ef'
  assert b'layout-tile-interaction-button-background' in bytes(writer_data['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'])
  assert writer_data['PrimaryColorDataLink']['m_path']=='' and writer_data['SecondaryColorDataLink']['m_path']==''
  writer_data['BindFunction']=copy.deepcopy(empty_function)
  allowed_serials.add(d.a(writer)['m_SerializedData']['rid'])

  cleared=[]
  for i in nodes:
   if i!=card and d.data(i).get('name') not in background_names:continue
   d.a(i)['m_Classes']=[c for c in d.a(i).get('m_Classes',[]) if c not in background_classes]
   edit(i,[(458752,d.val(4,{'r':0.0,'g':0.0,'b':0.0,'a':0.0})),(458753,{'m_ValueType':1,'valueIndex':3})])
   cleared.append(i)
  plot=one(nodes,lambda i:d.r.get(d.a(i).get('m_SerializedData',{}).get('rid'),{}).get('type',{}).get('class') in ['FMHeatMap/UxmlSerializedData','FMPassMapPanel/UxmlSerializedData'],'native pitch drawing')
  assert plot not in allowed_assets
  assert d.r[plot]==old_refs[plot] and d.data(plot)==sd(old_refs,plot),'Plot direction, data, or pitch background changed'
  assert d.a(card)['m_Children']==old_refs[card]['data']['m_Children']
  audit.append({'side':side,'kind':kind,'card':card,'title':caption,'title_font_before':14,'title_font_after':9,'hidden_fixture_date_row':fixture,'legend_group':legend,'legend_uniform_scale':.3 if legend else None,'direction_arrow':arrow,'arrow_degrees':(90 if home else -90) if arrow else None,'transparent_background_nodes':cleared,'background_writer':writer,'background_dynamic_class_binding_disabled':True,'native_pitch_record_unchanged':plot})

assert len(audit)==4
assert sum(a['legend_group'] is not None for a in audit)==2
assert sum(a['direction_arrow'] is not None for a in audit)==2
assert len(allowed_serials)==4
assert set(d.r)==set(old_refs), 'Unexpected added or removed nodes'
for rid,record in old_refs.items():
 if rid not in allowed_assets|allowed_serials:assert d.r[rid]==record,('Out-of-scope record changed',rid)
 elif rid in allowed_assets:
  expected=copy.deepcopy(record);expected['data']['m_RuleIndex']=d.r[rid]['data']['m_RuleIndex']
  expected['data']['m_Classes']=d.r[rid]['data'].get('m_Classes',[])
  assert d.r[rid]==expected,('Unexpected layout or hierarchy change',rid)
 else:
  expected=copy.deepcopy(record);expected['data']['BindFunction']=copy.deepcopy(empty_function)
  assert d.r[rid]==expected,('Unexpected data binding change',rid)
for key,value in old_sheet.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value,('Existing stylesheet data modified',key)
 else:assert d.s[key]==value

font_nodes={a['title'] for a in audit};legend_nodes={a['legend_group'] for a in audit if a['legend_group']};arrow_nodes={a['direction_arrow'] for a in audit if a['direction_arrow']};date_nodes={a['hidden_fixture_date_row'] for a in audit}
background_nodes={i for a in audit for i in a['transparent_background_nodes']}
for i in allowed_assets:
 before_props={p['m_Id']:p for p in old_sheet['m_Rules'][old_refs[i]['data']['m_RuleIndex']]['m_Properties']} if old_refs[i]['data'].get('m_RuleIndex',-1)>=0 else {}
 after_props={p['m_Id']:p for p in rule_properties(i)}
 allowed_properties=set()
 if i in font_nodes:allowed_properties.add(65537)
 if i in legend_nodes:allowed_properties.add(SCALE)
 if i in arrow_nodes:allowed_properties.add(ROTATE)
 if i in date_nodes:allowed_properties.add(131081)
 if i in background_nodes:allowed_properties|={458752,458753}
 for key in set(before_props)|set(after_props):
  if key not in allowed_properties:assert before_props.get(key)==after_props.get(key),('Unrequested style change',i,key)
 if i in background_nodes:
  color=after_props[458752]['m_Values'][0];assert d.s['colors'][color['valueIndex']]['a']==0.0
  assert after_props[458753]['m_Values']==[{'m_ValueType':1,'valueIndex':3}]
 if i in date_nodes:
  value=after_props[131081]['m_Values'][0];assert d.s['strings'][value['valueIndex']]=='none'
 if i in legend_nodes:
  assert len(after_props[SCALE]['m_Values'])==2
  assert all(abs(d.s['floats'][v['valueIndex']]-.3)<1e-6 for v in after_props[SCALE]['m_Values'])

for i in [1001,1002,1004,1006,1008,1009,1011,1013,1016,1022,d.named('HighlightPitchUpperHalf'),d.named('HighlightDataLowerHalf'),d.named('HighlightHomeAnalysisColumn'),d.named('HighlightAwayAnalysisColumn')]:
 assert d.r[i]==old_refs[i] and d.data(i)==sd(old_refs,i),('Main layout, selector, or data view changed',i)
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
report={'passed':True,'template':'MatchViewer_12x4','private_chart_changes':audit,'only_requested_style_properties_changed':True,'all_text_content_and_other_font_sizes_unchanged':True,'all_nodes_and_hierarchy_unchanged':True,'only_four_background_style_functions_disabled':True,'pitch_graphics_and_live_data_bindings_unchanged':True,'upper_lower_60_40_and_columns_25_50_25_unchanged':True,'selector_and_native_stats_only_page_unchanged':True,'existing_style_pools_and_rules_unchanged':True,'shared_templates_catalog_and_unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 中间区域四个图表的定点调整

只针对当前安装资源中 MatchViewer_12x4 的四个私有图表进行修改：

1. 四个标题字号 14→9；标题原内容、颜色、字重、位置不变。
2. 两个热点图对阵日期容器、两个传球图对阵日期模板设为 display:none，整行不显示且不占布局空间。
3. 两个色阶图例组整体等比缩放为 30%，包含色块及强弱标签；图例原有对齐及其他布局不变。
4. 只旋转热点图方向提示的箭头图标：主队 +90° 向右，客队 -90° 向左；文字及所在行不变。
5. 清除四个模块的底板、内衬背景色/背景图，停用其背景加类函数。球场绘图、底色、热点色块、球员及连线完全不改。

未新增或删除 UI 节点；未改节点层级。除上述样式及四个背景函数外，所有已有记录均逐项比较一致。
上下 60%/40%、横向 25%/50%/25%、区域高度、下方“仅数据”、选择器、外层网格和共用模板均保持原样。
通过样式差异白名单检查、文字/数据绑定一致性检查、序列化回读与无关对象校验。
尚未在游戏内检查真实显示、悬停及选中状态。

退出游戏后运行 install.ps1 安装；restore.ps1 用于只恢复本次修改。原始文件在 backup-game / backup-skin 中。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'titles':4,'fixture_date_rows_hidden':4,'legends':2,'arrows':2,'background_functions_disabled':4,'no_layout_or_data_binding_changes':True},ensure_ascii=False))
