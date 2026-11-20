from pathlib import Path
import json,copy
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','highlight-team-heatmaps-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];d=Doc(G,name='MatchViewer_12x4');counts=[]
 for setter in [2164,2300]:
  data=d.r[setter]['data'];changed=0
  for f in data['BindFunction']:
   raw=f.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
   if b'HeatMapHomeTeamDefaultPlayer' not in bytes(raw):continue
   args=unpack(raw);assert len(args)==6
   for index in [0,1]:
    head=args[index][:args[index][0]+2];path=b'const.NullRef';args[index]=head+bytes([len(path)])+path
   f['m_inputs']['m_variable']['m_argumentBytes']=pack(args);changed+=1
  assert changed==1
  assert next(v for v in data['ReferenceVariables'] if v['m_name']=='person')['m_initToNull']==1
  counts.append(changed)
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'default_player_filter_removed':counts,'home_away_heatmap_sources_unchanged':True,'person_filter':'const.NullRef','pitch_orientation_and_layout_unchanged':True,'runtime_verified':False})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅修改MatchViewer_12x4两个热点图的球员筛选赋值：默认球员改为const.NullRef。球队HomeHeatMap/AwayHeatMap数据源、SubjectTeamPlayerData原生绘图接口、主客方向及样式不变。预期无球员筛选时显示全队汇总；此行为尚未游戏内验证，不能将文件检查当作球队汇总已验证。','utf8')
