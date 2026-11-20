exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','restore-four-pitch-native-tooltips-'))
outputs={};audits=[];pid=-940000000018000
for folder in [GAME,SKIN]:
 we=UnityPy.load(before[folder/W]);wo={o.path_id:o for o in we.objects};native=wo[4269476442492208794].read_typetree();nr=refs(native);ns=wo[native['inlineSheet']['m_PathID']].read_typetree()
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[pid].read_typetree();rr=refs(doc);oldrefs=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();nextrid=max(rr)+1;nextid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 assert not any('NativePositionTooltip' in r.get('data',{}).get('name','') for r in rr.values())
 sourceids=[1002,1013,1016,1018,1020,1021];children={1002:[1013],1013:[1016],1016:[1018],1018:[1020,1021],1020:[],1021:[]};copies=[]
 for cell,r in list(rr.items()):
  v=r.get('data',{})
  if v.get('m_FullTypeName')!='SI.Bindable.SIButton':continue
  cellname=rr[v['m_SerializedData']['rid']]['data'].get('name','')
  if not cellname.startswith('PositionZone_'):continue
  mp={};eid={}
  for src in sourceids:
   srcsd=nr[src]['data']['m_SerializedData']['rid'];mp[src]=nextrid;mp[srcsd]=nextrid+1;nextrid+=2;eid[nr[src]['data']['m_Id']]=nextid;nextid+=1
  for src in sourceids:
   node=copy.deepcopy(nr[src]);srcsd=nr[src]['data']['m_SerializedData']['rid'];serial=copy.deepcopy(nr[srcsd]);node['rid']=mp[src];serial['rid']=mp[srcsd];nd=node['data'];nd['m_Id']=eid[nd['m_Id']];nd['m_SerializedData']={'rid':mp[srcsd]};nd['m_Parent']={'rid':cell if src==1002 else mp[next(k for k,cc in children.items() if src in cc)]};nd['m_Children']=[{'rid':mp[c]} for c in children[src]];serial['data']['uxmlAssetId']=nd['m_Id'];serial['data']['name']='NativePositionTooltip_'+cellname+'_'+str(src);serial['data']['name_UxmlAttributeFlags']=1
   ix=nd.get('m_RuleIndex',-1)
   if ix>=0:
    props=copy.deepcopy(ns['m_Rules'][ix]['m_Properties'])
    for p0 in props:
     for q in p0['m_Values']:
      typ=q['m_ValueType']
      if typ in poolmap:
       assert typ!=6,'unexpected cross-bundle asset in tooltip inline style';pool=poolmap[typ];sheet[pool].append(copy.deepcopy(ns[pool][q['valueIndex']]));q['valueIndex']=len(sheet[pool])-1
    nd['m_RuleIndex']=rule(props)
   doc['references']['RefIds'].extend([node,serial]);rr[node['rid']]=node;rr[serial['rid']]=serial
  v['m_Children'].append({'rid':mp[1002]})
  for src in [1002,1013,1016]:
   nd=rr[mp[src]]['data'];override(nd,[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,pct(100)),prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(262150,px(0)),prop(262151,px(0))])
  copies.append({'cell':cellname,'local_mapping':mp[1002],'tooltip':mp[1018]})
 assert len(copies)==14
 for i,r in oldrefs.items():
  if i not in [j for j in oldrefs if oldrefs[j].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIButton']:assert rr[i]==r
  elif rr[i]!=r:
   x=copy.deepcopy(rr[i]);x['data']['m_Children']=r['data']['m_Children'];assert x==r
 validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in [pid,sid]:assert sha(check[i].get_raw_data())==h
 cr=refs(check[pid].read_typetree());assert sum(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.Tooltip' for r in cr.values())==14
 for row in copies:
  s=cr[cr[row['local_mapping']]['data']['m_SerializedData']['rid']]['data'];assert s['Mappings']==nr[nr[1002]['data']['m_SerializedData']['rid']]['data']['Mappings']
 outputs[folder/G]=out;(OUT/('game-global.bundle' if folder==GAME else 'skin-global.bundle')).write_bytes(out);audits.append({'target':str(folder),'versions':[1,2,3,4],'native_source':'PlayerPositionAbilityWithCenterSidePrefTooltip','native_description':'player.PositionAbilityTooltip','local_position_mask':'position.Position','cells':copies,'existing_click_and_display_bindings_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'position_tooltips':14}))
