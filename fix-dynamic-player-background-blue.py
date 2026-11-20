import copy,datetime,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.helpers import TypeTreeHelper
original_write=TypeTreeHelper.write_value
def write_value(value,node,writer,config):
 if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(value,config.assetsfile) is None:
  for child in node.m_Children:
   if child.m_Type!='ReferencedObjectData':original_write(value[child.m_Name],child,writer,config)
  if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
  return
 return original_write(value,node,writer,config)
TypeTreeHelper.write_value=write_value
sha=lambda b:hashlib.sha256(b).hexdigest()
O=R/(sys.argv[sys.argv.index('--output-dir')+1] if '--output-dir' in sys.argv else 'player-dynamic-background-blue-20261101');M=O/'manifest.json'
if '--install' in sys.argv:
 m=json.loads(M.read_text('utf8'))
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 if p.stdout.strip():print('GAME_RUNNING_PENDING_INSTALL');sys.exit(0)
 old={}
 for x in m['install_files']:
  target=Path(x['target']);assert 'Project Taco' not in str(target);old[target]=target.read_bytes();assert sha(old[target])==x['before_sha256'];assert sha((O/x['source']).read_bytes())==x['after_sha256']
 for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
 try:
  for x in m['install_files']:
   target=Path(x['target']);tmp=target.with_name(target.name+'.blue.tmp');tmp.write_bytes((O/x['source']).read_bytes());os.replace(tmp,target);assert sha(target.read_bytes())==x['after_sha256']
 except BaseException:
  for p,b in old.items():p.write_bytes(b)
  raise
 m.update(installed=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());M.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 p=R/'AGENTS.md';s=p.read_text('utf8')+f'\n- 2026-11-01：GameWorldBackground 的原3D动态背景分支（SIRenderTextureImage）改为读取 backgrounds 的 TF skin V1（-910000000000149）；静态背景分支保留。迁移时恢复此UI分支，避免球员页等继续显示原黑灰动态背景。记录：{O.name}/manifest.json。\n';p.write_text(s,'utf8');print('INSTALLED');sys.exit(0)
assert not O.exists();loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);S=Path(loc['skin_packages']);AA=Path(loc['aa_root'])
WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';BN='ui-backgrounds_assets_common.bundle';D=-716828569427839901;BLUE=-910000000000149
before={p/WN:(p/WN).read_bytes() for p in [G,S]};assert before[G/WN]==before[S/WN]
protected={p:sha(p.read_bytes()) for folder in [G,S] for p in folder.glob('*.bundle') if p.name!=WN};protected.update({p:sha(p.read_bytes()) for folder in [AA,S] for p in [folder/'catalog.bin',folder/'catalog.hash'] if p.exists()})
we=UnityPy.load(before[G/WN]);af=we.assets[0];obs=af.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[D].read_typetree();assert doc['m_Name']=='GameWorldBackground';original=copy.deepcopy(doc);sid=doc['inlineSheet']['m_PathID'];style=obs[sid].read_typetree();oldstyle=copy.deepcopy(style)
be=UnityPy.load(str(G/BN));ba=be.assets[0];blue=ba.objects[BLUE];assert blue.peek_name()=='TF skin V1'
fid=next(i+1 for i,x in enumerate(af.externals) if x.path==f'archive:/{ba.name}/{ba.name}');ptr={'m_FileID':fid,'m_PathID':BLUE}
refs={r['rid']:r for r in doc['references']['RefIds']};node=refs[1005];data=refs[1008];assert node['data']['m_FullTypeName']=='SI.Bindable.SIRenderTextureImage';assert data['type']['class']=='SIRenderTextureImage/UxmlSerializedData'
template=json.loads((R/'investigate-black-player-background-20261101/visual-element-template.json').read_text('utf8'))
newdata=copy.deepcopy(template['data'])
for k in list(newdata):
 if k in data['data']:newdata[k]=copy.deepcopy(data['data'][k])
newdata.update(name='TFBlueDynamicBackground',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
data['type']=copy.deepcopy(template['type']);data['data']=newdata;node['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
ruleid=node['data']['m_RuleIndex'];rule=style['m_Rules'][ruleid];assetindex=len(style['assets']);style['assets'].append(ptr)
stringindex=len(style['strings']);style['strings'].append('scale-and-crop')
rule['m_Properties'] += [{'m_Id':458753,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':6,'valueIndex':assetindex}]},{'m_Id':262153,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':7,'valueIndex':stringindex}]}]
assert refs[1006]==next(r for r in original['references']['RefIds'] if r['rid']==1006)
assert refs[1007]==next(r for r in original['references']['RefIds'] if r['rid']==1007)
assert len(doc['references']['RefIds'])==len(original['references']['RefIds'])
for r in original['references']['RefIds']:
 if r['rid'] not in [1005,1008]:assert refs[r['rid']]==r
