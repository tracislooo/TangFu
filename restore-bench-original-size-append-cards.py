from pathlib import Path
import json,copy
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','bench-original-size-append-cards-').replace("'NAMES=[W,G]'","'NAMES=[M]'").replace('bases=(W,G)','bases=(M,)')
exec(compile(prefix,'backup-current-list-only','exec'))
audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix;d=Doc(bn,name='SquadOverview')
 def erase(i):
  for c in list(d.a(i).get('m_Children',[])):erase(c['rid'])
  a=d.a(i);p=a['m_Parent']['rid'];sr=a.get('m_SerializedData',{}).get('rid');d.a(p)['m_Children'].remove({'rid':i});ids={i,sr};d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in ids]
  for j in ids:d.r.pop(j,None)
 # Remove every custom >11 list wrapper, restoring original native slots.
 for original,parent in [(1038,1028),(1041,1029)]:
  wrapper=d.a(d.a(original)['m_Parent']['rid'])['m_Parent']['rid']
  assert d.data(wrapper).get('name')=='SubstituteCountForCompactCards'
  index=next(j for j,c in enumerate(d.a(parent)['m_Children']) if c['rid']==wrapper)
  d.move(original,parent,index);erase(wrapper)
 wrappers=[i for i,r in list(d.r.items()) if 'm_Parent' in r.get('data',{}) and d.data(i).get('name')=='NativeManyPlayersSmallBreakpointSwitch']
 assert len(wrappers)==1
 wrapper=wrappers[0];parent=d.a(wrapper)['m_Parent']['rid'];index=next(j for j,c in enumerate(d.a(parent)['m_Children']) if c['rid']==wrapper)
 d.move(1073,parent,index);erase(wrapper)
 # Keep native count switching but use identical original-size cards in both branches.
 regular=copy.deepcopy(d.data(1087)['RowTemplate']);small=copy.deepcopy(d.data(1073)['RowTemplate'])
 d.data(1088)['RowTemplate']=copy.deepcopy(regular);d.data(1088).update(FixedElementSize=d.data(1087)['FixedElementSize'],FixedElementSizeControllerOrTouch=d.data(1087)['FixedElementSizeControllerOrTouch'])
 # Reuse the native substitute pagination for the full-width list shown by the Subs switch.
 paginationkeys=['PaginationTemplate','PaginationStyle','ClampSizeToPage']
 for i,donor in [(1087,1038),(1088,1038),(1073,1041)]:
  data=d.data(i)
  for k in paginationkeys:
   data[k]=copy.deepcopy(d.data(donor)[k]);data[k+'_UxmlAttributeFlags']=1
  data.update(Truncate=0,Truncate_UxmlAttributeFlags=1)
 assert d.data(1087)['RowTemplate']==d.data(1088)['RowTemplate']==regular
 assert d.data(1087)['FixedElementSize']==d.data(1088)['FixedElementSize']==110.
 assert d.data(1073)['FixedElementSize']==80.
 assert not any('MatchManySubstitutes' in str(x) or 'SubstituteCountForCompactCards' in str(x) or '6ed5dfdc99cd53b282b9e69d836f8941' in str(x) or 'd8b28e612b34531ba0f09ff5a425e022' in str(x) for x in d.d['references']['RefIds'])
 d.save();audits.append({'variant':tag,'all_custom_many_subs_wrappers_removed':True,'ordinary_card_size_all_counts':110,'native_small_resolution_card_size':80,'truncate':False,'native_pagination_for_additional_cards':True,'shared_card_templates_untouched':True,'only_changed_template':'SquadOverview'})
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
 validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
 src=OUT/('skin-'+bases[0] if suffix else bases[0]);src.write_bytes(raw);target=folder/bases[0];assert target.read_bytes()==before[target]
 tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[0]),'before':sha(before[target]),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('取消本轮超过11人的所有紧凑卡片入口：移除独立sublist自定义人数计数/两路开关，恢复原始列表父节点；移除小断点自定义开关。底部实际全宽主列表原生showminres两支均使用原常规卡片、步长110，不再因超过11人切换到80或60px卡片。小分辨率原生卡片仍为80px，与同分辨率<=11人一致。三个实际列表复用原生替补分页模板与样式，Truncate=false，随数据自动追加12、13、15等卡片，溢出分页，不缩放卡片。gameworld普通卡片未改；global紧凑卡片已不再被比赛列表引用，其缩放/下移/隐藏评分/图标移动不再作用于本界面。仅增量修改当前游戏和独立皮肤的SquadOverview，不影响侧栏、菜单或其他对象。文件校验通过，实际显示待确认。','utf8')
print(str(OUT))
