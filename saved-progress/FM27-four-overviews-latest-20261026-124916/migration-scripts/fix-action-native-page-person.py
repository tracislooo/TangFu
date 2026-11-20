from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
assert rr[1109]['data']['BindingPaths']==[{'m_path':'person'}]
# Native menu references the page Person, without introducing a local Person alias.
rr[1109]['data']['BindingPaths']=[{'m_path':'Person'}]
assert not any(m.get('from')=='Person' for r in rr.values() for m in r.get('data',{}).get('Mappings',[]))
assert {i for i in old_refs if rr[i]!=old_refs[i]}=={1109}
assert sheet==old_sheet
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc)
output=env.file.save(packer='lz4')
saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i==FULL:assert saved[i].read_typetree()==doc
 else:assert sha(saved[i].get_raw_data())==h,('Unexpected change',i)
for p,data in before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('action-native-page-Person-binding-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'change':'Only native menu BindingPaths person -> Person; no local Person remapping','changed_asset':FULL,'unchanged_assets_verified':len(old_hashes)-1,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:
   (folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except Exception:
  for p,data in before.items():p.write_bytes(data)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),**report},ensure_ascii=False,indent=2))
