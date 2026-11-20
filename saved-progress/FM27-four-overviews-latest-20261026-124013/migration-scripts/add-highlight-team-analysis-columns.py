from pathlib import Path
import json,math

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-team-analysis-columns-').replace('NAMES=[W,G,M,F]','NAMES=[W,G]')
exec(compile(boot,'backup-live-resources-and-load-codecs','exec'))

d=Doc(G,name='MatchViewer_12x4')
heat=Doc(W,name='HeatMapsMatch_4x4')
passes=Doc(G,name='TeamPassMap_4x4')
fitter=Doc(G,pid=-9211596620732837621)
old=copy.deepcopy(d.d);old_refs=refs(old);old_style=copy.deepcopy(d.s)
upper=d.named('HighlightPitchUpperHalf');lower=d.named('HighlightDataLowerHalf')
left=d.named('HighlightPitchLeftBlank');right=d.named('HighlightPitchRightBlank')
assert d.a(upper)['m_Children']==[{'rid':left},{'rid':1022},{'rid':right}]
assert d.a(lower)['m_Children']==[{'rid':1011}]
assert next(v for v in d.data(1002)['ValueVariables'] if v['m_name']=='selectedTab')['m_scopeValue']['m_serializedData'].startswith('Int|1|')

VE=1015
TEXT=next(i for i,x in d.r.items() if x.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText')
ROTATE=327680
f32=lambda value:struct.unpack('<f',struct.pack('<f',value))[0]
def angle(value):return d.val(3,{'unit':5,'value':float(value)})
def plain(parent,name):
 i=d.add(d,VE,parent,name);d.a(i)['m_Classes']=[];return i
def fit_fill(i):
 d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
def title(parent,text,name):
 i=d.add(d,TEXT,parent,name);v=d.data(i)
 v.update(text=text,text_UxmlAttributeFlags=1,DebugDisplay='',TextBinding_UxmlAttributeFlags=0)
 v['TextBinding']={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
 d.a(i)['m_Classes']=['body-sm','global-text-primary','content-ellipsis']
 d.st(i,[(131102,d.enum('absolute')),(131104,d.px(2)),(131089,d.px(4)),(131103,d.px(4)),(131087,d.px(16)),(65537,d.px(10)),(65543,d.enum('bold')),(65546,d.enum('middle-left')),(65552,d.enum('nowrap'))])
 return i

for i,name in [(left,'HighlightHomeAnalysisColumn'),(right,'HighlightAwayAnalysisColumn')]:
 d.data(i).update(name=name,name_UxmlAttributeFlags=1)
 d.st(i,[(131102,d.enum('relative')),(131105,d.pct(25)),(131097,d.px(0)),(131095,d.pct(25)),(131087,d.pct(100)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0))])
d.a(1022)['m_Classes']=[c for c in d.a(1022)['m_Classes'] if c!='margin-horizontal-global-gap-extra-large']
d.st(1022,[(131105,d.pct(50)),(131097,d.px(0)),(131095,d.pct(50)),(131087,d.pct(100)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131091,d.px(0)),(131092,d.px(0))])
pitch_serials=[]
def subtree(doc,i):
 yield i
 for c in doc.a(i).get('m_Children',[]):yield from subtree(doc,c['rid'])
for i in subtree(d,1022):
 typ=d.r.get(d.a(i).get('m_SerializedData',{}).get('rid'),{}).get('type',{}).get('class','')
 if typ in ['FMMatchSimulationWidget/UxmlSerializedData','PitchDrawing/UxmlSerializedData']:
  d.data(i).update(FillAllAvailableSpace=0,FillAllAvailableSpace_UxmlAttributeFlags=1)
  pitch_serials.append(d.a(i)['m_SerializedData']['rid'])

def copy_node(source,src,parent,name):
 i=d.add(source,src,parent,name)
 for field in ['pickingMode','pickingMode_UxmlAttributeFlags']:
  if field in source.data(src):d.data(i)[field]=source.data(src)[field]
 idx=source.a(src).get('m_RuleIndex',-1)
 if idx>=0:
  rule=copy.deepcopy(source.s['m_Rules'][idx]);rule['m_ComplexSelectors']=[]
  for p in rule['m_Properties']:
   for v in p['m_Values']:
    typ=v['m_ValueType']
    if typ in poolmap:
     value=copy.deepcopy(source.s[poolmap[typ]][v['valueIndex']])
     if typ==6:pointer_remap(value,source.af,d.af)
     v['valueIndex']=len(d.s[poolmap[typ]]);d.s[poolmap[typ]].append(value)
  d.s['m_Rules'].append(rule);d.a(i)['m_RuleIndex']=len(d.s['m_Rules'])-1
 d.a(i)['m_Classes']=copy.deepcopy(source.a(src).get('m_Classes',[]))
 alias=source.a(src).get('m_TemplateAlias')
 if alias:d.using(source,alias)
 return i

def copy_branch(source,src,parent,prefix):
 i=copy_node(source,src,parent,prefix+'_'+str(src))
 for c in source.a(src).get('m_Children',[]):copy_branch(source,c['rid'],i,prefix)
 return i

def bind_args(raw):
 raw=bytes(raw);p=1;result=[]
 for _ in range(raw[0]):
  length=struct.unpack_from('<I',raw,p)[0];p+=4;result.append(raw[p:p+length]);p+=length
 assert p==len(raw);return result

cards=[]
for home,column,turn in [(True,left,90),(False,right,-90)]:
 side='Home' if home else 'Away';label='主队' if home else '客队';direction=' →' if home else ' ←'
 for kind,top,source,plot_src in [('Heat',0,heat,1023),('Pass',50,passes,1019)]:
  prefix='Highlight'+side+kind
  card=plain(column,prefix+'Card')
  d.st(card,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.pct(top)),(131105,d.pct(100)),(131087,d.pct(50)),(131097,d.px(0)),(131096,d.px(0))])
  title(card,label+('热点图' if kind=='Heat' else '传球图')+direction,prefix+'Title')
  body=plain(card,prefix+'Body')
  d.st(body,[(131102,d.enum('absolute')),(131089,d.px(4)),(131103,d.px(4)),(131104,d.px(20)),(131080,d.px(4)),(131097,d.px(0)),(131096,d.px(0)),(458768,d.enum('hidden'))])
  scope=d.add(d,1004,body,prefix+'Bindings');d.a(scope)['m_Classes']=[]
  is_home_key='isHomeTeam' if kind=='Heat' else 'ishometeam'
  mappings=[('team','match.HomeTeam' if home else 'match.AwayTeam',1145176088),(is_home_key,'const.True' if home else 'const.False',0),('fixture','fixturetouse',1718188148)]
  if kind=='Pass':mappings.append(('isonmainscreen','const.False',0))
  d.data(scope).update(Mappings=[{'m_serialisedType':0,'from':k,'to':{'m_path':v},'type':{'id':t}} for k,v,t in mappings],Mappings_UxmlAttributeFlags=1)
  fit_fill(scope)

  expect=copy_node(source,1001,scope,prefix+'Expect');fit_fill(expect)
  if kind=='Heat':
   variables=copy_node(source,1002,expect,prefix+'Variables');fit_fill(variables)
   setter=copy_node(source,1004,variables,prefix+'Setter');fit_fill(setter)
   switch=copy_node(source,1008,setter,prefix+'Available');fit_fill(switch)
   render=copy_node(source,1012,switch,prefix+'Render');d.a(render)['m_Classes']=[];fit_fill(render)
   copy_branch(source,1013,switch,prefix+'Empty')
  else:
   setter=copy_node(source,1002,expect,prefix+'Setter');fit_fill(setter)
   switch=copy_node(source,1006,setter,prefix+'Available');fit_fill(switch)
   render=copy_node(source,1010,switch,prefix+'Render');d.a(render)['m_Classes']=[];fit_fill(render)
   copy_branch(source,1011,switch,prefix+'Empty')
  d.st(render,[(131073,d.enum('center')),(131088,d.enum('center')),(131102,d.enum('relative'))])
  fit=copy_node(fitter,1145,render,prefix+'LandscapeFit')
  d.a(fit)['m_Classes']=[]
  d.data(fit).update(AspectMode=3,AspectMode_UxmlAttributeFlags=1,AspectRatio=1.5,AspectRatio_UxmlAttributeFlags=1)
  d.st(fit,[(131102,d.enum('relative')),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,d.pct(100)),(131094,d.pct(100)),(131084,d.num(0)),(131085,d.num(1)),(131074,d.enum('center'))])
  plot=copy_node(source,plot_src,fit,prefix+'Plot')
  d.data(plot).update(Orientation=0,Orientation_UxmlAttributeFlags=1,FillAllAvailableSpace=0,FillAllAvailableSpace_UxmlAttributeFlags=1)
  d.st(plot,[(131102,d.enum('absolute')),(131089,d.pct(f32(100/6))),(131104,d.pct(-25)),(131105,d.pct(f32(100/1.5))),(131087,d.pct(150)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131091,d.px(0)),(131092,d.px(0)),(131093,d.px(0)),(131090,d.px(0)),(ROTATE,angle(turn))])
  if kind=='Pass':
   marker_scope='highlight-'+side.lower()+'-pass-plot'
   d.a(plot)['m_Classes'].append(marker_scope)
   rule_index=len(d.s['m_Rules'])
   d.s['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':21,'m_Selectors':[{'m_Parts':[{'m_Value':marker_scope,'m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'match-simulation-player-10px-bold','m_Type':3}],'m_PreviousRelationship':2}],'ruleIndex':rule_index}],'m_Properties':[{'m_Id':ROTATE,'m_CustomName':'','m_Line':-1,'m_Values':[angle(-turn)]}],'line':-1})
  # Every data function and plot data path is copied exactly from the native module.
  assert d.data(setter)['BindFunction']==source.data(1004 if kind=='Heat' else 1002)['BindFunction']
  assert d.data(plot)['DataBinding']==source.data(plot_src)['DataBinding']
  if kind=='Heat':
   assert d.data(plot)['GridCellsAlongLengthBinding']==source.data(plot_src)['GridCellsAlongLengthBinding']
   assert d.data(plot)['GridCellsAcrossWidthBinding']==source.data(plot_src)['GridCellsAcrossWidthBinding']
  else:assert d.data(plot)['PlayerVisualElementTemplate']==source.data(plot_src)['PlayerVisualElementTemplate']
  cards.append({'side':side,'kind':kind,'card':card,'scope':scope,'setter':setter,'plot':plot,'fit':fit,'rotation_degrees':turn,'source_template':source.d['m_Name'],'data_path':d.data(plot)['DataBinding']['m_path'],'team_binding':'match.HomeTeam' if home else 'match.AwayTeam','native_empty_state_preserved':True})

# Register scoped counter-rotation selectors as a stylesheet on this instance only.
style_pointer={'m_FileID':0,'m_PathID':d.sid}
assert style_pointer not in d.a(1001)['m_Stylesheets']
d.a(1001)['m_Stylesheets'].append(style_pointer)
assert d.a(upper)['m_Children']==old_refs[upper]['data']['m_Children']
assert d.a(lower)==old_refs[lower]['data']
assert d.data(1002)==sd(old_refs,1002)
assert d.r[1009]==old_refs[1009] and d.r[1013]==old_refs[1013]
assert d.data(1009)==sd(old_refs,1009) and d.data(1013)==sd(old_refs,1013)
allowed={1001,left,right,1022,d.a(left)['m_SerializedData']['rid'],d.a(right)['m_SerializedData']['rid']}|set(pitch_serials)
for rid,record in old_refs.items():
 if rid not in allowed:assert d.r[rid]==record,('Unrelated existing UI record changed',rid)
for key,v in old_style.items():
 if isinstance(v,list):assert d.s[key][:len(v)]==v,('Existing style pool changed',key)
 else:assert d.s[key]==v

# Numeric geometry checks use an asymmetric top point and corner points, not a symmetric pitch alone.
geometry=[]
for width,height in [(1920,1080),(2526,1379)]:
 highlight_width=width-64;highlight_height=height-280
 center_width=highlight_width*.6;upper_height=highlight_height*.5-36
 column_width=(center_width-24)*.25
 body_w=column_width-8;body_h=upper_height*.5-24
 fitted_w=min(body_w,body_h*1.5);fitted_h=fitted_w/1.5
 assert body_w>0 and body_h>0 and fitted_w<=body_w+.001 and fitted_h<=body_h+.001
 for c in cards:
  sign=1 if c['side']=='Home' else -1
  def transform(x,y):return (1-y,x) if sign==1 else (y,1-x)
  assert transform(.5,0)==((1,.5) if sign==1 else (0,.5))
  for x,y in [(0,0),(0,1),(1,0),(1,1),(.2,.3),(.7,.9)]:
   xx,yy=transform(x,y);assert 0<=xx<=1 and 0<=yy<=1
  if c['kind']=='Pass':
   scope_class='highlight-'+c['side'].lower()+'-pass-plot'
   matching=[rule for rule in d.s['m_Rules'] if any(scope_class==p['m_Value'] for sel in rule['m_ComplexSelectors'] for selector in sel['m_Selectors'] for p in selector['m_Parts'])]
   assert len(matching)==1
   value=next(p for p in matching[0]['m_Properties'] if p['m_Id']==ROTATE)['m_Values'][0]
   compensation=d.s['dimensions'][value['valueIndex']]
   assert compensation['unit']==5 and c['rotation_degrees']+compensation['value']==0
 geometry.append({'viewport':[width,height],'analysis_card_body':[round(body_w,2),round(body_h,2)],'contained_landscape_pitch':[round(fitted_w,2),round(fitted_h,2)],'columns_percent':[25,50,25],'side_card_heights_percent':[50,50],'asymmetric_direction_and_bounds_checks_passed':True})
d.save()

# Update only the main asset's preload span if an actual new object pointer was introduced.
def allptr(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   if v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():allptr(x,out)
 elif isinstance(v,list):
  for x in v:allptr(x,out)
metaobj=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();meta_changed=False
for key,entry in meta['m_Container']:
 if entry['asset']['m_PathID']!=d.obj.path_id:continue
 span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]);previous_span=copy.deepcopy(span)
 allptr(d.d,span);allptr(d.s,span)
 if span!=previous_span:
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span);meta_changed=True
if meta_changed:metaobj.save_typetree(meta);changes[G][metaobj.path_id]=meta

output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated global asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected,('Roundtrip mismatch',pid)
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
for pid,h in hashes[W].items():assert sha(objs[W][pid].get_raw_data())==h,('Native donor changed',pid)
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.') or p.name==W:protected[p]=sha(before[p])
report={'passed':True,'template':'MatchViewer_12x4','private_inline_cards':cards,'columns_percent':[25,50,25],'upper_lower_percent':[50,50],'geometry_checks':geometry,'native_stats_only_page_and_initial_selection_unchanged':True,'selector_record_and_original_style_unchanged':True,'all_existing_styles_unchanged':True,'outer_grids_and_custom_saved_layout_unchanged':True,'native_donor_modules_unchanged':True,'catalog_unchanged':True,'unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# Highlight 主客队分析图

只修改中间区域 MatchViewer_12x4 的上半区，左右分析栏/实时球场为 25%/50%/25%。
两侧分析栏各分上下 50%，分别显示热点图和传球图。明确绑定 match.HomeTeam / match.AwayTeam。
原生竖向绘图层主队顺时针 90°、客队逆时针 90°，所以原来上方分别朝右、朝左。
使用原生等比例适配容器，旋转绘图层同步变换球场、热点、球员位置、传球线；传球号码反向旋转保持正立，标题位于旋转层之外。
复用原生数据初始化、空数据状态、传球球员标记；图表副本只内联在本页面，不修改共用模板。
中间下方原生“仅数据”页面、默认选项、选择器原位置和操作全部保持不变。外层网格、左右阵型和底部模块均不修改。

控制资源：ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle 内 MatchViewer_12x4 及其内联样式。
无需新增地址条目，catalog.bin / catalog.hash 保持一致。
已通过 1920×1080 / 2526×1379 的几何边界和方向计算、UI 层级/样式/序列化回读、共用资源及无关对象一致性检查。
这些是静态检查，不等于游戏实际渲染验证；游戏内换人、实时刷新、文字和悬浮提示尚待验证。

安装：退出游戏后运行 install.ps1。restore.ps1 仅恢复本次修改。备份位于 backup-game / backup-skin。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'private_analysis_cards':len(cards),'modified_global_objects':len(changes[G]),'native_donors_and_catalog_unchanged':True},ensure_ascii=False))
