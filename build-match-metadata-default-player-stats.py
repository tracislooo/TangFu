from pathlib import Path
import json,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','match-metadata-default-player-stats-').replace('NAMES=[W,G,M,F]','NAMES=[G,T]')
exec(compile(boot,'backup-current-resources','exec'))
d=Doc(G,pid=-7710242645031577538);old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
info=Doc(G,name='MatchdayInfo_4x4');info_before=copy.deepcopy(info.d)
allowed=set()
def style(i,props):d.st(i,props);allowed.add(i)
def space(i):style(i,[(p,d.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
def plain(parent,name):return d.add(d,1015,parent,name)
fontprop=next(p for p in d.s['m_Rules'][d.a(3328)['m_RuleIndex']]['m_Properties'] if p['m_Id']==65537)
font=d.s['dimensions'][fontprop['m_Values'][0]['valueIndex']]['value'];assert font==12
style(2431,[(131102,d.enum('relative'))])
host=plain(2431,'HighlightWeatherRefereeHeader')
style(host,[(131102,d.enum('absolute')),(131089,d.pct(25)),(131105,d.pct(50)),(131104,d.px(0)),(131080,d.px(6)),(131097,d.px(0)),(131096,d.px(0)),(131083,d.enum('row')),(131073,d.enum('center')),(131088,d.enum('center'))]);space(host)
weather=plain(host,'HighlightWeatherHeaderItem')
style(weather,[(131083,d.enum('row')),(131073,d.enum('center')),(131084,d.num(0)),(131085,d.num(0))]);space(weather)
referee=d.add(info,1014,host,'HighlightRefereeHeaderItem');d.a(referee)['m_Classes']=[]
style(referee,[(131083,d.enum('row')),(131073,d.enum('center')),(131097,d.px(0)),(131084,d.num(0)),(131085,d.num(1))]);space(referee);style(referee,[(131091,d.px(16))])
new_texts=[]
for parent,icon_source,text_source,name in [(weather,1022,1047,'Temperature'),(referee,1038,1060,'Referee')]:
 icon=d.add(info,icon_source,parent,'Highlight'+name+'Icon');d.a(icon)['m_Classes']=[c for c in info.a(icon_source)['m_Classes'] if c.startswith('game-concepts-')]
 d.size(icon,font,font);style(icon,[(131092,d.px(4))])
 text=d.add(info,text_source,parent,'Highlight'+name+'Text');d.a(text)['m_Classes']=['global-text-secondary','content-no-wrap','content-ellipsis']
 d.data(text).update(displayTooltipWhenElided=1,displayTooltipWhenElided_UxmlAttributeFlags=1)
 style(text,[(65537,d.px(font)),(65546,d.enum('middle-left')),(65552,d.enum('nowrap')),(131097,d.px(0)),(131085,d.num(1))]);space(text)
 assert d.data(text)['TextBinding']==info.data(text_source)['TextBinding'];new_texts.append(text)
assert d.data(referee)['Binding']==info.data(1014)['Binding']

# Explicitly use the same native theme color on every border orientation.
colorvar='--layout-modules-block-border-colour'
handles=[{'m_ValueType':10,'valueIndex':1},d.num(1),d.val(8,colorvar)]
line=plain(2429,'HighlightMetadataStatsSeparator')
d.move(line,2429,1);d.a(line)['m_Classes']=copy.deepcopy(d.a(3430)['m_Classes'])
style(line,[(131105,d.pct(100)),(131087,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131076,d.px(0)),(131077,d.px(0)),(131078,d.px(0)),(131079,d.px(1))]);space(line);style(line,[(131090,d.px(2))])
for node in [line,3430,3432,3434,3436,3438,3440]:
 style(node,[(prop,copy.deepcopy(handles)) for prop in [458758,458761,458762,458763]])
for rid,record in oldr.items():
 expected=copy.deepcopy(record)
 if rid in allowed:expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
 if rid in [2431,2429]:expected['data']['m_Children']=d.a(rid)['m_Children']
 assert d.r[rid]==expected,('Unrelated field/binding changed',rid)
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
assert info.d==info_before
d.save()

CK='<Configurations>k__BackingField';targets={};descriptor_audits=[]
for x,name in [(0,'PlayerStatsHomeTeamTileDescription'),(15,'PlayerStatsAwayTeamTileDescription')]:
 ob=find(T,name);tree=ob.read_typetree();cfg=next(c for c in tree[CK] if c['Size']=={'x':5,'y':4})
 targets[x]={'id':tree['<ID>k__BackingField'],'pid':ob.path_id,'config':copy.deepcopy(cfg)}
 descriptor_audits.append({'x':x,'selected':targets[x]['id'],'size':cfg['Size']})
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
versions={};layout_audits=[]
for name in layout_names:
 ob=find(T,name);tree=ob.read_typetree();original=copy.deepcopy(tree);version=tree['m_compositionVersion']+1
 for b in tree['m_gridComponents']:
  q=b['m_location']
  if q['y']!=4 or q['x'] not in targets:continue
  target=targets[q['x']];b['m_elementID']=target['id'];b['m_configDescriptions']=[{'m_FileID':0,'m_PathID':target['pid']}];b['m_configDescriptionKeys']=[];b['m_gridElementConfigs']=[copy.deepcopy(target['config'])]
 for target in targets.values():
  if not any(p['m_elementID']==target['id'] for p in tree['m_placementBindings']):tree['m_placementBindings'].append({'m_elementID':target['id'],'m_optionalConditions':[],'m_optionalConfigConditions':[]})
 tree['m_compositionVersion']=version
 for oldb,newb in zip(original['m_gridComponents'],tree['m_gridComponents']):
  assert oldb['m_location']==newb['m_location']
  if oldb['m_location']['y']!=4:assert oldb==newb
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;versions[name]={'before':original['m_compositionVersion'],'after':version}
 layout_audits.append({'name':name,'defaults':{str(b['m_location']['x']):b['m_elementID'] for b in tree['m_gridComponents'] if b['m_location']['y']==4}})

migration_code='''import copy
TARGETS={0:'PlayerStatsHomeTeam',15:'PlayerStatsAwayTeam'}
FIELDS=['m_elementID','m_configDescriptions','m_configDescriptionKeys','m_gridElementConfigs']
def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document)
 for block in result['m_gridComponents']:
  q=block['m_location']
  if q['y']!=4 or q['x'] not in TARGETS:continue
  assert q['width']==5 and q['height']==4
  if forward:
   block['m_elementID']=TARGETS[q['x']]
   block['m_configDescriptions']=[];block['m_configDescriptionKeys']=[TARGETS[q['x']]];block['m_gridElementConfigs']=[]
  else:
   assert limits_from is not None,'Original saved choices are required for restore'
   old=next(b for b in limits_from['m_gridComponents'] if b['m_location']==q)
   for field in FIELDS:block[field]=copy.deepcopy(old[field])
 if version is not None:result['m_compositionVersion']=version
 return result
'''
migration=types.ModuleType('default_stats_migration');exec(compile(migration_code,'grid_migration.py','exec'),migration.__dict__)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,version in versions.items():
 p=cache_root/name
 if not p.exists():continue
 original=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(original,version=version['after']);restored=migration.migrate_layout(updated,False,version=original['m_compositionVersion'],limits_from=original)
 assert restored==original
 previews.append({'name':name,'defaults':{str(b['m_location']['x']):b['m_elementID'] for b in updated['m_gridComponents'] if b['m_location']['y']==4}})
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
outputs={}
for bundle in NAMES:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 for doc in [doc for doc in documents if doc.n==bundle]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 outputs[bundle]=data;(OUT/bundle).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'metadata_position':'between team names in fixed stats header','fields':{'temperature':'match.Weather.WeatherDescriptionString','referee':'match.MatchReferee.Name'},'font_px_matches_team_names':font,'text_color_class':'global-text-secondary','weather_wind_and_referee_nationality_not_added':True,'native_referee_visibility_preserved':True,'new_separator':line,'separator_border_px':1,'all_comparison_line_color_variable':colorvar,'vertical_line_nodes':[3436,3438,3440],'defaults':descriptor_audits,'layouts':layout_audits,'cache_previews':previews,'all_data_bindings_and_existing_widgets_unchanged':True,'selector_switching_preserved':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8');(OUT/'grid_migration.py').write_text(migration_code,'utf8')
(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('在MatchViewer_12x4下方数据区队名标题行中间，横排温度与主裁判姓名，复制MatchdayInfo_4x4原生绑定与图标；字号与队名一致12px，暗白色沿用global-text-secondary，裁判保留原生信息可见性；不添加风力/国籍，不改共用比赛日信息页。标题行下新增1px横线；数据区全部横线和三条竖线显式使用相同原生主题边框颜色变量。四套大屏布局默认左下PlayerStatsHomeTeam、右下PlayerStatsAwayTeam，保持选择器可切换、所有位置尺寸和两侧上方阵型不变；同步对应缓存，仅改变两个下方槽位选择与解析键，不清空其他缓存，避免旧AssetRef覆盖新选择。备份、序列化回读、缓存迁移往返和无关对象一致性检查通过，未进行游戏内渲染验证。restore.ps1恢复本次修改与原槽位选择。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'metadata_font_px':font,'lower_defaults':['PlayerStatsHomeTeam','PlayerStatsAwayTeam'],'cache_previews':len(previews),'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
