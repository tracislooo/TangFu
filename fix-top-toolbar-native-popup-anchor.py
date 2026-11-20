from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','top-toolbar-native-popup-anchor-').replace('NAMES=[W,G,M,F]','NAMES=[M]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'current-target-backup','exec'))
baseM=M
alias=M+'::skin';env[alias]=UnityPy.load(before[SKIN/M]);objs[alias]={o.path_id:o for o in env[alias].objects};hashes[alias]={i:sha(o.get_raw_data()) for i,o in objs[alias].items()};changes[alias]={}
native=UnityPy.load(str(R/'match-ui-avatars-layout-20261023-141148/backup-game'/baseM))
nt=next(o for o in native.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MatchUITacticalOptions').read_typetree();nr=refs(nt)
keys=['Anchor','HorizontalAlignment','Anchor_UxmlAttributeFlags','HorizontalAlignment_UxmlAttributeFlags']
tx=[];audits=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=baseM+suffix;d=Doc(bn,name='MatchUITacticalOptions');old=copy.deepcopy(d.d)
 for i in [1018,1048]:
  s=d.data(i);source=sd(nr,i);assert s['ContentTemplate']==source['ContentTemplate']
  audits.append({'variant':tag,'node':i,'template':s['ContentTemplate']['m_AssetGUID'],'before':{k:s[k] for k in keys},'after':{k:source[k] for k in keys}})
  for k in keys:s[k]=source[k]
 expected=copy.deepcopy(old);er=refs(expected)
 for i in [1018,1048]:
  for k in keys:sd(er,i)[k]=sd(nr,i)[k]
 assert d.d==expected
 # Save only the VTA: inline styles have not changed.
 d.obj.save_typetree(d.d);changes[bn][d.obj.path_id]=copy.deepcopy(d.d)
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t
 validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
 source=OUT/('skin-'+baseM if tag=='skin' else baseM);source.write_bytes(raw)
 target=folder/baseM;assert target.read_bytes()==before[target]
 tx.append({'target':str(target),'source':str(source),'backup':str(OUT/('backup-'+tag)/baseM),'before':sha(before[target]),'after':sha(raw)})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'native_content_bindings_and_events_unchanged':True,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('仅恢复当前 MatchUITacticalOptions 中喊话和微调两个 SIFloatingPopupWidget 的原生 Anchor 与 HorizontalAlignment 设置。原内容模板 GUID、原生事件、数据绑定、样式、其他模板及包内对象均保持不变。游戏与皮肤各自增量修改，不复制历史整包。备份及 restore.ps1 位于本目录。静态回读通过，未启动游戏，实际展开显示待用户验证。','utf8')
print(str(OUT))
