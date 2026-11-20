from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
driver=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8')
prefix=driver.split('for tag,suffix in')[0].replace('live-match-fitness-tabs-','board-fitness-direct-branches-')
exec(compile(prefix,'backup-load','exec'))
helpers=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'clone-fitness-only','exec'))
clone_audits=[]
for tag,suffix in [('game',''),('skin','::skin')]:
 W,G,M,F=[n+suffix for n in bases];header=Doc(M,name='OverviewHeader')
 for name in ['TacticsPositionDetailed','TacticsPositionCombined']:
  d=Doc(W,name=name);root=d.named('PitchFitnessPlayerVisible');children=[c['rid'] for c in d.a(root)['m_Children']]
  switch=d.add(header,1066,root,'FitnessContextSwitch');binding=d.data(switch)['Binding'];binding['m_kind']=1;binding['m_direct']['Path']['m_path']='tactic.IsDuringMatch'
  outside=d.add(header,1035,switch,'OutsideMatchFitness');inside=d.add(header,1035,switch,'InsideMatchFitness')
  for node in [switch,outside,inside]:d.st(node,[(131105,d.pct(100)),(131087,d.pct(100)),(131096,d.px(0)),(131097,d.px(0))])
  outside_ids=set();inside_ids=set()
  def collect(i,out):
   if i in out or i==-2:return
   out.add(i);a=d.r[i].get('data',{})
   sr=a.get('m_SerializedData',{}).get('rid')
   if sr and sr!=-2:out.add(sr)
   for c in a.get('m_Children',[]):collect(c['rid'],out)
  for child in children:
   copied,mapping=clone_native(d,child,inside);inside_ids.update(mapping.values());d.move(child,outside);collect(child,outside_ids)
  for i in outside_ids:rewrite_binding(d.r[i],'LiveMatchBoardCondition','position.Player.Condition')
  for i in inside_ids:rewrite_binding(d.r[i],'LiveMatchBoardCondition','position.MatchPlayer.Condition')
  for r in d.r.values():
   s=r.get('data',{})
   if isinstance(s.get('ValueVariables'),list):s['ValueVariables']=[v for v in s['ValueVariables'] if v['m_name']!='LiveMatchBoardCondition']
   if isinstance(s.get('BindFunction'),list):s['BindFunction']=[f for f in s['BindFunction'] if not (isinstance(f,dict) and b'LiveMatchBoardCondition' in bytes(f.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])))]
  assert d.a(switch)['m_Children']==[{'rid':outside},{'rid':inside}]
  for ids,expected,forbidden in [(outside_ids,b'position.Player.Condition',b'position.MatchPlayer.Condition'),(inside_ids,b'position.MatchPlayer.Condition',b'position.Player.Condition')]:
   values=[bytes(r['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']) for i in ids for r in [d.r[i]] if isinstance(r.get('data',{}).get('Binding'),dict) and r['data']['Binding'].get('m_kind')==2]
   assert sum(expected in raw for raw in values)>=100
   assert not any(forbidden in raw or b'LiveMatchBoardCondition' in raw for raw in values)
  d.save()
 cats[tag]=before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']
 audits.append({'variant':tag,'only_fitness_subtree_split':True,'outside_direct':'position.Player.Condition','inside_direct':'position.MatchPlayer.Condition','intermediate_variable_removed':True,'player_card_and_match_list_unchanged':True})
tail=(R/'fix-live-match-fitness-and-tabs.py').read_text('utf8').split('W,G,M,F=bases;outputs={}')[1]
exec(compile('W,G,M,F=bases;outputs={}'+tail,'verify-package','exec'))
(OUT/'修改说明.md').write_text('移除未正确赋值的 LiveMatchBoardCondition。仅在原体能数字/条形图内部使用原生二选一控件：比赛外直接读取 position.Player.Condition，比赛内直接读取 position.MatchPlayer.Condition。头像、角色、拖拽根节点及表格不变。已完成序列化回读和分支绑定检查，尚未游戏内验证。\n','utf8')
