from pathlib import Path
import json,ast,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','home-away-stats-row21-font70-match-info-').replace('NAMES=[W,G,M,F]','NAMES=[G,F,T]')
exec(compile(boot,'backup-installed-resources','exec'))
env[W]=UnityPy.load(str(GAME/W));objs[W]={o.path_id:o for o in env[W].objects}
main=Doc(G,pid=-7710242645031577538);asset_clones=[];new_guids={}
source=(R/'build-highlight-five-column-native-player-lists.py').read_text('utf8');helper=ast.parse(source)
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc','allptr']],type_ignores=[]),'private-asset-helpers','exec'))
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
lookup={}
for bundle in [G,W]:
 meta=next(o for o in objs[bundle].values() if o.type.name=='AssetBundle').read_typetree()
 for key,entry in meta['m_Container']:
  obj=objs[bundle].get(entry['asset']['m_PathID'])
  if obj is None or obj.type.name!='MonoBehaviour':continue
  tree=obj.read_typetree()
  if 'm_VisualTree' in tree:lookup[key]=(bundle,obj.path_id)

old_refs=refs(copy.deepcopy(main.d));old_style=copy.deepcopy(main.s)
def data_before(i):return sd(old_refs,i)
resolver=(R/'reflow-highlight-comparison-four-by-four.py').read_text('utf8').split('# Resolve the existing desktop style metrics.')[1].split('\n',1)[1].split('f32=lambda value:')[0]
exec(compile(resolver,'resolve-native-table-font-metrics','exec'))
font_memo={};visiting=set();font_audits=[];font_docs={};next_pid=-981025000003000
def clone_font(guid):
 global old_refs,old_style,computed_cache,next_pid
 if guid in font_memo:return font_memo[guid]
 assert guid not in visiting,('Cyclic text template',guid)
 visiting.add(guid);bundle,pid=lookup[guid];donor=Doc(bundle,pid=pid)
 aliases={a['data']['m_TemplateAlias'] for a in donor.r.values() if a.get('data',{}).get('m_TemplateAlias')}
 nested={}
 for u in donor.d['m_Usings']:
  if u['alias'] in aliases:nested[u['alias']]=clone_font(u['path'])
 textnodes=[i for i,a in donor.r.items() if a.get('data',{}).get('m_FullTypeName') in ['SI.Bindable.SIText','UnityEngine.UIElements.Label','UnityEngine.UIElements.TextElement']]
 if not textnodes and all(v==next(u['path'] for u in donor.d['m_Usings'] if u['alias']==alias) for alias,v in nested.items()):
  visiting.remove(guid);font_memo[guid]=guid;return guid
 tile,newguid=clone_doc(donor,'HighlightStatsFont70_'+donor.d['m_Name']+'_'+guid[:6],next_pid);next_pid-=10
 original=copy.deepcopy(tile.d);br=refs(original)
 for u in tile.d['m_Usings']:
  if u['alias'] in nested:u['path']=nested[u['alias']]
 old_refs=refs(copy.deepcopy(donor.d));old_style=copy.deepcopy(donor.s);computed_cache={}
 for i in textnodes:
  metric=font_metric(i);assert len(metric)==1 and metric[0][0]==3 and metric[0][1]['unit']==1,(donor.d['m_Name'],i,metric)
  before_px=metric[0][1]['value'];after_px=f32(before_px*.7)
  tile.st(i,[(65537,tile.px(after_px))]);font_audits.append({'template':donor.d['m_Name'],'node':i,'before_px':before_px,'after_px':after_px})
 for rid,record in br.items():
  expected=copy.deepcopy(record)
  if rid in textnodes:expected['data']['m_RuleIndex']=tile.a(rid)['m_RuleIndex']
  assert tile.r[rid]==expected,('Table text binding/event/structure changed',donor.d['m_Name'],rid)
 tile.save();font_docs[newguid]=tile;font_memo[guid]=newguid;visiting.remove(guid);return newguid

factory_source=find(F,'MatchStatsTableFactory');factory_original=factory_source.read_typetree()
factory_obj,factory,factory_guid=register_clone(F,factory_source,'HighlightHomeAwayStatsRow21Font70Factory',-981025000003500,factory_original)
cell_roots=set()
for column in factory['m_rowData']:
 for key in ['m_uxmlRef','m_headerUxmlRef','m_footerUxmlRef']:
  guid=column[key]['m_AssetGUID']
  if not guid:continue
  newguid=clone_font(guid);column[key]['m_AssetGUID']=newguid
  if key=='m_uxmlRef':cell_roots.add(newguid)
for guid in cell_roots:
 tile=font_docs[guid];root=tile.a(tile.d['m_VisualTree']['rid'])['m_Children'][0]['rid']
 tile.st(root,[(131087,tile.pct(100)),(131096,tile.px(0)),(131094,tile.px(21))]);tile.save()
