"""Replace only user-listed background textures, keeping all identities intact."""
from pathlib import Path
import copy,datetime,json,re,sys
R=Path(__file__).resolve().parent
code=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8').split('payloads={};changes={}')[0]
code=code.replace("S='ui-styles_assets_default.bundle';BG=", "S='ui-backgrounds_assets_common.bundle';BG=")
exec(compile(code,'<current-background-catalog-audit>','exec'))
MODE_FM27='--fm27' in sys.argv
NAMES=['fm-skin-v2','Sky Bet League One','Sky Bet League Two','Sky Bet Championship','Premier League',
 "UEFA Women's Champions League",'fm-bundesliga-skin-min','fm-supercup-skin-min','efl-league-one-skin',
 'efl-league-two-skin','efl-league-cup-skin','fm-conference-league-skin-min','UEFA Conference League',
 'UEFA Super Cup','UEFA Champions League','uefa-cl_womens_league_skin_fm26','efl-bst-skin','UEFA Europa League',
 'pl-premier-league-skin','Bundesliga','uefa-cl_league_skin_fm26','efl-championship-skin','fm-europa-league-skin-min',
 'efl_skin_fm26','uefa-super-cup_league_skin_fm26','efl_vertu_skin_fm26','vertu_fm26','bundesliga_fm26',
 'uefa-europa_league_skin_fm26','uefa-conference_league_skin_fm26','premier_league_skin_fm26']
if MODE_FM27:
 discovered=[]
 for path in GAME.glob('ui-backgrounds_assets*.bundle'):
  for ob in UnityPy.load(str(path)).objects:
   if ob.type.name=='Texture2D' and 'fm27_skin' in ob.peek_name().lower():discovered.append(ob.peek_name())
 NAMES=sorted(set(discovered));assert NAMES,'No fm27_skin background textures found'
SOURCE=-910000000000149
base=UnityPy.load(before[GAME/BG]);srcobj=base.assets[0].objects[SOURCE]
assert srcobj.peek_name()=='TF skin V1' and SOURCE not in banned
src=srcobj.read_typetree();assert not src['m_StreamData']['path'] and not src['m_StreamData']['size']
source_pixels=srcobj.read().image.convert('RGBA').tobytes();source_hash=sha(srcobj.get_raw_data())
assert sha(before[GAME/BG])==registry['source_bundle_sha256']
# Inventory all native background bundle variants, including the newer ungrouped bundle.
envs={};inventory={n:[] for n in NAMES}
for path in GAME.glob('*background*.bundle'):
 en=UnityPy.load(str(path));oo={o.path_id:o for o in en.objects};envs[path.name]=(en,oo)
 for ob in oo.values():
  if ob.type.name=='Texture2D' and ob.peek_name() in inventory:inventory[ob.peek_name()].append((path.name,ob.path_id))
aliases={}
normalize=lambda n:re.sub('[^a-z0-9]','',n.lower())
for name in NAMES:
 if inventory[name]:continue
 matches=[(bn,ob.path_id,ob.peek_name()) for bn,(en,oo) in envs.items() for ob in oo.values() if ob.type.name=='Texture2D' and normalize(ob.peek_name())==normalize(name)]
 if len(matches)==1:
  bn,pid,actual=matches[0];inventory[name]=[(bn,pid)];aliases[name]=actual
missing=[n for n in NAMES if not inventory[n]]
targets={}
for requested,items in inventory.items():
 for bn,pid in items:targets.setdefault(bn,{})[pid]=requested
