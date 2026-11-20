exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','all-overviews-remove-portrait-backgrounds-'))
import uuid
PRIVATE=-940000000020000;KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27FirstOverviewIconsNoBlueLight').hex
pages=[-930000000001003,-940000000010000,-940000000012000];outputs={};audits=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};assert PRIVATE in obs
 ab=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();ce=next(v for k,v in meta['m_Container'] if k==KEY and v['asset']['m_PathID']==PRIVATE);private_span=copy.deepcopy(meta['m_PreloadTable'][ce['preloadIndex']:ce['preloadIndex']+ce['preloadSize']]);modified={ab.path_id}
 for pid in pages:
  doc=obs[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
  using=next(u for u in doc['m_Usings'] if u['alias']=='MovedHeader_ReportIconsBelowPlayerTopBackground');using.update(path=KEY,asset={'m_FileID':0,'m_PathID':PRIVATE})
  grad=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient' and rr[r['data']['m_SerializedData']['rid']]['data'].get('name')=='PlayerReportHeaderGradient')
  sdid=rr[grad]['data']['m_SerializedData']['rid'];oldsd=rr[sdid];template=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');base=copy.deepcopy(rr[template['data']['m_SerializedData']['rid']]);base['rid']=sdid
  for k in base['data']:
   if k in oldsd['data']:base['data'][k]=copy.deepcopy(oldsd['data'][k])
  base['data']['uxmlAssetId']=rr[grad]['data']['m_Id'];oldsd.clear();oldsd.update(base);rr[grad]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
  override(rr[grad]['data'],[prop(458752,val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),prop(458753,en('none'))])
  bg=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName') and rr.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='PlayerTopBackgroundTextureLayer');override(rr[bg]['data'],[prop(131081,en('none')),prop(458753,en('none'))])
  validate_ui(doc,sheet);obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);modified.update([pid,sid])
  for k,entry in meta['m_Container']:
   if entry['asset']=={'m_FileID':0,'m_PathID':pid}:
    span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
    for ptr in private_span:
     if ptr not in span:span.append(ptr)
    entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span);meta['m_PreloadTable'].extend(span)
  audits.append({'target':str(folder),'page':str(pid),'style':str(sid),'blue_light':'reuse existing private component without blue layer','team_gradient':'transparent layout container','top_background':'display none'})
 obs[ab.path_id].save_typetree(meta);out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};assert set(check)==set(obs)
 for i,h in original.items():
  if i not in modified:assert sha(check[i].get_raw_data())==h,(folder,i)
 for pid in [-930000000001001]+pages:
  doc=check[pid].read_typetree();rr=refs(doc);assert next(u for u in doc['m_Usings'] if u['alias']=='MovedHeader_ReportIconsBelowPlayerTopBackground')['path']==KEY
  assert not any(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient' and rr.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='PlayerReportHeaderGradient' for r in rr.values())
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'all_four_versions_now_without_blue_topbackground_team_gradient':True,'first_version_unchanged':True,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
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
