from pathlib import Path
import sys,json,copy,hashlib,datetime,subprocess,struct,importlib.util
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');sha=lambda b:hashlib.sha256(b).hexdigest()
O=R/('position-zone-opacity-minus30pct-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));O.mkdir()
before={p:p.read_bytes() for p in [GAME/G,SKIN/G]};assert before[GAME/G]==before[SKIN/G]
for p,b in before.items():folder=O/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/G).write_bytes(b)
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in [f/'ui-backgrounds_assets_common.bundle',f/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',f/'ui-tileslayouts_assets_all.bundle']};protected.update({p:sha(p.read_bytes()) for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin',SKIN/'catalog.hash']})
e=UnityPy.load(before[GAME/G]);obs={o.path_id:o for o in e.objects};styleid=-940000000018001;rowid=-940000000018000
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']};assert styleid not in reserved and rowid not in reserved
row=obs[rowid].read_typetree();rr={r['rid']:r for r in row['references']['RefIds']};sheet=obs[styleid].read_typetree();old=copy.deepcopy(sheet);edits=[]
for r in rr.values():
 a=r.get('data',{});s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if s.get('name','').startswith('PositionZoneColourFill_'):
  rule=sheet['m_Rules'][a['m_RuleIndex']];prop=next(p for p in rule['m_Properties'] if p['m_Id']==458767);handle=prop['m_Values'][0];assert handle['m_ValueType']==2;idx=handle['valueIndex'];v=sheet['floats'][idx];assert abs(v-.38)<1e-6
  result=struct.unpack('<f',struct.pack('<f',v*.7))[0];sheet['floats'][idx]=result;edits.append({'name':s['name'],'float_index':idx,'before':v,'after':result})
assert len(edits)==14 and len({x['float_index'] for x in edits})==14
expected=copy.deepcopy(old)
for x in edits:expected['floats'][x['float_index']]=x['after']
assert sheet==expected;obs[styleid].save_typetree(sheet)
out=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(out).objects};assert check.keys()==obs.keys();assert check[styleid].read_typetree()==sheet
for pid,o in obs.items():
 if pid!=styleid:assert check[pid].get_raw_data()==o.get_raw_data(),pid
# Validate the shared row remains registered in both installed catalogs with the correct owner.
meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle');key=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':rowid})
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for p in [GAME.parent/'catalog.bin',SKIN/'catalog.bin']:
 c=cm.Catalog(p.read_bytes())
 for loc in c.locations(key):
  v=c.location(loc);assert v['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and c.location(v['dependencies'][0])['internal'].endswith('\\'+G)
(O/G).write_bytes(out);report={'installed':False,'runtime_verified':False,'versions':4,'relative_reduction_percent':30,'background_opacity_before_percent':38,'background_opacity_after_percent':26.6,'digits_borders_clicks_geometry_unchanged':True,'only_modified_path_id':str(styleid),'edits':edits,'after_sha256':sha(out)};(O/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(O/'restore.ps1').write_text('\n'.join(['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first.' }"]+["Copy-Item -LiteralPath '"+str(O/('backup-game' if p.parent==GAME else 'backup-skin')/G)+"' -Destination '"+str(p)+"' -Force" for p in before]),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(O)}));sys.exit(0)
try:
 for p in before:p.write_bytes(out);assert p.read_bytes()==out
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(O/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(O),'before_percent':38,'after_percent':26.6,'zones':14,'versions':4}))
