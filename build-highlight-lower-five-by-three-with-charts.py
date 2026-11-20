from pathlib import Path
import json, math

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-lower-5x3-at55-charts-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-resources-and-load-codecs','exec'))
env[W]=UnityPy.load(str(GAME/W));objs[W]={o.path_id:o for o in env[W].objects}
d=Doc(G,name='MatchViewer_12x4')
old=copy.deepcopy(d.d);old_refs=refs(old);old_style=copy.deepcopy(d.s)
prior=R/'highlight-comparison-4x4-at75-20261024-133734'
metrics=json.loads((prior/'verification.json').read_text('utf8'))['scaled_pixel_metrics']
assert sha(before[GAME/G])==json.loads((prior/'manifest.json').read_text('utf8'))['after_sha256'][G], 'Installed baseline differs from the confirmed 75% page'
f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
AUTO={'m_ValueType':1,'valueIndex':2}
root=d.named('HighlightFixedStatsOnlyView');box=2465
assert root==2429 and box==2465
rows=[x['rid'] for x in d.a(box)['m_Children']]
assert len(rows)==4
cells=[x['rid'] for row in rows for x in d.a(row)['m_Children']]
assert len(cells)==16 and not d.a(cells[-1])['m_Children']
items=[d.a(cell)['m_Children'][0]['rid'] for cell in cells[:-1]]
names=['Possession','ClearCutChances','Fouls','Shots','Corners','YellowCards','ShotsOnTarget','ProgressivePasses','RedCards','xG','PassesCompleted','DistanceCovered','OPPDA','CrossesCompleted','AvgRating']
assert [d.data(i)['name'] for i in items]==names

def subtree(i,reference=None):
 ref=d.r if reference is None else reference
 yield i
 for c in ref[i]['data'].get('m_Children',[]):yield from subtree(c['rid'],ref)

item_nodes={item:list(subtree(item)) for item in items}
all_items={i for branch in item_nodes.values() for i in branch}
allowed=set();removed=set();scaled=[]
for entry in metrics:
 i=entry['node'];assert i in all_items
 values=[];audit=[]
 for original in entry['before']:
  if isinstance(original,dict) and set(original)=={'unit','value'}:
   value=copy.deepcopy(original)
   if value['unit']==1:value['value']=f32(value['value']*.55)
   values.append(d.val(3,value));audit.append(value)
  elif isinstance(original,(int,float)):
   value=f32(original*.55);values.append(d.num(value));audit.append(value)
  else:raise AssertionError(('Unhandled original metric',entry))
 d.st(i,[(entry['property'],values)]);allowed.add(i)
 scaled.append({'node':i,'property':entry['property'],'original':entry['before'],'at_55_percent':audit})

def plain(parent,name):return d.add(d,1015,parent,name)
def fill(i):
 d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
def clear_spacing(i):
 d.st(i,[(p,d.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])

d.st(root,[(131083,d.enum('column')),(131073,d.enum('stretch')),(131088,d.enum('flex-start'))]);allowed.add(root)
d.st(box,[(131087,AUTO),(131082,AUTO),(131084,d.num(0)),(131085,d.num(0)),(131096,d.px(0)),(131083,d.enum('column')),(131073,d.enum('stretch')),(131088,d.enum('flex-start'))]);clear_spacing(box);allowed.add(box)
for ri,row in enumerate(rows[:3]):
 d.st(row,[(131083,d.enum('row')),(131105,d.pct(100)),(131087,AUTO),(131082,AUTO),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131073,d.enum('stretch'))])
 clear_spacing(row);d.st(row,[(131090,d.px(3 if ri<2 else 0))]);allowed.add(row)
 for ci in range(5):
  cell=cells[ri*5+ci];item=items[ri*5+ci]
  d.move(cell,row);allowed.add(cell)
  d.st(cell,[(131083,d.enum('column')),(131105,d.px(0)),(131082,d.px(0)),(131097,d.px(0)),(131087,AUTO),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('center')),(131088,d.enum('center'))])
  clear_spacing(cell)
  d.st(item,[(131105,d.px(f32(288*.55))),(131095,d.pct(100)),(131087,AUTO),(131082,AUTO),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(1)),(131074,d.enum('center')),(131090,d.px(0)),(131093,d.px(0))]);allowed.add(item)
  label,bar=[x['rid'] for x in d.a(item)['m_Children']]
  d.st(label,[(131105,d.pct(100)),(131074,d.enum('stretch'))]);allowed.add(label)
  d.st(bar,[(131095,d.pct(100)),(131097,d.px(0)),(131085,d.num(1))]);allowed.add(bar)
