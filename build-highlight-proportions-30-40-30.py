from pathlib import Path
import json,math
from importlib.util import spec_from_file_location,module_from_spec

R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-30-40-30-split55-45-').replace('NAMES=[W,G,M,F]','NAMES=[G,T]')
exec(compile(boot,'backup-live-resources-and-load-codecs','exec'))
spec=spec_from_file_location('grid_migration',R/'highlight-grid-migration.py');migration=module_from_spec(spec);spec.loader.exec_module(migration)

CK='<Configurations>k__BackingField'
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
cache_versions={};layout_audits=[];descriptor_audits=[]
available=set()
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 for ref in find(T,name).read_typetree()['m_gridElementDescriptions']:
  assert ref['m_FileID']==0;available.add(ref['m_PathID'])
for name in layout_names:
 for block in find(T,name).read_typetree()['m_gridComponents']:
  for ref in block['m_configDescriptions']:available.add(ref['m_PathID'])
  for config in block['m_gridElementConfigs']:available.add(config['Description']['m_PathID'])
# Add width-six configurations using the same native assets, preserving every existing configuration.
for pid in sorted(available):
 obj=objs[T][pid];tree=obj.read_typetree()
 if CK not in tree:continue
 previous=copy.deepcopy(tree);configs=tree[CK];additions=[]
 for config in previous[CK]:
  if config['Size']['x']!=4:continue
  candidate=copy.deepcopy(config);candidate['Size']['x']=6
  if candidate not in configs:configs.append(candidate);additions.append(candidate['Size'])
 if additions:
  assert configs[:len(previous[CK])]==previous[CK]
  assert all(tree[k]==v for k,v in previous.items() if k!=CK)
  obj.save_typetree(tree);changes[T][pid]=tree
  descriptor_audits.append({'name':tree['m_Name'],'path_id':pid,'added_sizes':additions,'existing_configs_preserved':True})
viewer_obj=objs[T][2268119280419395392];viewer=viewer_obj.read_typetree();old_viewer=copy.deepcopy(viewer)
wide=next(copy.deepcopy(c) for c in viewer[CK] if c['Size']=={'x':12,'y':8})
center_config=copy.deepcopy(wide);center_config['Size']={'x':8,'y':8}
if center_config not in viewer[CK]:viewer[CK].append(center_config)
assert center_config['AssetRef']==wide['AssetRef']
viewer_obj.save_typetree(viewer);changes[T][viewer_obj.path_id]=viewer

for name in layout_names:
 obj=find(T,name);original=obj.read_typetree();version=original['m_compositionVersion']+1
 tree=migration.migrate_layout(original,version=version)
 for block in tree['m_gridComponents']:
  if not block['m_gridElementConfigs']:
   width=block['m_location']['width'];height=block['m_location']['height']
   options=[]
   for ref in block['m_configDescriptions']:
    options.extend(changes[T].get(ref['m_PathID'],objs[T][ref['m_PathID']].read_typetree()).get(CK,[]))
   match=next(copy.deepcopy(c) for c in options if c['Size']=={'x':width,'y':height})
   block['m_gridElementConfigs']=[match]
  for config in block['m_gridElementConfigs']:
   descriptor=changes[T].get(config['Description']['m_PathID'],objs[T][config['Description']['m_PathID']].read_typetree())
   assert config in descriptor[CK],('New size has no matching native asset',name,block['m_elementID'],config['Size'])
 obj.save_typetree(tree);changes[T][obj.path_id]=tree
 (OUT/'templates'/(name+'.json')).write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8')
 cache_versions[name]={'before':original['m_compositionVersion'],'after':version}
 layout_audits.append({'name':name,'columns':[6,8,6],'selected_modules':[c['m_elementID'] for c in tree['m_gridComponents']],'positions':{c['m_elementID']:c['m_location'] for c in tree['m_gridComponents']},'all_160_cells_covered_without_overlaps':True})

d=Doc(G,name='MatchViewer_12x4');old=copy.deepcopy(d.d);old_refs=refs(old);old_style=copy.deepcopy(d.s)
allowed=set();removed=set();heat_audits=[]
def subtree(i):
 yield i
 for child in d.a(i).get('m_Children',[]):yield from subtree(child['rid'])
def one(nodes,predicate,label):
 found=[i for i in nodes if predicate(i)];assert len(found)==1,(label,found);return found[0]
def edit(i,props):d.st(i,props);allowed.add(i)
def plain(parent,name):
 i=d.add(d,1015,parent,name);d.a(i)['m_Classes']=[];return i
def rule_properties(i):
 idx=d.a(i).get('m_RuleIndex',-1)
 return d.s['m_Rules'][idx]['m_Properties'] if idx>=0 else []

