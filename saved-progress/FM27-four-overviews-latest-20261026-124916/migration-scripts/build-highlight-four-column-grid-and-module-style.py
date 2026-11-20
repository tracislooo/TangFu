from pathlib import Path
import json, ast

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-4x4-75-dividers-transparent-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-resources-and-load-codecs','exec'))
env[W]=UnityPy.load(str(GAME/W));objs[W]={o.path_id:o for o in env[W].objects}
d=Doc(G,name='MatchViewer_12x4')
old=copy.deepcopy(d.d);old_refs=refs(old);old_style=copy.deepcopy(d.s)
previous=R/'highlight-lower-5x3-at55-charts-20261024-135416'
previous_manifest=json.loads((previous/'manifest.json').read_text('utf8'))
assert sha(before[GAME/G])==previous_manifest['after_sha256'][G], 'Installed baseline differs from the confirmed page'
modules=previous_manifest['layout']['modules']
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
AUTO={'m_ValueType':1,'valueIndex':2}
allowed=set();removed=set();converted=set();serialization_changes=set();clone_audits=[]

def subtree(i,reference=None):
 reference=d.r if reference is None else reference
 yield i
 for c in reference[i]['data'].get('m_Children',[]):yield from subtree(c['rid'],reference)
def plain(parent,name):return d.add(d,1015,parent,name)
def clear_spacing(i):d.st(i,[(p,d.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
def fill(i):d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
def transparent(i):d.st(i,[(458752,d.val(4,{'r':0.0,'g':0.0,'b':0.0,'a':0.0})),(458753,{'m_ValueType':1,'valueIndex':3})])

helper_ast=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper_ast.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'native-subtree-cloner','exec'))

template_cache={}
def resolve_template(alias):
 u=next(u for u in d.d['m_Usings'] if u['alias']==alias);guid=u['path']
 if guid in template_cache:return template_cache[guid]
 hits=[]
 for bundle in [G,W]:
  for key,ptr in env[bundle].container.items():
   if key!=guid:continue
   obj=objs[bundle].get(ptr.path_id)
   if obj is None or obj.type.name!='MonoBehaviour':continue
   tree=obj.read_typetree()
   if 'm_VisualTree' in tree:hits.append((bundle,obj.path_id))
 assert len(set(hits))==1,('Unresolved native template GUID',alias,guid,hits)
 bundle,pid=hits[0];result=Doc(bundle,pid=pid);template_cache[guid]=result;return result

override_audit=[]
def expand_template(i):
 a=d.a(i);assert d.r[i]['type']['class']=='TemplateAsset'
 assert not a.get('m_AttributeOverrides') and not a.get('m_SlotUsages')
 alias=a['m_TemplateAlias'];donor=resolve_template(alias)
 children=[x['rid'] for x in a['m_Children']]
 overrides=copy.deepcopy(a.get('m_SerializedDataOverride',[]))
 source_root=donor.d['references']['RefIds'][0]['rid']
 roots=donor.a(donor.d['m_VisualTree']['rid'])['m_Children'];assert len(roots)==1
 source_root=roots[0]['rid']
 native_root,mapping=clone_native(donor,source_root,i)
 ids={donor.a(j)['m_Id']:j for j in mapping if 'm_Parent' in donor.r[j]['data']}
 for override in overrides:
  source_id=ids.get(override['m_ElementId']);assert source_id is not None,('Native override target missing',alias,override)
  target=d.data(mapping[source_id]);value=d.r[override['m_SerializedData']['rid']]['data']
  for flag,enabled in value.items():
   if not flag.endswith('_UxmlAttributeFlags') or not enabled&1:continue
   field=flag[:-len('_UxmlAttributeFlags')]
   assert field in value and field in target,(alias,field)
   target[field]=copy.deepcopy(value[field]);target[flag]=enabled
   override_audit.append({'alias':alias,'field':field,'target':mapping[source_id],'value':copy.deepcopy(value[field])})
 content_id=donor.d['m_ContentContainerId']
 slot=mapping[ids[content_id]] if content_id else native_root
 for child in children:d.move(child,slot);allowed.add(child)
 old_a=copy.deepcopy(d.a(i));serial=old_a['m_SerializedData']['rid'];old_serial=copy.deepcopy(d.r[serial]['data'])
 prototype=d.r[1015];new_a=copy.deepcopy(prototype['data'])
 for key in new_a:
  if key in old_a:new_a[key]=copy.deepcopy(old_a[key])
 new_a['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
 new_a['m_Children']=[{'rid':native_root}]
 d.r[i]['type']=copy.deepcopy(prototype['type']);d.r[i]['data']=new_a
 prototype_serial=d.r[d.a(1015)['m_SerializedData']['rid']]
 new_serial=copy.deepcopy(prototype_serial['data'])
 for key in new_serial:
  if key in old_serial:new_serial[key]=copy.deepcopy(old_serial[key])
 d.r[serial]['type']=copy.deepcopy(prototype_serial['type']);d.r[serial]['data']=new_serial
 converted.update({i,serial});allowed.add(i)
 return native_root,mapping,donor

root=2429;box=2465;header=2431;button=3073
rows=[x['rid'] for x in d.a(box)['m_Children']];assert len(rows)==3
cells=[x['rid'] for row in rows for x in d.a(row)['m_Children']];assert len(cells)==15
items=[d.a(cell)['m_Children'][0]['rid'] for cell in cells]
names=['Possession','ClearCutChances','Fouls','Shots','Corners','YellowCards','ShotsOnTarget','ProgressivePasses','RedCards','xG','PassesCompleted','DistanceCovered','OPPDA','CrossesCompleted','AvgRating']
assert [d.data(i)['name'] for i in items]==names
item_nodes={item:list(subtree(item)) for item in items}
original_metrics=json.loads((R/'highlight-comparison-4x4-at75-20261024-133734/verification.json').read_text('utf8'))['scaled_pixel_metrics']
for entry in original_metrics:
 vals=[]
 for original in entry['before']:
  if isinstance(original,dict):
   value=copy.deepcopy(original)
   if value['unit']==1:value['value']=f32(value['value']*.75)
   vals.append(d.val(3,value))
  elif isinstance(original,(int,float)):vals.append(d.num(f32(original*.75)))
  else:raise AssertionError(entry)
 d.st(entry['node'],[(entry['property'],vals)]);allowed.add(entry['node'])
rows.append(plain(box,'HighlightComparisonRow4'))
cells.append(plain(rows[-1],'HighlightComparisonButtonCell'))
for ri,row in enumerate(rows):
 d.st(row,[(131102,d.enum('relative')),(131083,d.enum('row')),(131105,d.pct(100)),(131087,AUTO),(131082,AUTO),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131073,d.enum('stretch'))]);clear_spacing(row)
 d.st(row,[(131090,d.px(3 if ri<3 else 0))]);allowed.add(row)
 for ci in range(4):
  index=ri*4+ci;cell=cells[index];d.move(cell,row);allowed.add(cell)
  d.st(cell,[(131083,d.enum('column')),(131105,d.px(0)),(131082,d.px(0)),(131097,d.px(0)),(131087,AUTO),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('center')),(131088,d.enum('center'))]);clear_spacing(cell)
  if index==15:continue
  item=items[index]
  d.st(item,[(131105,d.px(216)),(131095,d.pct(100)),(131087,AUTO),(131082,AUTO),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(1)),(131074,d.enum('center')),(131090,d.px(0)),(131093,d.px(0))]);allowed.add(item)
  label,bar=[x['rid'] for x in d.a(item)['m_Children']]
  d.st(label,[(131105,d.pct(100)),(131074,d.enum('stretch'))]);allowed.add(label)
  d.st(bar,[(131095,d.pct(100)),(131097,d.px(0)),(131085,d.num(1))]);allowed.add(bar)
