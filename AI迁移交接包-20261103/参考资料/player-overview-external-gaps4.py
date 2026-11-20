exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','player-overview-external-gaps4-'))
outputs={};audits=[];pages=[-930000000001001,-930000000001003];host=7857044477279960178
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};modified=set()
 for pid in pages:
  doc=obs[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();override(rr[1002]['data'],[prop(131093,px(4))]);validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([pid,sid])
 doc=obs[host].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();scope='fm27-player-overview-tight-external-gaps';root=rr[1001]['data'];root.setdefault('m_Classes',[]).append(scope);ptr={'m_FileID':0,'m_PathID':sid}
 if ptr not in root['m_Stylesheets']:root['m_Stylesheets'].append(ptr)
 idx=rule([prop(131093,px(4))]);sheet['m_Rules'][idx]['m_ComplexSelectors']=[{'m_Specificity':20,'m_Selectors':[{'m_Parts':[{'m_Value':scope,'m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'si-grid-element-margin-top','m_Type':3}],'m_PreviousRelationship':2}],'ruleIndex':idx}]
 validate_ui(doc,sheet);obs[host].save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([host,sid]);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h
 for pid in pages:
  d=check[pid].read_typetree();cr=refs(d);cs=check[d['inlineSheet']['m_PathID']].read_typetree();p0=next(p for p in cs['m_Rules'][cr[1002]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131093);assert cs['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==4
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out);audits.append({'target':str(folder),'banner_to_attributes_gap_first_second':4,'native_grid_external_top_margin':4,'scope':'PlayerReport only','root_min674_body_min438_and_internal_heights_preserved':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
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
