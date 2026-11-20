"""Allow the player overview bottom row to grow; preserve upper overview objects."""
exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','player-bottom-absorb-remaining-height-'))
T='ui-tileslayouts_assets_all.bundle'
protected={p:h for p,h in protected.items() if p.name!=T}
for folder in [GAME,SKIN]:
 p=folder/T;before[p]=p.read_bytes();(OUT/('backup-game' if folder==GAME else 'backup-skin')/T).write_bytes(before[p])
outputs={};audits=[]
tilekeys=set('9cdfa760f3315e9184232a6fe6e8b285 7bf2fb8e6b295ffaac669e8fc3fcc216 15da2c5118555dbc85b4067d1c6879e8 493a167139025db182490a8a3568e3db ccfa4ff2f2295f5db7533839e44a2b9e'.split())
for folder in [GAME,SKIN]:
 for bn in [W,G,T]:
  e=UnityPy.load(before[folder/bn]);obs={o.path_id:o for o in e.objects};oldraw={i:o.get_raw_data() for i,o in obs.items()};modified=set();details=[];expected_docs={}
  if bn==T:
   pid=3901662990989568885;doc=obs[pid].read_typetree();old=copy.deepcopy(doc)
   assert len(doc['m_gridComponents'])==7
   upper=copy.deepcopy(doc['m_gridComponents'][0]);assert upper['m_location']=={'x':0,'y':0,'width':20,'height':8}
   for c in doc['m_gridComponents'][1:]:
    assert c['m_location']['y']==8 and c['m_location']['height']==2
    assert c['m_minSize']['y']==2
    assert c['m_maxSize']['y']==2
    c['m_maxSize']['y']=100
   # No composition-version reset: retain the native chooser and its saved selections.
   assert doc['m_gridComponents'][0]==upper
   allowed=copy.deepcopy(old)
   for c in allowed['m_gridComponents'][1:]:c['m_maxSize']['y']=100
   assert doc==allowed
   obs[pid].save_typetree(doc);expected_docs[pid]=copy.deepcopy(doc);modified.add(pid);details.append({'composition':pid,'bottom_min_rows':2,'bottom_max_rows':100,'upper_unchanged':True})
  else:
   meta=next(o for o in e.objects if o.type.name=='AssetBundle').read_typetree()
   candidates=set(v['asset']['m_PathID'] for k,v in meta['m_Container'] if k in tilekeys)
   for pid in sorted(candidates):
    doc=obs[pid].read_typetree()
    if 'references' not in doc:continue
    assert doc['m_Name'].startswith('Overview1080_Compact_'),doc['m_Name']
    rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();old=copy.deepcopy(doc)
    # Only the per-overview compact copies; leave native shared cards unchanged.
    root=rr[1001]['data'];assert 'm_FullTypeName' in root
    override(root,[prop(131094,none),prop(131087,pct(100)),prop(131096,px(0)),prop(131084,num(1)),prop(131085,num(1))])
    expected=copy.deepcopy(old);refs(expected)[1001]['data']['m_RuleIndex']=root['m_RuleIndex'];assert expected==doc
    obs[pid].save_typetree(doc);obs[sid].save_typetree(sheet);expected_docs[pid]=copy.deepcopy(doc);expected_docs[sid]=copy.deepcopy(sheet);modified.update([pid,sid]);details.append({'tile':pid,'style':sid,'name':doc['m_Name'],'old_max_height':154,'new_max_height':'none','height':'100%'})
  if not modified:continue
  raw=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(obs)
  for pid,b in oldraw.items():
   if pid not in modified:assert check[pid].get_raw_data()==b,(folder,bn,pid)
  for pid in modified:
   actual=check[pid].read_typetree();expected=expected_docs[pid]
   # JSON normalizes UnityPy's equivalent tuple/list representations.
   if json.dumps(actual,sort_keys=True)!=json.dumps(expected,sort_keys=True):
    def firstdiff(a,b,path=''):
     if isinstance(a,dict) and isinstance(b,dict):
      for k in a:
       if a[k]!=b[k]:return firstdiff(a[k],b[k],path+'/'+str(k))
     elif isinstance(a,(tuple,list)) and isinstance(b,(tuple,list)):
      if len(a)!=len(b):return path,len(a),len(b)
      for i,(x,y) in enumerate(zip(a,b)):
       if x!=y:return firstdiff(x,y,path+'/'+str(i))
     return path,a,b
    raise AssertionError((bn,pid,firstdiff(actual,expected)))
  outputs[folder/bn]=raw;dest=OUT/('stage-game' if folder==GAME else 'stage-skin');dest.mkdir(exist_ok=True);(dest/bn).write_bytes(raw)
  audits.append({'target':str(folder),'bundle':bn,'modified_objects':sorted(modified),'details':details,'all_other_objects_byte_identical':True})
assert len(outputs)==4,[(str(p)) for p in outputs]
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
caches=list(cache_root.glob('*PlayerReportOverviewComposition-Large*')) if cache_root.exists() else []
for p in caches:
 if not p.is_file():continue
 raw=p.read_bytes()
 try:d=json.loads(raw.decode('utf-8-sig'))
 except (ValueError,UnicodeError):continue
 cs=d.get('m_gridComponents',[])
 if len(cs)!=7 or sum(c.get('m_location',{}).get('y')==8 for c in cs)!=6:continue
 q=OUT/'backup-cache';q.mkdir(exist_ok=True);(q/p.name).write_bytes(raw);before[p]=raw
 for c in cs:
  if c['m_location']['y']==8:c['m_maxSize']['y']=100
 outputs[p]=json.dumps(d,ensure_ascii=False,separators=(',',':')).encode('utf8')
manifest={'installed':False,'runtime_verified':False,'audit':audits,'saved_cache_files':[str(p) for p in outputs if p.parent==cache_root],'upper_versions_unchanged':True,'widths_unchanged':[2,2,2,8,2,4]}
transactions=[]
for p,raw in outputs.items():
 backup=OUT/('backup-game' if p.parent==GAME else 'backup-skin' if p.parent==SKIN else 'backup-cache')/p.name
 transactions.append({'path':str(p),'backup':str(backup),'before_sha256':sha(before[p]),'installed_sha256':sha(raw)})
manifest['files']=transactions
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
lines=['$ErrorActionPreference="Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }",'$items=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot "manifest.json") | ConvertFrom-Json','foreach ($item in $items.files) { if ((Get-FileHash -LiteralPath $item.path -Algorithm SHA256).Hash.ToLower() -ne $item.installed_sha256) { throw "Current files changed; merge rollback instead of overwriting." } }','foreach ($item in $items.files) { Copy-Item -LiteralPath $item.backup -Destination $item.path -Force }']
(OUT/'restore.ps1').write_text('\n'.join(lines),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b,('concurrent edit',str(p))
for p,h in protected.items():assert sha(p.read_bytes())==h,('protected edit',str(p))
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip()
if running:print(json.dumps({'installed':False,'game_running':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p in outputs:p.write_bytes(before[p])
 raise
manifest.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(R/'current-player-bottom-height.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'script':str(Path(__file__).resolve()),'installed':True,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'files':len(outputs)},ensure_ascii=False))
