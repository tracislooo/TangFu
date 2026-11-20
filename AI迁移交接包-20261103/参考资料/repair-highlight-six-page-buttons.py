"""Fix non-pickable page buttons and reserve a visible selector strip."""
from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-six-page-buttons-repair-').replace('NAMES=[W,G,M,F]','NAMES=[G]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
exec(compile(boot,'backup-current-six-page-containers','exec'))
audits=[]
for side in ['Home','Away']:
 doc=Doc(G,name='HighlightLower'+side+'SixPageCarousel');original=copy.deepcopy(doc.d)
 tab=doc.named('tab-group');group=doc.named('TabButtons');switch=doc.named('TabsContent')
 pages=[x['rid'] for x in doc.a(switch)['m_Children']];buttons=[x['rid'] for x in doc.a(group)['m_Children']]
 assert len(pages)==len(buttons)==6
 for i in [tab,group,*buttons]:doc.data(i).update(pickingMode=0,pickingMode_UxmlAttributeFlags=1)
 # Reserve 28px inside the private container. Position controls independently
 # of native table preferred height so a full table cannot push them out.
 doc.st(tab,[(131102,doc.enum('relative')),(131098,doc.px(28)),(131096,doc.px(0)),(131097,doc.px(0))])
 doc.st(switch,[(131087,{'m_ValueType':1,'valueIndex':2}),(131082,doc.px(0)),(131084,doc.num(1)),(131085,doc.num(1)),(131096,doc.px(0)),(131097,doc.px(0))])
 doc.st(group,[(131102,doc.enum('absolute')),(131089,doc.px(0)),(131103,doc.px(0)),(131080,doc.px(2)),(131105,doc.pct(100)),(131087,doc.px(24)),(131096,doc.px(24)),(131094,doc.px(24)),(131083,doc.enum('row')),(131088,doc.enum('center')),(131073,doc.enum('center'))])
 for i in buttons:
  assert doc.a(i)['m_FullTypeName']=='SI.Bindable.SIButton'
  doc.data(i).update(OnlyAcceptsClickEvents=0,OnlyAcceptsClickEvents_UxmlAttributeFlags=1,OnlyAcceptsSubmitEvents=0,OnlyAcceptsSubmitEvents_UxmlAttributeFlags=1)
  doc.st(i,[(262148,doc.px(1)),(262146,doc.val(4,{'r':1.,'g':1.,'b':1.,'a':struct.unpack('<f',struct.pack('<f',0.6))[0]}))])
 assert [doc.data(p)['templateId'] for p in pages]==[sd(refs(original),p)['templateId'] for p in pages]
 for i,r in refs(original).items():
  if 'ValueVariables' in r.get('data',{}):assert doc.r[i]==r,('Persistent variables changed',i)
 doc.save();audits.append({'side':side,'six_clickable_buttons':all(doc.data(i)['pickingMode']==0 for i in buttons),'selector_strip_reserved_px':28,'six_page_templates_and_order_unchanged':True,'persistent_variables_unchanged':True})
outputs={}
for bn in NAMES:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree
 for doc in documents:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/bn;dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name.startswith('catalog.'):protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for bn in NAMES:
  p=folder/bn;tx.append({'target':str(p),'source':str(outputs[bn]),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(outputs[bn].read_bytes())})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'root_cause_found':'All 12 SIButton controls were created with pickingMode Ignore (1).','checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'no_catalog_or_texture_changes':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('修复六页按钮由通用克隆帮助函数写成pickingMode=Ignore，改为Position，可接收鼠标。圆点条固定在私有容器底部并预留28px，避免球员表格首选高度挤掉选择器。六页、顺序、原生页面、Persistent变量、上方中间布局不变。文件静态回读通过；实际切换仍需游戏内确认。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'clickable_buttons':12,'runtime_verified':False},ensure_ascii=False))
