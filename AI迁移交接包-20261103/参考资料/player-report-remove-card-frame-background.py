exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','player-report-remove-card-frame-background-'))
import uuid,importlib.util
SRC=-5643027006255053682;NEW=-940000000023000;STYLE=NEW-1;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27PlayerReportShellWithoutCardFrameBackground').hex;SOURCEKEY='c560d7c346514c04f9c84c4b55b94bb4';HOST=7857044477279960178
for i in [NEW,STYLE]:assert str(i) not in (R/'reserved-texture-ids.json').read_text('utf8')
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);outputs={};audits=[]
for folder in [GAME,SKIN]:
 es={bn:UnityPy.load(before[folder/bn]) for bn in [W,G]};os={bn:{o.path_id:o for o in es[bn].objects} for bn in [W,G]};original={bn:{i:sha(o.get_raw_data()) for i,o in os[bn].items()} for bn in [W,G]};go=os[G];assert NEW not in go and STYLE not in go
 doc=go[SRC].read_typetree();srcstyle=doc['inlineSheet']['m_PathID'];sheet=go[srcstyle].read_typetree();doc['m_Name']='PlayerReportShellWithoutCardFrameBackground';doc['inlineSheet']['m_PathID']=STYLE;sheet['m_Name']='PlayerReportShellWithoutCardFrameBackgroundStyle';rr=refs(doc);target=1012;sdid=rr[target]['data']['m_SerializedData']['rid'];oldsd=copy.deepcopy(rr[sdid]);assert oldsd['data']['name']=='Card-frame' and oldsd['data']['Binding']['m_direct']['Path']['m_path']=='game.BackgroundImage.BackgroundImage'
 donor=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');new=copy.deepcopy(rr[donor['data']['m_SerializedData']['rid']]);new['rid']=sdid
 for k in new['data']:
  if k in oldsd['data']:new['data'][k]=copy.deepcopy(oldsd['data'][k])
 new['data']['uxmlAssetId']=rr[target]['data']['m_Id'];rr[sdid].clear();rr[sdid].update(new);rr[target]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement';override(rr[target]['data'],[prop(458753,en('none')),prop(458752,val(4,{'r':0.,'g':0.,'b':0.,'a':0.}))]);validate_ui(doc,sheet)
 for src,pid,d in [(SRC,NEW,doc),(srcstyle,STYLE,sheet)]:
  o=copy.copy(go[src]);o.path_id=pid;o.assets_file.objects[pid]=o;go[pid]=o;o.save_typetree(d)
 ab=next(o for o in go.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();ent=next(v for k,v in meta['m_Container'] if k==SOURCEKEY and v['asset']['m_PathID']==SRC);span=copy.deepcopy(meta['m_PreloadTable'][ent['preloadIndex']:ent['preloadIndex']+ent['preloadSize']])
 for p in span:
  if p['m_FileID']==0 and p['m_PathID'] in [SRC,srcstyle]:p['m_PathID']={SRC:NEW,srcstyle:STYLE}[p['m_PathID']]
 meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':NEW}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);ab.save_typetree(meta)
 host=os[W][HOST].read_typetree();u=next(u for u in host['m_Usings'] if u['alias']=='FigmaBaseToolTabGroupTemplate');assert u['path']==SOURCEKEY;u.update(path=KEY,asset={'m_FileID':0,'m_PathID':0});os[W][HOST].save_typetree(host)
 for bn,changedids in [(W,{HOST}),(G,{NEW,STYLE,ab.path_id})]:
  out=es[bn].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
  for i,h in original[bn].items():
   if i not in changedids:assert sha(check[i].get_raw_data())==h
  if bn==G:
   cr=refs(check[NEW].read_typetree());assert cr[target]['data']['m_FullTypeName']=='UnityEngine.UIElements.VisualElement' and 'Binding' not in cr[sdid]['data']
  outputs[folder/bn]=out;dest=OUT/('prepared-game' if folder==GAME else 'prepared-skin');dest.mkdir(exist_ok=True);(dest/bn).write_bytes(out)
 catfolder=GAME.parent if folder==GAME else SKIN
 for name in ['catalog.bin','catalog.hash']:
  p=catfolder/name;before[p]=p.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/name).write_bytes(before[p])
 c=cm.Catalog(before[catfolder/'catalog.bin']);loc=next(x for x in c.locations(SOURCEKEY) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');c=cm.Catalog(c.add_key_location(KEY,loc,loc));nl=c.locations(KEY)[0];assert c.location(c.location(nl)['dependencies'][0])['internal'].endswith(G);outputs[catfolder/'catalog.bin']=bytes(c.data);outputs[catfolder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii');audits.append({'target':str(folder),'all_four_overviews':True,'removed_drawing_layer':'Card-frame','old_type':'SI.Bindable.SIImage','new_type':'UnityEngine.UIElements.VisualElement','old_image_binding':'game.BackgroundImage.BackgroundImage','shared_original_other_pages_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
report={'installed':False,'runtime_verified':False,'changes':audits,'new_shell':str(NEW),'inlineStyle':str(STYLE),'guid':KEY};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT)}))