old_button_host=d.a(button)['m_Parent']['rid'];d.move(button,cells[-1]);allowed.add(button)
assert not d.a(old_button_host)['m_Children']
d.a(root)['m_Children'].remove({'rid':old_button_host});allowed.add(root)
removed|={old_button_host,d.a(old_button_host)['m_SerializedData']['rid']}
d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in removed]
for i in removed:d.r.pop(i)
d.st(button,[(131074,d.enum('center'))]);clear_spacing(button)

for i in [2443,2447,2459,2463]:
 expand_template(i)
for i in list(subtree(header)):
 if d.r[i]['type']['class']=='TemplateAsset':expand_template(i)
button_root,button_mapping,button_donor=expand_template(button)

css_refs=refs(copy.deepcopy(d.d));css_style=copy.deepcopy(d.s)
resolver=(R/'reflow-highlight-comparison-four-by-four.py').read_text('utf8').split('# Resolve the existing desktop style metrics.')[1].split('\n',1)[1].split('f32=lambda value:')[0]
resolver=resolver.replace('old_refs','css_refs').replace('old_style','css_style').replace('data_before(i)','sd(css_refs,i)')
exec(compile(resolver,'resolve-native-header-and-button-metrics','exec'))
size_audit=[]
def scale_nodes(nodes,scale,label):
 plans=[]
 for i in nodes:
  if 'm_Parent' not in d.a(i) or d.r[i]['type']['class']=='UxmlObjectAsset':continue
  values=copy.copy(computed(i));serial=d.a(i).get('m_SerializedData',{}).get('rid',-2)
  if serial in d.r and d.r[serial]['type']['class'] in ['SIText/UxmlSerializedData','Label/UxmlSerializedData'] and 65537 not in values:values[65537]=(None,font_metric(i))
  plans.append((i,values))
 for i,metrics_ in plans:
  props=[]
  for prop,(sheet,handles) in metrics_.items():
   resolved=handles if sheet is None else resolve(sheet,handles)
   if resolved is None:continue
   out=[];before_=[];after_=[];changed=False
   for typ,value in resolved:
    before_.append(copy.deepcopy(value))
    if typ==3:
     new=copy.deepcopy(value)
     if value['unit']==1:new['value']=f32(value['value']*scale);changed=True
     out.append(d.val(3,new));after_.append(new)
    elif typ==2:
     new=f32(value*scale);out.append(d.num(new));after_.append(new);changed=True
    elif typ==1:out.append({'m_ValueType':1,'valueIndex':value});after_.append(value)
   if changed:
    props.append((prop,out));size_audit.append({'group':label,'node':i,'property':prop,'original':before_,'scaled':after_,'scale':scale})
  if props:d.st(i,props);allowed.add(i)
