from pathlib import Path
import json
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-full-menu-data-charts75-').replace('NAMES=[W,G,M,F]','NAMES=[G,T]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
exec(compile(boot,'backup-current-resources','exec'))
d=Doc(G,name='MatchViewer_12x4');old=copy.deepcopy(d.d);oldr=refs(old)
root=d.named('HighlightFixedStatsOnlyView');charts=d.named('HighlightLowerNativeCharts');box=2465
group=d.add(d,1015,root,'HighlightDataComparisonSevenParts');d.move(group,root,0)
for node in [2431,d.named('HighlightMetadataStatsSeparator'),box]:d.move(node,group)
def weighted(node,weight):
 d.st(node,[(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131084,d.num(weight)),(131085,d.num(1)),(131105,d.pct(100))])
weighted(group,7);weighted(charts,5);weighted(box,1)
d.st(group,[(131083,d.enum('column')),(131073,d.enum('stretch'))])
for row in [3079,3089,3099,3320]:weighted(row,1)
for i,record in oldr.items():
 if 'm_Parent' not in record.get('data',{}):assert d.r[i]==record,('Existing data binding changed',i)
d.save()

# Restore the full original menu registry, not the previous two-page wrapper.
baseline=R/'highlight-lower-oop-eightstats-footer-20261028-115922/backup-game'/T
be=UnityPy.load(str(baseline));bo={o.path_id:o for o in be.objects}
menu_audits=[]
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 ob=find(T,name);tree=ob.read_typetree();base=next(o.read_typetree() for o in be.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 for key in ['m_gridElementDescriptions','m_tileGroups']:tree[key]=copy.deepcopy(base[key])
 assert all(r['m_PathID'] in objs[T] for r in tree['m_gridElementDescriptions'])
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
 menu_audits.append({'name':name,'original_module_count':len(base['m_gridElementDescriptions']),'all_original_modules_and_groups_exactly_restored':True})
CK='<Configurations>k__BackingField';targets={}
restored_stats_guid='1ab3b171f1e25f8085d658e92ce964a4'
meta=next(o.read_typetree() for o in objs[G].values() if o.type.name=='AssetBundle')
assert any(k==restored_stats_guid for k,e in meta['m_Container'])
for side in ['Home','Away']:
 ob=find(T,'PlayerStats'+side+'TeamTileDescription');tree=ob.read_typetree();cfg=next(c for c in tree[CK] if c['Size']=={'x':5,'y':4})
 cfg['AssetRef']['m_AssetGUID']=restored_stats_guid;cfg['Type']=0
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;targets[side]=(ob.path_id,copy.deepcopy(cfg))
versions={}
for name in ['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']:
 ob=find(T,name);tree=ob.read_typetree();before_version=tree['m_compositionVersion']
 for side in ['Home','Away']:
  oldid='Highlight'+side+'EightStatsAndOOP';newid='PlayerStats'+side+'Team';pid,cfg=targets[side]
  for a in tree['m_gridComponents']:
   if a['m_elementID'] in [oldid,newid]:a.update(m_elementID=newid,m_configDescriptions=[{'m_FileID':0,'m_PathID':pid}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(cfg)])
  for a in tree['m_placementBindings']:
   if a['m_elementID']==oldid:a['m_elementID']=newid
 tree['m_compositionVersion']+=1;versions[name]={'before':before_version,'after':tree['m_compositionVersion']}
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
# Native OOP configs and all upper formation templates must remain untouched.
for name in ['HomeTeamFormationOOPTileDescription','AwayTeamFormationOOPTileDescription']:
 ob=find(T,name);assert ob.path_id not in changes[T]
for pid in [-981025000002000,-981025000002100]:assert pid not in changes[G]

outputs={}
for bn in NAMES:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree
 for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/bn;dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name.startswith('catalog.'):protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for n in NAMES:
  p=folder/n;src=outputs[n];tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[p]),'after':sha(src.read_bytes())})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');caches=[]
for name,ver in versions.items():
 p=cache_root/name
 if not p.exists():continue
 raw=p.read_bytes();tree=json.loads(raw)
 for side in ['Home','Away']:
  oldid='Highlight'+side+'EightStatsAndOOP';newid='PlayerStats'+side+'Team'
  for a in tree['m_gridComponents']:
   if a['m_elementID'] in [oldid,newid]:a.update(m_elementID=newid,m_configDescriptions=[],m_configDescriptionKeys=[newid],m_gridElementConfigs=[])
  for a in tree.get('m_placementBindings',[]):
   if a['m_elementID']==oldid:a['m_elementID']=newid
 tree['m_compositionVersion']=ver['after'];dest=OUT/'cache-output'/name;dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8');backup=OUT/'backup-custom'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(raw)
 tx.append({'target':str(p),'source':str(dest),'backup':str(backup),'before':sha(raw),'after':sha(dest.read_bytes())});caches.append(name)
for p in cache_root.iterdir() if cache_root.exists() else []:
 if p.is_file() and p.name not in caches:protected[p]=sha(p.read_bytes())
report={'installed':False,'runtime_verified':False,'output':str(OUT),'data_comparison_to_three_charts_ratio':[7,5],'whole_middle_ratio_45_55_preserved':True,'original_menu_registry':menu_audits,'original_default_stats_ids_restored':True,'latest_eight_stats_fields_retained':True,'oop_rotation_assets_and_upper_templates_unchanged':True,'no_new_assets_or_texture_changes':True,'catalogs_unchanged':True,'serialization_roundtrip':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8').replace("Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve()}","Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve(),Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve()}")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('用户确认：只改截图中数据对比与下方三个图表的高度比7:5，不改整个中间45:55。将数据对比标题/分隔线/四行包入上方7份弹性组，三个图表5份，既有字体/数据/图示不变。下方两模块恢复原生主客队统计ID、原版完整模块目录、分类和子菜单，撤回无球快捷项提升及两项内部菜单；保留最新进球/助攻/关键传球/关键抢断八列表格。无球阵型仍使用已旋转的独立模板，主队顺时针90、客队逆时针90，上方阵型不变。原生目录逐项与添加快捷项前备份一致；仅恢复菜单字段，不覆盖整份旧资源。静态/序列化与无关对象检查通过，游戏内显示未验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'ratio':[7,5],'menu_counts':[x['original_module_count'] for x in menu_audits],'runtime_verified':False},ensure_ascii=False),flush=True)
