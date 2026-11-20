from pathlib import Path
import sys,json,hashlib,subprocess,os,uuid
out=Path(next(x for x in sys.argv[1:] if not x.startswith('--'))).resolve();restore='--restore' in sys.argv
manifest=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def closed():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 assert not p.stdout.strip(),'Exit Football Manager normally before installing/restoring this patch.'
closed();current={};targets={}

for row in tx:
 p=Path(row['target'])
 if restore or p.parent.name!='CustomGridCompositions' or sha(p.read_bytes())==row['before']:continue
 existing=p.read_bytes();doc=json.loads(existing.decode('utf8'));baseline=json.loads(Path(row['backup']).read_text('utf8'));prepared=json.loads(Path(row['source']).read_text('utf8'))
 assert [b['m_elementID'] for b in doc['m_gridComponents']]==[b['m_elementID'] for b in baseline['m_gridComponents']], 'Custom layout changed structurally; cannot auto-migrate safely.'
 import copy
 moved=[copy.deepcopy(doc['m_gridComponents'][i]) for i in [0,2,4,5,1,6]]+[copy.deepcopy(prepared['m_gridComponents'][-1])]
 for b,target in zip(moved,prepared['m_gridComponents']):
  for key in ['m_location','m_minSize','m_maxSize']:b[key]=copy.deepcopy(target[key])
  for cfg in b['m_gridElementConfigs']:cfg['Size']=copy.deepcopy(target['m_gridElementConfigs'][0]['Size'])
 prepared['m_gridComponents']=moved;raw=json.dumps(prepared,ensure_ascii=False,indent=2).encode('utf8')
 Path(row['backup']).write_bytes(existing);Path(row['source']).write_bytes(raw);row['before']=sha(existing);row['after']=sha(raw)
(out/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')

allowed={Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64').resolve(),Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa').resolve(),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve()}
allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())
for row in tx:
 p=Path(row['target']);assert p.resolve().parent in allowed
 source=Path(row['backup' if restore else 'source']);data=source.read_bytes();assert sha(data)==row['before' if restore else 'after'],('Patch/backup damaged',source)
 previous=p.read_bytes();expected=row['after' if restore else 'before'];actual=sha(previous)
 assert actual==expected or (not restore and actual==row['after']),('Target changed since preparation',p)
 current[p]=previous;targets[p]=data
for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h,('Unrelated resource changed',path)
closed()
for p,data in current.items():assert p.read_bytes()==data
def atomic(p,data):
 temp=p.with_name(p.name+'.codex-fitness-'+uuid.uuid4().hex+'.tmp')
 try:temp.write_bytes(data);os.replace(temp,p)
 finally:
  if temp.exists():temp.unlink()
try:
 for p,data in targets.items():atomic(p,data);assert p.read_bytes()==data
 for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h
except BaseException:
 for p,data in current.items():atomic(p,data)
 raise
manifest.update(installed=not restore,installed_verified=not restore,restored=restore)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'verified_resource_files':len(targets),'runtime_verified':False,'output':str(out)},ensure_ascii=False))

state_path=out.parent/'current-highlight-layout.json'
if restore:
 state=json.loads((out/'previous-highlight-state.json').read_text('utf8'))
else:
 state=json.loads((out/'highlight-state.json').read_text('utf8'));state['status']='installed';state['installed_files']=len(tx)
state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
