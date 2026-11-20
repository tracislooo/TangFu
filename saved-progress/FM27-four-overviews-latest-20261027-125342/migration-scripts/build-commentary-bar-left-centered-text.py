from pathlib import Path
import json
R=Path(__file__).parent
source=(R/'build-commentary-left-toolbar-offset.py').read_text('utf8')
prefix=source.split('audits=[]')[0].replace("'commentary-left-toolbar-minus20-'","'commentary-bar-left-centered-text-'")
exec(compile(prefix,'backup-current-match-resource','exec'))
audits=[]
for name in ['MatchCommentaryBar','MatchCommentary']:
 d=Doc(M,name=name);old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
 if name=='MatchCommentaryBar':
  base_env=UnityPy.load(str(R/'commentary-left-toolbar-minus20-20261025-130959/backup-game'/M));base_objs={o.path_id:o for o in base_env.objects}
  base=base_objs[d.obj.path_id].read_typetree();br=refs(base);bs=base_objs[d.sid].read_typetree()
  for k,v in bs.items():
   if isinstance(v,list):assert d.s[k][:len(v)]==v
   else:assert d.s[k]==v
  for i in [1006,1008]:d.a(i)['m_RuleIndex']=br[i]['data']['m_RuleIndex']
  d.st(1001,[(131074,d.enum('flex-start')),(131093,d.px(0))])
  allowed={1001,1006,1008}
 else:
  assert d.a(1008)['m_TemplateAlias']=='MatchCommentaryBar'
  d.st(1008,[(131073,d.enum('flex-start')),(131093,d.px(0)),(131101,d.px(0))])
  allowed={1008}
 for rid,record in oldr.items():
  if rid not in allowed:assert d.r[rid]==record,('Unrelated node changed',name,rid)
  else:
   expected=copy.deepcopy(record);expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
   assert d.r[rid]==expected,('Binding/structure changed',name,rid)
 for k,v in olds.items():
  if isinstance(v,list):assert d.s[k][:len(v)]==v
  else:assert d.s[k]==v
 assert set(d.r)==set(oldr)
 d.save();audits.append({'template':name,'modified_style_nodes':sorted(allowed)})
validation=source.split('data=env[M]',1)[1].split("report={'commentary_alignment'",1)[0]
exec(compile('data=env[M]'+validation,'roundtrip-and-unrelated-check','exec'))
report={'commentary_text_alignment':'original middle-center restored','commentary_region_alignment':'left edge of full-width commentary host, zero left margin/padding','commentary_original_width_height_font_colors_preserved':True,'toolbar_minus20_unchanged':True,'audits':audits,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
tail="manifest={'installed':False"+source.split("manifest={'installed':False",1)[1]
tail=tail.replace('MatchCommentaryBar：文字纵向居中、水平左对齐，保留现有文字内边距、字号、颜色以及解说条背景和尺寸。SquadOverview/MatchBottomTacticalToolbar：left= -20px、right=20px，整体左移20px，宽度及高度不变。按钮、菜单、球员与替补区域、Highlight内容和全部绑定结构均不变。','MatchCommentaryBar：恢复原生文字水平/垂直居中。仅将解说条外层和其宿主改为靠左、左侧外边距/宿主内边距为零；原有解说条宽高、最大宽度、背景、颜色、文字内边距不变。战术栏上次左移20px的修改保持原样；按钮、球员、替补、Highlight和所有绑定结构均不变。')
exec(compile(tail,'write-reversible-patch','exec'))
