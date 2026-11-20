exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','third-radar-remove-outer-scroll-'))
outputs={};audits=[];pid=-940000000010000
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
 # Keep the 390px block and 200px radar; reclaim decorative vertical margins.
 for i in [6298,6266,6264]:override(rr[i]['data'],[prop(131093,px(0)),prop(131090,px(0))])
 # The upper block has no long lists requiring a whole-panel scroll view.
 scroll=1703;assert rr[scroll]['data']['m_FullTypeName']=='SI.UI.SIScrollView';sdid=rr[scroll]['data']['m_SerializedData']['rid'];previous=copy.deepcopy(rr[sdid]);template=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');base=copy.deepcopy(rr[template['data']['m_SerializedData']['rid']]);base['rid']=sdid
 for k in base['data']:
  if k in previous['data']:base['data'][k]=copy.deepcopy(previous['data'][k])
 base['data']['uxmlAssetId']=rr[scroll]['data']['m_Id'];rr[sdid].clear();rr[sdid].update(base);rr[scroll]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
 override(rr[scroll]['data'],[prop(131087,px(390)),prop(131096,px(390)),prop(131094,px(390)),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0)),prop(262151,px(0))])
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 d=check[pid].read_typetree();cr=refs(d);cs=check[sid].read_typetree();assert cr[1703]['data']['m_FullTypeName']=='UnityEngine.UIElements.VisualElement'
 for i in [6298,6228,1026,1043]:
  p0=next(p for p in cs['m_Rules'][cr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131087);assert cs['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==200
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out);audits.append({'target':str(folder),'reclaimed_decoration_margins_px':26,'upper_height':390,'radar_height':200,'outer_scroll_replaced_by_layout_container':True,'stats_and_bindings_unchanged':True})
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
