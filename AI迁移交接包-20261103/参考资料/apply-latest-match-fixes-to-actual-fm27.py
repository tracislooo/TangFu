"""Apply the current requested fixes against the actual FM27 installation."""
from pathlib import Path
R=Path(__file__).parent
source=(R/'fix-pending-anchor-and-stats-live-condition.py').read_text('utf8')
source=source.replace('pending-anchor-stats-live-condition-','actual-fm27-centered-upward-live-condition-')
source=source.replace("for tag,suffix in [('game',''),('skin','::skin')]:","for tag,suffix in [('game','')]:")
start=source.index(" header=Doc(M,name='OverviewHeader')")
end=source.index(" donor=Doc(W,name='TacticsConditionPercentageCell')",start)
replacement=""" header=Doc(M,name='OverviewHeader')
 if 'centre-avoid-centred' not in header.a(1034)['m_Classes']:header.a(1034)['m_Classes'].append('centre-avoid-centred')
 header.a(1034)['m_RuleIndex']=-1
 assert header.a(1089)['m_Parent']['rid']==1083
 header.save()
 toolbar=Doc(M,name='MatchUITacticalOptions')
 for node in [1018,1027,1048]:
  toolbar.data(node).update(Anchor=2,Anchor_UxmlAttributeFlags=1)
  if 'HorizontalAlignment' in toolbar.data(node):toolbar.data(node).update(HorizontalAlignment=2,HorizontalAlignment_UxmlAttributeFlags=1)
 toolbar.save()
"""
source=source[:start]+replacement+source[end:]
source=source.replace("for bn in [n+s for s in ['', '::skin'] for n in NAMES]:","for bn in NAMES:")
source=source.replace("for tag,folder in [('game',GAME),('skin',SKIN)]:","for tag,folder in [('game',GAME)]:")
source=source.replace("'popup_right_anchor_px':0,'native_controls_retain_position_in_row':True","'scoreboard_native_center':True,'menus_anchor':2,'pending_popup_and_tactics_page_original_positions_preserved':True")
exec(compile(source,'apply-against-correct-installation','exec'))
