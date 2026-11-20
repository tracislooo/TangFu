from pathlib import Path
import json,copy
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','commentary-fixed960-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];d=Doc(M,name='MatchCommentaryBar');old=copy.deepcopy(d.d)
 for i in [1001,1004]:
  d.st(i,[(131105,d.px(960)),(131097,d.px(960)),(131095,d.px(960)),(131084,d.num(0)),(131085,d.num(0)),(131074,d.enum('center'))])
 for i,r in refs(old).items():
  if i not in [1001,1004]:assert d.r[i]==r
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'width_ui_units':960,'min_width':960,'max_width':960,'flex_shrink':0,'text_and_binding_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('MatchCommentaryBar 根节点及可见容器宽度、最小/最大宽度固定960界面单位，flex-grow与flex-shrink为0，水平居中。文字、颜色、高度及数据绑定保持现状。仅去除随父容器变化的50%宽度；游戏自身UI缩放仍适用。文件检查通过，点球阶段实际显示未游戏内验证。','utf8')
