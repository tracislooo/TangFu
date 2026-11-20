exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','restore-role-list-vertical-scroll234-'))
outputs={};audits=[];pids=[-940000000008000,-940000000010020]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};modified=set()
 for pid in pids:
  doc=obs[pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();table=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedTable' and rr[r['data']['m_SerializedData']['rid']]['data'].get('SelectedItemsBinding',{}).get('m_path')=='rolemask');sdid=rr[table]['data']['m_SerializedData']['rid'];s=rr[sdid]['data']
  fields={'ScrollViewMode':0,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':1,'MouseWheelScrollSize':24.0,'ClampSizeToPage':0,'Truncate':0}
  for k,v in fields.items():s[k]=v;s[k+'_UxmlAttributeFlags']=1
  chain=[];i=table
  while i!=2002:
   chain.append(i);override(rr[i]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131074,en('stretch')),prop(131073,en('stretch'))]);i=rr[i]['data']['m_Parent']['rid']
  override(rr[table]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(458768,en('hidden'))])
  for i,r in old.items():
   if i==sdid:
    x=copy.deepcopy(rr[i]);
    for k in fields:
     x['data'][k]=r['data'][k];x['data'][k+'_UxmlAttributeFlags']=r['data'][k+'_UxmlAttributeFlags']
    assert x==r
   elif i not in chain:assert rr[i]==r
  validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([pid,sid]);audits.append({'target':str(folder),'module':str(pid),'versions':[2] if pid==pids[0] else [3,4],'bounded_role_chain':chain,'vertical_scroller':'AlwaysVisible','horizontal_scroller':'Hidden','wheel_step':24,'all_player_role_phase_selection_bindings_unchanged':True})
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h,(folder,i)
 for pid in pids:
  d=check[pid].read_typetree();rr=refs(d);s=next(r['data'] for r in rr.values() if r.get('data',{}).get('SelectedItemsBinding',{}).get('m_path')=='rolemask');assert s['ScrollViewMode']==0 and s['VerticalScrollerVisibility']==1 and s['HorizontalScrollerVisibility']==2
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'first_version_unchanged':True,'pitch_and_comparison_unchanged':True,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
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
