from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,shutil,struct,subprocess,sys,zipfile
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
t=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module([n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='write'],[]),'writer','exec'));TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
state=json.loads((R/'current-sidebar-version.json').read_text('utf8'));base=Path(state['installed_variant']);rows=json.loads((base/'transaction.json').read_text('utf8'))
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');out=R/('sidebar-to-main-'+stamp);arch=R/'saved-progress'/('FM27-sidebar-saved-'+stamp)
out.mkdir();arch.mkdir();outputs={};before={};audit=[]
guids={'2f7f33f147615f32bb80061b0ecda1bf','2384a857dfa15051ac87a35445fa03ab'}
for row in rows:
 p=Path(row['target']);cur=p.read_bytes();before[p]=cur;back=Path(row['backup']).read_bytes();assert sha(back)==row['before']
 if sha(cur)==row['after']:outputs[p]=back;continue
 if p.name in ('catalog.bin','catalog.hash'):continue
 assert 'gameworldvisualtreeassetpreload' in p.name
 e=UnityPy.load(cur);a=e.assets[0];side=UnityPy.load(row['source']).assets[0];main=UnityPy.load(back).assets[0];expected={}
 for pid,old in side.objects.items():
  if pid not in main.objects:
   assert a.objects[pid].get_raw_data()==old.get_raw_data();a.objects.pop(pid);continue
  native=main.objects[pid].get_raw_data()
  if native==old.get_raw_data():continue
  assert a.objects[pid].get_raw_data()==old.get_raw_data(),('Overlapping new edit',pid)
  a.objects[pid].set_raw_data(native);expected[pid]=native
 payload=e.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
 assert set(check.objects)==set(a.objects)
 current_objects=UnityPy.load(cur).assets[0].objects
 for pid,o in check.objects.items():
  assert o.get_raw_data()==(expected[pid] if pid in expected else current_objects[pid].get_raw_data())
 outputs[p]=payload
# Remove only sidebar locations from the current catalog, preserving later registrations.
catpath=next(p for p in before if p.name=='catalog.bin')
if catpath not in outputs:
 spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 cat=mod.Catalog(before[catpath]);keys=cat.keys();removed=set()
 for guid in guids:removed.update(cat.locations(guid))
 records=[]
 for (key,ptr),(ko,_) in zip(keys,cat.key_records):
  if key in guids:continue
  ls=[v[0] for v in cat.array(ptr,'I')];keep=[v for v in ls if v not in removed]
  if ls!=keep:ptr=cat.append(b''.join(struct.pack('<I',v) for v in keep),True)
  records.append((ko,ptr))
 struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*v) for v in records),True));outputs[catpath]=bytes(cat.data)
 new=mod.Catalog(outputs[catpath]);nk=dict(new.keys())
 for key,ptr in keys:
  if key in guids:assert key not in nk
  else:assert [v[0] for v in new.array(nk[key],'I')]==[v[0] for v in cat.array(ptr,'I') if v[0] not in removed]
 hashpath=next(p for p in before if p.name=='catalog.hash');outputs[hashpath]=hashlib.md5(outputs[catpath]).hexdigest().encode('ascii')
loc=json.loads((R/'current-game-location.json').read_text('utf8'));game=Path(loc['bundle_root'])
protected={str(p):sha(p.read_bytes()) for p in list(game.glob('*.bundle'))+list(Path(loc['skin_packages']).glob('*')) if p.is_file() and p not in outputs}
tx=[]
for p,payload in outputs.items():
 for folder,sub,data in [(out,'packages',payload),(out,'backup-game',before[p]),(arch,'packages',before[p]),(arch,'non-sidebar-backup',payload)]:
  dest=folder/sub/p.name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(data)
 rel=Path('aa/StandaloneWindows64' if p.suffix=='.bundle' else 'aa')/p.name;dest=arch/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(before[p])
 tx.append(dict(target=str(p),source=str(out/'packages'/p.name),backup=str(out/'backup-game'/p.name),before=sha(before[p]),after=sha(payload)))
for folder,value in [(out,tx),(arch,[dict(target=r['target'],source=str(arch/'packages'/Path(r['target']).name),backup=str(arch/'non-sidebar-backup'/Path(r['target']).name),before=r['after'],after=r['before']) for r in tx])]:
 (folder/'transaction.json').write_text(json.dumps(value,indent=2),'utf8')
 (folder/'manifest.json').write_text(json.dumps(dict(installed=False,runtime_verified=False,protected_sha256=protected,club_height_runtime_confirmation_pending=True),indent=2),'utf8')
 shutil.copy2(R/'install-independent-resource-patch.py',folder/'installer.py')
 for name,flag in [('install',''),('restore',' --restore')]:
  (folder/(name+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
shutil.copy2(R/'current-sidebar-version.json',arch/'sidebar-state.json')
shutil.copy2(R/'build-sidebar-club-row-heights.py',arch/'build-sidebar-club-row-heights.py')
zipout=R/'exports'/('FM27-'+arch.name+'-aa.zip')
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED) as z:
 for p in (arch/'aa').rglob('*'):
  if p.is_file():z.write(p,p.relative_to(arch).as_posix())
with zipfile.ZipFile(zipout) as z:assert z.testzip() is None and len(z.namelist())==6
subprocess.run([sys.executable,str(out/'installer.py'),str(out)],check=True)
state.update(current_game_mode='non-sidebar',latest_saved_sidebar_archive=str(arch),latest_saved_sidebar_export=str(zipout),sidebar_removal_record=str(out),restore_saved_sidebar=str(out/'restore.ps1'),latest_prepared_sidebar_installed=False)
(R/'current-sidebar-version.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
with (R/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n- 2026-11-06：用户要求保存侧栏后回退。当前侧栏6资源已归档 '+str(arch)+'，aa包 '+str(zipout)+'。已恢复顶部导航主版，保留之后的球场面板及目录注册修改。回退记录 '+str(out)+'，6文件安装校验通过，俱乐部增行试修实际高度仍未确认。后续启用侧栏须迁移最新主版增量。\n')
print(json.dumps(dict(archive=str(arch),zip=str(zipout),rollback=str(out),files=len(tx)),ensure_ascii=False))

