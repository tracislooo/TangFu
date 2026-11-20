from pathlib import Path
import json,re,types
R=Path(__file__).parent
previous=(R/'build-highlight-lower-oop-eightstats-footer.py').read_text('utf8')
prefix=previous.split('# Native eight-field data')[0].replace('highlight-lower-oop-eightstats-footer-','repair-highlight-native-stats-menu-cards-')
exec(compile(prefix,'backup-current-not-old-packages','exec'))
prior=json.loads((R/'highlight-lower-oop-eightstats-footer-20261028-115922/manifest.json').read_text('utf8'))
factory_guid=next(x['guid'] for x in prior['new_assets'] if x['name']=='HighlightEightFieldsFactory')
view_guid=next(x['guid'] for x in prior['new_assets'] if x['name']=='HighlightEightFieldsView')
stats,stats_guid=clone_doc(Doc(G,pid=-981025000003600),'HighlightRestoredNativeEightStats',-981028000006000)
for node in [1028,1032]:
 v=stats.data(node);v['FactoryAsset']['m_AssetGUID']=factory_guid
 raw=bytes(v['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert b'c08126334cf0c614a85c220cf1a73090' in raw
 v['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(raw.replace(b'c08126334cf0c614a85c220cf1a73090',view_guid.encode()))
 v.update(FixedElementSize=24.,FixedElementSize_UxmlAttributeFlags=1,FixedElementSizeControllerOrTouch=24.,FixedElementSizeControllerOrTouch_UxmlAttributeFlags=1,ScrollViewMode=2,ScrollViewMode_UxmlAttributeFlags=1)
mapper_node=next(i for i,a in stats.r.items() if a.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRemapper')
mapping=stats.data(mapper_node)['Mappings']
for path,t in [('tactic',2003981124),('inpossession',0)]:
 if not any(x['from']==path for x in mapping):mapping.append({'m_serialisedType':0,'from':path,'to':{'m_path':'match.Tactic' if path=='tactic' else 'const.True'},'type':{'id':t}})
stats.save()
CK='<Configurations>k__BackingField';oop_pids={};oop_guids={}
native_bn,native_pid=resolve('dd14815c08cb7834590fb5317e2bf64a')
for side,flip in [('Home',1),('Away',0)]:
 doc,guid=clone_doc(Doc(native_bn,pid=native_pid),'HighlightNative'+side+'OOPHorizontal',-981028000006100-(0 if side=='Home' else 10))
 upper=Doc(G,pid=-981025000002000 if side=='Home' else -981025000002100)
 for panel,source_panel in [(1019,1064),(1024,1065)]:
  v=doc.data(panel);v.update(Orientation=1,Orientation_UxmlAttributeFlags=1,FlipPositions=flip,FlipPositions_UxmlAttributeFlags=1)
  v['PositionTemplateAsset']=copy.deepcopy(upper.data(source_panel)['PositionTemplateAsset'])
  node=panel
  while node in doc.r and node!=doc.d['m_VisualTree']['rid']:
   doc.st(node,[(131105,doc.pct(100)),(131095,doc.pct(100)),(131097,doc.px(0))]);node=doc.a(node)['m_Parent']['rid']
 doc.save();oop_guids[side]=guid
 ob=find(T,side+'TeamFormationOOPTileDescription');tree=ob.read_typetree();oop_pids[side]=ob.path_id
 cfg=next(c for c in tree[CK] if c['Size']=={'x':5,'y':4});cfg['AssetRef']['m_AssetGUID']=guid
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
for side in ['Home','Away']:
 ob=find(T,'Highlight'+side+'EightStatsAndOOP');tree=ob.read_typetree()
 for cfg in tree[CK]:cfg['AssetRef']['m_AssetGUID']=stats_guid;cfg['Type']=0
 ob.save_typetree(tree);changes[T][ob.path_id]=tree

# Restore native menu structure. OOP entries are promoted out of the formation submenu.
menu_audits=[]
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 ob=find(T,name);tree=ob.read_typetree();old=copy.deepcopy(tree)
 for group in tree['m_tileGroups']:group['m_tiles']=[r for r in group['m_tiles'] if r['m_PathID'] not in oop_pids.values()]
 ids=tree['m_gridElementDescriptions'];remaining=[x for x in ids if x['m_PathID'] not in oop_pids.values()];out=[]
 for ref in remaining:
  out.append(ref)
  for side in ['Home','Away']:
   if objs[T][ref['m_PathID']].peek_name()=='Highlight'+side+'EightStatsAndOOP':out.append({'m_FileID':0,'m_PathID':oop_pids[side]})
 assert {r['m_PathID'] for r in out}=={r['m_PathID'] for r in ids};tree['m_gridElementDescriptions']=out
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
 menu_audits.append({'name':name,'all_original_modules_retained':True,'oop_promoted_to_root':True,'each_oop_after_corresponding_stats':True})
versions={}
for name in ['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']:
 ob=find(T,name);tree=ob.read_typetree();old=copy.deepcopy(tree)
 for side in ['Home','Away']:
  for a in tree['m_gridComponents']:
   if a['m_elementID']=='Highlight'+side+'EightStatsAndOOP':
    a['m_gridElementConfigs'][0]['AssetRef']['m_AssetGUID']=stats_guid;a['m_gridElementConfigs'][0]['Type']=0
    a['m_configDescriptions']=[a['m_configDescriptions'][0],{'m_FileID':0,'m_PathID':oop_pids[side]}]
 tree['m_compositionVersion']+=1;versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
 ob.save_typetree(tree);changes[T][ob.path_id]=tree

# Use native person-reference translation rather than repeatedly reading Name strings.
footer_source=Doc(W,name='SquadOverviewPlayerBlock');native_role=footer_source.data(footer_source.named('MatchCardRoleAndDutyText'))['TextBinding']
person_name=copy.deepcopy(native_role)
rewrite_binding(person_name,'[%tactical_role#1]','[%person#1]');rewrite_binding(person_name,'tactical_role','person');rewrite_binding(person_name,'roledata','match.MatchReferee')
ref=main.named('HighlightRefereeText');main.data(ref)['TextBinding']=person_name;main.data(ref)['TextBinding_UxmlAttributeFlags']=1
main.save()

card_audits=[]
for name,frame,picture_size in [('SquadOverviewPlayerBlock',1063,52),('SquadOverviewPlayerBlockSmall',1061,44)]:
 doc=Doc(W,name=name)
 for i,h in [(1021,82),(1028,56),(1029,26),(1022,28),(1032,28)]:
  doc.st(i,[(131087,doc.px(h)),(131096,doc.px(h)),(131094,doc.px(h)),(131084,doc.num(0)),(131085,doc.num(0))])
 doc.st(1021,[(131098,doc.px(0))]);doc.st(1022,[(131093,doc.px(0)),(131098,doc.px(0))])
 doc.size(frame,picture_size,picture_size)
 for i,a in list(doc.r.items()):
  if 'm_Parent' not in a.get('data',{}):continue
  label=doc.data(i).get('name','')
  if label=='MatchPlayerPortraitBinding':doc.size(i,picture_size,picture_size)
  if label.startswith('MatchCondition'):
   if '_Ring' in label or label.endswith('MissingRing'):doc.size(i,18,18)
   elif '_Number' in label or label.endswith('MissingNumber'):
    doc.st(i,[(65537,doc.px(9)),(131087,doc.px(10)),(131096,doc.px(10)),(131094,doc.px(10))])
   elif '_Percent' in label or label.endswith('_Missing'):doc.size(i,22,28)
  if a['data'].get('m_FullTypeName')=='SI.Bindable.SIText' and doc.data(i).get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path')=='person.ShirtName':doc.st(i,[(65537,doc.px(13))])
 root=doc.a(1032)['m_Children'][0]['rid'];doc.st(root,[(131087,doc.px(28)),(131096,doc.px(28)),(131094,doc.px(28))])
 doc.save();card_audits.append({'name':name,'status_height':28,'portrait_name_area':82,'portrait_px':picture_size,'footer_ring_px':18,'name_font_px':13})

# Reuse verified preload, catalog, and independent serialization routines.
reg=previous.split('# Update preload spans including dependencies of new private objects.')[1].split('# Save independent packages, verify every untouched original object, and preserve all image bundles.')[0]
exec(compile(reg,'register-new-native-templates','exec'))
save=previous.split('# Save independent packages, verify every untouched original object, and preserve all image bundles.')[1].split('migration_code=')[0]
# This repair changes no upper template; native fixed OOP copies are separate objects.
exec(compile(save,'roundtrip-check-all-other-objects','exec'))
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for n in NAMES:
  src=outputs[VS if n==V and tag=='skin' else n];p=folder/n;tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[p]),'after':sha(src.read_bytes())})
 for n,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  src=OUT/n;src.write_bytes(data);p=(folder.parent if tag=='game' else folder)/n;tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[p]),'after':sha(data)})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');caches=[]
