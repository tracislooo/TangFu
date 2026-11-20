from pathlib import Path
import json,types

R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-grid-5-10-5-').replace('NAMES=[W,G,M,F]','NAMES=[T]')
exec(compile(boot,'backup-current-grid-resource-and-load-codecs','exec'))
migration_code=(R/'highlight-grid-migration.py').read_text('utf8')
assert 'OLD={(0,4):(0,6),(4,12):(6,8),(16,4):(14,6)}' in migration_code
migration_code=migration_code.replace('OLD={(0,4):(0,6),(4,12):(6,8),(16,4):(14,6)}','OLD={(0,6):(0,5),(6,8):(5,10),(14,6):(15,5)}')
migration=types.ModuleType('grid_migration_five_ten_five');exec(compile(migration_code,'grid_migration.py','exec'),migration.__dict__)

# Reuse the established configuration-extension and full-grid validation logic; no visual template is loaded or saved.
previous=(R/'build-highlight-proportions-30-40-30.py').read_text('utf8')
logic="CK='<Configurations>k__BackingField'"+previous.split("CK='<Configurations>k__BackingField'",1)[1].split("d=Doc(G,name='MatchViewer_12x4')",1)[0]
assert "candidate['Size']['x']=6" in logic and "center_config['Size']={'x':8,'y':8}" in logic
logic=logic.replace("candidate['Size']['x']=6","candidate['Size']['x']=5").replace("center_config['Size']={'x':8,'y':8}","center_config['Size']={'x':10,'y':8}").replace("'columns':[6,8,6]","'columns':[5,10,5]")
exec(compile(logic,'extend-width-five-native-configurations-and-migrate-four-large-grids','exec'))
assert center_config['Size']=={'x':10,'y':8}

data=env[T].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects}
assert set(check)==set(objs[T])
for pid,h in hashes[T].items():
 if pid not in changes[T]:assert sha(check[pid].get_raw_data())==h,('Unrelated object changed',pid)
for pid,expected in changes[T].items():assert check[pid].read_typetree()==expected,('Roundtrip mismatch',pid)
(OUT/T).write_bytes(data)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
previews=[]
for name,versions in cache_versions.items():
 path=cache_root/name
 if not path.exists():continue
 original=json.loads(path.read_text('utf8'));updated=migration.migrate_layout(original,version=versions['after'])
 assert migration.migrate_layout(updated,False,version=versions['before'],limits_from=original)['m_gridComponents']==original['m_gridComponents']
 previews.append({'file':name,'module_choices_preserved':[b['m_elementID'] for b in updated['m_gridComponents']],'columns':[5,10,5]})
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
for path,b in before.items():assert path.read_bytes()==b
for path,h in protected.items():assert sha(path.read_bytes())==h
for path in before:
 if path.name.startswith('catalog.'):protected[path]=sha(before[path])
report={'passed':True,'outer_grid_columns':[5,10,5],'outer_width_percent':[25,50,25],'layouts':layout_audits,'extended_native_size_configurations':descriptor_audits,'center_config_reuses_same_visual_asset':center_config,'custom_layout_migration_previews':previews,'migration_roundtrip_preserves_original_configuration':True,'global_visual_bundle_and_middle_45_55_split_untouched':True,'all_chart_data_styles_gap_and_separator_untouched':True,'unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{T:{str(pid):tree.get('m_Name','AssetBundle') for pid,tree in changes[T].items()}},'before_sha256':{str(path):sha(b) for path,b in before.items()},'after_sha256':{T:sha(data)},'protected_sha256':{str(path):h for path,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[T],'cache_root':str(cache_root),'cache_versions':cache_versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 script="$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed; see diagnostics above.' }\n"
 (OUT/name).write_text(script,'utf8')
watcher=(R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_text('utf8').replace("'G:/Doc/ChatGPT/New project/install-match-ui-patch.py'","(Join-Path $PSScriptRoot 'installer.py')")
(OUT/'install-after-game-exits.ps1').write_text(watcher,'utf8')
(OUT/'修改说明.md').write_text('''# Highlight 整体横向 5:10:5

四套桌面大屏执教/旁观、有无积分榜布局调整为5/10/5列，即25%/50%/25%。
各模块的纵向位置、内容、模板引用保持不变；为5列侧栏和10列中间模块增加对应原生配置。
安装时迁移最新本地比赛布局，只改横向坐标、宽度及版本，保留槽位当前选择的模块。
未改全局视觉模板资源，因此中间上下45%/55%、2px间隔、横线和全部图表设置保持原样。
通过网格无重叠、模块配置匹配、缓存迁移回迁、序列化回读及无关对象一致性校验。
退出游戏后运行install.ps1安装；restore.ps1恢复本次横向比例并保留当前模块选择。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'outer_columns':[5,10,5],'layouts':len(layout_audits),'custom_layouts_to_migrate':len(previews)},ensure_ascii=False))
