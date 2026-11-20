from pathlib import Path
import sys,json,hashlib,datetime,subprocess,ast
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<codec>','exec'))
TypeTreeHelper.write_value=write
isgame='--game' in sys.argv
OUT=R/(('game-' if isgame else '')+'retired-image-cleanup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
folder=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64') if isgame else Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
P=folder/('ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle' if '--global' in sys.argv else 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={p:sha(p.read_bytes()) for p in folder.glob('*.bundle') if p!=P}
for p in [folder/'catalog.bin',folder/'catalog.hash',folder.parent/'catalog.bin',folder.parent/'catalog.hash']:
 if p.exists():protected[p]=sha(p.read_bytes())
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Exit game first'
raw=P.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};orig={pid:sha(o.get_raw_data()) for pid,o in oo.items()};expected={};changes=[]
retired={'ReportBlueLightBelowPlayerTopBackground','PlayerTopBackgroundTextureLayer'}
for o in list(e.objects):
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree();counts={}
 if 'm_Rules' in d:
  for rule in d['m_Rules']:
   bad=[s for s in rule['m_ComplexSelectors'] if 'ReportBlueLightBelowPlayerTopBackground' in str(s)]
   if bad:
    rule['m_ComplexSelectors']=[s for s in rule['m_ComplexSelectors'] if s not in bad]
    if not rule['m_ComplexSelectors']:rule['m_Properties']=[]
    counts['retired_selectors']=counts.get('retired_selectors',0)+len(bad)
   for prop in rule['m_Properties']:
    if prop['m_Id']!=458753:continue
    for h in prop['m_Values']:
     isnull=h['m_ValueType']==6 and not d['assets'][h['valueIndex']]['m_PathID']
     isenum=h['m_ValueType']==7 and d['strings'][h['valueIndex']]=='none'
     if isnull or isenum:h.update(m_ValueType=1,valueIndex=6);counts['invalid_image_values']=counts.get('invalid_image_values',0)+1
 elif 'inlineSheet' in d:
  refs=d['references']['RefIds'];rr={r['rid']:r for r in refs};drop=set()
  for r in refs:
   a=r.get('data',{});sd=a.get('m_SerializedData',{}).get('rid');sddata=rr.get(sd,{}).get('data',{})
   if sddata.get('name') in retired and not a.get('m_Children') and not sddata.get('bindings'):
    drop.update([r['rid'],sd])
  if drop:
   for r in refs:
    a=r.get('data',{})
    if 'm_Children'in a:a['m_Children']=[v for v in a['m_Children'] if v['rid'] not in drop]
   d['references']['RefIds']=[r for r in refs if r['rid'] not in drop]
   assert not any("'rid': "+str(rid)+'}' in str(d) for rid in drop)
   counts['retired_empty_nodes']=len(drop)//2
 if counts:o.save_typetree(d);expected[o.path_id]=d;changes.append({'object':o.path_id,'name':d['m_Name'],**counts})
data=e.file.save(packer='lz4');cc={o.path_id:o for o in UnityPy.load(data).objects};assert cc.keys()==orig.keys()
for pid,o in cc.items():
 if pid in expected:assert o.read_typetree()==expected[pid]
 else:assert sha(o.get_raw_data())==orig[pid]
for o in cc.values():
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree()
 if 'm_Rules'in d:
  assert not any('ReportBlueLightBelowPlayerTopBackground' in str(r['m_ComplexSelectors']) for r in d['m_Rules'])
  assert not any(h['m_ValueType']==6 and not d['assets'][h['valueIndex']]['m_PathID'] for r in d['m_Rules'] for p in r['m_Properties'] if p['m_Id']==458753 for h in p['m_Values'])
(OUT/'backup.bundle').write_bytes(raw);(OUT/P.name).write_bytes(data)
report={'target':str(P),'before':sha(raw),'after':sha(data),'changes':changes,'installed':False,'game_files_modified':isgame,'textures_deleted':0,'runtime_verified':False,'protected_files':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore="$ErrorActionPreference='Stop'\nif (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }\nif ((Get-FileHash -LiteralPath '"+str(P)+"').Hash.ToLower() -ne '"+sha(data)+"') { throw 'Later changes detected' }\nCopy-Item -LiteralPath '"+str(OUT/'backup.bundle')+"' -Destination '"+str(P)+"' -Force\n"
(OUT/'restore.ps1').write_text(restore,'utf-8-sig')
assert P.read_bytes()==raw
assert all(sha(p.read_bytes())==h for p,h in protected.items())
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Game started; prepared only'
P.write_bytes(data);assert sha(P.read_bytes())==sha(data)
assert all(sha(p.read_bytes())==h for p,h in protected.items())
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'output':str(OUT),'changed_objects':len(changes),'invalid_image_values':sum(r.get('invalid_image_values',0) for r in changes),'selectors':sum(r.get('retired_selectors',0) for r in changes),'nodes':sum(r.get('retired_empty_nodes',0) for r in changes)}))
