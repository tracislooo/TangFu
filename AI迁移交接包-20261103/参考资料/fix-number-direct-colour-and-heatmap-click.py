from pathlib import Path
import copy,json
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
exec(compile(driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','number-direct-colour-heatmap-click-'),'backup-current','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 proto=Doc(W,name='SpiderChartPointCircle');fn=next(r['data']['BindFunction'] for r in proto.r.values() if isinstance(r.get('data',{}).get('BindFunction'),dict) and r['data']['BindFunction'].get('m_target',{}).get('m_guid')=='76b11a74d053f6a469f7dd0da19d3c91')
 for name in ['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']:
  d=Doc(W,name=name);holder=d.named('MatchCardNumberKitColourBinding');v=d.data(holder);f=copy.deepcopy(fn);args=unpack(f['m_inputs']['m_variable']['m_argumentBytes']);path=b'team.KitForMatch.BackgroundColour';args[0]=args[0][:args[0][0]+2]+bytes([len(path)])+path
  f['m_inputs']['m_variable']['m_argumentBytes']=pack(args);v['BindFunction']=f;v['BindFunction_UxmlAttributeFlags']=1;d.save()
 source=Doc(W,name='HeatMapsMatch_4x6');click=copy.deepcopy(source.r[1010]['data']);buttondonor=Doc(W,name='OppositionInstructionsBlock')
 d=Doc(G,name='MatchViewer_12x4');remapdonor=next(i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingRemapper')
 pitches=[i for i,r in d.r.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMHeatMap'];assert len(pitches)==2
 for pitch,side in zip(sorted(pitches),['Home','Away']):
  remap=d.add(d,remapdonor,pitch,'Highlight'+side+'HeatmapClickContext');s=d.data(remap)
  s['Mappings']=[{'m_serialisedType':0,'from':a,'to':{'m_path':b},'type':{'id':t}} for a,b,t in [('fixture','fixturetouse',1718188148),('team','fixturetouse.'+side+'Team',1145176088),('isHomeTeam','const.True' if side=='Home' else 'const.False',0)]];s['Mappings_UxmlAttributeFlags']=1
  button=d.add(buttondonor,1069,remap,'Highlight'+side+'HeatmapOpenDetails');rid=d.a(button)['m_SerializedData']['rid'];identifier=d.data(button)['uxmlAssetId'];s=copy.deepcopy(click);s.update(uxmlAssetId=identifier,name='Highlight'+side+'HeatmapOpenDetails',name_UxmlAttributeFlags=1,pickingMode=0,pickingMode_UxmlAttributeFlags=1);d.r[rid]['data']=s
  d.a(button)['m_Classes']=[]
  for node in [remap,button]:d.st(node,[(131102,d.enum('absolute')),(131089,d.px(0)),(131103,d.px(0)),(131104,d.px(0)),(131080,d.px(0)),(131105,d.pct(100)),(131087,d.pct(100))])
  d.st(button,[(458752,d.val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),(262148,d.px(0))])
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'number_background_native_direct_binding':True,'heatmap_click':'copied native HeatMapsMatch_4x6 event unchanged','home_away_contexts':True,'runtime_verified':False})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
