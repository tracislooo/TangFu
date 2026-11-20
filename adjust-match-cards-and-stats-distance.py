from pathlib import Path
import copy,json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','match-cards-distance-pass-stats-')
prefix=prefix.replace(".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]')", ".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,\"ui-tableviews_assets_all.bundle\"]')")
exec(compile(prefix,'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];V='ui-tableviews_assets_all.bundle'+suffix
 native=find(F,'PlayerStatsExtendedFactory').read_typetree()
 replacements={old:copy.deepcopy(next(c for c in native['m_rowData'] if c['m_id']==new)) for old,new in [('condition','run'),('sharpness','pass%')]}
 for ob in objs[F].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsFactory':continue
  t=ob.read_typetree()
  for i,c in enumerate(t['m_rowData']):
   if c['m_id'] in replacements:
    new=copy.deepcopy(replacements[c['m_id']]);new.update(m_defaultWidth=50.,m_minimumWidth=35.,m_allowWidthAutoResizing=1);t['m_rowData'][i]=new
  ob.save_typetree(t);changes[F][ob.path_id]=t
 for ob in objs[V].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsView':continue
  t=ob.read_typetree()
  for c in t['m_tableView']['m_tableConfig']:
   if c['m_columnID'] in replacements:
    c['m_columnID']=replacements[c['m_columnID']]['m_id'];c['m_columnMetadata'].update(m_widthOverride=50.,m_minWidthOverride=35.)
  ob.save_typetree(t);changes[V][ob.path_id]=t
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);yellow=d.named('YellowCardVisible');cards=d.a(yellow)['m_Parent']['rid']
  d.move(cards,1043)
  d.st(cards,[(131102,d.enum('absolute')),(131089,{'m_ValueType':1,'valueIndex':2}),(131103,d.pct(50)),(131092,d.px(34)),(131104,d.px(10)),(131105,d.px(12)),(131087,d.px(18))]);d.save()
 for name,nodes in [('HighlightLowerHomeSixPageCarousel',[1001,1002]),('HighlightLowerAwaySixPageCarousel',[1001,1002]),('HighlightRestoredNativeEightStats',[1001,1002,1004,1006,1028,1032])]:
  d=Doc(G,name=name)
  for i in nodes:d.st(i,[(131105,d.pct(100)),(131095,{'m_ValueType':1,'valueIndex':3}),(131097,d.px(0)),(131074,d.enum('stretch'))])
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'native_columns':['run','pass%'],'booking_icons':'avatar left','lower_panel_width':'100% no max width','runtime_verified':False})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
