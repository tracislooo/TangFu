exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','undo-overview-flex-height-169-'))
SOURCE=R/'four-overviews-flex-height-169-20261031-110248';pages=[-930000000001001,-930000000001003,-940000000010000,-940000000012000];outputs={}
for folder in [GAME,SKIN]:
 tag='backup-game' if folder==GAME else 'backup-skin';baseline={o.path_id:o for o in UnityPy.load(str(SOURCE/tag/W)).objects};installed={o.path_id:o for o in UnityPy.load(str(SOURCE/('game-world.bundle' if folder==GAME else 'skin-world.bundle'))).objects}
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};changedids=set()
 for pid in pages:
  sid=baseline[pid].read_typetree()['inlineSheet']['m_PathID']
  for i in [pid,sid]:
   assert sha(obs[i].get_raw_data())==sha(installed[i].get_raw_data()),('page changed after this adjustment; requires merge',i)
   obs[i].set_raw_data(baseline[i].get_raw_data());changedids.add(i)
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in changedids:assert sha(check[i].get_raw_data())==h
 for i in changedids:assert check[i].get_raw_data()==baseline[i].get_raw_data()
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out)
for p,b in before.items():assert p.read_bytes()==b
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
(OUT/'manifest.json').write_text(json.dumps({'installed':True,'runtime_verified':False,'reverted_only':'four-overviews-flex-height-169-20261031-110248','root_min_height_restored':674,'first_second_body_min_restored':438,'other_objects_unchanged':True,'gk_list312_and_radar200_preserved':True},indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT)}))
