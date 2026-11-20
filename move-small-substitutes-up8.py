from pathlib import Path
import json,copy
R=Path(__file__).parent
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','small-substitutes-up8-').replace("'NAMES=[W,G]'","'NAMES=[G]'").replace('bases=(W,G)','bases=(G,)')
exec(compile(prefix,'backup-small-sub-offset','exec'))
tx=[];audits=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix;d=Doc(bn,name='SmallSubstituteCardLowerNoRating');original=copy.deepcopy(d.d);gate=d.named('OnlySmallSubstitutePresentation');body=d.a(gate)['m_Children'][1]['rid'];rule=d.s['m_Rules'][d.a(body)['m_RuleIndex']];h=next(p for p in rule['m_Properties'] if p['m_Id']==131104)['m_Values'][0];old=d.s['dimensions'][h['valueIndex']]['value'];assert old==16;d.st(body,[(131104,d.px(8))]);d.save()
 for i,r in refs(original).items():
  if i!=body:assert d.r[i]==r
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t
 validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree());src=OUT/(('skin-' if suffix else '')+bases[0]);src.write_bytes(raw);target=folder/bases[0];tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[0]),'before':sha(before[target]),'after':sha(raw)});audits.append({'variant':tag,'old_top':16,'new_top':8,'delta':-8,'all_other_nodes_and_bindings_unchanged':True})
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}},indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes());print(OUT)
