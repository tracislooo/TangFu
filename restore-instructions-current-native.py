from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,subprocess,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
oldwrite=TypeTreeHelper.write_value
h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[x for x in h.body if isinstance(x,ast.FunctionDef) and x.name=='write'],type_ignores=[]),'helper','exec'));TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text());GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);BN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BASE=Path(json.loads((R/'current-game-update-comparison.json').read_text())['archive'])/'updated-native/aa/StandaloneWindows64'
OUT=R/('instructions-native-default-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
ne=UnityPy.load(str(BASE/BN));no={o.path_id:o for o in ne.objects};naf=ne.assets[0]
natives={o.peek_name():o for o in ne.objects if o.type.name=='MonoBehaviour' and (o.peek_name()=='InstructionTileBaseTemplate' or o.peek_name().startswith(('TeamInstructionTile','PlayerInstructionGroup')))}
tx=[];audits=[];protected={}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 for p in folder.glob('*.bundle'):
  if p.name!=BN:protected[str(p)]=sha(p.read_bytes())
 before=(folder/BN).read_bytes();en=UnityPy.load(before);obs={o.path_id:o for o in en.objects};af=en.assets[0];hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};byname={o.peek_name():o for o in en.objects if o.type.name=='MonoBehaviour'};changed={};rows=[]
 known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
 for t in naf.ref_types:
  key=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
  if key not in known:af.ref_types.append(copy.copy(t));known.add(key)
 schema={}
 for nm in natives:
  if nm in byname:
   for row in byname[nm].read_typetree().get('references',{}).get('RefIds',[]):
    if 'data' in row:schema.setdefault(str(row['type']),set(row['data']))
 for name,src in natives.items():
  if name not in byname:continue
  dst=byname[name];nd=src.read_typetree();old=dst.read_typetree();sid=old['inlineSheet']['m_PathID'];nsid=nd['inlineSheet']['m_PathID']
  localmap={src.path_id:dst.path_id,nsid:sid}
  def remap(v):
   if isinstance(v,dict):
    if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
     if v['m_FileID']==0:
      pid=localmap.get(v['m_PathID'],v['m_PathID']);assert pid in obs,('missing local',name,pid);return {'m_FileID':0,'m_PathID':pid}
     ext=naf.externals[v['m_FileID']-1];idx=next((i+1 for i,x in enumerate(af.externals) if x.name==ext.name),None)
     if idx is None:af.externals.append(copy.deepcopy(ext));idx=len(af.externals)
     return {'m_FileID':idx,'m_PathID':v['m_PathID']}
    return {k:remap(x) for k,x in v.items()}
   if isinstance(v,list):return [remap(x) for x in v]
   if isinstance(v,tuple):return tuple(remap(x) for x in v)
   return v
  if tag=='skin':
   for row in nd.get('references',{}).get('RefIds',[]):
    if 'data' in row and str(row['type']) in schema:
     for k in set(row['data'])-schema[str(row['type'])]:
      assert row['data'][k] in [0,0.0,'',[],{}],(name,k);del row['data'][k]
  for ob,data in [(dst,remap(nd)),(obs[sid],remap(no[nsid].read_typetree()))]:
   if ob.read_typetree()!=data:ob.save_typetree(data);changed[ob.path_id]=data
  rows.append({'name':name,'path_id':dst.path_id,'native_refs_exact':dst.read_typetree()['references']==nd['references']})
 data=en.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects}
 for i,o in check.items():
  if i in changed:
   actual=o.read_typetree()
   if actual!=changed[i]:
    (OUT/('mismatch-'+tag+'.json')).write_text(json.dumps({'id':i,'expected':changed[i],'actual':actual},indent=2),'utf8');raise AssertionError((tag,i))
  else:assert sha(o.get_raw_data())==hashes[i],i
 catpath=(folder.parent if tag=='game' else folder)/'catalog.bin';cb=catpath.read_bytes();c=cm.Catalog(cb)
 rd=EndianBinaryReader(data);bu=object.__new__(BundleFile);bu.signature=rd.read_string_to_null();bu.version=rd.read_u_int();bu.version_player=rd.read_string_to_null();bu.version_engine=rd.read_string_to_null();_,block=bu.read_fs(rd);crc=zlib.crc32(block.bytes)
 locations={i:c.location(i) for _,ls in c.keys() for i, in c.array(ls,'I')};count=0
 for i,v in locations.items():
  if v['type'][1].endswith('IAssetBundleResource') and v['internal'].replace('\\','/').endswith('/'+BN):
   typ,payload=c.unpack(v['raw'][5],'2I');raw=list(c.unpack(payload,'5I'));raw[2:4]=[crc,len(data)];ex=c.append(struct.pack('<2I',typ,c.append(struct.pack('<5I',*raw))));record=list(v['raw']);record[5]=ex;struct.pack_into('<7I',c.data,i,*record);count+=1
 assert count
 for target,payload in [(folder/BN,data),(catpath,bytes(c.data)),(catpath.with_name('catalog.hash'),hashlib.md5(bytes(c.data)).hexdigest().encode())]:
  dest=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name;dest.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True);dest.write_bytes(payload);prior=target.read_bytes();backup.write_bytes(prior);tx.append({'target':str(target),'source':str(dest),'backup':str(backup),'before':sha(prior),'after':sha(payload)})
 audits.append({'variant':tag,'restored_templates':rows,'changed_objects':list(changed),'all_other_objects_byte_identical':True,'crc_updated':True})
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'native_baseline':str(BASE),'audits':audits,'protected_sha256':protected},indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
watch="""from pathlib import Path
import subprocess,sys,time,json
out=Path(sys.argv[1])
while subprocess.run(['powershell','-NoProfile','-Command','Get-Process fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():time.sleep(4)
p=subprocess.run([sys.executable,str(out/'installer.py'),str(out)],capture_output=True,text=True)
(out/'automatic-install-status.txt').write_text(p.stdout+p.stderr,encoding='utf8')
if p.returncode==0:
 Path(out.parent/'current-instructions-native-default.json').write_text(json.dumps({'manifest':str(out/'manifest.json'),'installed':True,'runtime_verified':False},indent=2),encoding='utf8')
"""
(OUT/'wait-install.py').write_text(watch,'utf8');running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip()
if running:subprocess.Popen([sys.executable,str(OUT/'wait-install.py'),str(OUT)],creationflags=subprocess.CREATE_NO_WINDOW)
else:subprocess.run([sys.executable,str(OUT/'wait-install.py'),str(OUT)],check=True)
(R/'current-instructions-native-default.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'installed':not bool(running),'waiting_for_game_exit':bool(running),'runtime_verified':False},indent=2),'utf8')
print(json.dumps({'output':str(OUT),'templates':len(natives),'waiting_for_exit':bool(running)},ensure_ascii=True))
