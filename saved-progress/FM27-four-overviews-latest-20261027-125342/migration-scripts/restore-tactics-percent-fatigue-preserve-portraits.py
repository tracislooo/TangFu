from pathlib import Path
import sys,copy,json,hashlib,datetime,subprocess,importlib.util
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');F='ui-tablefactories_assets_all.bundle';V='ui-tableviews_assets_all.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'tactics-width90-fatigue40-colours-20261023-060121';OUT=R/('restore-tactics-percent-fatigue-preserve-portraits-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
source=next(o.read_typetree() for o in UnityPy.load(str(BASE/F)).objects if o.path_id==-7014073910555419620);columns={c['m_id']:copy.deepcopy(c) for c in source['m_rowData'] if c['m_id'] in ['condition','tactics-fatigue-value']};assert len(columns)==2
assert columns['condition']['m_defaultWidth']==90 and columns['tactics-fatigue-value']['m_defaultWidth']==40
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [F,V]};protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name not in [F,V]}
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:protected[p]=sha(p.read_bytes())
for p,b in before.items():
 tag='game' if p.parent==GAME else 'skin';folder=OUT/('backup-'+tag);folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
# Confirm the restored columns point to already-installed direct-percent and raw-fatigue assets.
world={o.path_id:o for o in UnityPy.load(str(GAME/W)).objects};assert all(i in world for i in [-970000000001000,-970000000002000,-970000000004000,-970000000008000]);spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for cp in [GAME.parent/'catalog.bin',SKIN/'catalog.bin']:
 cat=cm.Catalog(cp.read_bytes())
 for c in columns.values():
  assert cat.locations(c['m_uxmlRef']['m_AssetGUID'])
  if c['m_headerUxmlRef']['m_AssetGUID']:assert cat.locations(c['m_headerUxmlRef']['m_AssetGUID'])
install={};details=[]
for p,b in before.items():
 env=UnityPy.load(b);os={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in os.items()};changed={}
 if p.name==F:
  pid=-7014073910555419620;d=os[pid].read_typetree();original=copy.deepcopy(d);avatar=copy.deepcopy(next(c for c in d['m_rowData'] if c['m_id']=='name'));assert avatar['m_uxmlRef']['m_AssetGUID']=='cdb2d09d50d35c2d8871cf922546aa7f'
  rows=[copy.deepcopy(c) for c in d['m_rowData'] if c['m_id']!='tactics-fatigue-value'];idx=next(i for i,c in enumerate(rows) if c['m_id']=='condition');rows[idx]=copy.deepcopy(columns['condition']);rows.insert(idx+1,copy.deepcopy(columns['tactics-fatigue-value']));d['m_rowData']=rows
  assert next(c for c in rows if c['m_id']=='name')==avatar
  assert [c for c in rows if c['m_id'] not in columns]==[c for c in original['m_rowData'] if c['m_id'] not in columns]
  os[pid].save_typetree(d);changed[pid]=d
 else:
  for o in os.values():
   if o.type.name!='MonoBehaviour' or not o.peek_name().startswith('TacticTeamSelection') or 'InMatch' in o.peek_name():continue
   d=o.read_typetree();configs=d.get('m_tableView',{}).get('m_tableConfig',[])
   if not any(c['m_columnID']=='condition' for c in configs):continue
   original=copy.deepcopy(configs);configs=[copy.deepcopy(c) for c in configs if c['m_columnID'] not in ['sharpness','tactics-fatigue-value']];idx=next(i for i,c in enumerate(configs) if c['m_columnID']=='condition');cond=configs[idx];cond['m_columnMetadata'].update(m_widthOverride=90.,m_minWidthOverride=90.);fat=copy.deepcopy(cond);fat['m_columnID']='tactics-fatigue-value';fat['m_columnMetadata'].update(m_widthOverride=40.,m_minWidthOverride=40.);fat['m_columnMetadata']['m_titleTranslationIdOverride']['GameID']=0;configs.insert(idx+1,fat);d['m_tableView']['m_tableConfig']=configs
   assert [c for c in configs if c['m_columnID'] not in ['condition','tactics-fatigue-value']]==[c for c in original if c['m_columnID'] not in ['condition','sharpness','tactics-fatigue-value']]
   assert configs[idx+1]['m_columnID']=='tactics-fatigue-value';o.save_typetree(d);changed[o.path_id]=d
  assert len(changed)==6
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==os.keys()
 for i,h in hashes.items():
  if i not in changed:assert sha(check[i].get_raw_data())==h,(p,i)
 for i,d in changed.items():assert check[i].read_typetree()==d,(p,i)
 tag='game' if p.parent==GAME else 'skin';dest=OUT/('output-'+tag);dest.mkdir(exist_ok=True);(dest/p.name).write_bytes(output);install[p]=output;details.append({'path':str(p),'changed_objects':list(changed)})
report={'installed':False,'runtime_verified':False,'condition_and_sharpness':'direct 0..100%, coloured concentric rings','combined_width':90,'fatigue_width':40,'fatigue':'raw value;0 green;1000 red;-500 orange','portraits_preserved':True,'other_view_objects_and_custom_views_preserved':True,'details':details,'after_sha256':{str(p):sha(b) for p,b in install.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"];installer=list(restore)
for p,b in before.items():
 tag='game' if p.parent==GAME else 'skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-'+tag)/p.name)+"' -Destination '"+str(p)+"' -Force");installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Package changed since preparation.' }")
for p in install:
 tag='game' if p.parent==GAME else 'skin';installer.append("Copy-Item -LiteralPath '"+str(OUT/('output-'+tag)/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in install.items():p.write_bytes(b)
 for p,b in install.items():assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'widths':[90,40],'portraits_preserved':True}))
