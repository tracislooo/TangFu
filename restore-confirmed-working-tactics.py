from pathlib import Path
import json,copy
R=Path(__file__).parent
src=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=src.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','restore-confirmed-tactics-')
exec(compile(prefix,'load-current-resources','exec'))
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases]
 oldenv=UnityPy.load(str(R/'separate-match-fitness-toolbar-colors-20261030-102713'/('backup-'+tag)/bases[0]))
 oldobjs={o.path_id:o for o in oldenv.objects}
 for name in ['TacticsPositionDetailed','TacticsPositionCombined']:
  old=next(o for o in oldenv.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name)
  current=Doc(W,name=name);tree=copy.deepcopy(old.read_typetree());style=copy.deepcopy(oldobjs[tree['inlineSheet']['m_PathID']].read_typetree())
  pointer_remap(tree,old.assets_file,current.af);pointer_remap(style,old.assets_file,current.af)
  restored=Doc(W,pid=current.obj.path_id,tree=tree,style=style);restored.save()
 oldenv=UnityPy.load(str(R/'live-match-fitness-tabs-20261030-092133'/('backup-'+tag)/bases[3]))
 oldobjs={o.path_id:o for o in oldenv.objects}
 restored_columns=[]
 for ob in objs[F].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsFactory':continue
  tree=ob.read_typetree();old=oldobjs[ob.path_id].read_typetree()
  index=next(i for i,c in enumerate(tree['m_rowData']) if c['m_id']=='condition')
  tree['m_rowData'][index]=copy.deepcopy(next(c for c in old['m_rowData'] if c['m_id']=='condition'))
  guid=tree['m_rowData'][index]['m_uxmlRef']['m_AssetGUID']
  cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin'
  assert cm.Catalog(before[cp]).locations(guid),('Missing original cell catalog entry',guid)
  ob.save_typetree(tree);changes[F][ob.path_id]=tree;restored_columns.append({'factory':ob.path_id,'column':tree['m_rowData'][index]})
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'board_restored_to_user_confirmed_in_match_version':True,'working_in_match_list_unchanged':True,'toolbar_colors_unchanged':True,'highlight_original_column_restored':restored_columns,'highlight_realtime_fixed':False,'outside_match_zero_issue_not_resolved_by_this_rollback':True})
W,G,M,F=bases
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'validate-and-package','exec'))
(OUT/'问题说明.md').write_text('本次撤销新增的战术板切换容器，精确恢复用户确认比赛内正常的两个战术板模板及样式。比赛内列表和工具栏颜色不变。Highlight 仅恢复实时改造之前的体能列，避免全零；实时刷新尚未修复。比赛外体能为零问题仍需另行隔离处理。本次没有游戏内验证。\n','utf8')
log=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log')
if log.exists():(OUT/'Player-before-rollback.log').write_bytes(log.read_bytes())
