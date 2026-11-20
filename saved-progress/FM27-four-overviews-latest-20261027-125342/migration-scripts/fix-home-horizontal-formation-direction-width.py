from pathlib import Path
import json
R=Path(__file__).parent
source=(R/'build-commentary-left-toolbar-offset.py').read_text('utf8')
prefix=source.split('audits=[]')[0].replace("'commentary-left-toolbar-minus20-'","'highlight-home-formation-direction-fullwidth-'").replace('NAMES=[M]','NAMES=[G]')
exec(compile(prefix,'backup-current-private-formation','exec'))
d=Doc(G,pid=-981025000002000);old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
assert d.d['m_Name']=='HighlightHomeHorizontalFormation'
serials=set()
for i in [1064,1065]:
 v=d.data(i);assert v['Orientation']==1
 v.update(FlipPositions=1,FlipPositions_UxmlAttributeFlags=1)
 serials.add(d.a(i)['m_SerializedData']['rid'])
 d.st(i,[(131105,d.pct(100)),(131097,d.px(0)),(131074,d.enum('stretch'))])
assert d.a(1064)['m_Parent']['rid']==1045 and d.a(1065)['m_Parent']['rid']==1045
d.st(1045,[(131105,d.pct(100)),(131095,d.pct(100)),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131074,d.enum('stretch'))])
d.st(1029,[(131105,d.pct(100)),(131097,d.px(0)),(131074,d.enum('stretch'))])
allowed={1029,1045,1064,1065}
for rid,record in oldr.items():
 expected=copy.deepcopy(record)
 if rid in allowed:expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
 if rid in serials:expected['data'].update(FlipPositions=1,FlipPositions_UxmlAttributeFlags=1)
 assert d.r[rid]==expected,('Unrelated record/field changed',rid)
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
assert set(d.r)==set(oldr)
d.save();audits=[{'template':d.d['m_Name'],'style_nodes':sorted(allowed),'native_flip_nodes':[1064,1065]}]
validation=source.split('data=env[M]',1)[1].split("report={'commentary_alignment'",1)[0]
exec(compile(('data=env[M]'+validation).replace('env[M]','env[G]').replace('objs[M]','objs[G]').replace('hashes[M]','hashes[G]').replace('changes[M]','changes[G]').replace('(OUT/M)','(OUT/G)'),'roundtrip-and-unrelated-check','exec'))
report={'orientation':'native horizontal','native_flip_positions':True,'goalkeeper':'left','forwards':'right','removed_fixed_pitch_width_px':270,'pitch_width':'100% of available formation content','pitch_aspect_and_all_player_template_bindings_preserved':True,'audits':audits,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
tail="manifest={'installed':False"+source.split("manifest={'installed':False",1)[1]
tail=tail.replace("{M:{str(pid):tree.get('m_Name','') for pid,tree in changes[M].items()}}","{G:{str(pid):tree.get('m_Name','') for pid,tree in changes[G].items()}}")
tail=tail.replace("{M:sha(data)}","{G:sha(data)}").replace("'files':[M]","'files':[G]")
tail=tail.replace('MatchCommentaryBar：文字纵向居中、水平左对齐，保留现有文字内边距、字号、颜色以及解说条背景和尺寸。SquadOverview/MatchBottomTacticalToolbar：left= -20px、right=20px，整体左移20px，宽度及高度不变。按钮、菜单、球员与替补区域、Highlight内容和全部绑定结构均不变。','仅调整 HighlightHomeHorizontalFormation 私有模板：直播和历史球场使用原生 FlipPositions，门将在左、前锋在右，文字保持正立。移除 tactics-pitch-match-switch 原固定270px宽度与上限，设为可用内容宽度100%；父容器和两个绘图分支同步占满宽度，保留原高度和球场比例。标题、选择器、球员模板与实时绑定、右侧阵型和其他模块保持原样。')
exec(compile(tail,'write-reversible-patch','exec'))
