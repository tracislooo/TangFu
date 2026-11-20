exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','rectangle-pitch-transparent-background-'))
outputs={};audits=[];pids=[-940000000005000,-940000000008000,-940000000010020,-960000000003030]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};modified=set()
 for pid in pids:
  doc=obs[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();old=copy.deepcopy(sheet);nodes=[1022]+([2014] if pid==pids[-1] else []);changes=[]
  for i in nodes:
   ix=rr[i]['data']['m_RuleIndex'];r=sheet['m_Rules'][ix];p0=next(p for p in r['m_Properties'] if p['m_Id']==458752);q=p0['m_Values'][0];assert q['m_ValueType']==4;oldcolor=copy.deepcopy(sheet['colors'][q['valueIndex']]);sheet['colors'].append({'r':0.,'g':0.,'b':0.,'a':0.});p0['m_Values']=[{'m_ValueType':4,'valueIndex':len(sheet['colors'])-1}];changes.append({'node':i,'old_color':oldcolor,'new_color':'transparent'})
  # Only background-color properties and newly appended transparent colors differ.
  expected=copy.deepcopy(sheet);expected['colors']=old['colors']
  for i in nodes:
   ix=rr[i]['data']['m_RuleIndex'];expected['m_Rules'][ix]=old['m_Rules'][ix]
  assert expected==old
  validate_ui(doc,sheet);obs[sid].save_typetree(sheet);modified.add(sid);audits.append({'target':str(folder),'module':str(pid),'style':str(sid),'background_changes':changes,'visual_tree_bindings_geometry_grid_fill_borders_and_text_unchanged':True})
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h
 for pid in pids:
  d=check[pid].read_typetree();rr=refs(d);s=check[d['inlineSheet']['m_PathID']].read_typetree()
  for i in [1022]+([2014] if pid==pids[-1] else []):
   p0=next(p for p in s['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458752);assert s['colors'][p0['m_Values'][0]['valueIndex']]['a']==0.
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'scope':'four main overviews plus shared player popup pitch','only_inline_background_colors_changed':True,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT)}))
