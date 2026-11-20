from pathlib import Path
import copy,json,ast,struct
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','match-card-flag-number-'),'backup-current','exec'))
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'clone-native-flag','exec'))
clone_audits=[]
def rgba(r,g,b):return {k:struct.unpack('<f',struct.pack('<f',v))[0] for k,v in zip(['r','g','b','a'],[r/255,g/255,b/255,1.])}
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];flag=Doc(G,name='NationFlag_Small');image=flag.named('NationFlag')
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);hero=1028
  node,mapping=clone_native(flag,image,hero)
  for i in mapping.values():rewrite_binding(d.r[i],'Nation.','person.Nation.')
  d.data(node).update(name='MatchCardNationalityFlag',name_UxmlAttributeFlags=1)
  d.st(node,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.px(28)),(131105,d.px(22)),(131087,d.px(14)),(131084,d.num(0)),(131085,d.num(0))])
  num=d.add(Doc(W,name='SquadOverviewPlayerBlock'),1068,hero,'MatchCardShirtNumber');d.a(num)['m_Classes']=[]
  data=d.data(num);data['TextBinding']['m_direct']['Path']['m_path']='person.SquadNumberBlankIfInvalid'
  data['TextBinding_UxmlAttributeFlags']=1
  d.st(num,[(131102,d.enum('absolute')),(131103,d.px(-8)),(131104,d.px(28)),(131105,d.px(30)),(131087,d.px(16)),(65537,d.px(10)),(65546,d.enum('middle-center')),(65536,d.val(4,rgba(24,24,24))),(458752,d.val(4,rgba(239,213,137))),(262147,[d.px(8),d.px(0),d.px(0),d.px(8)]),(131099,d.px(2)),(131100,d.px(2)),(131084,d.num(0)),(131085,d.num(0))])
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'flag':'person.Nation native SIImage','number':'person.SquadNumberBlankIfInvalid','number_tab':'gold, left corners 8 right corners 0','first_team_and_substitute_variants':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('首发和替补球员卡的两个展开模板：头像左侧22×14原生国旗，右侧30×16浅金色号码底板，左侧8px圆角、右侧直角。号码沿用球员球衣号码绑定，缺失时原生空值。现有红黄牌和姓名位置保留。静态检查通过，实际游戏显示未验证。','utf8')