for name,ver in versions.items():
 p=cache_root/name
 if not p.exists():continue
 original=p.read_bytes();tree=json.loads(original)
 for a in tree['m_gridComponents']:
  if a['m_elementID'] in ['HighlightHomeEightStatsAndOOP','HighlightAwayEightStatsAndOOP']:
   a['m_configDescriptions']=[];a['m_configDescriptionKeys']=[a['m_elementID']];a['m_gridElementConfigs']=[]
 tree['m_compositionVersion']=ver['after'];dest=OUT/'cache-output'/name;dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8');backup=OUT/'backup-custom'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(original)
 tx.append({'target':str(p),'source':str(dest),'backup':str(backup),'before':sha(original),'after':sha(dest.read_bytes())});caches.append(name)
for p in cache_root.iterdir() if cache_root.exists() else []:
 if p.is_file() and p.name not in caches:protected[p]=sha(p.read_bytes())
report={'installed':False,'runtime_verified':False,'output':str(OUT),'statistics_container':'native PlayerStats_4x6 copied from working version, no adaptive StreamedTable wrapper','menu':menu_audits,'native_oop_directions':{'Home':'clockwise90 / goalkeeper left','Away':'counterclockwise90 / goalkeeper right'},'cards':card_audits,'referee_mode':'native person-reference formatted translation, match.MatchReferee','new_assets':asset_clones,'checks':checks,'cache_migrations':caches,'protected_sha256':{str(p):h for p,h in protected.items()},'serialization_roundtrip':True,'no_texture_changes':True,'native_menu_actual_order_requires_runtime_verification':True}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8').replace("Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve()}","Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve(),Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve()}")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('修复上版：下方从自带两项菜单的自适应阵型包装器恢复为此前可显示的原生PlayerStats_4x6容器，保留新八列表格工厂和视图、24px行高，恢复完整原生模块菜单。将主/客队无球阵型从阵型子菜单提升到顶层，并配置在各自统计项后，原菜单其余模块全部保留；上下两个位置仍保留OOP入口。使用原生固定无球阵型模板的独立副本，主队顺时针90度、客队逆时针90度，原生无球绑定及头像文字正立。球员卡片体能评分区域28px，头像+姓名区域82px，头像52px/44px、名字13px，底部圆环18px加百分比10px以匹配28px区域。裁判采用人物引用格式化姓名，不再直接读取Name字符串。静态回读和对象一致性通过；统计实际显示、原生菜单最终排序及裁判姓名都需游戏内验证，不宣称已通过运行验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'native_statistics_restored':True,'native_menu_restored':True,'runtime_verified':False},ensure_ascii=False),flush=True)
