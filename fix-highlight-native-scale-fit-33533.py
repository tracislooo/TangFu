from pathlib import Path
import json,copy
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-native-scale-fit-33533-').replace("'NAMES=[W,G]'","'NAMES=[M,T]'").replace('bases=(W,G)','bases=(M,T)')
exec(compile(prefix,'backup-current-responsive-fix','exec'))
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
setnames=['MatchExperienceHumanGridCompositionSet','MatchExperienceHumanGridCompositionSet-NoLeague','MatchExperienceGridCompositionSet','MatchExperienceGridCompositionSet-NoLeague']
CK='<Configurations>k__BackingField';NONE={'m_ValueType':1,'valueIndex':3};AUTO={'m_ValueType':1,'valueIndex':2};tx=[];audits=[];game_layouts={}
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');cache_before={p:p.read_bytes() for n in layout_names for p in [cache_root/n] if p.exists()}
for p,b in cache_before.items():q=OUT/'backup-cache'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(b)
def pending(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def save(bn,pid,t):objs[bn][pid].save_typetree(t);changes[bn][pid]=t
positions=[(0,0,12,6),(12,0,12,6),(24,0,20,6),(44,0,12,6),(56,0,12,6),(0,6,17,4),(17,6,17,4),(34,6,17,4),(51,6,17,4)]
def resize_layout(bn,tr):
 assert len(tr['m_gridComponents'])==9
 for block,(x,y,w,h) in zip(tr['m_gridComponents'],positions):
  block['m_location']={'x':x,'y':y,'width':w,'height':h};block['m_minSize']={'x':w,'y':h};block['m_maxSize']={'x':w,'y':h}
  for c in block['m_gridElementConfigs']:
   c['Size']={'x':w,'y':h};dp=c['Description']['m_PathID'];desc=pending(bn,dp)
   if c not in desc[CK]:desc[CK].append(copy.deepcopy(c));save(bn,dp,desc)
 tr['m_compositionVersion']+=1
 return tr
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 M,T=[x+suffix for x in bases];layouts={}
 for name in layout_names:
  ob=find(T,name);tr=resize_layout(T,ob.read_typetree());save(T,ob.path_id,tr);layouts[name]=(ob.path_id,tr)
  if tag=='game':game_layouts[name]=copy.deepcopy(tr)
 # Every desktop breakpoint gets the same proportional layout. Phone entries are kept.
 set_audits=[]
 for name in setnames:
  ob=find(T,name);tr=ob.read_typetree();original=copy.deepcopy(tr)
  target=name.replace('CompositionSet','Composition-Large');pid,layout=layouts[target]
  for entry in tr['m_gridBreakpointCompositionData']['m_values']:
   if entry['m_key'] in [1,2,3]:entry['m_value']=[{'m_FileID':0,'m_PathID':pid}]
  tr['m_availableGridElements']=copy.deepcopy(layout['m_gridElementSet']);save(T,ob.path_id,tr)
  assert [x for x in tr['m_gridBreakpointCompositionData']['m_values'] if x['m_key'] in [4,5]]==[x for x in original['m_gridBreakpointCompositionData']['m_values'] if x['m_key'] in [4,5]]
  set_audits.append({'set':name,'desktop_layout':target,'desktop_breakpoints':[1,2,3]})
 # Complete native menus must still resolve the wider bottom slots.
 regs={v[1]['m_gridElementSet']['m_PathID'] for v in layouts.values()}
 for regpid in regs:
  reg=pending(T,regpid)
  for ref in reg['m_gridElementDescriptions']:
   pid=ref['m_PathID'];desc=pending(T,pid)
   if not any(c['Size']=={'x':17,'y':4} for c in desc.get(CK,[])):
    sourcecfg=next((c for c in desc.get(CK,[]) if c['Size']=={'x':6,'y':4}),None)
    if sourcecfg is None:sourcecfg=desc[CK][0]
    c=copy.deepcopy(sourcecfg);c['Size']={'x':17,'y':4};desc[CK].append(c);save(T,pid,desc)
 # Use the existing native ScalableBindableGridLayoutElement, as on TeamNewsPanel.
 donor=Doc(M,name='TeamNewsPanel');source_node=next(i for i,r in donor.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.ScalableBindableGridLayoutElement')
 d=Doc(M,name='OverviewPrototype');original=copy.deepcopy(d.d);scaled_nodes=[]
 for old in [1021,1022]:
  groups=copy.deepcopy(d.data(old)['GridCompositionSets']);assert len(groups)==2
  parent=d.a(old)['m_Parent']['rid'];idx=next(i for i,c in enumerate(d.a(parent)['m_Children']) if c['rid']==old)
  wrapper=d.add(d,1002,parent,'ResponsiveDesktopOrNativePhone_'+str(old));d.data(wrapper)['Binding']['m_kind']=1;d.data(wrapper)['Binding']['m_direct']['Path']['m_path']='config.ShowPhonePanels';d.data(wrapper)['Binding_UxmlAttributeFlags']=1
  league=d.add(d,1002,wrapper,'ResponsiveLeagueGrid_'+str(old));d.data(league)['Binding']['m_kind']=1;d.data(league)['Binding']['m_direct']['Path']['m_path']='match.MatchHasLiveLeagueTable';d.data(league)['Binding_UxmlAttributeFlags']=1
  # Native bool switch order is false, true.
  for hasleague in [False,True]:
   matching=[g for g in groups if ('-NoLeague' not in objs[T][g['m_gridCompositionSetBindings']['m_gridCompositionSet']['m_PathID']].peek_name())==hasleague];assert len(matching)==1
   node=d.add(donor,source_node,league,'ResponsiveNativeGrid_'+str(old)+'_'+str(hasleague));s=d.data(node);s['Bindings']=copy.deepcopy(matching[0]['m_gridCompositionSetBindings']);s['Bindings_UxmlAttributeFlags']=1;s.update(IsCustomisable=0,IsCustomisable_UxmlAttributeFlags=1,IgnoreOuterPadding=1,IgnoreOuterPadding_UxmlAttributeFlags=1,CentreContent=0,CentreContent_UxmlAttributeFlags=1,pickingMode=0,pickingMode_UxmlAttributeFlags=1)
   d.a(node)['m_Classes']=['flex-grow-class'];scaled_nodes.append(node)
  d.move(old,wrapper);d.move(wrapper,parent,idx)
  for node in [wrapper,league]+scaled_nodes[-2:]:
   d.st(node,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,d.pct(100)),(131094,d.pct(100)),(131084,d.num(1)),(131085,d.num(1)),(131082,d.px(0)),(131074,d.enum('stretch'))])
  assert d.a(wrapper)['m_Children']==[{'rid':league},{'rid':old}]
  assert d.data(old)==sd(refs(original),old)
 # Constrain the visible area above the player/footer strip, not the modules' nominal sizes.
 for i in [1001,1002,1010]:
  d.st(i,[(131097,d.px(0)),(131096,d.px(0)),(131095,d.pct(100)),(131094,d.pct(100)),(131084,d.num(1)),(131085,d.num(1)),(131105,d.pct(100))])
 d.st(1001,[(131087,d.pct(100)),(131083,d.enum('column'))])
 for i in [1002,1010]:d.st(i,[(131082,d.px(0)),(131087,AUTO)])
 d.save();audits.append({'variant':tag,'native_scalable_nodes':scaled_nodes,'desktop_breakpoint_routing':set_audits,'phone_multi_grid_kept':True,'top_ratio':[3,3,5,3,3],'bottom_ratio':[1,1,1,1],'outer_ratio':[3,2],'no_hide_overflow_workaround':True})
 # Refresh preload spans for modified composition sets and descriptions; no new GUIDs.
 ob=next(o for o in objs[T].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
 def ptrs(v,out):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
   else:
    for x in v.values():ptrs(x,out)
  elif isinstance(v,list):
   for x in v:ptrs(x,out)
 for k,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[T]:continue
  span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[T][pid],span);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
 ob.save_typetree(meta);changes[T][ob.path_id]=meta
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr,(bn,pid)
  for ob in saved.values():
   if ob.path_id in changes[bn] and ob.type.name=='MonoBehaviour':
    tr=ob.read_typetree()
    if 'inlineSheet' in tr:validate_ui(tr,saved[tr['inlineSheet']['m_PathID']].read_typetree())
  src=OUT/('skin-'+base if suffix else base);src.write_bytes(raw);target=folder/base;assert target.read_bytes()==before[target]
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
# Migrate only existing large-grid caches, preserving selected modules and configs.
for p,data in cache_before.items():
 tr=json.loads(data.decode('utf8'));assert len(tr['m_gridComponents'])==9
 for b,(x,y,w,h) in zip(tr['m_gridComponents'],positions):
  b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
  for c in b['m_gridElementConfigs']:c['Size']={'x':w,'y':h}
 tr['m_compositionVersion']=game_layouts[p.name]['m_compositionVersion'];raw=json.dumps(tr,ensure_ascii=False,indent=2).encode('utf8');sp=OUT/('cache-'+p.name+'.json');sp.write_bytes(raw)
 tx.append({'target':str(p),'source':str(sp),'backup':str(OUT/'backup-cache'/p.name),'before':sha(data),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'layout_ratio_grid':[68,10],'serialization_roundtrip':True,'unrelated_objects_identical':True,'catalogs_and_global_bundle_unchanged':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if cache_before:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''修正Highlight可见区域适配：桌面分支改用本游戏TeamNewsPanel已使用的ScalableBindableGridLayoutElement，保留原生所有网格绑定，按有无实时积分榜选择对应布局。手机分支保留原MultiGrid控件。桌面Small/Standard/Large统一引用当前九模块大屏布局；手机4/5断点条目不改。
上方3:3:5:3:3，下方四等分，上下3:2，中间原2:1和两图保持。使用68x10仅表达精确比例（上12/12/20/12/12，下17/17/17/17），由原生Scalable容器按区域计算显示大小，不以固定像素宽高铺出屏幕。取消外层最小宽高撑开，限定在球员条上方可用空间；没有通过overflow:hidden裁切来伪装适配，不新增整页ScrollView。模块内原生统计列表滚动保留。
所有修改基于当前游戏/皮肤独立增量。Global模块、图表、头像、轮播、数据绑定、中场/赛后/历史回放报告对象未修改，未改目录或公共API。序列化回读与未指定对象字节检查通过；实际分辨率显示仍需游戏内确认。备份及restore.ps1在本目录，带哈希保护。
''','utf8')
print(str(OUT))
