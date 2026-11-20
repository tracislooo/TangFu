from pathlib import Path
import json,copy
R=Path(__file__).parent
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-comparison-number-widths-').replace("'NAMES=[W,G]'","'NAMES=[G]'").replace('bases=(W,G)','bases=(G,)')
exec(compile(prefix,'backup-current-comparison','exec'))
audits=[];tx=[];AUTO={'m_ValueType':1,'valueIndex':2};NONE={'m_ValueType':1,'valueIndex':3}
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G=bases[0]+suffix;d=Doc(G,name='HighlightCompactMatchStatsThreeByThree');original=copy.deepcopy(d.d)
 def space(i):d.st(i,[(p,d.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
 def walk(i):
  yield i
  for c in d.a(i)['m_Children']:yield from walk(c['rid'])
 groups=[]
 for bar in [1032,1035,1038,1041,1044]:
  children=[c['rid'] for c in d.a(bar)['m_Children']];assert len(children)==3;left,track,right=children
  space(bar);d.st(bar,[(131083,d.enum('row')),(131105,d.pct(100)),(131097,d.px(0)),(131095,d.pct(100)),(131087,d.px(14)),(131096,d.px(0)),(131074,d.enum('stretch')),(131088,d.enum('flex-start')),(131084,d.num(0)),(131085,d.num(1))])
  for frame,align in [(left,'middle-left'),(right,'middle-right')]:
   space(frame);d.st(frame,[(131105,d.px(32)),(131097,d.px(32)),(131095,d.px(32)),(131087,d.px(14)),(131096,d.px(0)),(131082,d.px(32)),(131084,d.num(0)),(131085,d.num(0))])
   for i in walk(frame):
    if i==frame:continue
    d.st(i,[(131105,d.pct(100)),(131097,d.px(0)),(131095,d.pct(100)),(131087,d.px(14)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
    if d.a(i)['m_FullTypeName']=='SI.Bindable.SIText':d.st(i,[(65537,d.px(10)),(65546,d.enum(align))])
  space(track);d.st(track,[(131105,AUTO),(131097,d.px(0)),(131095,NONE),(131082,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131091,d.px(4)),(131092,d.px(4)),(131087,d.px(8)),(131096,d.px(0)),(131074,d.enum('center'))])
  for c in d.a(track)['m_Children']:
   i=c['rid'];d.st(i,[(131105,d.pct(100)),(131097,d.px(0)),(131095,d.pct(100)),(131084,d.num(1)),(131085,d.num(1))])
  groups.append({'bar':bar,'left':left,'track':track,'right':right,'number_width_each':32,'gaps_each':4,'track':'remaining width'})
 for i,r in refs(original).items():
  if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Data binding changed',i)
 d.save();raw=env[G].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 for pid,h in hashes[G].items():
  if pid not in changes[G]:assert sha(saved[pid].get_raw_data())==h
 for pid,tr in changes[G].items():assert saved[pid].read_typetree()==tr
 validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
 src=OUT/(('skin-' if suffix else '')+bases[0]);src.write_bytes(raw);target=folder/bases[0];tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[0]),'before':sha(before[target]),'after':sha(raw)});audits.append({'variant':tag,'groups':groups,'all_serialized_bindings_unchanged':True,'all_other_objects_byte_identical':True})
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
state=json.loads((R/'current-highlight-layout.json').read_text('utf8'));(OUT/'previous-highlight-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8');state.update(status='prepared',patch=str(OUT),source_script=str(Path(__file__)),restore=str(OUT/'restore.ps1'),verification=str(OUT/'manifest.json'),runtime_verified=False,comparison_numbers='32px columns either side, 4px gaps, bars shrink to remaining width',backup_directories=[str(OUT/('backup-'+t)) for t in ['game','skin']]);(OUT/'highlight-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8');installer+="\nstate=json.loads((out/('previous-highlight-state.json' if restore else 'highlight-state.json')).read_text('utf8'))\nif not restore:state.update(status='installed',installed_files=len(tx))\n(out.parent/'current-highlight-layout.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')\n";(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes());print(OUT)