for old,new in zip(factory_original['m_rowData'],factory['m_rowData']):
 expected=copy.deepcopy(old)
 for key in ['m_uxmlRef','m_headerUxmlRef','m_footerUxmlRef']:expected[key]=copy.deepcopy(new[key])
 assert new==expected,('Column order/width/binding changed',old['m_id'])
factory_obj.save_typetree(factory);changes[F][factory_obj.path_id]=copy.deepcopy(factory)
native_tile=Doc(G,name='PlayerStats_4x6')
stats,stats_guid=clone_doc(native_tile,'HighlightHomeAwayStatsRow21Font70',-981025000003600)
stats_before=copy.deepcopy(stats.d);sr=refs(stats_before);table_serials=set()
for node in [1028,1032]:
 v=stats.data(node);assert v['FixedElementSize']==35
 v.update(FixedElementSize=21.,FixedElementSize_UxmlAttributeFlags=1,FixedElementSizeControllerOrTouch=21.,FixedElementSizeControllerOrTouch_UxmlAttributeFlags=1)
 v['FactoryAsset']['m_AssetGUID']=factory_guid
 v['HeaderCellAsset']['m_AssetGUID']=clone_font(v['HeaderCellAsset']['m_AssetGUID'])
 table_serials.add(stats.a(node)['m_SerializedData']['rid'])
for rid,record in sr.items():
 expected=copy.deepcopy(record)
 if rid in table_serials:
  for key in ['FixedElementSize','FixedElementSize_UxmlAttributeFlags','FixedElementSizeControllerOrTouch','FixedElementSizeControllerOrTouch_UxmlAttributeFlags','FactoryAsset','HeaderCellAsset']:expected['data'][key]=copy.deepcopy(stats.r[rid]['data'][key])
 assert stats.r[rid]==expected,('Stats view/event/data path changed',rid)
stats.save()

main_before=copy.deepcopy(main.d);mr=refs(main_before);allowed={main.named('HighlightRefereeHeaderItem'),main.named('HighlightRefereeText')}
ref=main.named('HighlightRefereeHeaderItem');reftext=main.named('HighlightRefereeText');host=main.named('HighlightWeatherRefereeHeader')
main.data(ref)['Binding']['m_direct']['Path']['m_path']='const.True'
main.data(ref).update(InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1)
main.st(ref,[(131105,main.px(0)),(131082,main.px(0)),(131097,main.px(0)),(131084,main.num(1)),(131085,main.num(1))])
main.st(reftext,[(131084,main.num(1)),(131085,main.num(1)),(131097,main.px(0))])
info=Doc(G,name='MatchdayInfo_4x4')
stadium=main.add(main,1015,host,'HighlightStadiumHeaderItem')
main.st(stadium,[(131083,main.enum('row')),(131073,main.enum('center')),(131105,main.px(0)),(131082,main.px(0)),(131097,main.px(0)),(131084,main.num(1)),(131085,main.num(1)),(131091,main.px(16))])
icon=main.add(info,1018,stadium,'HighlightStadiumIcon');main.a(icon)['m_Classes']=['game-concepts-stadium_medium'];main.size(icon,12,12);main.st(icon,[(131092,main.px(4))])
text=main.add(info,1045,stadium,'HighlightStadiumText');main.a(text)['m_Classes']=['global-text-secondary','content-no-wrap','content-ellipsis']
main.data(text).update(displayTooltipWhenElided=1,displayTooltipWhenElided_UxmlAttributeFlags=1)
main.st(text,[(65537,main.px(12)),(65546,main.enum('middle-left')),(65552,main.enum('nowrap')),(131097,main.px(0)),(131084,main.num(1)),(131085,main.num(1))])
for prop in [131090,131091,131092,131093,131098,131099,131100,131101]:main.st(text,[(prop,main.px(0))])
assert main.data(text)['TextBinding']==info.data(1045)['TextBinding']
for rid,record in mr.items():
 expected=copy.deepcopy(record)
 if rid in allowed:expected['data']['m_RuleIndex']=main.a(rid)['m_RuleIndex']
 if rid==host:expected['data']['m_Children']=main.a(rid)['m_Children']
 if rid==main.a(ref)['m_SerializedData']['rid']:
  expected['data']['Binding']['m_direct']['Path']['m_path']='const.True';expected['data'].update(InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1)
 assert main.r[rid]==expected,('Other match content/line-color changed',rid)
main.save()

