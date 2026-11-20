exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','third-radar-match-fourth-height-'))
outputs={};audits=[];pid=-940000000010000
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};hashes0={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
 fourth=obs[-940000000012000].read_typetree();fr=refs(fourth);fs=obs[fourth['inlineSheet']['m_PathID']].read_typetree()
 fp=next(p for p in fs['m_Rules'][fr[6298]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131087);height=fs['dimensions'][fp['m_Values'][0]['valueIndex']]['value'];assert height==200.
 for i in [6298,6228,1026,1043]:override(rr[i]['data'],[prop(131087,px(height)),prop(131096,px(height)),prop(131094,px(height))])
 override(rr[6298]['data'],[prop(131082,{'m_ValueType':1,'valueIndex':2}),prop(131084,num(0)),prop(131085,num(0))])
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in hashes0.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 d=check[pid].read_typetree();cr=refs(d);cs=check[sid].read_typetree()
 for i in [6298,6228,1026,1043]:
  for propid in [131087,131096,131094]:
   p0=next(p for p in cs['m_Rules'][cr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==propid);assert cs['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==200.
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out);audits.append({'target':str(folder),'height':height,'modified_path_ids':[str(pid),str(sid)],'all_other_objects_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'third_bans_radar_height':200,'width_ratio':'2:3 unchanged','changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'height':height,'output':str(OUT)}))
