from pathlib import Path
import json,copy
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','native-highlight-context-fitness-')
prefix=prefix.replace(".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F]')", ".replace('NAMES=[W,G,M,F]','NAMES=[W,G,M,F,\"ui-tableviews_assets_all.bundle\"]')")
exec(compile(prefix,'backup-and-load','exec'))
VF='7401d638fac886647b252bd4c3b8232c'
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];V='ui-tableviews_assets_all.bundle'+suffix
 # Use the native tactics condition selector, with its actual bool argument order.
 donor=Doc(W,name='TacticsPositionOppositionInstructions')
 proto=next(f for r in donor.r.values() for f in (r.get('data',{}).get('BindFunction',[]) if isinstance(r.get('data',{}).get('BindFunction'),list) else []) if isinstance(f,dict) and f.get('m_target',{}).get('m_guid')==VF)
 args=unpack(proto['m_inputs']['m_variable']['m_argumentBytes']);assert len(args)==6
 assert b'tactic.IsDuringMatch' in args[4]
 func=copy.deepcopy(proto)
 for i,path in [(0,'position.MatchPlayer.Condition'),(1,'position.Player.Condition'),(2,'LiveMatchBoardCondition')]:
  pre=args[i][:args[i][0]+2];args[i]=pre+bytes([len(path)])+path.encode()
 func['m_inputs']['m_variable']['m_argumentBytes']=pack(args)
 for name in ['TacticsPositionDetailed','TacticsPositionCombined']:
  board=Doc(W,name=name);matches=[]
  for r in board.r.values():
   functions=r.get('data',{}).get('BindFunction',[])
   if not isinstance(functions,list):continue
   for i,f in enumerate(functions):
    if isinstance(f,dict) and b'LiveMatchBoardCondition' in bytes(f.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])):
     matches.append((functions,i))
  assert len(matches)==1,(name,len(matches))
  functions,i=matches[0];functions[i]=copy.deepcopy(func);board.save()
 # Original stats condition cell, and original native sharpness cell.
 stats=find(F,'PlayerStatsExtendedFactory').read_typetree()
 native_tactics=find(F,'TacticTeamSelectionTableFactory').read_typetree()
 condition=copy.deepcopy(next(c for c in stats['m_rowData'] if c['m_id']=='condition'))
 sharpness=copy.deepcopy(next(c for c in native_tactics['m_rowData'] if c['m_id']=='sharpness'))
 assert condition['m_uxmlRef']['m_AssetGUID']=='4873fa63429f48944abf1edead6c87a4'
 assert sharpness['m_uxmlRef']['m_AssetGUID']=='975b939baf439c944abc1b0be94bfc76'
 for ob in objs[F].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsFactory':continue
  tree=ob.read_typetree();cols=tree['m_rowData'];idx=next(i for i,c in enumerate(cols) if c['m_id']=='condition')
  assert not any(c['m_id']=='sharpness' for c in cols)
  cols[idx:idx+1]=[copy.deepcopy(condition),copy.deepcopy(sharpness)]
  ob.save_typetree(tree);changes[F][ob.path_id]=tree
 for ob in objs[V].values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name()!='HighlightEightFieldsView':continue
  tree=ob.read_typetree();cols=tree['m_tableView']['m_tableConfig'];idx=next(i for i,c in enumerate(cols) if c['m_columnID']=='condition')
  original=copy.deepcopy(cols[idx]);replacement=[]
  for native in [condition,sharpness]:
   c=copy.deepcopy(original);c['m_columnID']=native['m_id']
   c['m_columnMetadata']['m_widthOverride']=native['m_defaultWidth'];c['m_columnMetadata']['m_minWidthOverride']=native['m_minimumWidth']
   c['m_columnMetadata']['m_titleTranslationIdOverride']={'GameID':0};replacement.append(c)
  cols[idx:idx+1]=replacement;ob.save_typetree(tree);changes[V][ob.path_id]=tree
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';cat=cm.Catalog(before[cp])
 for guid in [VF,condition['m_uxmlRef']['m_AssetGUID'],sharpness['m_uxmlRef']['m_AssetGUID']]:
  assert cat.locations(guid),('Native resource not registered',guid)
 cats[tag]=before[cp]
 audits.append({'variant':tag,'board_condition_selector':'tactic.IsDuringMatch','true':'position.MatchPlayer.Condition','false':'position.Player.Condition','native_condition_column':condition,'native_sharpness_column':sharpness,'no_board_hierarchy_changes':True,'working_match_list_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-and-package','exec'))
(OUT/'修改说明.md').write_text('左右 Highlight 下方：恢复原生 PlayerConditionCell 和 PlayerSharpnessCell 两列，使用原生列定义、提示与绑定。战术板：仅将体能绑定函数改为原生 tactic.IsDuringMatch 条件选择，比赛内 position.MatchPlayer.Condition、比赛外 position.Player.Condition。不改战术板层级和比赛内列表。已完成序列化回读、未指定对象一致性和原生资源目录登记检查；未进行游戏内验证。\n','utf8')
