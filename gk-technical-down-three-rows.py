exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','gk-technical-down-three-rows-'))
outputs={};audits=[];pid=-930000000001003
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);oldrefs=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
 assert rr[1063]['data']['m_Parent']=={'rid':1011};assert rr[rr[1063]['data']['m_SerializedData']['rid']]['data']['name']=='GKTechnical'
 oldrule=sheet['m_Rules'][rr[1063]['data']['m_RuleIndex']];p0=next((p for p in oldrule['m_Properties'] if p['m_Id']==131093),None);oldmargin=0.
 if p0:
  v=p0['m_Values'][0];assert v['m_ValueType']==3;oldmargin=sheet['dimensions'][v['valueIndex']]['value']
 newmargin=oldmargin+72.;override(rr[1063]['data'],[prop(131093,px(newmargin))])
 for i,r in oldrefs.items():
  if i!=1063:assert rr[i]==r,('unexpected binding/tree edit',i)
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 cd=check[pid].read_typetree();cr=refs(cd);cs=check[sid].read_typetree();p0=next(p for p in cs['m_Rules'][cr[1063]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131093);assert cs['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==newmargin
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out);audits.append({'target':str(folder),'table':str(pid),'style':str(sid),'technical_node':1063,'old_margin_top':oldmargin,'new_margin_top':newmargin,'row_height':24,'rows_shifted':3,'all_serialized_bindings_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'shared_table_used_by_four_versions':True,'outfielder_layout_unchanged':True,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'shift_px':72,'output':str(OUT)}))
