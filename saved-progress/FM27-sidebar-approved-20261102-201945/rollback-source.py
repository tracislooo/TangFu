from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,shutil,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
t=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'write','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);AA=GAME.parent
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
OUT=R/('sidebar-to-main-'+stamp);OUT.mkdir()
ARCH=R/'saved-progress'/('FM27-sidebar-approved-'+stamp);ARCH.mkdir()
BASE=R/'sidebar-approved-rebased-20261102-092833'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
ids={-980000000041001,-980000000041002,-980000000041003,-980000000041004}
guids={'2f7f33f147615f32bb80061b0ecda1bf','2384a857dfa15051ac87a35445fa03ab'}
sha=lambda b:hashlib.sha256(b).hexdigest()
before={};outputs={};audits=[]
def undo(side,base,cur,path=''):
 if side==base:return copy.deepcopy(cur)
 if cur==side:return copy.deepcopy(base)
 if isinstance(side,dict) and isinstance(base,dict) and isinstance(cur,dict):
  res=copy.deepcopy(cur)
  for k in side:
   if k not in base:
    assert cur.get(k)==side[k],('new field changed',path,k)
    res.pop(k,None)
   else:res[k]=undo(side[k],base[k],cur[k],path+'/'+str(k))
  return res
 if isinstance(side,list) and isinstance(base,list) and isinstance(cur,list):
  if path.endswith('/RefIds'):
   sm={x['rid']:x for x in side};bm={x['rid']:x for x in base};res=[]
   for x in cur:
    rid=x['rid']
    if rid in sm and rid not in bm:
     assert x==sm[rid],('added node changed',path,rid)
    elif rid in sm:res.append(undo(sm[rid],bm[rid],x,path+'/'+str(rid)))
    else:res.append(copy.deepcopy(x))
   return res
  assert side[:len(base)]==base,('list conflict',path)
  res=copy.deepcopy(cur)
  for x in side[len(base):]:res.remove(x)
  return res
 raise AssertionError(('overlapping edit',path))
for name in [W,D,M]:
 p=GAME/name;before[p]=p.read_bytes();env=UnityPy.load(before[p]);asset=env.assets[0]
 base=UnityPy.load(str(BASE/'non-sidebar-backup'/name)).assets[0]
 side=UnityPy.load(str(BASE/'packages'/name)).assets[0]
 raw={i:o.get_raw_data() for i,o in asset.objects.items()};expected={}
 for pid,o in side.objects.items():
  if pid not in base.objects or o.type.name=='AssetBundle' or o.get_raw_data()==base.objects[pid].get_raw_data():continue
  sd=o.read_typetree();bd=base.objects[pid].read_typetree();cd=asset.objects[pid].read_typetree()
  if name==D:
   start=len(bd['m_Rules']);assert len(sd['m_Rules'])==start+8
   # Sidebar occupies the eight rules appended at installation; later main rules follow.
   removed=cd['m_Rules'][start:start+8]
   assert len(removed)==8 and 'tf-reference' in str(removed)
   assert [r['m_ComplexSelectors'] for r in removed]==[r['m_ComplexSelectors'] for r in sd['m_Rules'][start:start+8]]
   result=copy.deepcopy(cd);del result['m_Rules'][start:start+8]
   for i,rule in enumerate(result['m_Rules']):
    for selector in rule['m_ComplexSelectors']:selector['ruleIndex']=i
   assert result['m_Rules'][:start]==cd['m_Rules'][:start]
   for i,r in enumerate(cd['m_Rules'][start+8:]):
    rr=copy.deepcopy(r)
    for s in rr['m_ComplexSelectors']:s['ruleIndex']-=8
    assert rr==result['m_Rules'][start+i]
  else:result=undo(sd,bd,cd,name+':'+str(pid))
  asset.objects[pid].save_typetree(result);expected[pid]=result
 if name==W:
  for pid in ids:assert pid in asset.objects;asset.objects.pop(pid)
  ab=next(o for o in asset.objects.values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
  meta['m_Container']=[(k,v) for k,v in meta['m_Container'] if k not in guids]
  for ptr in meta['m_PreloadTable']:
   if ptr['m_FileID']==0 and ptr['m_PathID'] in ids:ptr['m_PathID']=0
  ab.save_typetree(meta);expected[ab.path_id]=meta
 payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
 assert set(check.objects)==set(asset.objects)
 for pid,o in check.objects.items():
  if pid in expected:assert o.read_typetree()==expected[pid],(name,pid)
  else:assert o.get_raw_data()==raw[pid],(name,pid,'unrelated changed')
 assert all('tf-reference' not in str(o.read_typetree()).lower() for o in check.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name() in ['PrimaryNavigationBar'])
 outputs[p]=payload;audits.append({'bundle':name,'changed_object_ids':list(expected),'unrelated_objects_byte_identical':True})
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
p=AA/'catalog.bin';before[p]=p.read_bytes();cat=mod.Catalog(before[p]);original=cat.keys();removedlocs=set()
for g in guids:removedlocs.update(cat.locations(g))
records=[]
for (key,ptr),(ko,_) in zip(original,cat.key_records):
 if key in guids:continue
 ls=[x[0] for x in cat.array(ptr,'I')];new=[x for x in ls if x not in removedlocs]
 if ls!=new:ptr=cat.append(b''.join(struct.pack('<I',x) for x in new),True)
 records.append((ko,ptr))
struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True))
outputs[p]=bytes(cat.data);newcat=mod.Catalog(outputs[p]);newkeys=dict(newcat.keys())
for key,ptr in original:
 if key in guids:assert key not in newkeys;continue
 assert [x[0] for x in newcat.array(newkeys[key],'I')]==[x[0] for x in cat.array(ptr,'I') if x[0] not in removedlocs]
p=AA/'catalog.hash';before[p]=p.read_bytes();outputs[p]=hashlib.md5(outputs[AA/'catalog.bin']).hexdigest().encode('ascii')
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('*.bundle'))+list(Path(loc['skin_packages']).glob('*')) if p.is_file() and p not in outputs}
tx=[]
for target,data in outputs.items():
 assert target.read_bytes()==before[target]
 src=OUT/'packages'/target.name;bak=OUT/'backup-game'/target.name
 src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(data);bak.write_bytes(before[target])
 rel=Path('aa')/(Path('StandaloneWindows64')/target.name if target.parent==GAME else Path(target.name))
 ap=ARCH/rel;ap.parent.mkdir(parents=True,exist_ok=True);ap.write_bytes(before[target])
 tx.append(dict(target=str(target),source=str(src),backup=str(bak),before=sha(before[target]),after=sha(data)))
manifest=dict(installed=False,operation='remove sidebar while preserving later common changes',approved_sidebar_archive=str(ARCH),runtime_verified=False,bundle_audits=audits,protected_sha256=protected)
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
shutil.copy2(R/'install-independent-resource-patch.py',OUT/'installer.py')
shutil.copy2(R/'current-sidebar-version.json',ARCH/'sidebar-state.json');shutil.copy2(__file__,ARCH/'rollback-source.py')
(ARCH/'manifest.json').write_text(json.dumps(dict(user_approved=True,files=[dict(path=str(Path(x['target']).relative_to(AA)),sha256=x['before']) for x in tx],restore_policy='Rebase sidebar delta onto latest common resources; do not overwrite future common changes',non_sidebar_conversion=str(OUT)),ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install-non-sidebar',''),('restore-saved-sidebar',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
print(json.dumps({'output':str(OUT),'archive':str(ARCH),'files':len(tx),'audits':audits},ensure_ascii=False),flush=True)
