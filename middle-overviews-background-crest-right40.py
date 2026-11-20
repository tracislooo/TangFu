exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','middle-overviews-background-crest-right40-'))
import uuid,importlib.util
SRC=-940000000020000;NEW=-940000000022000;STYLE=NEW-1;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27MiddleOverviewBackgroundClubRight40').hex
for i in [NEW,STYLE]:assert str(i) not in (R/'reserved-texture-ids.json').read_text('utf8')
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);outputs={};audits=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};assert NEW not in obs and STYLE not in obs
 doc=obs[SRC].read_typetree();oldstyle=doc['inlineSheet']['m_PathID'];sheet=obs[oldstyle].read_typetree();doc['inlineSheet']['m_PathID']=STYLE;doc['m_Name']='MiddleOverviewBackgroundClubRight40';sheet['m_Name']='MiddleOverviewBackgroundClubRight40Style';rr=refs(doc)
 assert rr[1154]['data']['m_Parent']['rid']==1148
 override(rr[1154]['data'],[prop(131102,en('relative')),prop(131089,px(40))])
 reachable=set()
 def walk(i):
  reachable.add(i)
  for ch in rr[i]['data'].get('m_Children',[]):walk(ch['rid'])
 walk(doc['m_VisualTree']['rid']);orphan={i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and i not in reachable};orphan.update(rr[i]['data']['m_SerializedData']['rid'] for i in list(orphan) if rr[i]['data'].get('m_SerializedData',{}).get('rid',-2)!=-2);doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in orphan]
 validate_ui(doc,sheet)
 for source,pid,d in [(SRC,NEW,doc),(oldstyle,STYLE,sheet)]:
  o=copy.copy(obs[source]);o.path_id=pid;o.assets_file.objects[pid]=o;obs[pid]=o;o.save_typetree(d)
 oldkey=None
 for pid in [-930000000001001,-930000000001003]:
  page=obs[pid].read_typetree();u=next(u for u in page['m_Usings'] if u['alias']=='MovedHeader_ReportIconsBelowPlayerTopBackground');assert u['asset']['m_PathID']==SRC;oldkey=u['path'];u.update(path=KEY,asset={'m_FileID':0,'m_PathID':NEW});obs[pid].save_typetree(page)
 ab=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();entry=next(v for k,v in meta['m_Container'] if k==oldkey and v['asset']['m_PathID']==SRC);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for ptr in span:
  if ptr['m_FileID']==0 and ptr['m_PathID'] in [SRC,oldstyle]:ptr['m_PathID']={SRC:NEW,oldstyle:STYLE}[ptr['m_PathID']]
 for ptr in [{'m_FileID':0,'m_PathID':NEW},{'m_FileID':0,'m_PathID':STYLE}]:
  if ptr not in span:span.append(ptr)
 meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':NEW}}));meta['m_PreloadTable'].extend(span)
 for k,en0 in meta['m_Container']:
  if en0['asset']['m_FileID']==0 and en0['asset']['m_PathID'] in [-930000000001001,-930000000001003]:
   ps=copy.deepcopy(meta['m_PreloadTable'][en0['preloadIndex']:en0['preloadIndex']+en0['preloadSize']])
   for ptr in span:
    if ptr not in ps:ps.append(ptr)
   en0['preloadIndex']=len(meta['m_PreloadTable']);en0['preloadSize']=len(ps);meta['m_PreloadTable'].extend(ps)
 meta['m_Container'].sort(key=lambda x:x[0]);ab.save_typetree(meta);changedids={NEW,STYLE,ab.path_id,-930000000001001,-930000000001003};out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects}
 for i,h in original.items():
  if i not in changedids:assert sha(check[i].get_raw_data())==h
 cr=refs(check[NEW].read_typetree());cs=check[STYLE].read_typetree();p0=next(p for p in cs['m_Rules'][cr[1154]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131089);assert cs['dimensions'][p0['m_Values'][0]['valueIndex']]['value']==40
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out)
 catfolder=GAME.parent if folder==GAME else SKIN
 for name in ['catalog.bin','catalog.hash']:
  p=catfolder/name;before[p]=p.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/name).write_bytes(before[p])
 c=cm.Catalog(before[catfolder/'catalog.bin']);loc=next(x for x in c.locations(oldkey) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');c=cm.Catalog(c.add_key_location(KEY,loc,loc));nl=c.locations(KEY)[0];assert c.location(c.location(nl)['dependencies'][0])['internal'].endswith(W)
 outputs[catfolder/'catalog.bin']=bytes(c.data);outputs[catfolder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii');audits.append({'target':str(folder),'versions':[1,2],'club_container_rid':1154,'right_offset':40,'third_fourth_original_module_unchanged':True,'flag_portrait_and_data_bindings_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
report={'installed':False,'runtime_verified':False,'changes':audits,'private_component':str(NEW),'inlineStyle':str(STYLE),'guid':KEY};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'right_offset':40}))

