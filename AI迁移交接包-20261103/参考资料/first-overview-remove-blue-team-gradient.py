exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','first-overview-remove-blue-team-gradient-'))
import uuid,importlib.util
KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27FirstOverviewIconsNoBlueLight').hex;PID=-940000000020000;SRC=-910000000000201;PAGE=-930000000001001
assert str(PID) not in (R/'reserved-texture-ids.json').read_text('utf8')
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};audits=[]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in e.objects};original={i:sha(o.get_raw_data()) for i,o in obs.items()};assert PID not in obs
 clone=obs[SRC].read_typetree();clone['m_Name']='FirstOverviewIconsWithoutBlueLight';rr=refs(clone)
 blue=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName') and rr.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='ReportBlueLightBelowPlayerTopBackground');parent=rr[blue]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':blue})
 o=copy.copy(obs[SRC]);o.path_id=PID;o.assets_file.objects[PID]=o;obs[PID]=o;o.save_typetree(clone)
 doc=obs[PAGE].read_typetree();rr=refs(doc)
 using=next(u for u in doc['m_Usings'] if u['alias']=='MovedHeader_ReportIconsBelowPlayerTopBackground');oldkey=using['path'];using.update(path=KEY,asset={'m_FileID':0,'m_PathID':PID})
 grad=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient' and rr[r['data']['m_SerializedData']['rid']]['data'].get('name')=='PlayerReportHeaderGradient')
 sdid=rr[grad]['data']['m_SerializedData']['rid'];oldsd=rr[sdid];template=next(r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');base=copy.deepcopy(rr[template['data']['m_SerializedData']['rid']]);base['rid']=sdid
 for k in base['data']:
  if k in oldsd['data']:base['data'][k]=copy.deepcopy(oldsd['data'][k])
 base['data']['uxmlAssetId']=rr[grad]['data']['m_Id'];oldsd.clear();oldsd.update(base);rr[grad]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
 sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();override(rr[grad]['data'],[prop(458752,val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),prop(458753,en('none'))]);validate_ui(doc,sheet);obs[PAGE].save_typetree(doc);obs[sid].save_typetree(sheet)
 ab=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();source=next(v for k,v in meta['m_Container'] if k==oldkey and v['asset']['m_PathID']==SRC);span=copy.deepcopy(meta['m_PreloadTable'][source['preloadIndex']:source['preloadIndex']+source['preloadSize']])
 for p0 in span:
  if p0['m_FileID']==0 and p0['m_PathID']==SRC:p0['m_PathID']=PID
 meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);ab.save_typetree(meta)
 out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};changedids={PAGE,sid,PID,ab.path_id}
 for i,h in original.items():
  if i not in changedids:assert sha(check[i].get_raw_data())==h,(folder,i)
 cdoc=check[PID].read_typetree();cr=refs(cdoc);assert {'rid':blue} not in cr[parent]['data']['m_Children'];assert refs(check[PAGE].read_typetree())[grad]['data']['m_FullTypeName']=='UnityEngine.UIElements.VisualElement'
 outputs[folder/W]=out;(OUT/('game-world.bundle' if folder==GAME else 'skin-world.bundle')).write_bytes(out)
 catfolder=GAME.parent if folder==GAME else SKIN
 for name in ['catalog.bin','catalog.hash']:
  path=catfolder/name;before[path]=path.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/name).write_bytes(before[path])
 c=cm.Catalog(before[catfolder/'catalog.bin']);loc=next(x for x in c.locations(oldkey) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');c=cm.Catalog(c.add_key_location(KEY,loc,loc));newloc=c.locations(KEY)[0];assert c.location(c.location(newloc)['dependencies'][0])['internal'].endswith(W)
 outputs[catfolder/'catalog.bin']=bytes(c.data);outputs[catfolder/'catalog.hash']=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii');audits.append({'target':str(folder),'only_first_page':True,'clone':str(PID),'guid':KEY,'team_gradient_replaced_with_transparent_layout_container':True,'blue_light_removed_from_instantiated_children':True})
for p0,b in before.items():assert p0.read_bytes()==b
for p0,b in outputs.items():
 f=OUT/('prepared-game' if p0.parent in [GAME,GAME.parent] else 'prepared-skin');f.mkdir(exist_ok=True);(f/p0.name).write_bytes(b)
report={'installed':False,'runtime_verified':False,'changes':audits};(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for p0 in outputs:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p0.parent in [GAME,GAME.parent] else 'backup-skin')/p0.name)+"' -Destination '"+str(p0)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
if subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():print(json.dumps({'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p0,b in outputs.items():p0.write_bytes(b);assert p0.read_bytes()==b
except BaseException:
 for p0 in outputs:p0.write_bytes(before[p0])
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT)}))