# Remove the entire old selector subtree. Its unused state remains isolated in the hidden legacy view.
selector_nodes=list(subtree(1009))
for i in selector_nodes:
 removed.add(i);removed.add(d.a(i)['m_SerializedData']['rid'])
parent=d.a(1009)['m_Parent']['rid'];d.a(parent)['m_Children'].remove({'rid':1009});allowed.add(parent)
d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in removed]
for rid in removed:d.r.pop(rid)

upper=d.named('HighlightPitchUpperHalf');lower=d.named('HighlightDataLowerHalf')
assert d.a(1008)['m_Children']==[{'rid':upper},{'rid':lower}]
edit(1008,[(131083,d.enum('column')),(131101,d.px(0)),(131098,d.px(0))])
for node,grow in [(upper,55),(lower,45)]:
 edit(node,[(131102,d.enum('relative')),(131104,d.px(0)),(131089,d.px(0)),(131103,d.px(0)),(131080,d.px(0)),(131105,d.pct(100)),(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131084,d.num(grow)),(131085,d.num(1)),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0))])
edit(upper,[(131098,d.px(0))])
separator=plain(1008,'HighlightTwoPixelSeparator')
d.move(separator,1008,1)
d.st(separator,[(131102,d.enum('relative')),(131105,d.pct(100)),(131087,d.px(2)),(131096,d.px(2)),(131094,d.px(2)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
line=plain(separator,'HighlightMiddleDividerLine')
d.a(line)['m_Classes']=['border-color-layout-modules-block-border-colour']
d.st(line,[(131102,d.enum('absolute')),(131104,d.px(.5)),(131089,d.px(0)),(131103,d.px(0)),(131087,d.px(0)),(131079,d.px(1)),(131076,d.px(0)),(131077,d.px(0)),(131078,d.px(0))])
assert d.a(1008)['m_Children']==[{'rid':upper},{'rid':separator},{'rid':lower}]

# Resolve the native default style values instead of inventing sizes for the legend.
style_env=UnityPy.load(str(GAME/'ui-styles_assets_default.bundle'));definitions={};square_size=None
for obj in style_env.objects:
 if obj.type.name!='MonoBehaviour':continue
 sheet=obj.read_typetree()
 if sheet.get('m_Name') not in ['AlwaysAppliedStyleSheet','FigmaStyleVariables']:continue
 for rule in sheet.get('m_Rules',[]):
  for prop in rule['m_Properties']:
   if prop.get('m_CustomName','').startswith('--'):definitions[prop['m_CustomName']]=(sheet,prop['m_Values'])
  if any(len(sel['m_Selectors'])==1 and sel['m_Selectors'][0]['m_Parts']==[{'m_Value':'data_display-graphs-data_points-large-square','m_Type':3}] for sel in rule['m_ComplexSelectors']):
   width=next((p for p in rule['m_Properties'] if p['m_Id']==131105),None)
   if width:
    value=width['m_Values'][0];square_size=sheet['dimensions'][value['valueIndex']]['value']
def scalar(name,seen=None):
 seen=set() if seen is None else seen;assert name not in seen;seen.add(name)
 sheet,values=definitions[name]
 refs=[sheet['strings'][v['valueIndex']] for v in values if v['m_ValueType']==8]
 if refs:return scalar(refs[0],seen)
 dimensions=[sheet['dimensions'][v['valueIndex']]['value'] for v in values if v['m_ValueType']==3]
 assert len(dimensions)==1;return dimensions[0]
font_size=scalar('--label-regular-size');micro=scalar('--global-gap-micro');close=scalar('--global-gap-close')
assert square_size==16 and font_size==14

for side in ['Home','Away']:
 card=d.named('HighlightNative'+side+'HeatCard');nodes=list(subtree(card))
 frame=one(nodes,lambda i:d.data(i).get('name')=='heat_map-frame','heatmap frame')
 direction=one(nodes,lambda i:d.data(i).get('name')=='direction-of-play-frame' and len(d.a(i)['m_Children'])==2,'direction text and arrow group')
 direction_parent=d.a(direction)['m_Parent']['rid']
 legend=one(nodes,lambda i:d.data(i).get('name')=='heat-maps-visuals-keys-frame','color legend')
 legend_parent=d.a(legend)['m_Parent']['rid']
 slot=d.named('HighlightNative'+side+'HeatPlotSlot')
 for node in [direction_parent,direction]:
  edit(node,[(131073,d.enum('center')),(131088,d.enum('center')),(131074,d.enum('center')),(131084,d.num(0)),(131085,d.num(0)),(131087,{'m_ValueType':1,'valueIndex':2}),(131105,d.pct(100) if node==direction_parent else {'m_ValueType':1,'valueIndex':2}),(131093,d.px(0)),(131090,d.px(0)),(131091,d.px(0)),(131092,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
 for child in d.a(direction)['m_Children']:edit(child['rid'],[(131084,d.num(0)),(131085,d.num(0))])
 edit(frame,[(131083,d.enum('column')),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0)),(131098,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
 edit(slot,[(131105,d.pct(100)),(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
 # Remove the native chrome's fixed-height constraint along this heatmap's own ancestor path.
 cursor=d.a(frame)['m_Parent']['rid']
 while cursor!=card:
  if d.data(cursor).get('name')!='states-templates-tile-content':
   edit(cursor,[(131087,d.pct(100)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
  cursor=d.a(cursor)['m_Parent']['rid']
 edit(legend_parent,[(131105,d.pct(100)),(131087,{'m_ValueType':1,'valueIndex':2}),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131073,d.enum('center')),(131088,d.enum('center')),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
 native_pixel_props=[]
 for prop in list(rule_properties(legend)):
  if prop['m_Id'] in [131101,131098,131099,131100,327681]:continue
  vals=[];has_pixels=False
  for value in prop['m_Values']:
   if value['m_ValueType']==3 and d.s['dimensions'][value['valueIndex']]['unit']==1:
    vals.append(d.px(d.s['dimensions'][value['valueIndex']]['value']*.75));has_pixels=True
   else:vals.append(copy.deepcopy(value))
  if has_pixels:native_pixel_props.append((prop['m_Id'],vals))
 # Scale the actual legend metrics, not just its transform, so unused unscaled space is reclaimed.
 edit(legend,native_pixel_props+[(327681,[d.num(1),d.num(1)]),(131074,d.enum('center')),(131105,{'m_ValueType':1,'valueIndex':2}),(131084,d.num(0)),(131085,d.num(0)),(131101,d.px(0)),(131098,d.px(0)),(131099,d.px(0)),(131100,d.px(0))])
 for child in d.a(legend)['m_Children']:
  node=child['rid'];classes=d.a(node)['m_Classes'];props=[]
  typ=d.r[d.a(node)['m_SerializedData']['rid']]['type']['class']
  if typ=='SIText/UxmlSerializedData':props.append((65537,d.px(font_size*.75)))
  if 'data_display-graphs-data_points-large-square' in classes:props.extend([(131105,d.px(square_size*.75)),(131087,d.px(square_size*.75))])
  if 'margin-right-global-gap-extra-small' in classes:props.append((131092,d.px(micro*.75)))
  elif 'margin-right-global-gap-small' in classes:props.append((131092,d.px(close*.75)))
  if props:edit(node,props)
 plot=one(nodes,lambda i:d.r.get(d.a(i).get('m_SerializedData',{}).get('rid'),{}).get('type',{}).get('class')=='FMHeatMap/UxmlSerializedData','live heatmap renderer')
 assert d.r[plot]==old_refs[plot] and d.data(plot)==sd(old_refs,plot)
 heat_audits.append({'side':side,'direction_order_preserved':[d.data(c['rid']).get('name') for c in d.a(direction)['m_Children']],'direction_top_center':True,'legend_bottom_center':True,'native_color_square_size':square_size,'new_color_square_size':square_size*.75,'native_legend_font':font_size,'new_legend_font':font_size*.75,'actual_layout_metrics_scaled_instead_of_retaining_unscaled_space':True,'remaining_area_allocated_to_pitch':True,'pitch_data_and_orientation_unchanged':plot})

for rid,record in old_refs.items():
 if rid in removed:continue
 if rid not in allowed:assert d.r[rid]==record,('Unrequested existing record changed',rid)
 else:
  expected=copy.deepcopy(record)
  for field in ['m_RuleIndex','m_Children']:expected['data'][field]=copy.deepcopy(d.r[rid]['data'][field])
  assert d.r[rid]==expected,('Unrequested text, binding or element changed',rid)
assert all(rid not in d.r for rid in removed)
fixed=d.named('HighlightFixedStatsOnlyView')
for rid in subtree(fixed):assert d.r[rid]==old_refs[rid] and d.data(rid)==sd(old_refs,rid),'Fixed comparison page changed'
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value,('Original stylesheet modified',key)
 else:assert d.s[key]==value
d.save()

geometry=[]
for width,height in [(1920,1080),(2526,1379)]:
 usable_w=width-64;usable_h=height-280
 upper_h=(usable_h-2)*.55;lower_h=(usable_h-2)*.45
 assert math.isclose(upper_h+2+lower_h,usable_h)
 assert math.isclose(upper_h/lower_h,55/45)
 assert .5>=0 and .5+1<=2
 geometry.append({'viewport':[width,height],'outer_widths':[usable_w*.3,usable_w*.4,usable_w*.3],'middle_usable_height':usable_h,'upper_height':upper_h,'gap':2,'lower_height':lower_h,'line_height':1,'line_top_within_gap':.5,'sum_matches_original_total_height':True})

outputs={}
for name in [G,T]:
 data=env[name].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(check)==set(objs[name])
 for pid,h in hashes[name].items():
  if pid not in changes[name]:assert sha(check[pid].get_raw_data())==h,('Unrelated object changed',name,pid)
 for pid,expected in changes[name].items():assert check[pid].read_typetree()==expected,('Roundtrip failed',name,pid)
 if name==G:validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
 outputs[name]=data;(OUT/name).write_bytes(data)

cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
preview=[]
for name,versions in cache_versions.items():
 path=cache_root/name
 if not path.exists():continue
 original=json.loads(path.read_text('utf8'));result=migration.migrate_layout(original,version=versions['after'])
 assert migration.migrate_layout(result,False,version=versions['before'],limits_from=original)['m_gridComponents']==original['m_gridComponents']
 preview.append({'file':name,'selected_modules_preserved':[c['m_elementID'] for c in result['m_gridComponents']],'new_positions':{c['m_elementID']:c['m_location'] for c in result['m_gridComponents']}})
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
for path,data in before.items():assert path.read_bytes()==data
for path,h in protected.items():assert sha(path.read_bytes())==h
for path in before:
 if path.name.startswith('catalog.'):protected[path]=sha(before[path])
report={'passed':True,'layouts':layout_audits,'extended_native_size_descriptions':descriptor_audits,'center_config_8x8_reuses_current_matchviewer_asset':center_config,'heatmaps':heat_audits,'geometry':geometry,'selector_subtree_removed':selector_nodes,'fixed_comparison_page_unchanged':True,'custom_layout_previews':preview,'selected_modules_and_other_user_settings_preserved':True,'catalog_and_shared_chart_templates_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[n].items()} for n in [G,T]},'before_sha256':{str(path):sha(b) for path,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(path):h for path,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G,T],'cache_root':str(cache_root),'cache_versions':cache_versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_bytes((R/'highlight-grid-migration.py').read_bytes())
(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,filename in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 script="$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed; see diagnostics above.' }\n"
 (OUT/filename).write_text(script,'utf8')
watcher=(R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_text('utf8')
watcher=watcher.replace("'G:/Doc/ChatGPT/New project/install-match-ui-patch.py'","(Join-Path $PSScriptRoot 'installer.py')")
(OUT/'install-after-game-exits.ps1').write_text(watcher,'utf8')
(OUT/'修改说明.md').write_text('''# Highlight 30/40/30、上下55/45

- 大屏执教/旁观、有无积分榜四套网格改为 6/8/6 列。侧栏和中间仍使用现有模块与模板，补充相应宽度的原生配置。
- 中间扣除 2px 后，上下按 55:45 分配；分隔区内以现有主题分隔线颜色居中绘制 1px 横线。移除交界处额外内外边距。
- 删除原选择器整个子树，并释放顶部预留空间。下方固定的完整“仅数据”页面原样保留。
- 热点图方向提示顶部居中，保留主客队文字/箭头顺序和方向。色阶底部居中，按原始度量的75%设置：色块16→12，图例字体14→10.5，间距同比缩放；以真实布局度量取代仅视觉缩放，回收原始尺寸的多余占位。
- 移除热点图内部多余间距和固定高度约束，球场以原比例最大化适配剩余空间，不裁切、不拉伸。中间上半区仍是25/50/25，两侧各图上下各一半。
- 安装时读取最新的四份对应本地自定义布局，只迁移坐标、宽度及版本；保留槽位已选模块和其他设置。备份放在 backup-custom。不会清空其他缓存。
- 恢复脚本回退资源，并反向迁移当前自定义布局的坐标，尽量保留安装后新选择的模块。恢复前也备份当前布局。

运行 install.ps1 安装、restore.ps1 恢复。游戏运行时等待正常退出后安装。
通过网格覆盖、缓存迁移/回迁、尺寸/方向/布局约束、序列化回读及无关对象一致性检查。几何检查覆盖1920×1080及2526×1379，但不等同于游戏实机渲染验证；实际显示和实时刷新仍待进游戏检查。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'layouts':len(layout_audits),'extended_descriptors':len(descriptor_audits),'selector_removed':True,'custom_layouts_to_migrate':len(preview),'geometry_checks':len(geometry)},ensure_ascii=False))
