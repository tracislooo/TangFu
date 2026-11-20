exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','four-pitches-native-ratio-zones-sync-'))
outputs={};audits=[];pids=[-940000000005000,-940000000008000,-940000000010020]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};modified=set()
 source=obs[-940000000008000].read_typetree();sr=refs(source);sourcefit=sr[2012];sourceserial=sr[sourcefit['data']['m_SerializedData']['rid']];ratio=sourceserial['data']['AspectRatio'];assert abs(ratio-.7)<1e-6
 for pid in pids:
  doc=obs[pid].read_typetree();rr=refs(doc);oldrefs=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();fit=1010 if pid==pids[0] else (2012 if pid==pids[1] else 2014);sdid=rr[fit]['data']['m_SerializedData']['rid']
  if pid==pids[0]:
   prev=copy.deepcopy(rr[sdid]);new=copy.deepcopy(sourceserial);new['rid']=sdid
   for k in new['data']:
    if k in prev['data']:new['data'][k]=copy.deepcopy(prev['data'][k])
   new['data']['uxmlAssetId']=rr[fit]['data']['m_Id'];rr[sdid].clear();rr[sdid].update(new);rr[fit]['data']['m_FullTypeName']='SI.Bindable.SIAspectRatioFitter'
  rr[sdid]['data'].update(AspectMode=2,AspectMode_UxmlAttributeFlags=1,AspectRatio=ratio,AspectRatio_UxmlAttributeFlags=1)
  override(rr[fit]['data'],[prop(131102,en('relative')),prop(131105,pct(100)),prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(131095,pct(100)),prop(131094,pct(100)),prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('center')),prop(131099,px(0)),prop(131100,px(0)),prop(131098,px(0)),prop(131101,px(0)),prop(262150,px(0)),prop(262151,px(0))])
  zones=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.WrappedObjectList' and rr[r['data']['m_SerializedData']['rid']]['data'].get('name')=='OverviewFourteenPositionZones')
  for i in [1022,1023,zones]:
   parent=rr[i]['data']['m_Parent']['rid']
   if parent!=fit:rr[parent]['data']['m_Children'].remove({'rid':i});rr[fit]['data']['m_Children'].append({'rid':i});rr[i]['data']['m_Parent']={'rid':fit}
   override(rr[i]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131103,px(0)),prop(131080,px(0)),prop(131105,pct(100)),prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(131095,pct(100)),prop(131094,pct(100)),prop(262150,px(0)),prop(262151,px(0))])
  # Preserve player data, zone mapping, colours, line shapes and interaction bindings.
  for i,r in oldrefs.items():
   if i!=sdid and 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('binding changed',pid,i)
  validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([pid,sid]);audits.append({'target':str(folder),'module':str(pid),'versions':[1] if pid==pids[0] else ([2] if pid==pids[1] else [3,4]),'native_width_height':'10:7','aspect_mode':2,'same_parent':fit,'zone_layer':zones,'bindings_preserved':True})
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h
 for pid in pids:
  doc=check[pid].read_typetree();rr=refs(doc);fit=1010 if pid==pids[0] else (2012 if pid==pids[1] else 2014);sd0=rr[rr[fit]['data']['m_SerializedData']['rid']]['data'];assert sd0['AspectMode']==2 and abs(sd0['AspectRatio']-.7)<1e-6
  assert rr[1022]['data']['m_Parent']['rid']==fit and rr[1023]['data']['m_Parent']['rid']==fit
  zones=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.WrappedObjectList' and rr[r['data']['m_SerializedData']['rid']]['data'].get('name')=='OverviewFourteenPositionZones');assert rr[zones]['data']['m_Parent']['rid']==fit
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'changes':audits,'no_new_resources_or_catalog_changes':True};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'ratio':'10:7'}))
