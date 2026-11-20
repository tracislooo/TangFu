exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','dedupe-four-overviews-white-values-'))
import uuid,importlib.util,re
L='ui-tileslayouts_assets_all.bundle';pages=[-950000000000187,-950000000000185,-950000000000162,-950000000000156];oldpages=[-930000000001001,-930000000001003,-940000000010000,-940000000012000];descmap={-930000000001004:-950000000000232,-930000000001005:-950000000000231,-940000000010030:-950000000000230,-940000000012030:-950000000000229};NEW=-940000000024000;STYLE=NEW-1;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27OverviewWhiteAttributeBadge').hex;SOURCEKEY='e61c9f83ee67aae4aadfec4ae509ae84';SRC=-2713051656084895352
for i in [NEW,STYLE]:assert str(i) not in (R/'reserved-texture-ids.json').read_text('utf8')
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);outputs={};audits=[]
for folder in [GAME,SKIN]:
 path=folder/L;before[path]=path.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/L).write_bytes(before[path])
 es={bn:UnityPy.load(before[folder/bn]) for bn in [W,G,L]};os={bn:{o.path_id:o for o in es[bn].objects} for bn in es};hh={bn:{i:sha(o.get_raw_data()) for i,o in os[bn].items()} for bn in es};changed={bn:set() for bn in es};go=os[G]
 assert NEW not in go
 doc=go[SRC].read_typetree();ss=doc['inlineSheet']['m_PathID'];sheet=go[ss].read_typetree();doc['m_Name']='OverviewWhiteAttributeBadge';doc['inlineSheet']['m_PathID']=STYLE;sheet['m_Name']='OverviewWhiteAttributeBadgeStyle';rr=refs(doc);override(rr[1008]['data'],[prop(65536,val(4,{'r':1.,'g':1.,'b':1.,'a':1.}))]);validate_ui(doc,sheet)
 for src,pid,d in [(SRC,NEW,doc),(ss,STYLE,sheet)]:
  o=copy.copy(go[src]);o.path_id=pid;o.assets_file.objects[pid]=o;go[pid]=o;o.save_typetree(d);changed[G].add(pid)
 gab=next(o for o in go.values() if o.type.name=='AssetBundle');gm=gab.read_typetree();entry=next(v for k,v in gm['m_Container'] if k==SOURCEKEY and v['asset']['m_PathID']==SRC);span=copy.deepcopy(gm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for p in span:
  if p['m_FileID']==0 and p['m_PathID'] in [SRC,ss]:p['m_PathID']={SRC:NEW,ss:STYLE}[p['m_PathID']]
 gm['m_Container'].append((KEY,{'preloadIndex':len(gm['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':NEW}}));gm['m_PreloadTable'].extend(span);gm['m_Container'].sort(key=lambda x:x[0]);gab.save_typetree(gm);changed[G].add(gab.path_id)
 for pid in [-930000000001001,-940000000021000]:
  d=go[pid].read_typetree();u=next(u for u in d['m_Usings'] if u['alias']=='AttributeBadge');assert u['path']==SOURCEKEY;u.update(path=KEY,asset={'m_FileID':0,'m_PathID':0});go[pid].save_typetree(d);changed[G].add(pid)
 valuecount=0
 for pid,o in list(os[W].items()):
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name() or ''
  if pid not in pages+oldpages and name not in ['OverviewSeasonTwelveStats','OverviewSeasonTwelveStatsCompact']:continue
  d=o.read_typetree()
  if 'references' not in d:continue
  rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=os[W][sid].read_typetree();count=0
  for r in rr.values():
   n=r.get('data',{})
   if n.get('m_FullTypeName')!='SI.Bindable.SIText':continue
   s=rr[n['m_SerializedData']['rid']]['data'];nm=s.get('name','')
   numeric=any(k in nm for k in ['StatValue_','Number','CurrentAbilityValue','PotentialAbilityValue','LeagueRatingValue']) or nm.endswith('Value') or nm in ['PlayerReputationText','PersonHeightText']
   if numeric and not any(k in nm for k in ['Title','Description']):override(n,[prop(65536,val(4,{'r':1.,'g':1.,'b':1.,'a':1.}))]);count+=1
  for u in d.get('m_Usings',[]):
   if u['alias']=='RightHiddenAttributeBadge' and u['path']==SOURCEKEY:u.update(path=KEY,asset={'m_FileID':0,'m_PathID':0})
  if count or pid in pages+oldpages:validate_ui(d,sheet);o.save_typetree(d);os[W][sid].save_typetree(sheet);changed[W].update([pid,sid]);valuecount+=count
 # Remove obsolete descriptors from the chooser; keep current descriptions and other tiles.
 lo=os[L];d=lo[1332213496068314481].read_typetree();beforecount=len(d['m_gridElementDescriptions']);d['m_gridElementDescriptions']=[p for p in d['m_gridElementDescriptions'] if not(p['m_FileID']==0 and p['m_PathID'] in descmap)];assert beforecount-len(d['m_gridElementDescriptions'])==4
 assert [p['m_PathID'] for p in d['m_gridElementDescriptions'] if p['m_PathID'] in descmap.values()]==list(descmap.values());lo[1332213496068314481].save_typetree(d);changed[L].add(1332213496068314481)
 # Refresh only description pointers in player overview compositions, preserving placement.
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_FileID']==0 and v['m_PathID'] in descmap:v['m_PathID']=descmap[v['m_PathID']]
   else:
    for x in v.values():remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 for pid,o in lo.items():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name() or ''
  if not name.startswith('PlayerReportOverviewComposition'):continue
  d=o.read_typetree();old=copy.deepcopy(d);remap(d)
  if d!=old:o.save_typetree(d);changed[L].add(pid)
 for bn in es:
  out=es[bn].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
  for i,h in hh[bn].items():
   if i not in changed[bn]:assert sha(check[i].get_raw_data())==h,(folder,bn,i)
  if bn==L:assert len([p for p in check[1332213496068314481].read_typetree()['m_gridElementDescriptions'] if p['m_PathID'] in set(descmap)|set(descmap.values())])==4
  outputs[folder/bn]=out;dest=OUT/('prepared-game' if folder==GAME else 'prepared-skin');dest.mkdir(exist_ok=True);(dest/bn).write_bytes(out)
 catfolder=GAME.parent if folder==GAME else SKIN
 for name in ['catalog.bin','catalog.hash']:
  p=catfolder/name;before[p]=p.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/name).write_bytes(before[p])
 c=cm.Catalog(before[catfolder/'catalog.bin']);loc=next(x for x in c.locations(SOURCEKEY) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');c=cm.Catalog(c.add_key_location(KEY,loc,loc));nl=c.locations(KEY)[0];assert c.location(c.location(nl)['dependencies'][0])['internal'].endswith(G);outputs[catfolder/'catalog.bin']=bytes(c.data);outputs[catfolder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii')
 audits.append({'target':str(folder),'chooser_count_before':8,'chooser_count_after':4,'kept_descriptions':[str(x) for x in descmap.values()],'white_numeric_text_nodes':valuecount,'white_attribute_badge':str(NEW),'changed_objects':{bn:[str(x) for x in ids] for bn,ids in changed.items()},'all_other_objects_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
report={'installed':False,'runtime_verified':False,'changes':audits,'row_heights_layout_and_data_bindings_preserved':True,'new_badge_guid':KEY};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'chooser_count':4,'white_nodes':audits[0]['white_numeric_text_nodes']}))
