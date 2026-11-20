import copy,datetime,hashlib,importlib.util,json,os,subprocess,sys,struct,zlib
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.helpers import TypeTreeHelper
orig=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for x in n.m_Children:
   if x.m_Type!='ReferencedObjectData':orig(v[x.m_Name],x,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return orig(v,n,w,c)
TypeTreeHelper.write_value=write
O=R/'card-frame-blue-20261101-rebased';M=O/'manifest.json';sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),'utf8')
if '--install' in sys.argv or '--rollback' in sys.argv:
 m=json.loads(M.read_text('utf8'));back='--rollback' in sys.argv
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 if p.stdout.strip():print('GAME_RUNNING_PENDING_INSTALL');sys.exit(0)
 changes=[]
 for x in m['install_files']:
  target=Path(x['target']);assert 'Project Taco' not in str(target);old=target.read_bytes();new=(O/x['backup' if back else 'source']).read_bytes()
  assert sha(old)==x['after_sha256' if back else 'before_sha256'],str(target)
  assert sha(new)==x['before_sha256' if back else 'after_sha256'];changes.append((target,old,new))
 assert sha(Path(m['blue_bundle']).read_bytes())==m['blue_bundle_sha256']
 try:
  for target,old,new in changes:
   tmp=target.with_name(target.name+'.cardblue.tmp');tmp.write_bytes(new);os.replace(tmp,target);assert target.read_bytes()==new
 except BaseException:
  for target,old,new in changes:target.write_bytes(old)
  raise
 m.update(installed=not back,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(M,m)
 if not back:
  p=R/'AGENTS.md';p.write_text(p.read_text('utf8')+'\n- 2026-11-01：13个页面外壳 Card-frame 图片层取消 game.BackgroundImage.BackgroundImage 动态绑定，改为直接显示 TF skin V1；保留元素名称、ID及布局。更新后恢复规则见 card-frame-blue-20261101-rebased/manifest.json 和 fix-card-frame-blue.py。\n','utf8')
 print('ROLLED_BACK' if back else 'INSTALLED');sys.exit(0)
assert not O.exists();loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);S=Path(loc['skin_packages']);AA=Path(loc['aa_root'])
BN='ui-backgrounds_assets_common.bundle';BLUE=-910000000000149
bb=(G/BN).read_bytes();be=UnityPy.load(bb);ba=be.assets[0];blue=ba.objects[BLUE];assert blue.peek_name()=='TF skin V1'
template=json.loads((R/'investigate-black-player-background-20261101/visual-element-template.json').read_text('utf8'))
targets=json.loads((R/'card-frame-targets.json').read_text('utf8'));before={};outputs={};records=[];guids=set()
for folder in [G,S]:
 for name in sorted({t['bundle'] for t in targets}):
  p=folder/name;raw=p.read_bytes();before[p]=raw;e=UnityPy.load(raw);a=e.assets[0];obs=a.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};changed=set();desired={}
  fid=next(i+1 for i,x in enumerate(a.externals) if x.path==f'archive:/{ba.name}/{ba.name}');ptr={'m_FileID':fid,'m_PathID':BLUE}
  bm=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bm.read_typetree();oldmeta=copy.deepcopy(meta);ds=set()
  for t in [t for t in targets if t['bundle']==name]:
   pid=int(t['id']);doc=obs[pid].read_typetree();refs={r['rid']:r for r in doc['references']['RefIds']};data=refs[t['rid']];d=data['data']
   assert d['name']=='Card-frame' and d['Binding']['m_direct']['Path']['m_path']=='game.BackgroundImage.BackgroundImage'
   node=next(r for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==t['rid']);assert node['data']['m_FullTypeName']=='SI.Bindable.SIImage'
   nd=copy.deepcopy(template['data'])
   for k in nd:
    if k in d:nd[k]=copy.deepcopy(d[k])
   data['data']=nd;data['type']=copy.deepcopy(template['type']);node['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
   sid=doc['inlineSheet']['m_PathID'];style=obs[sid].read_typetree();ruleid=node['data']['m_RuleIndex']
   if ruleid<0:
    ruleid=len(style['m_Rules']);style['m_Rules'].append({'m_Line':-1,'m_Properties':[]});node['data']['m_RuleIndex']=ruleid
   rule=style['m_Rules'][ruleid];idx=len(style['assets']);style['assets'].append(ptr.copy());si=len(style['strings']);style['strings'].append('scale-and-crop')
   rule['m_Properties']=[x for x in rule['m_Properties'] if x['m_Id'] not in [458753,262153]]+[{'m_Id':458753,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':6,'valueIndex':idx}]},{'m_Id':262153,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':7,'valueIndex':si}]}]
   desired[pid]=copy.deepcopy(doc);desired[sid]=copy.deepcopy(style);obs[pid].save_typetree(doc);obs[sid].save_typetree(style);changed.update([pid,sid]);ds.update([pid,sid]);records.append(dict(t,target=str(p),m_FileID=fid))
  pre=copy.deepcopy(meta['m_PreloadTable'])
  for key,entry in meta['m_Container']:
   span=copy.deepcopy(pre[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
   if entry['asset']['m_PathID'] in ds and entry['asset']['m_FileID']==0:guids.add(key)
   if (entry['asset']['m_PathID'] in ds and entry['asset']['m_FileID']==0) or any(x['m_PathID'] in ds and x['m_FileID']==0 for x in span):
    if ptr not in span:span.append(ptr.copy())
    entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span);meta['m_PreloadTable'].extend(span)
  if ba.name.lower() not in meta['m_Dependencies']:meta['m_Dependencies'].append(ba.name.lower())
  desired[bm.path_id]=copy.deepcopy(meta);bm.save_typetree(meta);changed.add(bm.path_id);out=e.file.save(packer='lz4');check=UnityPy.load(out,bb);ca=next(x for x in check.assets if x.name==a.name)
  assert set(ca.objects)==set(hashes)
  for i,h in hashes.items():
   if i not in changed:assert sha(ca.objects[i].get_raw_data())==h
  for i in changed:assert ca.objects[i].read_typetree()==desired[i]
  assert PPtr(m_FileID=fid,m_PathID=BLUE,assetsfile=ca).deref().get_raw_data()==blue.get_raw_data()
  outputs[p]=out
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for folder in [AA,S]:
 p=folder/'catalog.bin';raw=p.read_bytes();c=cm.Catalog(raw);keys={k:v for k,v in c.keys() if isinstance(k,str)};locs={q for v in keys.values() for (q,) in c.array(v,'I')}
 bg=next(q for q in locs if c.location(q)['provider'].endswith('.AssetBundleProvider') and c.location(q)['internal'].endswith('\\'+BN))
 for key in guids:
  assert key in keys,key
  for (q,) in c.array(keys[key],'I'):
   deps=c.location(q)['dependencies']
   if bg not in deps:
    data=struct.pack('<'+'I'*(len(deps)+1),*(deps+[bg]));ix=c.append(data,True);struct.pack_into('<I',c.data,q+12,ix);struct.pack_into('<I',c.data,q+16,zlib.crc32(data))
   assert bg in c.location(q)['dependencies']
 if bytes(c.data)!=raw:
  before[p]=raw;outputs[p]=bytes(c.data);hp=folder/'catalog.hash';before[hp]=hp.read_bytes();outputs[hp]=hashlib.md5(bytes(c.data)).hexdigest().encode('ascii')
O.mkdir();files=[]
for target,out in outputs.items():
 tag='game' if target.parent in [G,AA] else 'skin';source=tag+'/'+target.name;backup='backup/'+source
 for rel,b in [(source,out),(backup,before[target])]:
  p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 files.append(dict(target=str(target),source=source,backup=backup,before_sha256=sha(before[target]),after_sha256=sha(out)))
dump(M,dict(installed=False,runtime_verified=False,targets=records,install_files=files,blue_bundle=str(G/BN),blue_bundle_sha256=sha(bb),element_ids_and_layout_preserved=True))
for back in [False,True]:
 (O/('回退.ps1' if back else '安装.ps1')).write_text("$ErrorActionPreference='Stop'\n& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' "+('--rollback' if back else '--install')+"\nif($LASTEXITCODE -ne 0){throw 'Failed.'}\n",'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
print(json.dumps({'prepared':True,'templates_per_copy':len(targets),'files':len(files)}))
