exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','undo-card-frame-background-reference-only-'))
import uuid
KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27PlayerReportShellWithoutCardFrameBackground').hex;OLD='c560d7c346514c04f9c84c4b55b94bb4';outputs={};pid=7857044477279960178;audits=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();old=copy.deepcopy(doc);u=next(u for u in doc['m_Usings'] if u['alias']=='FigmaBaseToolTabGroupTemplate');assert u['path'] in [KEY,OLD];u.update(path=OLD,asset={'m_FileID':0,'m_PathID':0});expected=copy.deepcopy(old);eu=next(u for u in expected['m_Usings'] if u['alias']=='FigmaBaseToolTabGroupTemplate');eu.update(path=OLD,asset={'m_FileID':0,'m_PathID':0});assert doc==expected;obs[pid].save_typetree(doc)
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i!=pid:assert sha(check[i].get_raw_data())==h
 assert next(u for u in check[pid].read_typetree()['m_Usings'] if u['alias']=='FigmaBaseToolTabGroupTemplate')['path']==OLD
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out);audits.append({'target':str(folder),'restored_native_shell_guid':OLD,'later_changes_preserved':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Exit game first'
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
(OUT/'manifest.json').write_text(json.dumps({'installed':True,'runtime_verified':False,'background_removal_reverted':True,'unused_private_shell_left_unreferenced_to_preserve_later_catalog_changes':True,'changes':audits},indent=2),'utf8');print(json.dumps({'reverted':True,'output':str(OUT)}))