outputs={};records=[];bundle_records=[]
for bn,wanted in targets.items():
 for folder in [GAME,SKIN]:
  path=folder/bn
  if path not in before:before[path]=path.read_bytes() if path.exists() else None
  protected.pop(str(path),None)
  # A skin override absent on disk starts from the game's current native bundle.
  raw=before[path] if before[path] is not None else before[GAME/bn]
  en=UnityPy.load(raw);a=en.assets[0];oo=a.objects
  assert banned.isdisjoint(oo)
  hashes={pid:sha(ob.get_raw_data()) for pid,ob in oo.items()}
  aux={k:sha(v.bytes) for k,v in en.file.files.items() if k!=a.name};expected={}
  for ob in oo.values():
   if ob.type.name=='Sprite':assert ob.read_typetree().get('m_RD',{}).get('texture',{}).get('m_PathID') not in wanted,'Sprite rect migration required'
  for pid,requested in wanted.items():
   ob=oo[pid];name=aliases.get(requested,requested);assert ob.type.name=='Texture2D' and ob.peek_name()==name
   assert pid not in banned and name.lower() not in bnames and pid!=SOURCE
   old=ob.read_typetree();new=copy.deepcopy(src);new['m_Name']=name
   if new!=old:ob.save_typetree(new)
   expected[pid]=new
   if folder==GAME:records.append({'requested_name':requested,'actual_name':name,'bundle':bn,'path_id':str(pid),
    'before_size':[old['m_Width'],old['m_Height']],'after_size':[src['m_Width'],src['m_Height']],
    'already_identical':new==old,'name_and_path_id_preserved':True})
  payload=en.file.save(packer='lz4');saved=UnityPy.load(payload);sa=saved.assets[0];so=sa.objects
  assert sa.name==a.name and set(so)==set(hashes)
  for pid,ob in so.items():
   if pid in expected:
    assert ob.read_typetree()==expected[pid]
    assert ob.read_typetree()['image data']==src['image data']
    assert ob.read().image.convert('RGBA').tobytes()==source_pixels
   else:assert sha(ob.get_raw_data())==hashes[pid],('Unrelated resource changed',bn,pid)
  for k,h in aux.items():assert sha(saved.file.files[k].bytes)==h,('Native stream changed',bn,k)
  meta=next(ob.read_typetree() for ob in so.values() if ob.type.name=='AssetBundle')
  assert all(v['asset']['m_PathID'] not in banned and k.lower() not in bnames for k,v in meta['m_Container'])
  assert all(v['m_PathID'] not in banned for v in meta['m_PreloadTable'])
  if bn==BG:
   assert -910000000000146 not in so
   for t in registry['textures']:
    ob=so[int(t['path_id'])];assert ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256'],t['name']
   assert sha(so[SOURCE].get_raw_data())==source_hash
  outputs[path]=payload;bundle_records.append({'target':str(path),'textures':len(expected),'new_skin_bundle':before[path] is None,
   'all_other_objects_container_preload_streams_unchanged':True})
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/(('fm27-skin-backgrounds-to-TF-skin-V1-' if MODE_FM27 else 'listed-backgrounds-to-TF-skin-V1-')+stamp);out.mkdir()
regpath=R/'current-custom-textures.json';rulespath=R/'AGENTS.md'
before[regpath]=regpath.read_bytes();before[rulespath]=rulespath.read_bytes()
updated=copy.deepcopy(registry)
updated.update(version=registry['version']+1,date='2026-10-29',manifest=str(out/'manifest.json'))
if GAME/BG in outputs:
 updated.update(authoritative_source_bundle=str(out/'game'/BG),source_bundle_sha256=sha(outputs[GAME/BG]))
else:
 for folder in [GAME,SKIN]:protected[str(folder/BG)]=sha(before[folder/BG])
previous=registry.get('native_background_overrides',{})
combined={(t['bundle'],t['path_id']):t for t in previous.get('textures',[])}
for t in records:combined[t['bundle'],t['path_id']]=t
bundle_sources=copy.deepcopy(previous.get('bundle_sources',{}))
bundle_sources.update({bn:{'bundle':str(out/'game'/bn),'sha256':sha(outputs[GAME/bn])} for bn in targets})
updated['native_background_overrides']={'source_texture':'TF skin V1','source_path_id':str(SOURCE),
 'textures':list(combined.values()),'requested_names':list(dict.fromkeys(previous.get('requested_names',[])+NAMES)),
 'missing_names':list(dict.fromkeys(previous.get('missing_names',[])+missing)),
 'name_aliases':{**previous.get('name_aliases',{}),**aliases},'bundle_sources':bundle_sources}
