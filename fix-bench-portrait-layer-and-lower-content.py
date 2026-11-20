from pathlib import Path
import json,copy
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','bench-portrait-front-lower-content-')
exec(compile(prefix,'backup-latest-card-layers','exec'))
audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G=[n+suffix for n in bases]
 for bn,name,compact in [(W,'SquadOverviewPlayerBlock',False),(W,'SquadOverviewPlayerBlockSmall',False),(G,'MatchManySubstitutesSmallCard',True),(G,'MatchManySubstitutesRegularCard',True)]:
  d=Doc(bn,name=name);original=copy.deepcopy(d.d)
  hero=1028;portrait_holder=1043;assert d.a(portrait_holder)['m_Parent']['rid']==hero
  flag=d.named('MatchCardNationalityFlag');number=d.named('MatchCardNumberKitColourBinding')
  assert d.a(flag)['m_Parent']['rid']==hero and d.a(number)['m_Parent']['rid']==hero
  d.move(portrait_holder,hero)
  assert d.a(hero)['m_Children'][-1]['rid']==portrait_holder
  if compact:
   root=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRoot')
   d.st(root,[(131102,d.enum('relative')),(131104,d.px(16))])
  for i,r in refs(original).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Binding/event changed',tag,name,i)
  d.save();audits.append({'variant':tag,'template':name,'portrait_drawn_after_flag_and_number':True,'compact_top_offset_ui_units':16 if compact else 0,'right_number_and_flag_bindings_preserved':True})
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
(OUT/'修改说明.md').write_text('普通卡片位于gameworld的SquadOverviewPlayerBlock/Small；超过11人卡片位于global的MatchManySubstitutesRegularCard/SmallCard。四模板均将头像容器1043放至头像区域1028子元素末尾，以后绘制方式显示在国旗和号码上方；保留国旗、右侧号码和原数据绑定。仅两份超过11人卡片额外向下偏移16个界面单位，保留75%缩放及原生列表分页。游戏与皮肤独立增量修改，备份及restore.ps1在本目录；未修改侧栏或其他模板。文件校验通过，实际显示待用户验证。','utf8')
print(str(OUT))
