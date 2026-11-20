exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','four-overviews-frame-min666-'))
outputs={};audits=[];pages=[-930000000001001,-930000000001003,-940000000010000,-940000000012000]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};modified=set()
 for pid in pages:
  doc=obs[pid].read_typetree();rr=refs(doc);oldrefs=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();targets=[1001]
  for i in targets:
   p0=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131096);assert sheet['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==674
   override(rr[i]['data'],[prop(131096,px(666))])
  for i,r in oldrefs.items():
   if i not in targets:assert rr[i]==r
  validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([pid,sid]);audits.append({'target':str(folder),'page':str(pid),'nodes':targets,'root_min_height':666,'attribute_height_425_preserved':True,'other_layout_and_bindings_unchanged':True})
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h
 for pid in pages:
  doc=check[pid].read_typetree();rr=refs(doc);sheet=check[doc['inlineSheet']['m_PathID']].read_typetree()
  for i in [1001]:
   for key in [131096]:
    p0=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==key);assert sheet['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==666
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out)
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
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'root_min_height':666}))