for i in [cells[-1],rows[-1]]:
 assert not d.a(i)['m_Children']
 parent=d.a(i)['m_Parent']['rid'];d.a(parent)['m_Children'].remove({'rid':i})
 removed|={i,d.a(i)['m_SerializedData']['rid']}
d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in removed]
for i in removed:d.r.pop(i)

button=3073;header=2431
button_host=plain(root,'HighlightDataTopButton')
d.st(button_host,[(131083,d.enum('row')),(131105,d.pct(100)),(131087,AUTO),(131082,AUTO),(131084,d.num(0)),(131085,d.num(0)),(131073,d.enum('center')),(131088,d.enum('center'))])
d.move(button,button_host);d.move(button_host,root,0);allowed.add(button)

charts=plain(root,'HighlightLowerNativeCharts')
d.st(charts,[(131083,d.enum('row')),(131105,d.pct(100)),(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('stretch'))]);clear_spacing(charts)

def copy_style(source,record):
 idx=record['data'].get('m_RuleIndex',-1)
 if idx<0:return
 rule=copy.deepcopy(source.s['m_Rules'][idx]);rule['m_ComplexSelectors']=[]
 for prop in rule['m_Properties']:
  for handle in prop['m_Values']:
   typ=handle['m_ValueType']
   if typ not in poolmap:continue
   value=copy.deepcopy(source.s[poolmap[typ]][handle['valueIndex']])
   if typ==6:pointer_remap(value,source.af,d.af)
   handle['valueIndex']=len(d.s[poolmap[typ]]);d.s[poolmap[typ]].append(value)
 record['data']['m_RuleIndex']=len(d.s['m_Rules']);d.s['m_Rules'].append(rule)

clone_audits=[]
def clone_native(source,source_root,parent):
 collected=set()
 def collect(i):
  if i==-2 or i in collected:return
  assert i in source.r,('Missing native reference',source.d['m_Name'],i)
  collected.add(i)
  def scan(v):
   if isinstance(v,dict):
    if set(v)=={'rid'}:collect(v['rid'])
    else:
     for key,x in v.items():
      if key!='m_Parent':scan(x)
   elif isinstance(v,list):
    for x in v:scan(x)
  scan(source.r[i]['data'])
 collect(source_root)
 rid_map={}
 for i in sorted(collected):rid_map[i]=d.nr;d.nr+=1
 asset_map={}
 for i in sorted(collected):
  if 'm_Parent' in source.r[i]['data']:
   asset_map[source.r[i]['data']['m_Id']]=d.nid;d.nid+=1
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:v['rid']=rid_map.get(v['rid'],v['rid'])
   else:
    for key,x in v.items():
     if key in ['m_Id','uxmlAssetId','m_ParentId'] and isinstance(x,int):v[key]=asset_map.get(x,x)
     else:remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 records=[]
 for i in sorted(collected):
  record=copy.deepcopy(source.r[i]);record['rid']=rid_map[i];remap(record['data']);pointer_remap(record,source.af,d.af)
  if i==source_root:record['data']['m_Parent']={'rid':parent}
  if 'm_Parent' in record['data']:
   copy_style(source,record)
   alias=record['data'].get('m_TemplateAlias')
   if alias:
    incoming=next(u for u in source.d['m_Usings'] if u['alias']==alias)
    existing=next((u for u in d.d['m_Usings'] if u['alias']==alias),None)
    assert existing is None or existing['path']==incoming['path'],('Conflicting native template alias',alias)
    d.using(source,alias)
  records.append(record)
  d.r[record['rid']]=record;d.d['references']['RefIds'].append(record)
 import_types(source.af,d.af,records)
 d.a(parent)['m_Children'].append({'rid':rid_map[source_root]})
 native_serials=[i for i in collected if 'm_Parent' not in source.r[i]['data']]
 for i in native_serials:
  expected=copy.deepcopy(source.r[i]['data']);remap(expected);pointer_remap(expected,source.af,d.af)
  assert d.r[rid_map[i]]['data']==expected
 clone_audits.append({'template':source.d['m_Name'],'records':len(collected),'serialized_records':len(native_serials),'native_bindings_text_events_and_components_identical':True,'map':rid_map})
 return rid_map[source_root],rid_map

def unpack_args(raw):
 raw=bytes(raw);at=1;out=[]
 for _ in range(raw[0]):
  n=struct.unpack_from('<I',raw,at)[0];at+=4;out.append(raw[at:at+n]);at+=n
 assert at==len(raw);return out
