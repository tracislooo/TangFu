from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
base=R/'profile-beside-contract-position-comparison-20261019-020338'
rep=json.loads((base/'manifest.json').read_text(encoding='utf8'))
imp=rep['inline_imports'][0];assert imp['prefix']=='OverviewPosition_'
source_env=UnityPy.load(str(base/'backup-game'/WN));so={o.path_id:o for o in source_env.objects}
sd=so[FULL].read_typetree();sr={r['rid']:r for r in sd['references']['RefIds']}
ss=so[sid].read_typetree()
for pool in ['m_Rules','floats','dimensions','colors','strings','assets']:
 assert sheet[pool][:len(ss[pool])]==ss[pool],pool
# Restore the original native instance and its exact template serialized data.
template_sd=sr[1007]['data']['m_SerializedData']['rid']
for i in [1007,template_sd]:rr[i]=copy.deepcopy(sr[i])
removed={int(v) for k,v in imp['mapping'].items() if int(k)!=1000 and int(v) in rr}
assert not ({1007,template_sd}&removed)
doc['references']['RefIds']=[rr[r['rid']] for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed:del rr[i]
doc['m_Usings']=[u for u in doc['m_Usings'] if not u['alias'].startswith('OverviewPosition_')]
# Restore its original width allocation and the original right sidebar width limits.
rr[1014]['data']['Settings']=copy.deepcopy(sr[1014]['data']['Settings'])
for i in [1703,1011]:rr[i]['data']['m_RuleIndex']=sr[i]['data']['m_RuleIndex']
# Profile details remain beside the existing contract, with the old Info header removed.
assert rr[1031]['data']['m_Parent']=={'rid':1184}
assert rr[1184]['data']['m_Children']==[{'rid':1031},{'rid':1199}]
assert 1029 not in rr
assert rr[1007]==sr[1007] and rr[template_sd]==sr[template_sd]
changed={i for i in rr if rr[i]!=old_refs[i]}
assert changed<={1007,template_sd,1014,1703,1011},changed
for i in [1031,1184,1199,1049,1050,1051,1072,1087,1066,1069,1096]:assert rr[i]==old_refs[i],i
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i==FULL:assert saved[i].read_typetree()==doc
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('restore-native-position-compare-only-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL],'native_role_selector_restored':True,'native_width_settings_restored':True,'profile_beside_contract_preserved':True,'removed_import_records':sorted(removed),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-1}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  (folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output)},ensure_ascii=False))