CK='<Configurations>k__BackingField';ids=['PlayerStatsHomeTeam','PlayerStatsAwayTeam'];old_guid='6a4b032b28fee7b47941ca946d06eafb'
for name in ['PlayerStatsHomeTeamTileDescription','PlayerStatsAwayTeamTileDescription']:
 ob=find(T,name);tree=ob.read_typetree()
 for cfg in tree[CK]:assert cfg['AssetRef']['m_AssetGUID']==old_guid;cfg['AssetRef']['m_AssetGUID']=stats_guid
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague'];versions={}
for name in layout_names:
 ob=find(T,name);tree=ob.read_typetree();before_tree=copy.deepcopy(tree)
 for b in tree['m_gridComponents']:
  if b['m_elementID'] in ids:
   for cfg in b['m_gridElementConfigs']:
    assert cfg['AssetRef']['m_AssetGUID']==old_guid;cfg['AssetRef']['m_AssetGUID']=stats_guid
 tree['m_compositionVersion']+=1;versions[name]={'before':before_tree['m_compositionVersion'],'after':tree['m_compositionVersion']}
 ob.save_typetree(tree);changes[T][ob.path_id]=tree

meta_code=source.split('for bundle in NAMES:\n metaobj=',1)[1].split('spec=importlib.util',1)[0]
exec(compile('for bundle in [G,F]:\n metaobj='+meta_code,'register-private-fonts-and-factory','exec'))
catalog_code=source.split("spec=importlib.util.spec_from_file_location('five_column_catalog'",1)[1].split('outputs={}\n',1)[0]
exec(compile("spec=importlib.util.spec_from_file_location('five_column_catalog'"+catalog_code,'extend-catalog-preserving-originals','exec'))
outputs={}
for bundle in NAMES:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 for doc in [doc for doc in documents if doc.n==bundle]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 outputs[bundle]=data;(OUT/bundle).write_bytes(data)
outputs['catalog.bin']=catalog;outputs['catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
(OUT/'catalog.bin').write_bytes(catalog);(OUT/'catalog.hash').write_bytes(outputs['catalog.hash'])
migration_code='''import copy
OLD=__OLD__;NEW=__NEW__
def migrate_layout(document,forward=True,version=None,**kwargs):
 result=copy.deepcopy(document);old,new=(OLD,NEW) if forward else (NEW,OLD)
 for block in result['m_gridComponents']:
  if block['m_elementID'] not in ['PlayerStatsHomeTeam','PlayerStatsAwayTeam']:continue
  for cfg in block['m_gridElementConfigs']:
   if cfg['AssetRef']['m_AssetGUID']==old:cfg['AssetRef']['m_AssetGUID']=new
 if version is not None:result['m_compositionVersion']=version
 return result
'''.replace('__OLD__',repr(old_guid)).replace('__NEW__',repr(stats_guid))
migration=types.ModuleType('compact_stats_migration');exec(compile(migration_code,'grid_migration.py','exec'),migration.__dict__)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,version in versions.items():
 p=cache_root/name
 if not p.exists():continue
 original=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(original,version=version['after']);restored=migration.migrate_layout(updated,False,version=original['m_compositionVersion']);assert restored==original
 previews.append(name)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'row_height_before_px':35,'row_height_after_px':21,'table_font_scale':.7,'font_audits':font_audits,'private_font_template_count':len(font_docs),'five_columns_native_order_widths_sorting_formats_events_preserved':True,'only_home_and_away_descriptors_changed':True,'human_and_opposition_stats_options_unchanged':True,'referee_header_visibility':'const.True, no config gate','referee_name_path':'match.MatchReferee.Name','stadium_path':'match.Stadium.Name','metadata_font_px':12,'metadata_color_class':'global-text-secondary','no_new_inline_var_functions':True,'crash_hotfix_line_colors_preserved':True,'cache_previews':previews,'serialization_roundtrip':True,'unrelated_objects_and_catalog_locations_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8');(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8').replace('path=folder/name;assert path.parent.resolve()==folder',"path=(folder.parent/name if folder==game and name.startswith('catalog.') else folder/name);assert path.parent.resolve() in [folder,game.parent]")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('按用户确认：仅主队统计/客队统计使用私有PlayerStats_4x6、私有原生五列工厂及私有字号模板，球员行高35→21px，每种原有文字字号按0.7换算为实际px。保留列顺序/宽度、姓名、所有数据绑定/数值格式/排序/导航/标题点击事件；模块标题与其他两种统计选项原样保留。修改两项描述及默认网格配置指向私有模板，缓存仅迁移对应资产引用和版本，不改位置大小或所选项。主裁判区域取消config.HasMatchOfficialsInfo门控，保留match.MatchReferee.Name原生绑定；加入match.Stadium.Name球场信息，12px暗白色，放在温度、裁判之后，长名称省略并可悬停查看。横竖分隔线保持崩溃修复后的具体Color值，不新增行内var。完成序列化回读、绑定/事件/字段比对与无关对象/目录一致性；未进行游戏内渲染与实时刷新验证。restore.ps1回退本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'row_height_px':21,'font_scale':.7,'private_font_templates':len(font_docs),'font_metrics':len(font_audits),'stadium_added':True,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
