exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','player-report-remove-grid-outer-padding-'))
outputs={};audits=[];pid=7857044477279960178
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);sid=rr[1010]['data']['m_SerializedData']['rid'];old=copy.deepcopy(rr[sid]);s=rr[sid]['data'];assert s['IgnoreOuterPadding']==0;s['IgnoreOuterPadding']=1;s['IgnoreOuterPadding_UxmlAttributeFlags']=1
 expected=copy.deepcopy(old);expected['data']['IgnoreOuterPadding']=1;expected['data']['IgnoreOuterPadding_UxmlAttributeFlags']=1;assert rr[sid]==expected
 obs[pid].save_typetree(doc);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i!=pid:assert sha(check[i].get_raw_data())==h
 cr=refs(check[pid].read_typetree());assert cr[sid]['data']['IgnoreOuterPadding']==1
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out);audits.append({'target':str(folder),'path_id':str(pid),'grid_ignore_outer_padding':True,'all_four_versions_inherit_host':True,'only_two_serialized_fields_changed':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'changes':audits,'cause_not_yet_runtime_confirmed':True};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT)}))
