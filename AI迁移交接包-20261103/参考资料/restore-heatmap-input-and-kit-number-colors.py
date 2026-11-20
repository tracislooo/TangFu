from pathlib import Path
import copy,json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','heatmap-input-kit-number-colors-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 oldenv=UnityPy.load(str(R/'highlight-team-heatmaps-20261101-033959'/('backup-'+tag)/bases[1]))
 old=next(o.read_typetree() for o in oldenv.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MatchViewer_12x4');oldrefs=refs(old)
 d=Doc(G,name='MatchViewer_12x4')
 for i in [2164,2300]:
  original=next(f for f in oldrefs[i]['data']['BindFunction'] if b'HeatMapHomeTeamDefaultPlayer' in bytes(f.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])))
  current=d.r[i]['data']['BindFunction'];matches=[j for j,f in enumerate(current) if len(unpack(f.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])))==6 and b'const.NullRef' in bytes(f['m_inputs']['m_variable']['m_argumentBytes'])]
  assert len(matches)==1;current[matches[0]]=copy.deepcopy(original)
 d.save()
 donor=Doc(W,name='PlayerKitShoutNameCell')
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);number=d.named('MatchCardShirtNumber');parent=d.a(number)['m_Parent']['rid']
  holder=d.add(donor,1015,parent,'MatchCardNumberKitColourBinding')
  v=d.data(holder);v['PrimaryColorDataLink']['m_path']='team.KitForMatch.BackgroundColour';v['SecondaryColorDataLink']['m_path']='team.KitForMatch.TextColour'
  v['PrimaryColorDataLink_UxmlAttributeFlags']=1;v['SecondaryColorDataLink_UxmlAttributeFlags']=1
  v['BindFunction']['m_target']['m_guid']='';v['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=[];v['BindFunction_UxmlAttributeFlags']=1
  d.st(holder,[(131102,d.enum('absolute')),(131103,d.px(-8)),(131104,d.px(34)),(131105,d.px(30)),(131087,d.px(16))])
  d.move(number,holder);d.a(number)['m_Classes']=['fm-club-primary-color','fm-club-secondary-color']
  props=d.s['m_Rules'][d.a(number)['m_RuleIndex']]['m_Properties'];d.st(number,[(131102,d.enum('relative')),(131103,{'m_ValueType':1,'valueIndex':2}),(131104,{'m_ValueType':1,'valueIndex':2})])
  # Remove the inline gold/black values so the native style setter supplies both colors.
  props=d.s['m_Rules'][d.a(number)['m_RuleIndex']]['m_Properties'];props[:]=[p for p in props if p['m_Id'] not in [458752,65536]]
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'heatmap_invalid_null_filter_reverted':True,'team_heatmap_aggregation_verified':False,'number_background':'team.KitForMatch.BackgroundColour','number_text':'team.KitForMatch.TextColour'})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())