def pack_args(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
def replace_paths(value,replacements):
 if isinstance(value,dict):
  for key,x in value.items():
   if key=='m_argumentBytes' and x:
    args=unpack_args(x)
    for oi,original in enumerate(args):
     target=original
     for before_path,after_path in replacements.items():
      a=before_path.encode();b=after_path.encode();target=target.replace(bytes([len(a)])+a,bytes([len(b)])+b)
     args[oi]=target
    value[key]=pack_args(args)
   else:replace_paths(x,replacements)
 elif isinstance(value,list):
  for x in value:replace_paths(x,replacements)

module_specs=[('Momentum',G,'MatchMomentum_4x2'),('ActionZones',W,'TeamActionZonesMapTile_4x4'),('XG',G,'xGStoryTile_4x2')]
modules=[]
for kind,bundle,template in module_specs:
 host=plain(charts,'HighlightLower'+kind+'Cell')
 d.st(host,[(131105,d.px(0)),(131082,d.px(0)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('stretch'))]);clear_spacing(host)
 donor=Doc(bundle,name=template)
 parent=host
 if kind=='ActionZones':
  setter=d.add(d,1002,host,'HighlightActionZonesDefaultTeam');d.a(setter)['m_Classes']=[];fill(setter)
  v=d.data(setter);v.update(ValueVariables=[],ReferenceVariables=[{'m_type':{'id':1145176088},'m_initToNull':1,'m_name':'HighlightActionZonesTeam'}])
  base=copy.deepcopy(sd(old_refs,1002)['BindFunction'][1]);home=copy.deepcopy(base);human=copy.deepcopy(base)
  replace_paths(home,{'const.One':'match.HomeTeam','selectedTab':'HighlightActionZonesTeam'})
  replace_paths(human,{'const.One':'match.MatchHumanTeam','selectedTab':'HighlightActionZonesTeam','const.True':'match.MatchHumanTeam'})
  v.update(BindFunction=[home,human],ValueVariables_UxmlAttributeFlags=1,ReferenceVariables_UxmlAttributeFlags=1,BindFunction_UxmlAttributeFlags=1)
  parent=setter
  team_path='HighlightActionZonesTeam'
 else:team_path='match.MatchHumanTeam'
 scope=d.add(d,1004,parent,'HighlightLower'+kind+'Context');d.a(scope)['m_Classes']=[];fill(scope)
 mappings=[('fixture','fixturetouse',1718188148),('isonmainscreen','const.False',0)]
 if kind=='ActionZones':mappings.extend([('actionzonesmap','match.ActionZonesVisualisation',1278767938),('team',team_path,1145176088)])
 d.data(scope).update(Mappings=[{'m_serialisedType':0,'from':key,'to':{'m_path':path},'type':{'id':typ}} for key,path,typ in mappings],Mappings_UxmlAttributeFlags=1)
 native_root,mapping=clone_native(donor,1001,scope);fill(native_root)
 for old_id,new_id in mapping.items():
  a=donor.r[old_id]['data']
  if 'm_Parent' not in a or donor.r[old_id]['type']['class']=='UxmlObjectAsset':continue
  if a.get('m_TemplateAlias') in ['tile-wide-4x2','tile-square-4x4']:
   fill(new_id)
  elif 'flex-grow-class' in a.get('m_Classes',[]) or a.get('m_FullTypeName') in ['SI.Bindable.BindingSetter','SI.Bindable.BindingRemapper','SI.Bindable.BindableSwitchElement']:
   d.st(new_id,[(131097,d.px(0)),(131096,d.px(0)),(131085,d.num(1))])
 if kind=='Momentum':
  plot=mapping[1022]
  d.st(mapping[1017],[(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))]);fill(plot)
 elif kind=='XG':
  plot=mapping[1021]
  d.st(plot,[(131105,d.pct(100)),(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
 else:
  plot=mapping[1047]
  # Native plot orientation and both live/empty graph branches are retained.
  d.st(mapping[1025],[(131096,d.px(0)),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
 modules.append({'module':kind,'template':template,'cell':host,'root':native_root,'scope':scope,'plot':plot})

assert d.a(root)['m_Children']==[{'rid':button_host},{'rid':header},{'rid':box},{'rid':charts}]
assert d.a(box)['m_Children']==[{'rid':i} for i in rows[:3]]
assert all(len(d.a(row)['m_Children'])==5 for row in rows[:3])
assert [d.data(d.a(cell['rid'])['m_Children'][0]['rid'])['name'] for row in rows[:3] for cell in d.a(row)['m_Children']]==names
for branch in item_nodes.values():
 for i in branch:
  assert d.data(i)==sd(old_refs,i),('Existing binding/text/event/tooltip changed',i)
  assert d.a(i)['m_Classes']==old_refs[i]['data']['m_Classes']
for i in subtree(header,old_refs):assert d.r[i]==old_refs[i] and d.data(i)==sd(old_refs,i),'Header changed'
for rid,record in old_refs.items():
 if rid in removed:continue
 if rid not in allowed:assert d.r[rid]==record,('Out-of-scope record changed',rid)
 else:
  expected=copy.deepcopy(record)
  for key in ['m_RuleIndex','m_Parent','m_Children']:
   if key in expected.get('data',{}):expected['data'][key]=copy.deepcopy(d.r[rid]['data'][key])
  assert d.r[rid]==expected,('Unexpected existing field changed',rid)
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value
 else:assert d.s[key]==value
assert d.data(button)==sd(old_refs,button)
for clone in clone_audits:
 mapping=clone['map'];donor=Doc(next(b for k,b,t in module_specs if t==clone['template']),name=clone['template'])
 for source_id,target_id in mapping.items():
  if 'm_Parent' in donor.r[source_id]['data']:continue
  source=copy.deepcopy(donor.r[source_id]['data']);actual=copy.deepcopy(d.r[target_id]['data'])
  # Component references have been relocated, while their complete serialized content is preserved.
  if 'uxmlAssetId' in source:actual['uxmlAssetId']=source['uxmlAssetId']
  def normalize(value):
   if isinstance(value,dict):
    if set(value)=={'rid'}:value['rid']={v:k for k,v in mapping.items()}.get(value['rid'],value['rid'])
    else:
     for x in value.values():normalize(x)
   elif isinstance(value,list):
    for x in value:normalize(x)
  normalize(actual)
  assert actual==source,('Native serialized behavior changed',clone['template'],source_id)

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
 # A conservative static budget; this is not an engine-rendered screenshot check.
 native_header_and_button_budget=100;three_rows_budget=3*32+6
 remaining=lower_height-native_header_and_button_budget-three_rows_budget
 assert data_width/5>=288*.55 and remaining>200
 geometry.append({'viewport':[width,height],'comparison_cell_width':data_width/5,'comparison_width':f32(288*.55),'assumed_maximum_data_row_height':32,'exact_row_gaps':[3,3],'native_header_and_button_budget':100,'remaining_native_chart_height':remaining,'each_module_width':data_width/3,'static_budget_only':True})
report={'passed':True,'rows':3,'columns':5,'data_order':[names[i:i+5] for i in range(0,15,5)],'scale_relative_to_original':.55,'row_gaps_px':[3,3],'data_height':'content','button':'top-center-before-team-header','header_badges_button_behavior_and_size_preserved':True,'existing_data_text_bindings_events_tooltips_and_colors_preserved':True,'modules':modules,'native_clone_audits':[{k:v for k,v in a.items() if k!='map'} for a in clone_audits],'activity_data_path':'match.ActionZonesVisualisation','module_sizes':'equal width and height; all remaining lower-area space','scaled_metrics':scaled,'geometry_checks':geometry,'outer_5_10_5_middle_45_55_separator_upper_charts_unchanged':True,'shared_donors_catalog_cache_and_unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 中间下半区：55%、五列三行与三个原生模块

仅修改 MatchViewer_12x4 的私有下半区。15项数据保持原有逐行顺序，改成五列三行，行距固定3px。尺寸按原始55%计算，不是当前75%的55%；比较条288→158.4，条高8→4.4，名称字号12→6.6，数值字号14→7.7，内部间距同比调整。
“查看数据”按钮移动到顶部居中、队名队徽上方；保留其原生模板、尺寸样式、点击事件。队名队徽不变。
数据区按内容占高，下方剩余空间由比赛势头、活动区域、预计进球视图从左到右等宽等高使用。
三个原生模板完整复制至私有实例，包含模板覆盖、标题、图例、空状态、绑定、事件与预计进球视图的组件引用。活动区域沿用 OverviewPrototype 中确认的 match.ActionZonesVisualisation 数据路径；球队上下文优先比赛玩家球队，旁观时使用主队。共用模板不变。
整体5:10:5、中间45%/55%、2px分隔区和横线、所有上方图表保持不变。本地网格缓存未写入。
已检查15项顺序、尺寸、行距、所有原有文字绑定事件提示和颜色、三个原生实例的序列化行为一致性；已完成序列化回读和无关对象哈希检查。两种分辨率仅通过静态空间预算检查，未进行游戏内实际渲染或实时刷新验证。
正常退出游戏后安装；restore.ps1只恢复本次修改。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'items':15,'rows':3,'columns':5,'scale':.55,'row_gap':3,'modules':[m['module'] for m in modules],'roundtrip':True,'runtime_verified':False},ensure_ascii=False))
