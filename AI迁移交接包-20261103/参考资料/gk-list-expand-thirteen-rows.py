exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','gk-list-expand-thirteen-rows-'))
outputs={};audits=[];pid=-930000000001003
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);oldrefs=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
 s=rr[rr[1056]['data']['m_SerializedData']['rid']]['data'];assert s['Binding']['m_direct']['Path']['m_path']=='Person.AttributesGoalkeeping';assert s['FixedElementSize']==24.
 oldprops=sheet['m_Rules'][rr[1056]['data']['m_RuleIndex']]['m_Properties'];oldp=next(p for p in oldprops if p['m_Id']==131087);oldheight=sheet['dimensions'][oldp['m_Values'][0]['valueIndex']]['value'];assert oldheight==240.
 override(rr[1056]['data'],[prop(131087,px(312)),prop(131096,px(312)),prop(131094,px(312)),prop(131085,num(0))])
 override(rr[1063]['data'],[prop(131093,px(0))])
 for i,r in oldrefs.items():
  if i not in [1056,1063]:assert rr[i]==r,('unrelated record changed',i)
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 cd=check[pid].read_typetree();cr=refs(cd);cs=check[sid].read_typetree()
 for node,propid,expected in [(1056,131087,312),(1056,131096,312),(1056,131094,312),(1063,131093,0)]:
  p=next(p for p in cs['m_Rules'][cr[node]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==propid);assert cs['dimensions'][p['m_Values'][0]['valueIndex']]['value']==expected
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out);audits.append({'target':str(folder),'old_goalkeeping_list_height':240,'new_height':312,'row_height':24,'technical_margin_top':0,'main_and_technical_height':384,'all_bindings_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'all_four_versions_shared_table':True,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'height':312}))
