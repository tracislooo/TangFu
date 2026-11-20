from pathlib import Path
import json
R=Path(__file__).parent
source=(R/'build-commentary-left-toolbar-offset.py').read_text('utf8')
prefix=source.split('audits=[]')[0].replace('commentary-left-toolbar-minus20-','commentary-centered50-')
exec(compile(prefix,'backup-current-match-resource','exec'))
audits=[]
for name in ['MatchCommentaryBar','MatchCommentary']:
 d=Doc(M,name=name);old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
 if name=='MatchCommentaryBar':
  d.st(1001,[(131074,d.enum('center'))])
  d.st(1004,[(131105,d.pct(50)),(131095,d.pct(50)),(131074,d.enum('center')),(131089,d.px(0))])
  allowed={1001,1004}
 else:
  assert d.a(1008)['m_TemplateAlias']=='MatchCommentaryBar'
  d.st(1008,[(131073,d.enum('center'))])
  allowed={1008}
 for rid,record in oldr.items():
  expected=copy.deepcopy(record)
  if rid in allowed:expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
  assert d.r[rid]==expected,('Unrelated node or binding changed',name,rid)
 for k,v in olds.items():
  if isinstance(v,list):assert d.s[k][:len(v)]==v
  else:assert d.s[k]==v
 assert set(d.r)==set(oldr)
 d.save();audits.append({'template':name,'modified_style_nodes':sorted(allowed)})
validation=source.split('data=env[M]',1)[1].split("report={'commentary_alignment'",1)[0]
exec(compile('data=env[M]'+validation,'roundtrip-and-unrelated-check','exec'))
report={'commentary_visible_width_original_percent':50,'commentary_screen_alignment':'center','horizontal_offset_px':0,'text_alignment':'middle-center unchanged','height_font_colors_padding_bindings_unchanged':True,'toolbar_and_all_other_modules_unchanged':True,'audits':audits,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
tail="manifest={'installed':False"+source.split("manifest={'installed':False",1)[1]
start=tail.index("(OUT/'修改说明.md').write_text(")
end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('解说条按原始基准的50%宽度显示，替换75%；宿主、原宽度计算容器和可见容器水平居中，取消右移20px。文字保持水平及垂直居中，高度、字号、颜色、内边距、绑定、战术栏及其他模块不变。已通过序列化回读和无关对象一致性检查；游戏内显示尚未验证。restore.ps1恢复本次修改。','utf8')"+tail[end:]
exec(compile(tail,'write-reversible-patch','exec'))
