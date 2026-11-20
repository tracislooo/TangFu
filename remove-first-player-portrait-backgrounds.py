exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','remove-first-player-portrait-backgrounds-'))
outputs={};audits=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};oldhash={i:sha(o.get_raw_data()) for i,o in obs.items()};modified=set()
 for pid,o in list(obs.items()):
  if pid!=-930000000001001:continue
  doc=o.read_typetree()
  if 'references' not in doc or 'inlineSheet' not in doc:continue
  rr=refs(doc);hits=[]
  for i,r in rr.items():
   v=r.get('data',{})
   if 'm_FullTypeName' not in v:continue
   name=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','')
   if name in ['PlayerTopBackgroundTextureLayer','ReportBlueLightBelowPlayerTopBackground']:hits.append((i,name))
  if not hits:continue
  sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
  for i,name in hits:override(rr[i]['data'],[prop(131081,en('none')),prop(458753,en('none'))])
  root=next(i for i,r in rr.items() if r.get('data',{}).get('m_Parent',{}).get('rid')==1000 and 'm_Classes' in r.get('data',{}))
  rr[root]['data']['m_Classes'].append('fm27-first-without-top-backgrounds');rr[root]['data']['m_Stylesheets'].append({'m_FileID':0,'m_PathID':sid})
  idx=rule([prop(131081,en('none')),prop(458753,en('none'))]);sheet['m_Rules'][idx]['m_ComplexSelectors']=[{'m_Specificity':110,'m_Selectors':[{'m_Parts':[{'m_Value':'fm27-first-without-top-backgrounds','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'ReportBlueLightBelowPlayerTopBackground','m_Type':4}],'m_PreviousRelationship':2}],'ruleIndex':idx}]
  validate_ui(doc,sheet);o.save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([pid,sid]);audits.append({'target':str(folder),'page':doc.get('m_Name'),'path_id':str(pid),'style_id':str(sid),'hidden_layers':[n for _,n in hits]})
 assert len(modified)==2
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};assert set(check)==set(obs)
 for i,h in oldhash.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h
 for i in modified:assert check[i].read_typetree()['m_Name']==obs[i].read_typetree()['m_Name']
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out)
for path,b in before.items():assert path.read_bytes()==b
for path,h in protected.items():assert sha(path.read_bytes())==h
report={'installed':False,'runtime_verified':False,'textures_not_deleted':True,'background_catalogs_global_and_other_objects_unchanged':True,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for path in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if path.parent==GAME else 'backup-skin')/W)+"' -Destination '"+str(path)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for path,b in outputs.items():path.write_bytes(b);assert path.read_bytes()==b
 for path,h in protected.items():assert sha(path.read_bytes())==h
except BaseException:
 for path in outputs:path.write_bytes(before[path])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'layers_per_target':len(audits)//2}))


