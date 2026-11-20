from pathlib import Path
import copy,json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','official-formation-lower-carousel-'),'backup-load','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 donor=Doc(G,name='TeamFormationIPOOPPlayerStatsCarousel_4x8')
 for side in ['Home','Away']:
  current=Doc(G,name='HighlightLower'+side+'SixPageCarousel')
  pages=copy.deepcopy(current.d['m_Usings'])
  tree=copy.deepcopy(donor.d);style=copy.deepcopy(donor.s)
  tree['m_Name']=current.d['m_Name'];tree['inlineSheet']=copy.deepcopy(current.d['inlineSheet'])
  tree['m_Usings']=pages
  d=Doc(G,pid=current.obj.path_id,tree=tree,style=style)
  # Keep the native BindingExpect -> BindableCarouselTileRoot hierarchy.
  # Remove only the native page instances and replace with the requested six.
  remove=[]
  for c in list(d.a(1002)['m_Children']):
   i=c['rid'];remove.extend([i,d.a(i)['m_SerializedData']['rid']])
  d.d['references']['RefIds']=[r for r in d.d['references']['RefIds'] if r['rid'] not in remove]
  for i in remove:del d.r[i]
  d.a(1002)['m_Children']=[]
  for page in pages:
   i=d.add(donor,1006,1002,'')
   d.a(i)['m_TemplateAlias']=page['alias'];d.data(i)['templateId']=page['alias']
   d.a(i)['m_Classes']=copy.deepcopy(donor.a(1006)['m_Classes'])
   for key in ['m_AttributeOverrides','m_SerializedDataOverride','m_SlotUsages']:d.a(i)[key]=[]
  # Native session persistence, independent for the two sides.
  d.data(1002)['SharedPersistenceID']='TF27.Highlight.Lower.'+side+'.SixPages.v1'
  d.data(1002)['SharedPersistenceID_UxmlAttributeFlags']=1
  assert len(d.a(1002)['m_Children'])==6
  assert not any('CurrentMatchBindings' in str(r.get('data',{})) for r in d.r.values())
  assert d.data(1001)==donor.data(1001)
  d.save()
  audits.append({'variant':tag,'side':side,'source':donor.d['m_Name'],'native_expect_unchanged':True,'native_carousel_hierarchy_and_styles':True,'forced_team_and_main_screen_remapper_removed':True,'pages':[p['alias'] for p in pages],'stats_table_not_modified':True})
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'修改说明.md').write_text('左右下方容器基于当前游戏 TeamFormationIPOOPPlayerStatsCarousel_4x8 完整结构及样式重建。移除自定义强制 team/ishometeam/isonmainscreen 重映射，沿用外层网格提供的数据。仅替换六页引用并保留左右独立原生会话记忆。统计表与体能字段不改；本补丁不能视为体能显示已通过游戏内验证。\n','utf8')
