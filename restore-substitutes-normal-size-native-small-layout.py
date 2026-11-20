from pathlib import Path
import json,copy
R=Path(__file__).parent
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','substitutes-normal-size-native-small-layout-').replace("'NAMES=[W,G]'","'NAMES=[M]'").replace('bases=(W,G)','bases=(M,)')
exec(compile(prefix,'backup-substitute-layout-only','exec'))
native_path=R/'match-ui-avatars-layout-20261023-141148/backup-game'/bases[0];ne=UnityPy.load(str(native_path));no={o.path_id:o for o in ne.objects};nt=next(o.read_typetree() for o in ne.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='SquadOverview');nr=refs(nt);ns=no[nt['inlineSheet']['m_PathID']].read_typetree();tx=[];audits=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix;d=Doc(bn,name='SquadOverview');original=copy.deepcopy(d.d);removed=[]
 def erase(i):
  for c in list(d.a(i).get('m_Children',[])):erase(c['rid'])
  a=d.a(i);p=a['m_Parent']['rid'];sr=a.get('m_SerializedData',{}).get('rid');d.a(p)['m_Children'].remove({'rid':i});ids={i,sr};d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in ids]
  for j in ids:d.r.pop(j,None)
 for i,parent in [(1038,1028),(1041,1029)]:
  holder=d.a(i)['m_Parent']['rid']
  if holder!=parent:
   wrapper=d.a(holder)['m_Parent']['rid'];assert d.data(wrapper).get('name')=='SubstituteCountForCompactCards'
   order=d.a(parent)['m_Children'].index({'rid':wrapper});d.move(i,parent,order);erase(wrapper);removed.append(wrapper)
 # Any previous compact override on the small full-width list also goes away.
 wrappers=[i for i,a in list(d.r.items()) if 'm_SerializedData' in a.get('data',{}) and d.data(i).get('name')=='NativeManyPlayersSmallBreakpointSwitch']
 for wrapper in wrappers:
  parent=d.a(wrapper)['m_Parent']['rid'];order=d.a(parent)['m_Children'].index({'rid':wrapper});d.move(1073,parent,order);erase(wrapper);removed.append(wrapper)
 layoutkeys=['FixedElementSize','FixedElementSizeControllerOrTouch','PaginationTemplate','PaginationStyle','ClampSizeToPage','Truncate','Direction','ScrollViewMode','NumPreviewElements']
 for i in [1038,1041,1073,1087,1088]:
  current=d.data(i);native=sd(nr,i);assert current['uxmlAssetId']==native['uxmlAssetId']
  oldtemplate=copy.deepcopy(current['RowTemplate']);binding=copy.deepcopy(current['Binding'])
  for key in layoutkeys:
   if key in current and key in native:
    current[key]=copy.deepcopy(native[key])
    flag=key+'_UxmlAttributeFlags'
    if flag in native:current[flag]=native[flag]
  current['RowTemplate']['m_AssetGUID']='b1f80633e62ce0e43b18cbe67256ad14' if i in [1038,1087] else 'eb433e33a56539049910c63aabdec0d2'
  current['RowTemplate_UxmlAttributeFlags']=1
  assert current['Binding']==binding
 # Restore only layout properties of the small-resolution containers/lists.
 for i in [1029,1041,1073,1088]:
  record=nr[i]['data'];idx=record.get('m_RuleIndex',-1);nativeprops=ns['m_Rules'][idx]['m_Properties'] if idx>=0 else []
  props=[]
  for prop in nativeprops:
   if not 131072<=prop['m_Id']<=131105:continue
   handles=[]
   for h in prop['m_Values']:
    typ=h['m_ValueType'];handles.append(d.val(typ,copy.deepcopy(ns[poolmap[typ]][h['valueIndex']])) if typ in poolmap else copy.deepcopy(h))
   props.append((prop['m_Id'],handles))
  currentidx=d.a(i).get('m_RuleIndex',-1)
  if currentidx>=0:
   currentprops=copy.deepcopy(d.s['m_Rules'][currentidx]['m_Properties']);keep=[p for p in currentprops if not 131072<=p['m_Id']<=131105];d.s['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':keep,'line':-1});d.a(i)['m_RuleIndex']=len(d.s['m_Rules'])-1
  if props:d.st(i,props)
 assert d.a(1038)['m_Parent']['rid']==1028 and d.a(1041)['m_Parent']['rid']==1029
 assert d.data(1038)['RowTemplate']==d.data(1087)['RowTemplate']
 assert d.data(1038)['FixedElementSize']==d.data(1087)['FixedElementSize']==110.
 assert d.data(1041)['FixedElementSize']==d.data(1073)['FixedElementSize']==80.
 assert not any('SubstituteCountForCompactCards' in str(x) or '6ed5dfdc99cd53b282b9e69d836f8941' in str(x) or 'd8b28e612b34531ba0f09ff5a425e022' in str(x) for x in d.d['references']['RefIds'])
 d.save();raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t
 validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
 src=OUT/(('skin-' if suffix else '')+bases[0]);src.write_bytes(raw);target=folder/bases[0];tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[0]),'before':sha(before[target]),'after':sha(raw)})
 audits.append({'variant':tag,'old_compact_wrappers_removed':removed,'regular_substitute_card_matches_regular_starting_card':True,'regular_card_step':110,'small_native_step':80,'native_substitute_pagination_restored':True,'all_player_card_templates_and_contents_untouched':True})
report={'installed':False,'runtime_verified':False,'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅改当前游戏和独立皮肤SquadOverview的替补入口及小分辨率布局。移除独立替补列表超过11人转入75%紧凑卡片的旧包装层，大分辨率恢复与首发相同的当前常规卡片、110px原生步长，保留右侧替补区及原生分页。小分辨率恢复原生容器/列表布局、80px原生步长及分页参数。头像/姓名/国旗/号码/体能百分比/评分/表情等卡片模板及绑定均未修改，原生大屏人数分支原样保留。其他包受哈希保护，不改Highlight等资源。序列化、原生参数及无关对象检查通过，实际大小与翻页仍待游戏验证。备份及restore.ps1在本目录，带哈希保护。','utf8')
print(OUT)
