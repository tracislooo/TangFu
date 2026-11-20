from pathlib import Path
import json
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','portal-message-portrait3x-').replace('NAMES=[W,G,M,F]','NAMES=[W]')
exec(compile(boot,'backup-current-portal-resource','exec'))

d=Doc(W,name='PortalMessagesContentBlock')
old=copy.deepcopy(d.d);olds=copy.deepcopy(d.s)
assert d.a(1019)['m_TemplateAlias']=='thumbnails-alt-person-picture'
assert d.a(1019)['m_Parent']['rid']==d.named('SenderArea')
props=d.s['m_Rules'][d.a(1019)['m_RuleIndex']]['m_Properties']
for key in [131105,131087]:
 p=next(p for p in props if p['m_Id']==key)
 assert [d.s['dimensions'][v['valueIndex']] for v in p['m_Values']]==[{'unit':1,'value':48.0}]
d.size(1019,144,144)
expected=copy.deepcopy(old)
refs(expected)[1019]['data']['m_RuleIndex']=d.a(1019)['m_RuleIndex']
assert d.d==expected
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
d.save()

data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(objs[W])
for pid,h in hashes[W].items():
 if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,tree in changes[W].items():assert saved[pid].read_typetree()==tree
validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
assert len(changes[W])==2
(OUT/W).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'template':'PortalMessagesContentBlock','portrait_node':1019,'before_px':[48,48],'after_px':[144,144],'scale':3,'bindings_structure_classes_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{W:{str(pid):t.get('m_Name','') for pid,t in changes[W].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{W:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[W],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-match-ui-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('Portal-messages 收件箱右侧消息顶部头像由48×48改为144×144，宽高均为原来三倍，固定尺寸避免被横向布局压缩。仅修改该头像实例样式；姓名、标题、消息内容、绑定及共享头像模板保持原样。已通过序列化回读和无关资源一致性校验；游戏内显示尚未验证。restore.ps1可恢复本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),**report},ensure_ascii=False),flush=True)
