from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','many-subs-lower-no-rating-status-').replace("'NAMES=[W,G]'","'NAMES=[G]'").replace('bases=(W,G)','bases=(G,)')
exec(compile(prefix,'backup-current-compact-only','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'native-state-icon-copy','exec'))
clone_audits=[];audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix;donor=Doc(bn,name='MatchManySubstitutesRegularCard')
 for name in ['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard']:
  d=Doc(bn,name=name);original=copy.deepcopy(d.d);rating=1050
  assert d.data(rating).get('name')=='Background'
  d.st(rating,[(131081,d.enum('none'))])
  if name.endswith('SmallCard'):
   icon,mapping=clone_native(donor,donor.named('BodyLanguageMorphIcon'),1032)
  else:icon=d.named('BodyLanguageMorphIcon')
  d.move(icon,1032,2)
  d.st(icon,[(131102,d.enum('relative')),(131089,{'m_ValueType':1,'valueIndex':2}),(131103,{'m_ValueType':1,'valueIndex':2}),(131104,{'m_ValueType':1,'valueIndex':2}),(131080,{'m_ValueType':1,'valueIndex':2}),(131091,d.px(8)),(131092,d.px(0)),(131105,d.px(18)),(131087,d.px(18)),(131097,d.px(18)),(131096,d.px(18)),(131084,d.num(0)),(131085,d.num(0)),(131074,d.enum('center'))])
  d.st(1032,[(131088,d.enum('flex-start'))])
  # Offset the actual visual content rather than relying only on BindingRoot layout.
  d.st(1006,[(131102,d.enum('relative')),(131104,d.px(40))])
  for i,r in refs(original).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Existing binding/event changed',tag,name,i)
  d.save();audits.append({'variant':tag,'template':name,'content_container_down_ui_units':40,'previous_root_offset_preserved':16,'rating_hidden':True,'native_state_icon_at_old_rating_position':True,'condition_and_portrait_bindings_unchanged':True})
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
  for doc in [x for x in documents if x.n==bn and x.obj.path_id in changes[bn]]:
   if saved[doc.obj.path_id].read_typetree()==doc.d:validate_ui(doc.d,saved[doc.sid].read_typetree())
  src=OUT/('skin-'+base if suffix else base);src.write_bytes(raw);target=folder/base;assert target.read_bytes()==before[target]
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'native_subtree_copy':clone_audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'normal_cards_unchanged':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('仅修改global内超过11人两份紧凑卡片，不改gameworld普通卡片或SquadOverview列表。实际内容容器Horizontal新增相对向下40界面单位（沿用75%缩放），此前根偏移16保留。隐藏评分Background容器，将原生BodyLanguageMorphIcon置于体能后方，左间距8、18x18；小卡片原本缺少该控件，直接复制常规紧凑卡片的原生子树，保留状态绑定与提示。卡面头像、右侧号码、国旗、选择和翻页均保留。游戏和独立皮肤基于各自当前文件增量安装，备份和restore.ps1在本目录。序列化回读及未修改对象字节校验通过；未启动游戏，实际显示待确认。','utf8')
print(str(OUT))
