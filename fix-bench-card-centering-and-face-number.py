from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','bench-cards-centered-no-face-number-').replace('NAMES=[W,G,M,F]','NAMES=[W,G]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-current-bench-cards','exec'))
bases=(W,G)
for bn in NAMES:
 alias=bn+'::skin';env[alias]=UnityPy.load(before[SKIN/bn]);objs[alias]={o.path_id:o for o in env[alias].objects};hashes[alias]={i:sha(o.get_raw_data()) for i,o in objs[alias].items()};changes[alias]={}
audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G=[n+suffix for n in bases]
 for bn,name,compact in [(W,'SquadOverviewPlayerBlock',False),(W,'SquadOverviewPlayerBlockSmall',False),(G,'MatchManySubstitutesSmallCard',True),(G,'MatchManySubstitutesRegularCard',True)]:
  d=Doc(bn,name=name);original=copy.deepcopy(d.d)
  right=d.named('MatchCardShirtNumber');right_data=copy.deepcopy(d.data(right));hidden=[]
  for i,r in list(d.r.items()):
   a=r.get('data',{})
   if 'm_Parent' not in a:continue
   s=d.data(i);typ=a.get('m_FullTypeName','')
   if typ=='FM.UI.FMTacticsShirt' or (typ=='SI.Bindable.SIText' and s.get('name')=='Number' and s.get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path')=='playerinfo.SquadNumber'):
    d.st(i,[(131081,d.enum('none'))]);hidden.append(i)
  assert hidden,(tag,name,'No legacy number layer found')
  if compact:
   root=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRoot')
   d.st(root,[(131087,d.pct(100)),(131096,d.px(0)),(131094,{'m_ValueType':1,'valueIndex':3}),(327682,[d.px(0),d.pct(50)])])
  assert d.data(right)==right_data
  for i,r in refs(original).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Binding/event changed',tag,name,i)
  d.save();audits.append({'variant':tag,'template':name,'hidden_legacy_number_nodes':hidden,'right_number_preserved':True,'compact_transform_origin':'left center' if compact else 'unchanged','scale':.75 if compact else 'unchanged'})
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
  for d in [d for d in documents if d.n==bn]:validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
  src=OUT/('skin-'+base if suffix else base);src.write_bytes(raw);target=folder/base;assert target.read_bytes()==before[target]
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'native_bindings_and_events_unchanged':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('超过11人分支的两份紧凑替补卡片保留75%整体缩放及现有原生列表翻页，缩放原点从左上改为左侧垂直中心，根高度明确为可用行高100%，让缩放后上下留白均分。12人、15人均继续走同一紧凑分支，超出可见宽度使用现有翻页，不压缩相邻卡片。普通及紧凑四份卡片分别隐藏旧球衣号码层；保留头像和右侧 MatchCardShirtNumber 及颜色、绑定、交互。当前游戏和独立皮肤分别增量修改，不改变已安装侧栏或其他模板。备份及受哈希保护的 restore.ps1 在本目录。静态回读与未修改对象比较通过，实际显示待游戏验证。','utf8')
print(str(OUT))
