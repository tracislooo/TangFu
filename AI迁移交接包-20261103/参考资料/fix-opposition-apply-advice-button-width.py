from pathlib import Path
import copy,json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','opposition-apply-advice-width-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];d=Doc(W,name='OppositionInstructionsBlock');old=copy.deepcopy(d.d)
 button=d.named('ApplyAdviceButton');data=d.data(button)
 fn=data['BindTextFunction'];args=unpack(fn['m_inputs']['m_variable']['m_argumentBytes']);assert len(args)==1
 # Preserve the localized translation ID; only supply the missing native fallback.
 assert args[0][-2:]==bytes([1,0]);text=b'Apply Advice';args[0]=args[0][:-1]+bytes([len(text)])+text
 fn['m_inputs']['m_variable']['m_argumentBytes']=pack(args)
 d.st(button,[(131097,d.px(88)),(131105,{'m_ValueType':1,'valueIndex':2}),(131085,d.num(0)),(131099,d.px(12)),(131100,d.px(12))])
 d.st(d.a(button)['m_Parent']['rid'],[(131097,d.px(88)),(131085,d.num(0))])
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'button':'ApplyAdviceButton','min_width':88,'horizontal_padding':12,'translation_id_unchanged':True,'native_fallback':'Apply Advice','click_events_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