obs[D].save_typetree(doc);obs[sid].save_typetree(style)
bundle=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta);guidkeys=[];pre=copy.deepcopy(meta['m_PreloadTable'])
for key,entry in meta['m_Container']:
 span=copy.deepcopy(pre[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 if entry['asset']['m_FileID']==0 and entry['asset']['m_PathID']==D:guidkeys.append(key)
 if (entry['asset']['m_FileID']==0 and entry['asset']['m_PathID'] in [D,sid]) or any(p['m_FileID']==0 and p['m_PathID'] in [D,sid] for p in span):
  if ptr not in span:span.append(copy.deepcopy(ptr))
  entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span);meta['m_PreloadTable'].extend(span)
dep=ba.name.lower()
if dep not in meta['m_Dependencies']:meta['m_Dependencies'].append(dep)
bundle.save_typetree(meta);output=we.file.save(packer='lz4');check=UnityPy.load(output,(G/BN).read_bytes());sa=next(a for a in check.assets if a.name==af.name)
assert set(sa.objects)==set(hashes)
for i,h in hashes.items():
 if i not in [D,sid,bundle.path_id]:assert sha(sa.objects[i].get_raw_data())==h
assert sa.objects[D].read_typetree()==doc and sa.objects[sid].read_typetree()==style and sa.objects[bundle.path_id].read_typetree()==meta
assert PPtr(m_FileID=fid,m_PathID=BLUE,assetsfile=sa).deref().get_raw_data()==blue.get_raw_data()
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
catalog_outputs={}
for catdir in [AA,S]:
 c=cm.Catalog((catdir/'catalog.bin').read_bytes());keys={k:p for k,p in c.keys() if isinstance(k,str)};locs={q for p in keys.values() for (q,) in c.array(p,'I')};bgloc=next(q for q in locs if c.location(q)['provider'].endswith('.AssetBundleProvider') and c.location(q)['internal'].endswith('\\'+BN))
 wanted=set()
 for key in guidkeys:
  assert key in keys
  for (q,) in c.array(keys[key],'I'):
   assert c.location(q)['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','UnityEngine.UIElements.StyleSheet'];wanted.add(q)
 for q in wanted:
  fields=c.unpack(q,'7I');deps=c.location(q)['dependencies']
  if bgloc not in deps:
   depbytes=__import__('struct').pack('<'+'I'*(len(deps)+1),*(deps+[bgloc]));newdeps=c.append(depbytes,True);__import__('struct').pack_into('<I',c.data,q+12,newdeps);__import__('struct').pack_into('<I',c.data,q+16,__import__('zlib').crc32(depbytes))
  assert bgloc in c.location(q)['dependencies']
 raw=(catdir/'catalog.bin').read_bytes();new=bytes(c.data)
 if raw!=new:
  oldc=cm.Catalog(raw);assert c.keys()==oldc.keys()
  for q in locs:
   if q not in wanted:assert c.unpack(q,'7I')==oldc.unpack(q,'7I')
  for name,payload in [('catalog.bin',new),('catalog.hash',hashlib.md5(new).hexdigest().encode('ascii'))]:
   p=catdir/name;before[p]=p.read_bytes();catalog_outputs[p]=payload;protected.pop(p,None)
O.mkdir();(O/WN).write_bytes(output);files=[]
for target,b in before.items():
 tag='game' if target.parent in [G,AA] else 'skin';name=target.name;payload=output if name==WN else catalog_outputs[target];source=WN if name==WN else tag+'-'+name
 (O/source).write_bytes(payload);backup=Path('backup')/tag/name;(O/backup).parent.mkdir(parents=True,exist_ok=True);(O/backup).write_bytes(b);files.append({'target':str(target),'source':source,'backup':backup.as_posix(),'before_sha256':sha(b),'after_sha256':sha(payload)})
m={'installed':False,'runtime_verified':False,'game_background_asset':{'name':'GameWorldBackground','path_id':str(D),'guid_keys':guidkeys},'source_blue_texture':{'name':'TF skin V1','path_id':str(BLUE),'m_FileID':fid,'sha256':sha(blue.get_raw_data())},'change':'Only generated 3D-background child replaced by static blue VisualElement; existing switch and static background branch preserved','changed_objects':[str(D),str(sid),str(bundle.path_id)],'unrelated_objects_preserved':len(hashes)-3,'current_non_sidebar_baseline_preserved':True,'install_files':files,'protected_sha256':{str(p):h for p,h in protected.items()}}
M.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(O/'安装.ps1').write_text("$ErrorActionPreference='Stop'\n& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' --output-dir '"+O.name+"' --install\nif($LASTEXITCODE -ne 0){throw 'Install failed.'}\n",'utf-8-sig')
lines=["$ErrorActionPreference='Stop'","if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}"]
for x in files:lines.append("if((Get-FileHash -LiteralPath '"+x['target']+"' -Algorithm SHA256).Hash.ToLower() -ne '"+x['after_sha256']+"'){throw 'Version mismatch.'}")
for x in files:lines.append("Copy-Item -LiteralPath (Join-Path $PSScriptRoot '"+x['backup']+"') -Destination '"+x['target']+"' -Force")
(O/'回退.ps1').write_text('\n'.join(lines),'utf-8-sig')
for target,b in before.items():assert target.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'changed_objects':3,'non_sidebar_preserved':True,'static_backgrounds_preserved':True,'background_guid_keys':guidkeys,'source':'TF skin V1'}))
