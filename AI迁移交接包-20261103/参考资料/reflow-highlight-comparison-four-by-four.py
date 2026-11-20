from pathlib import Path
import json,collections,math

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-comparison-4x4-at75-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-visual-resource-and-load-codecs','exec'))

d=Doc(G,name='MatchViewer_12x4');old=copy.deepcopy(d.d);old_refs=refs(old);old_style=copy.deepcopy(d.s)
root=d.named('HighlightFixedStatsOnlyView')
def subtree(i,reference=None):
 ref=d.r if reference is None else reference
 yield i
 for child in ref[i]['data'].get('m_Children',[]):yield from subtree(child['rid'],ref)
def data_before(i):return sd(old_refs,i)
def one(nodes,predicate,label):
 found=[i for i in nodes if predicate(i)];assert len(found)==1,(label,found);return found[0]
nodes=list(subtree(root));box=one(nodes,lambda i:d.data(i).get('name')=='statsBox','comparison body')
columns=[x['rid'] for x in d.a(box)['m_Children']]
assert [d.data(i).get('name') for i in columns]==['leftStats','middleStats','rightStats']
original_columns=[[c['rid'] for c in d.a(i)['m_Children']] for i in columns]
assert all(len(c)==5 for c in original_columns)
ordered=[original_columns[c][row] for row in range(5) for c in range(3)]
expected_names=['Possession','ClearCutChances','Fouls','Shots','Corners','YellowCards','ShotsOnTarget','ProgressivePasses','RedCards','xG','PassesCompleted','DistanceCovered','OPPDA','CrossesCompleted','AvgRating']
assert [d.data(i)['name'] for i in ordered]==expected_names
item_nodes={item:list(subtree(item)) for item in ordered};all_item_nodes={i for items in item_nodes.values() for i in items}
assert len(ordered)==15 and len(all_item_nodes)==300

# Resolve the existing desktop style metrics. Bindings and percentage-based data widths are not edited.
style_sheets=[]
for bundle,selected_names in [('ui-styles_assets_common.bundle',{'SIStyles'}),('ui-styles_assets_default.bundle',{'AlwaysAppliedStyleSheet','FigmaStyleVariables'})]:
 style_env=UnityPy.load(str(GAME/bundle))
 for obj in style_env.objects:
  if obj.type.name=='MonoBehaviour' and obj.peek_name() in selected_names:style_sheets.append(obj.read_typetree())
definitions={};selectors=[]
for sheet_order,sheet in enumerate(style_sheets):
 for rule_order,rule in enumerate(sheet.get('m_Rules',[])):
  for prop in rule['m_Properties']:
   if prop.get('m_CustomName','').startswith('--'):definitions[prop['m_CustomName']]=(sheet,prop['m_Values'])
  for selector in rule['m_ComplexSelectors']:
   selectors.append((selector['m_Specificity'],sheet_order,rule_order,sheet,selector,rule['m_Properties']))
selectors.sort(key=lambda x:x[:3])

def match_parts(i,parts):
 a=old_refs[i]['data'];v=data_before(i)
 for part in parts:
  typ=part['m_Type'];value=part['m_Value']
  if typ==1:continue
  if typ==2:
   if value not in [a.get('m_FullTypeName'),a.get('m_FullTypeName','').rsplit('.',1)[-1]]:return False
  elif typ==3:
   if value not in a.get('m_Classes',[]):return False
  elif typ==6:
   if value!=v.get('name'):return False
  else:return False
 return True
def matches(i,selectors_,index=None):
 index=len(selectors_)-1 if index is None else index
 if not match_parts(i,selectors_[index]['m_Parts']):return False
 if index==0:return True
 relationship=selectors_[index]['m_PreviousRelationship'];parent=old_refs[i]['data'].get('m_Parent',{}).get('rid',-2)
 if relationship==1:return parent in old_refs and matches(parent,selectors_,index-1)
 if relationship==2:
  while parent in old_refs and parent!=-2:
   if matches(parent,selectors_,index-1):return True
   parent=old_refs[parent].get('data',{}).get('m_Parent',{}).get('rid',-2)
 return False

metric_ids={65537,65538,65539,65540,131076,131077,131078,131079,131080,131082,131087,131089,131090,131091,131092,131093,131094,131095,131096,131097,131098,131099,131100,131101,131103,131104,131105,196608,196609,196610,196611,262147,262148,262150,262151}
computed_cache={}
def computed(i):
 if i in computed_cache:return computed_cache[i]
 result={}
 for _,_,_,sheet,selector,properties in selectors:
  if matches(i,selector['m_Selectors']):
   for prop in properties:
    if prop['m_Id'] in metric_ids:result[prop['m_Id']]=(sheet,prop['m_Values'])
 idx=old_refs[i]['data'].get('m_RuleIndex',-1)
 if idx>=0:
  for prop in old_style['m_Rules'][idx]['m_Properties']:
   if prop['m_Id'] in metric_ids:result[prop['m_Id']]=(old_style,prop['m_Values'])
 computed_cache[i]=result;return result
