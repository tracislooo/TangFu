from pathlib import Path
import json,copy
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','highlight-high-resolution-fill-')
prefix=prefix.replace(".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]')", ".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,\"ui-tileslayouts_assets_all.bundle\"]')")
exec(compile(prefix,'backup-current','exec'))
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];T='ui-tileslayouts_assets_all.bundle'+suffix
 for name in names:
  ob=find(T,name);t=ob.read_typetree();old=copy.deepcopy(t);t['m_layoutMode']=0
  assert t['m_gridComponents']==old['m_gridComponents']
  ob.save_typetree(t);changes[T][ob.path_id]=t
 d=Doc(M,name='OverviewPrototype')
 for i in [1021,1022]:d.st(i,[(131105,d.pct(100)),(131095,{'m_ValueType':1,'valueIndex':3}),(131097,d.px(0)),(131084,d.num(1)),(131074,d.enum('stretch'))])
 d.save();cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'large_grid_mode':0,'columns_unchanged':'5:10:5','grid_coordinates_and_contents_unchanged':True,'container_width':'100% uncapped','runtime_verified':False})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
# Preserve locally chosen modules; migrate only the grid's sizing mode.
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
tx=json.loads((OUT/'transaction.json').read_text('utf8'))
for name in names:
 p=cache/name
 if not p.exists():continue
 old=p.read_bytes();t=json.loads(old);t['m_layoutMode']=0;new=json.dumps(t,ensure_ascii=False,indent=2).encode('utf8')
 bp=OUT/('cache-backup-'+name+'.json');sp=OUT/('cache-'+name+'.json');bp.write_bytes(old);sp.write_bytes(new)
 tx.append({'target':str(p),'source':str(sp),'backup':str(bp),'before':sha(old),'after':sha(new)})
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(OUT/'installer.py').read_text('utf8').replace("for row in tx:","allowed.add(Path("+repr(str(cache))+ ").resolve())\nfor row in tx:")
(OUT/'installer.py').write_text(installer,'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅调整四套桌面大屏 Highlight 网格的布局模式 4→0，并让外层网格宽度为100%、取消宽度上限；三列5:10:5、坐标、模块内容及字号不变。对应本地缓存只迁移布局模式，保留所选模块。已完成文件检查，未完成高分辨率游戏内验证。','utf8')