scale_nodes(list(subtree(header)),.75,'team_names_and_badges')
scale_nodes(list(subtree(button)),.5,'view_data_button')

lines=[]
def divider(parent,name,vertical=False):
 i=plain(parent,name);d.a(i)['m_Classes']=copy.deepcopy(d.a(3077)['m_Classes'])
 d.st(i,[(131102,d.enum('absolute')),(131097,d.px(0)),(131096,d.px(0)),(131076,d.px(0)),(131077,d.px(1 if vertical else 0)),(131078,d.px(0)),(131079,d.px(0 if vertical else 1))])
 lines.append(i);return i
for ri,row in enumerate(rows[:3]):
 line=divider(row,'HighlightDataRowDivider'+str(ri+1))
 d.st(line,[(131089,d.px(0)),(131103,d.px(0)),(131080,d.px(-2)),(131087,d.px(0))])
d.st(box,[(131102,d.enum('relative'))]);allowed.add(box)
for ci in range(1,4):
 line=divider(box,'HighlightDataColumnDivider'+str(ci),True)
 d.st(line,[(131089,d.pct(ci*25)),(131104,d.px(0)),(131080,d.px(0)),(131105,d.px(0)),(131087,AUTO)])

module_style_audit=[]
for module in modules:
 candidates=[i for i in subtree(module['root']) if d.a(i).get('m_TemplateAlias') in ['tile-wide-4x2','tile-square-4x4']];assert len(candidates)==1
 wrapper=candidates[0]
 base_root,mapping,base=expand_template(wrapper)
 fill(base_root)
 for source_id in [1002,1004,1006,1008]:
  target=mapping[source_id];fill(target);transparent(target)
 for source_id in [1010,1011,1012]:transparent(mapping[source_id])
 setter=mapping[1006]
 d.data(setter)['BindFunction']['m_target']['m_guid']=''
 serialization_changes.add(d.a(setter)['m_SerializedData']['rid'])
 frame,scroller,title=mapping[1011],mapping[1016],mapping[1020]
 d.st(frame,[(131105,d.pct(100)),(131073,d.enum('center')),(131088,d.enum('center'))])
 d.st(mapping[1015],[(131081,d.enum('none'))])
 d.st(scroller,[(131105,d.pct(100)),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131074,d.enum('center'))])
 d.st(title,[(131105,d.pct(100)),(131097,d.px(0)),(131074,d.enum('center')),(65546,d.enum('middle-center'))])
 transparent(module['plot']);allowed.add(module['plot'])
 # Card transparency is independent of native field paint and chart data.
 for target in [module['cell'],module['scope'],module['root'],wrapper]:transparent(target);allowed.add(target)
 module_style_audit.append({'module':module['module'],'wrapper':wrapper,'private_base':base_root,'background_setter':setter,'title':title,'native_caption':copy.deepcopy(d.data(title)['TextBinding']),'plot':module['plot']})

activity=next(m for m in modules if m['module']=='ActionZones')
keys=[i for i in subtree(activity['root']) if d.data(i).get('name')=='HomeAndAwayKey'];assert len(keys)==2
for i in keys:
 d.st(i,[(131081,d.enum('none')),(131087,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0))]);clear_spacing(i);allowed.add(i)

for audit in override_audit:
 assert d.data(audit['target'])[audit['field']]==audit['value'],('Native override changed',audit['alias'],audit['field'])
