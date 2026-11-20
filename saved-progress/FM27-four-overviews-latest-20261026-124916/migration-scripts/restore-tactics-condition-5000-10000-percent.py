from pathlib import Path
import sys,json,hashlib,datetime,struct,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';CELL=-970000000001000;sha=lambda b:hashlib.sha256(b).hexdigest()
BASE=R/'tactics-condition-direct-percent-20261023-035355';last=json.loads((BASE/'manifest.json').read_text('utf8'));before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
for b in before.values():assert sha(b)==last['after_sha256'],'Current package has changed since the last patch'
target=(BASE/'backup-game'/W).read_bytes();assert target==(BASE/'backup-skin'/W).read_bytes()
old={o.path_id:o for o in UnityPy.load(next(iter(before.values()))).objects};new={o.path_id:o for o in UnityPy.load(target).objects};assert old.keys()==new.keys()
for i in old:
 if i!=CELL:assert sha(old[i].get_raw_data())==sha(new[i].get_raw_data()),i
doc=new[CELL].read_typetree();r={a['rid']:a for a in doc['references']['RefIds']}
def sd(i):return r[r[i]['data']['m_SerializedData']['rid']]['data']
gate=next(i for i,a in r.items() if a.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and sd(i).get('name')=='TacticsConditionAbove-1')
def selected(i,value):
 a=r[i]['data'];s=sd(i)
 if a['m_FullTypeName']!='SI.Bindable.BindableSwitchElement':return s['text']
 b=bytes(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);p=1;args=[]
 for _ in range(b[0]):n=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+n]);p+=n
 limit=struct.unpack_from('<i',args[1],len(args[1])-4)[0]
 return selected(a['m_Children'][int(value is not None and value>limit)]['rid'],value)
for v in [None,-2147483648]+list(range(-1,151)):assert selected(gate,v)==('--' if v is None or v<0 else str(max(0,min(100,(v-50)*2)))+'%'),v
OUT=R/('tactics-condition-5000-10000-percent-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
for p,b in before.items():
 f=OUT/('backup-game' if p.parent==GAME else 'backup-skin');f.mkdir();(f/W).write_bytes(b)
(OUT/W).write_bytes(target)
restore=['$ErrorActionPreference = "Stop"']
for p in before:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
report={'installed':False,'runtime_verified':False,'requested_scale':{'5000':'0%','7500':'50%','10000':'100%'},'ui_field_scale':{'50':selected(gate,50),'75':selected(gate,75),'100':selected(gate,100)},'changed_object':CELL,'other_objects_unchanged':True,'avatar_120_percent_preserved':True,'after_sha256':sha(target)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
for p,b in before.items():assert p.read_bytes()==b
try:
 for p in before:p.write_bytes(target);assert p.read_bytes()==target
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'requested_scale':report['requested_scale']}))