def resolve(sheet,handles,seen=None):
 seen=set() if seen is None else seen
 if len(handles)==3 and handles[0]['m_ValueType']==10 and handles[2]['m_ValueType']==8:
  name=sheet['strings'][handles[2]['valueIndex']]
  assert name not in seen and name in definitions,('Unknown/cyclic metric variable',name)
  seen.add(name);other,values=definitions[name];return resolve(other,values,seen)
 result=[]
 for h in handles:
  typ=h['m_ValueType'];idx=h['valueIndex']
  if typ==1:result.append((1,idx))
  elif typ==2:result.append((2,sheet['floats'][idx]))
  elif typ==3:result.append((3,copy.deepcopy(sheet['dimensions'][idx])))
  else:return None
 return result
def font_metric(i):
 cursor=i
 while cursor in old_refs and cursor!=-2:
  if 65537 in computed(cursor):
   sheet,handles=computed(cursor)[65537];value=resolve(sheet,handles)
   if value:return value
  cursor=old_refs[cursor].get('data',{}).get('m_Parent',{}).get('rid',-2)
 return [(3,{'unit':1,'value':14.0})]
f32=lambda value:struct.unpack('<f',struct.pack('<f',value))[0]
allowed=set();metric_audit=[]
for i in sorted(all_item_nodes):
 metrics=copy.copy(computed(i))
 serial_type=d.r[d.a(i)['m_SerializedData']['rid']]['type']['class']
 if serial_type=='SIText/UxmlSerializedData' and 65537 not in metrics:metrics[65537]=(None,font_metric(i))
 props=[]
 for prop_id,(sheet,handles) in metrics.items():
  values=handles if sheet is None else resolve(sheet,handles)
  if values is None:continue
  scaled=[];changed=False;before_values=[];after_values=[]
  for typ,value in values:
   before_values.append(copy.deepcopy(value))
   if typ==3 and value['unit']==1:
    target=copy.deepcopy(value);target['value']=f32(target['value']*.75);scaled.append(d.val(3,target));after_values.append(target);changed=True
   elif typ==2:
    target=f32(value*.75);scaled.append(d.num(target));after_values.append(target);changed=True
   elif typ==3:scaled.append(d.val(3,value));after_values.append(copy.deepcopy(value))
   elif typ==1:scaled.append({'m_ValueType':1,'valueIndex':value});after_values.append(value)
  if changed:
   props.append((prop_id,scaled));metric_audit.append({'node':i,'property':prop_id,'before':before_values,'after':after_values})
 if props:d.st(i,props);allowed.add(i)

# Four equal rows, each with four equal cells. Only the lower comparison body is restructured.
def plain(parent,name):
 i=d.add(d,1015,parent,name);d.a(i)['m_Classes']=[];return i
d.st(box,[(131083,d.enum('column')),(131073,d.enum('stretch')),(131088,d.enum('flex-start')),(131096,d.px(0))]);allowed.add(box)
rows=[];cells=[];empty=None
for row_index in range(4):
 row=plain(box,'HighlightComparisonRow'+str(row_index+1));rows.append(row)
 d.st(row,[(131083,d.enum('row')),(131105,d.pct(100)),(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('stretch'))])
 for col_index in range(4):
  cell=plain(row,'HighlightComparisonCell'+str(row_index+1)+'_'+str(col_index+1));cells.append(cell)
  d.st(cell,[(131083,d.enum('column')),(131105,d.px(0)),(131082,d.px(0)),(131097,d.px(0)),(131087,d.pct(100)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('center')),(131088,d.enum('center'))])
  index=row_index*4+col_index
  if index==15:empty=cell;continue
  item=ordered[index];d.move(item,cell);allowed.add(item)
  d.st(item,[(131105,d.px(216)),(131095,d.pct(100)),(131087,{'m_ValueType':1,'valueIndex':2}),(131082,{'m_ValueType':1,'valueIndex':2}),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(1)),(131074,d.enum('center')),(131090,d.px(0)),(131093,d.px(0))])
  label,bar=[x['rid'] for x in d.a(item)['m_Children']]
  d.st(label,[(131105,d.pct(100)),(131074,d.enum('stretch'))]);allowed.add(label)
  d.st(bar,[(131095,d.pct(100)),(131097,d.px(0)),(131085,d.num(1))]);allowed.add(bar)

removed=set()
for i in columns:
 assert d.a(i)['m_Children']==[]
 d.a(box)['m_Children'].remove({'rid':i})
 removed|={i,d.a(i)['m_SerializedData']['rid']}
