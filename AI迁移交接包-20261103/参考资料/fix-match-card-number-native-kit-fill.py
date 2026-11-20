from pathlib import Path
import json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','match-card-number-native-kit-fill-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];donor=Doc(W,name='PlayerKitShoutNameCell')
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);holder=d.named('MatchCardNumberKitColourBinding');number=d.named('MatchCardShirtNumber')
  data=d.data(holder);data['SecondaryColorDataLink']['m_path']='team.KitForMatch.NumberColour'
  fill=d.add(donor,1021,holder,'MatchCardNumberNativeKitFill');d.a(fill)['m_Classes']=list(donor.a(1021)['m_Classes'])
  d.st(fill,[(131105,d.px(30)),(131087,d.px(16)),(131084,d.num(0)),(131085,d.num(0)),(262147,[d.px(3),d.px(0),d.px(0),d.px(3)])])
  d.move(number,fill);d.a(number)['m_Classes']=['fm-club-secondary-color']
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'native_structure':'SIStyleSetter > shirt-badge-fill > number text','background_binding':'team.KitForMatch.BackgroundColour','number_binding':'team.KitForMatch.NumberColour','layout_size_and_radius_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
