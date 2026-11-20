exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','third-fourth-pitch-scale85-'))
outputs={};audits=[];pid=-940000000010020
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);oldrefs=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();fit=2014;s=rr[rr[fit]['data']['m_SerializedData']['rid']]['data'];assert s['AspectMode']==2 and abs(s['AspectRatio']-.7)<1e-6
 override(rr[fit]['data'],[prop(327681,num(.85),num(.85)),prop(327682,pct(50),pct(0))])
 for i,r in oldrefs.items():
  if i!=fit:assert rr[i]==r
 assert all(rr[i]['data']['m_Parent']['rid']==fit for i in [1022,1023,2018])
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 cr=refs(check[pid].read_typetree());cs=check[sid].read_typetree();pr=next(p for p in cs['m_Rules'][cr[fit]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==327681);assert all(abs(cs['floats'][v['valueIndex']]-.85)<1e-6 for v in pr['m_Values'])
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out);audits.append({'target':str(folder),'versions':[3,4],'scale':.85,'ratio':'10:7','origin':'top centre','position_data_colours_and_click_bindings_unchanged':True,'first_second_objects_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'scale':.85}))
