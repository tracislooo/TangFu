from pathlib import Path
import json

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-height-48-52-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-bundle-and-load-codecs','exec'))
d=Doc(G,name='MatchViewer_12x4');old=copy.deepcopy(d.d);rr=refs(old);old_style=copy.deepcopy(d.s)
upper=d.named('HighlightPitchUpperHalf');lower=d.named('HighlightDataLowerHalf');separator=d.named('HighlightTwoPixelSeparator')
assert d.a(1008)['m_Children']==[{'rid':upper},{'rid':separator},{'rid':lower}]
for node,previous,new in [(upper,55,48),(lower,45,52)]:
 rule=d.s['m_Rules'][d.a(node)['m_RuleIndex']]
 prop=next(p for p in rule['m_Properties'] if p['m_Id']==131084)
 assert d.s['floats'][prop['m_Values'][0]['valueIndex']]==previous
 d.st(node,[(131084,d.num(new))])
for rid,record in rr.items():
 if rid not in [upper,lower]:assert d.r[rid]==record,('Unrequested record changed',rid)
 else:
  expected=copy.deepcopy(record);expected['data']['m_RuleIndex']=d.r[rid]['data']['m_RuleIndex'];assert d.r[rid]==expected
  previous_props={p['m_Id']:p for p in old_style['m_Rules'][record['data']['m_RuleIndex']]['m_Properties']}
  current_props={p['m_Id']:p for p in d.s['m_Rules'][d.a(rid)['m_RuleIndex']]['m_Properties']}
  assert all(previous_props.get(k)==v for k,v in current_props.items() if k!=131084)
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value
 else:assert d.s[key]==value
d.save()
data=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h
for pid,tree in changes[G].items():assert check[pid].read_typetree()==tree
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/G).write_bytes(data)
for path,b in before.items():assert path.read_bytes()==b
for path,h in protected.items():assert sha(path.read_bytes())==h
for path in before:
 if path.name.startswith('catalog.'):protected[path]=sha(before[path])
report={'passed':True,'upper_percent':48,'lower_percent':52,'gap_preserved_pixels':2,'only_two_flex_weights_changed':True,'all_other_records_styles_and_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'upper_percent':48,'lower_percent':52},ensure_ascii=False))