if MODE_FM27:updated['native_background_overrides']['fm27_skin_match_policy']='All Texture2D names containing fm27_skin in ui-backgrounds_assets bundles'
outputs[regpath]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
note='\n- '+('ui-backgrounds_assets 内名称包含 `fm27_skin` 的全部 ' if MODE_FM27 else '用户清单内当前存在的 ')+str(len(records))+' 张原生默认/赛事背景已统一使用 `TF skin V1` 的图像数据，名称、Path ID、容器与预加载记录均保留；涉及 '+', '.join(targets)+'。完整累计目标、实际名称映射与缺失名单见 `current-custom-textures.json` 的 `native_background_overrides`。游戏更新后需在新版各原生包重做这些内容覆盖，不恢复缺失旧资源。\n'
outputs[rulespath]=(rulespath.read_text('utf8')+note).encode('utf8')
for p in [regpath,rulespath]:protected.pop(str(p),None)
for p,b in before.items():assert (p.read_bytes() if p.exists() else None)==b,p
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
sources={};backups={}
for path,raw in outputs.items():
 tag='game' if path.parent==GAME else 'skin' if path.parent==SKIN else 'workspace'
 (out/tag).mkdir(exist_ok=True);(out/('backup-'+tag)).mkdir(exist_ok=True)
 source=out/tag/path.name;source.write_bytes(raw);previous=before[path]
 backup=out/('backup-'+tag)/path.name if previous is not None else None
 if backup:backup.write_bytes(previous)
 sources[str(path)]=str(source);backups[str(path)]=str(backup) if backup else None
verification={'source':'TF skin V1','source_path_id':str(SOURCE),'source_unchanged':True,'textures':records,
 'requested_count':len(NAMES),'matched_count':len(records),'cumulative_overrides':len(combined),'match_mode':'fm27_skin substring' if MODE_FM27 else 'explicit list','missing_names':missing,'name_aliases':aliases,'bundles':bundle_records,
 'encoded_pixels_copied_without_recompression':True,'all_decoded_pixels_identical_to_source':True,
 'all_179_custom_textures_unchanged':len(registry['textures'])==179,'no_new_texture_objects':True,
 'catalog_audits':audits,'reserved_70_absent':True,'runtime_verified':False}
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(before[p]) if before[p] is not None else None for p in outputs},
 'after_sha256':{str(p):sha(raw) for p,raw in outputs.items()},'protected_sha256':protected,'verification':verification}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':sources,'before':backups},ensure_ascii=False,indent=2),'utf8')
(out/'installer.py').write_bytes((R/'install-native-background-overrides.py').read_bytes())
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'替换及缺失名单.json').write_text(json.dumps({'textures':records,'aliases':aliases,'missing_names':missing},ensure_ascii=False,indent=2),'utf8')
(out/'说明.md').write_text(('匹配 ui-backgrounds_assets 中全部包含 fm27_skin 的纹理名称。\n' if MODE_FM27 else '按用户名称清单匹配。\n')+'替换当前存在的默认/赛事背景为 TF skin V1，保留各资源名称和 Path ID。直接复制既有DXT5数据，不重压缩、不重新导入纹理；图片为2668×1500。\n具体修改包、目标与缺失名称见verification.json；不恢复旧版本资源。\n其他图片和资源流、目录及预加载不变；当前自定义图片数量和源纹理不变。此前已替换的背景及其恢复记录保留，累计记录合并到最新图片清单。install.ps1安装；restore.ps1校验后仅回退本次修改。游戏实际显示待启动后确认。','utf8')
print(json.dumps({'prepared':True,'output':str(out),'matched_count':len(records),'missing_names':missing,'aliases':aliases,
 'bundles':bundle_records,'runtime_verified':False},ensure_ascii=False),flush=True)
