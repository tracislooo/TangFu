from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','substitutes-reset-native-cards-').replace("'NAMES=[W,G]'","'NAMES=[W,G,M]'").replace('bases=(W,G)','bases=(W,G,M)')
exec(compile(prefix,'backup-current-for-native-subs','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'native-subtree-copy','exec'))
clone_audits=[];audits=[];tx=[]
# Load original UI references read-only, never restore an old whole bundle.
for base in [bases[0],bases[2]]:
 alias=base+'::native';env[alias]=UnityPy.load(str(R/'match-ui-avatars-layout-20261023-141148/backup-game'/base));objs[alias]={o.path_id:o for o in env[alias].objects};changes[alias]={}
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G,M=[x+suffix for x in bases]
 for currentname,privatename,pid in [('SquadOverviewPlayerBlock','MatchManySubstitutesRegularCard',-981101000010200),('SquadOverviewPlayerBlockSmall','MatchManySubstitutesSmallCard',-981101000010210)]:
  current=Doc(W,name=currentname);native=Doc(bases[0]+'::native',name=currentname);target=Doc(G,pid=pid)
  assert current.a(1004)['m_Properties']==native.a(1004)['m_Properties'] and current.a(1005)['m_Properties']==native.a(1005)['m_Properties']
  # Replace the formerly scaled private card with an unscaled native-size card.
  tree=copy.deepcopy(current.d);style=copy.deepcopy(current.s);tree['m_Name']=privatename;tree['inlineSheet']={'m_FileID':0,'m_PathID':target.sid};style['m_Name']=privatename+'_Style'
  pointer_remap(tree,current.af,target.af);pointer_remap(style,current.af,target.af);import_types(current.af,target.af,tree['references']['RefIds'])
  d=Doc(G,pid=pid,tree=tree,style=style)
  switch=d.add(d,1025,1002,'NativeSubstituteCardSwitch')
  # IsSub is the existing native condition used by the card's position/title switch.
  assert d.data(switch)['Binding']==current.data(1025)['Binding']
  d.move(1006,switch)
  nativebody,mapping=clone_native(native,1006,switch)
  assert [c['rid'] for c in d.a(switch)['m_Children']]==[1006,nativebody]
  d.st(switch,[(131084,d.num(1)),(131087,d.pct(100)),(131097,d.px(0))])
  d.save();audits.append({'variant':tag,'template':privatename,'native_substitute_body_copied_from':currentname,'first_team_body_from_current_installed_template':True,'no_scale_or_offset':True,'original_native_rating_and_status':True})
 # Restore all native expanded list properties, including native widths/pagination.
 native=Doc(bases[2]+'::native',name='SquadOverview');d=Doc(M,name='SquadOverview')
 regular='6ed5dfdc99cd53b282b9e69d836f8941';small='d8b28e612b34531ba0f09ff5a425e022'
 for i in [1038,1041,1073,1087,1088]:
  actual=d.data(i);source=native.data(i)
  assert actual['uxmlAssetId']==source['uxmlAssetId']
  for key,value in source.items():
   if key in actual:actual[key]=copy.deepcopy(value)
  actual['RowTemplate']['m_AssetGUID']=small if i in [1041,1073,1088] else regular
  actual['RowTemplate_UxmlAttributeFlags']=1
  assert actual['FixedElementSize']==source['FixedElementSize']
 d.save()
 # Refresh only the existing private assets' preload spans for their new native content.
 def pointers(v,out):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
   else:
    for x in v.values():pointers(x,out)
  elif isinstance(v,list):
   for x in v:pointers(x,out)
 ob=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
 for pid in [-981101000010200,-981101000010210]:
  span=[{'m_FileID':0,'m_PathID':pid},{'m_FileID':0,'m_PathID':pid-1}];pointers(changes[G][pid],span);pointers(changes[G][pid-1],span)
  entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
 ob.save_typetree(meta);changes[G][ob.path_id]=meta
 for base in [bases[1],bases[2]]:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
  for ob in saved.values():
   if ob.path_id in changes[bn] and ob.type.name=='MonoBehaviour':
    t=ob.read_typetree()
    if 'inlineSheet' in t:validate_ui(t,saved[t['inlineSheet']['m_PathID']].read_typetree())
  src=OUT/('skin-'+base if suffix else base);src.write_bytes(raw);target=folder/base;assert target.read_bytes()==before[target]
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'gameworld_bundle_untouched':True,'native_list_properties_restored':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('按用户最新要求重置替补原版：两份原紧凑私有卡片改为未缩放、无位移的普通卡片，由原生playerinfo.IsSub条件区分，首发使用当前已安装自定义内容，替补使用原版球衣、姓名、评分、体能/伤病和状态图标子树。原版仅从原生备份读取对应节点及样式，不覆盖历史整包。五个展开列表的原生宽度、模板参数和分页/滚动属性恢复，替补和首发数据绑定保持。普通断点110、小断点80，超过11人按原生行为处理，不再使用先前的75%缩放、偏移、评分隐藏或图标移位。当前gameworld包（首发来源）未修改；Highlight布局、有球竖向修复、侧栏、工具栏及其他对象保持。现有GUID复用并刷新对应资源预加载跨度，无新增公共API。游戏内实际显示待用户验证。','utf8')
print(str(OUT))
