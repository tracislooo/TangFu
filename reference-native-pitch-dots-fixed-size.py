exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','reference-native-pitch-dots-fixed-size-'))
OLD=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');refbytes={bn:(OLD/bn).read_bytes() for bn in [W,G]};refobjs={bn:{o.path_id:o for o in UnityPy.load(refbytes[bn]).objects} for bn in [W,G]};native=refobjs[W][4269476442492208794].read_typetree();nativesheet=refobjs[W][native['inlineSheet']['m_PathID']].read_typetree();nr=refs(native);circle_rule=nativesheet['m_Rules'][nr[1010]['data']['m_RuleIndex']];sizeprop=next(p for p in circle_rule['m_Properties'] if p['m_Id']==131095);diameter=nativesheet['dimensions'][sizeprop['m_Values'][0]['valueIndex']]['value'];assert diameter==12.
outputs={};audits=[];PID=-940000000025000;SID=-940000000025001
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};current=obs[PID].read_typetree();currsheet=obs[SID].read_typetree();doc=copy.deepcopy(native);sheet=copy.deepcopy(nativesheet);doc.update(m_Name=current['m_Name'],m_Script=current['m_Script'],inlineSheet=current['inlineSheet']);sheet.update(m_Name=currsheet['m_Name'],m_Script=currsheet['m_Script']);rr=refs(doc)
 # Lock the reference size; the raw numeric caption is out of the circle's layout flow.
 for i in [1006,1008,1010]:override(rr[i]['data'],[prop(131105,px(diameter)),prop(131097,px(diameter)),prop(131095,px(diameter)),prop(131087,px(diameter)),prop(131096,px(diameter)),prop(131094,px(diameter)),prop(131084,num(0)),prop(131085,num(0)),prop(458768,en('visible'))])
 for i in [1001,1002,1004]:override(rr[i]['data'],[prop(458768,en('visible'))])
 proto=rr[1021];ps=rr[proto['data']['m_SerializedData']['rid']];node=copy.deepcopy(proto);serial=copy.deepcopy(ps);rid=max(rr)+1;eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;node['rid']=rid;serial['rid']=rid+1;node['data'].update(m_Id=eid,m_Parent={'rid':1010},m_Children=[],m_SerializedData={'rid':rid+1},m_Classes=['content-no-wrap'],m_RuleIndex=-1,m_Stylesheets=[],m_StylesheetPaths=[]);serial['data'].update(uxmlAssetId=eid,name='NativePositionProficiencyValue',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,text='--',text_UxmlAttributeFlags=1,DebugDisplay='',DebugDisplay_UxmlAttributeFlags=0,TextBinding={'m_kind':1,'m_direct':{'Path':{'m_path':'position.PropertyValue'},'Nullable':1},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},TextBinding_UxmlAttributeFlags=1)
 override(node['data'],[prop(131102,en('absolute')),prop(131089,pct(50)),prop(131091,px(-12)),prop(131104,pct(100)),prop(131093,px(2)),prop(131105,px(24)),prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(131084,num(0)),prop(131085,num(0)),prop(65537,px(10)),prop(65543,en('bold')),prop(65546,en('middle-center')),prop(65536,val(4,{'r':1.,'g':1.,'b':1.,'a':1.})),prop(262151,px(0)),prop(458768,en('visible'))]);rr[1010]['data']['m_Children'].append({'rid':rid});doc['references']['RefIds'].extend([node,serial]);validate_ui(doc,sheet)
 # Native title/description and native proficiency colour functions remain exactly as supplied.
 cr=refs(current)
 for i in [1002,1004,1008,1018,1020,1021]:
  oldsd=nr[nr[i]['data']['m_SerializedData']['rid']];newsd=rr[rr[i]['data']['m_SerializedData']['rid']];assert oldsd==newsd
 obs[PID].save_typetree(doc);obs[SID].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [PID,SID]:assert sha(check[i].get_raw_data())==h
 d=check[PID].read_typetree();r=refs(d);s=check[SID].read_typetree()
 for i in [1006,1008,1010]:
  for key in [131105,131087,131097,131096]:
   p=next(p for p in s['m_Rules'][r[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==key);assert s['dimensions'][p['m_Values'][0]['valueIndex']]['value']==diameter
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out);audits.append({'target':str(folder),'reference_dot_diameter':diameter,'native_circle_selected_ring_and_tooltip_from_user_reference':True,'caption_binding':'position.PropertyValue','caption_outside_circle_layout':True,'all_unrelated_objects_unchanged':True})
for bn,b in refbytes.items():assert (OLD/bn).read_bytes()==b
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'read_only_reference_directory':str(OLD),'reference_hashes':{bn:sha(b) for bn,b in refbytes.items()},'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'circle_diameter':diameter}))
