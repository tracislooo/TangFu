exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','native-position-dots-with-values-all-'))
import uuid,importlib.util,struct
SRC=4269476442492208794;NEW=-940000000025000;STYLE=NEW-1;SOURCEKEY='d6b3b3e4fa729864cbe89c7957538b2c';KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27NativePositionDotsWithRawValues').hex;pids=[-940000000005000,-940000000008000,-940000000010020,-960000000003030]
for i in [NEW,STYLE]:assert str(i) not in (R/'reserved-texture-ids.json').read_text('utf8')
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);outputs={};audits=[]
for folder in [GAME,SKIN]:
 es={bn:UnityPy.load(before[folder/bn]) for bn in [W,G]};os={bn:{o.path_id:o for o in es[bn].objects} for bn in es};hh={bn:{i:sha(o.get_raw_data()) for i,o in os[bn].items()} for bn in es};changed={W:set(),G:set()};wo=os[W];assert NEW not in wo and STYLE not in wo
 doc=wo[SRC].read_typetree();srcstyle=doc['inlineSheet']['m_PathID'];sheet=wo[srcstyle].read_typetree();doc['m_Name']='NativePositionDotsWithRawValues';doc['inlineSheet']['m_PathID']=STYLE;sheet['m_Name']='NativePositionDotsWithRawValuesStyle';rr=refs(doc)
 proto=rr[1021];ps=rr[proto['data']['m_SerializedData']['rid']];node=copy.deepcopy(proto);serial=copy.deepcopy(ps);rid=max(rr)+1;eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;node['rid']=rid;serial['rid']=rid+1;node['data'].update(m_Id=eid,m_Parent={'rid':1010},m_Children=[],m_SerializedData={'rid':rid+1},m_Classes=['content-no-wrap'],m_RuleIndex=-1,m_Stylesheets=[],m_StylesheetPaths=[]);serial['data'].update(uxmlAssetId=eid,name='NativePositionProficiencyValue',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,text='--',text_UxmlAttributeFlags=1,DebugDisplay='',DebugDisplay_UxmlAttributeFlags=0,TextBinding={'m_kind':1,'m_direct':{'Path':{'m_path':'position.PropertyValue'},'Nullable':1},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},TextBinding_UxmlAttributeFlags=1)
 override(node['data'],[prop(131102,en('absolute')),prop(131089,pct(50)),prop(131091,px(-12)),prop(131104,pct(100)),prop(131093,px(1)),prop(131105,px(24)),prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(131084,num(0)),prop(131085,num(0)),prop(65537,px(10)),prop(65543,en('bold')),prop(65546,en('middle-center')),prop(65536,val(4,{'r':1.,'g':1.,'b':1.,'a':1.})),prop(262151,px(0)),prop(458768,en('visible'))]);rr[1010]['data']['m_Children'].append({'rid':rid});doc['references']['RefIds'].extend([node,serial]);override(rr[1010]['data'],[prop(458768,en('visible'))]);validate_ui(doc,sheet)
 for src,pid,d in [(SRC,NEW,doc),(srcstyle,STYLE,sheet)]:
  o=copy.copy(wo[src]);o.path_id=pid;o.assets_file.objects[pid]=o;wo[pid]=o;o.save_typetree(d);changed[W].add(pid)
 ab=next(o for o in wo.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();entry=next(v for k,v in meta['m_Container'] if k==SOURCEKEY and v['asset']['m_PathID']==SRC);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for ptr in span:
  if ptr['m_FileID']==0 and ptr['m_PathID'] in [SRC,srcstyle]:ptr['m_PathID']={SRC:NEW,srcstyle:STYLE}[ptr['m_PathID']]
 for ptr in [{'m_FileID':0,'m_PathID':NEW},{'m_FileID':0,'m_PathID':STYLE}]:
  if ptr not in span:span.append(ptr)
 meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':NEW}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);ab.save_typetree(meta);changed[W].add(ab.path_id)
 edits=[]
 for pid in pids:
  d=os[G][pid].read_typetree();rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=os[G][sid].read_typetree();removed=set()
  def remove(i):
   if i in removed:return
   removed.add(i)
   for c in rr[i]['data'].get('m_Children',[]):remove(c['rid'])
   sd0=rr[i]['data'].get('m_SerializedData',{}).get('rid',-2)
   if sd0!=-2:removed.add(sd0)
  targets=[]
  for i,r in rr.items():
   a=r.get('data',{});s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=s.get('name','')
   if (a.get('m_FullTypeName')=='SI.Bindable.WrappedObjectList' and name=='OverviewFourteenPositionZones') or ('m_FullTypeName' in a and name.startswith('BlackPitchLine_')):targets.append(i)
  for i in targets:
   parent=rr[i]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':i});remove(i)
  d['references']['RefIds']=[r for r in d['references']['RefIds'] if r['rid'] not in removed]
  image=rr[1022]['data'];ims=rr[image['m_SerializedData']['rid']]['data'];ims['tintColor']={'r':1.,'g':1.,'b':1.,'a':1.};ims['tintColor_UxmlAttributeFlags']=1;override(image,[prop(458752,val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),prop(458767,num(1))])
  panel=rr[1023]['data'];s=rr[panel['m_SerializedData']['rid']]['data'];s['PositionTemplateAsset']['m_AssetGUID']=KEY;s['PositionTemplateAsset_UxmlAttributeFlags']=1;s['pickingMode']=0;s['pickingMode_UxmlAttributeFlags']=1;override(panel,[prop(65551,en('visible')),prop(458767,num(1)),prop(131081,en('flex'))])
  if pid==pids[-1]:override(rr[2014]['data'],[prop(458752,val(4,{'r':0.,'g':0.,'b':0.,'a':0.}))])
  validate_ui(d,sheet);os[G][pid].save_typetree(d);os[G][sid].save_typetree(sheet);changed[G].update([pid,sid]);edits.append({'module':str(pid),'native_dots_visible':True,'rectangle_and_black_line_nodes_removed':len(targets),'native_pitch_tint_restored':True,'orientation':s['Orientation'],'proficiency':'position.PropertyValue','native_hover_and_selection_preserved':True})
 for bn in es:
  out=es[bn].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
  for i,h in hh[bn].items():
   if i not in changed[bn]:assert sha(check[i].get_raw_data())==h,(folder,bn,i)
  if bn==G:
   for pid in pids:
    cr=refs(check[pid].read_typetree());s=cr[cr[1023]['data']['m_SerializedData']['rid']]['data'];assert s['PositionTemplateAsset']['m_AssetGUID']==KEY
    assert not any('BlackPitchLine_' in r.get('data',{}).get('name','') or r.get('data',{}).get('name')=='OverviewFourteenPositionZones' for r in cr.values())
  outputs[folder/bn]=out;f=OUT/('prepared-game' if folder==GAME else 'prepared-skin');f.mkdir(exist_ok=True);(f/bn).write_bytes(out)
 catfolder=GAME.parent if folder==GAME else SKIN
 for name in ['catalog.bin','catalog.hash']:
  p=catfolder/name;before[p]=p.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/name).write_bytes(before[p])
 c=cm.Catalog(before[catfolder/'catalog.bin']);loc=next(x for x in c.locations(SOURCEKEY) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');c=cm.Catalog(c.add_key_location(KEY,loc,loc));nl=c.locations(KEY)[0];assert c.location(c.location(nl)['dependencies'][0])['internal'].endswith(W)
 for idx,(ko,ptr) in enumerate(list(c.key_records)):
  k=c.object(ko)
  if not isinstance(k,str) or 'Preload' not in k:continue
  locs=[x[0] for x in c.array(ptr,'I')]
  if loc not in locs or nl in locs:continue
  nset=c.append(b''.join(struct.pack('<I',x) for x in locs+[nl]),True);records=list(c.key_records);records[idx]=(ko,nset);table=c.append(b''.join(struct.pack('<2I',*r) for r in records),True);struct.pack_into('<I',c.data,8,table);c=cm.Catalog(bytes(c.data))
 outputs[catfolder/'catalog.bin']=bytes(c.data);outputs[catfolder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii');audits.append({'target':str(folder),'changes':edits})
for p,b in before.items():assert p.read_bytes()==b
report={'installed':False,'runtime_verified':False,'native_dot_template':str(NEW),'inlineStyle':str(STYLE),'guid':KEY,'changes':audits,'no_texture_changes':True};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'main_versions':4,'popup_pitch':True}))
