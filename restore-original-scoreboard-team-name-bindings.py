from pathlib import Path
import sys,json
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','scoreboard-original-names-restored-').replace('NAMES=[W,G,M,F]','NAMES=[M]')
exec(compile(boot,'backup-current-bundle-and-load-codecs','exec'))
baseline=R/'scoreboard-three-letter-names-20261023-235308'/'backup-game'/M
original_objects={o.path_id:o for o in UnityPy.load(str(baseline)).objects}
first_manifest=json.loads((R/'scoreboard-three-letter-names-20261023-235308/manifest.json').read_text('utf8'))
restored=[]
for entry in first_manifest['changed_templates']:
 pid=entry['path_id'];obj=objs[M][pid];doc=obj.read_typetree();rr=refs(doc);old=copy.deepcopy(rr);native=original_objects[pid].read_typetree();nr=refs(native);changed=set()
 for rid,r in nr.items():
  binding=r.get('data',{}).get('TextBinding',{});vf=binding.get('m_visualFunction',{})
  if vf.get('m_target',{}).get('m_guid')!='596043a56cb28154d905f709e29ca7c7':continue
  raw=vf['m_inputs']['m_variable']['m_argumentBytes']
  if b'[%team#1-3letter]' not in bytes(raw):continue
  rr[rid]['data']['TextBinding']=copy.deepcopy(binding);changed.add(rid)
  assert rr[rid]['data']['TextBinding']==binding
  restored.append({'template':doc['m_Name'],'path_id':pid,'text_record':rid})
 for rid in old:
  if rid not in changed:assert rr[rid]==old[rid],('unrelated record changed',pid,rid)
  else:
   expected=copy.deepcopy(old[rid]);expected['data']['TextBinding']=nr[rid]['data']['TextBinding'];assert expected==rr[rid]
 validate_ui(doc,objs[M][doc['inlineSheet']['m_PathID']].read_typetree());obj.save_typetree(doc);changes[M][pid]=copy.deepcopy(doc)
 (OUT/'templates'/(doc['m_Name']+'-'+str(pid)+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
assert len(restored)==20 and len(changes[M])==9
output=env[M].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[M])
for pid,h in hashes[M].items():
 if pid not in changes[M]:assert sha(check[pid].get_raw_data())==h,('unrelated asset changed',pid)
for pid,expected in changes[M].items():assert check[pid].read_typetree()==expected
(OUT/M).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'restored_original_bindings':restored,'baseline':str(baseline),'changes':{M:{str(pid):d['m_Name'] for pid,d in changes[M].items()}},'scoreboard_position_goal_popup_and_other_ui_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{M:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[],'unrelated_objects_unchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps({'passed':True,'original_team_name_bindings_exactly_restored':20,'templates':9,'all_other_records_and_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[M],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'original_bindings_restored':len(restored)},ensure_ascii=False))