d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in removed]
for rid in removed:d.r.pop(rid)
assert d.a(box)['m_Children']==[{'rid':i} for i in rows]
assert d.a(empty)['m_Children']==[]
assert [d.data(d.a(cell)['m_Children'][0]['rid'])['name'] for cell in cells if d.a(cell)['m_Children']]==expected_names
assert len(set(ordered))==15
for item in ordered:
 for i in item_nodes[item]:
  assert d.data(i)==data_before(i),('Text, data binding, event or tooltip changed',i)
  assert d.a(i)['m_Classes']==old_refs[i]['data']['m_Classes']
  assert d.a(i)['m_Children']==old_refs[i]['data']['m_Children']
for rid,record in old_refs.items():
 if rid in removed:continue
 if rid not in allowed:assert d.r[rid]==record,('Out-of-scope record changed',rid)
 else:
  expected=copy.deepcopy(record)
  for key in ['m_RuleIndex','m_Parent','m_Children']:expected['data'][key]=copy.deepcopy(d.r[rid]['data'][key])
  assert d.r[rid]==expected,('Unexpected property or serialization change',rid)
for child in old_refs[root]['data']['m_Children']:
 if child['rid']==box:continue
 for i in subtree(child['rid'],old_refs):assert d.r[i]==old_refs[i] and d.data(i)==data_before(i),'Team header or footer changed'
assert d.a(root)==old_refs[root]['data']
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value
 else:assert d.s[key]==value

# Confirm the important native metrics were resolved and reduced, instead of scaling the whole page.
fonts=[];bar_heights=[];bar_widths=[]
for entry in metric_audit:
 if entry['property']==65537:fonts.append(entry)
 if entry['property']==131087 and entry['before']==[{'unit':1,'value':8.0}]:bar_heights.append(entry)
 if entry['property']==131105 and entry['before']==[{'unit':1,'value':288.0}]:bar_widths.append(entry)
assert len(fonts)==75 and len(bar_widths)==15
assert all(x['after']==[{'unit':1,'value':216.0}] for x in bar_widths)
assert len(bar_heights)>=15 and all(x['after']==[{'unit':1,'value':6.0}] for x in bar_heights)
assert any(x['before']==[{'unit':1,'value':14.0}] and x['after']==[{'unit':1,'value':10.5}] for x in fonts)
assert any(x['before']==[{'unit':1,'value':12.0}] and x['after']==[{'unit':1,'value':9.0}] for x in fonts)
d.save()

geometry=[]
for width,height in [(1920,1080),(2526,1379)]:
 data_width=(width-64)*.5-24
 lower_height=((height-280)-2)*.55
 # Header/footer keep their native size. Reserve 100px to bound their combined space conservatively.
 cell_width=data_width/4;cell_height=(lower_height-100)/4
 assert cell_width>=216 and cell_height>=40
 geometry.append({'viewport':[width,height],'four_equal_column_width':cell_width,'four_equal_row_height_with_100px_header_footer_reserve':cell_height,'comparison_width':216,'fit_checks_passed':True})

output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected,('Roundtrip failed',pid)
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'passed':True,'data_order':[expected_names[i:i+4] for i in range(0,15,4)],'rows':4,'columns':4,'last_cell_empty':True,'scale':.75,'scaled_pixel_metrics':metric_audit,'data_text_bindings_events_tooltips_and_colors_preserved':True,'team_names_badges_and_footer_unchanged':True,'lower_page_size_and_all_outer_layout_unchanged':True,'geometry_checks':geometry,'shared_templates_catalog_and_unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 下方15项数据对比：75%、四行四列

仅调整 HighlightFixedStatsOnlyView 内的15项数据对比：按原画面逐行顺序重排，每行4项，末行3项，右下角为空。
顺序：控球率/绝佳机会/犯规/射门；角球/黄牌/射正/推进传球；红牌/预期进球/传球成功/跑动距离；OPPDA/传中成功/平均评分/空。
从现有桌面样式读取像素尺寸并乘0.75：比较条288→216，条高8→6，名称字号12→9，数值字号14→10.5，内部间距同比缩小。没有对整个页面使用缩放变换。
四行等高、四列等宽，内容在单元格中居中；空间不足时比较条以单元格宽度为上限。
现有15个组件直接移动，75个文字节点及其绑定、事件、提示、颜色均未更改；队名、队徽、底部按钮不变。
整体5:10:5、中间上下45%/55%、2px间隔、横线和上方图表均不变。不更改共用模板或本地布局缓存。
通过重排顺序、尺寸计算、绑定一致性、序列化回读及无关对象检查。几何检查不是游戏实际渲染验证。
退出游戏后运行install.ps1安装；restore.ps1仅恢复本次修改。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'items':15,'rows':4,'columns':4,'scaled_text_nodes':len(fonts),'comparison_width':216,'team_header_and_footer_unchanged':True},ensure_ascii=False))
