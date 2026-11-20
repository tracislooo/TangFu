from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf8')
exec(compile(source.split('\nportrait = rr[1285]')[0], '<loader>', 'exec'))
base=R/'tight-identity-loans-native-contract-20261019-012840'
srcenv=UnityPy.load(str(base/'backup-game'/WN))
srcobjects={o.path_id:o for o in srcenv.objects}
srcdoc=srcobjects[FULL].read_typetree()
sr={r['rid']:r for r in srcdoc['references']['RefIds']}
srcsheet=srcobjects[sid].read_typetree()
for pool in ['m_Rules','floats','dimensions','colors','strings','assets']:
    assert sheet[pool][:len(srcsheet[pool])]==srcsheet[pool],pool
rep=json.loads((R/'gk-no-title-left-stars-horizontal-loans-20261019-011613'/'manifest.json').read_text(encoding='utf8'))
cm={int(k):int(v) for k,v in rep['inline_imports'][2]['mapping'].items()}
nodes=[1182,1180,1196,1212,1193,1295]+[cm[i] for i in [1001,1002,1004,1006,1007,1012,1013,1021,1026]]
changes=[]
for i in nodes:
    old=rr[i]['data']['m_RuleIndex']; new=sr[i]['data']['m_RuleIndex']
    if old!=new:
        rr[i]['data']['m_RuleIndex']=new
        changes.append({'rid':i,'before_rule':old,'after_rule':new})
assert changes
# Every binding, event, child relationship, template and unrelated record remains identical.
expected=copy.deepcopy(old_doc)
er={r['rid']:r for r in expected['references']['RefIds']}
for i in nodes:er[i]['data']['m_RuleIndex']=sr[i]['data']['m_RuleIndex']
assert doc==expected
assert sheet==old_sheet
assert property_value(rr[1199],131083)=='column'
assert property_value(rr[cm[1007]],131083)=='row'
assert dimension(rr[1295],131096)==64
assert rr[1203]==old_refs[1203] and rr[1217]==old_refs[1217]
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc)
output=env.file.save(packer='lz4')
saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
    if i==FULL:assert saved[i].read_typetree()==doc
    else:assert sha(saved[i].get_raw_data())==h,('unrelated change',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('restore-safe-identity-spacing-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
    bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changes':changes,'source_backup':str(base/'backup-game'/WN),'only_style_rule_indices_changed':True,'bindings_events_templates_unchanged':True,'native_vertical_contract_preserved':True,'right_stars_preserved':True,'unchanged_objects_verified':len(old_hashes)-1,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
    for folder in [GAME,SKIN]:
        (folder/WN).write_bytes(output)
        assert (folder/WN).read_bytes()==output
    for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
    for p,b in before.items():p.write_bytes(b)
    raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'restored_nodes':len(changes),'sha256':sha(output)},ensure_ascii=False))