for branch in item_nodes.values():
 for i in branch:
  assert d.data(i)==sd(old_refs,i),('Data binding/text/event changed',i)
  assert d.a(i)['m_Classes']==old_refs[i]['data']['m_Classes']
for i in subtree(header,old_refs):
 if i not in converted:assert d.data(i)==sd(old_refs,i),('Original team binding changed',i)
for rid,record in old_refs.items():
 if rid in removed or rid in converted:continue
 if rid not in allowed:assert d.r[rid]==record,('Out-of-scope record changed',rid)
 else:
  expected=copy.deepcopy(record)
  for key in ['m_RuleIndex','m_Parent','m_Children']:
   if key in expected.get('data',{}):expected['data'][key]=copy.deepcopy(d.r[rid]['data'][key])
  assert d.r[rid]==expected,('Unexpected existing field changed',rid)
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value
 else:assert d.s[key]==value
for i in [2147,2149,3075,3077]:assert d.r[i]==old_refs[i],('Upper/lower sizing or original divider changed',i)
assert len(lines)==6 and d.a(button)['m_Parent']['rid']==cells[-1]
assert len([x for x in size_audit if x['group']=='team_names_and_badges' and x['property']==65537])>=4
assert any(x['group']=='view_data_button' and x['property']==65537 for x in size_audit)

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
geometry=[]
for width,height in [(1920,1080),(2526,1379)]:
 data_width=(width-64)*.5-24;lower_height=(height-282)*.55
 reserve_header=60;reserve_rows=4*40+9;remaining=lower_height-reserve_header-reserve_rows
 assert data_width/4>=217 and remaining>150
 geometry.append({'viewport':[width,height],'cell_width':data_width/4,'comparison_width':216,'static_header_budget':reserve_header,'static_four_rows_budget':reserve_rows,'remaining_chart_height':remaining,'static_budget_only':True})
report={'passed':True,'rows':4,'columns':4,'data_order':[names[i:i+4] for i in range(0,15,4)],'data_scale_original':.75,'button_cell':[4,4],'button_scale_original':.5,'header_names_badges_scale_original':.75,'row_gaps_px':[3,3,3],'horizontal_lines':lines[:3],'vertical_lines':lines[3:],'line_width_px':1,'line_color_class':d.a(3077)['m_Classes'],'scale_audit':size_audit,'modules':modules,'module_style':module_style_audit,'activity_legends_hidden':keys,'private_template_expansion_count':len(clone_audits),'native_override_audit':override_audit,'existing_data_bindings_events_tooltips_colors_preserved':True,'native_module_bindings_and_paint_parameters_preserved':True,'card_and_plot_backdrops_transparent_pitch_paint_preserved':True,'outer_5_10_5_middle_45_55_separator_upper_charts_unchanged':True,'shared_templates_catalog_cache_and_unrelated_objects_unchanged':True,'geometry_checks':geometry,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 中间下半区：75%四列、按钮50%、分隔线与透明模块

15项比较组件恢复原始75%，前三行每行4项，第四行3项：控球率/绝佳机会/犯规/射门；角球/黄牌/射正/推进传球；红牌/预期进球/传球成功/跑动距离；OPPDA/传中成功/平均评分/查看数据按钮。
按钮移到第四行第四列居中，实际文字、尺寸、间距和点击区域缩至原始50%；移除顶部按钮容器。队名、队徽及内部间距通过本页私有展开的俱乐部/国家队组件缩为原始75%，保留原绑定和导航事件。
数据区按内容占高，四列等宽；行距3px，其中居中放1px横线，共3条；列间3条1px竖线贯穿4行，不加外边框。颜色沿用原有中间横线的主题边框颜色。
下方三个模块仍等宽等高使用剩余空间，卡片底板与绘图区衬底透明；仅在三个私有实例关闭背景设置器，保留球场底色、线条、图形和实时绑定。原生标题内容、字号、颜色不变，位置改为各模块顶部居中。
活动区域有数据与无数据两分支的底部颜色/队名图例均隐藏且收回占位；方向提示保留。
只修改已安装的MatchViewer_12x4及其内联样式，共用模板、外层5:10:5、中间45%/55%、2px分隔区和上方图表、本地布局缓存均不改。
已进行序列化回读、原生覆盖字段与绑定事件一致性、尺寸和分隔线检查、无关对象哈希检查。1920×1080与2526×1379仅做静态空间预算，尚未进行游戏内实际渲染、点击或实时刷新验证。
退出游戏后安装；restore.ps1仅恢复本次修改。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'rows':4,'columns':4,'data_scale':.75,'button_scale':.5,'header_scale':.75,'lines':6,'native_overrides_preserved':len(override_audit),'serialization_roundtrip':True,'runtime_verified':False},ensure_ascii=False))
