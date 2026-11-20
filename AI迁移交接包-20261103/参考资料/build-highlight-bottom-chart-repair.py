from pathlib import Path
import json
R=Path(__file__).parent
source=(R/'build-highlight-bottom-chart-space.py').read_text('utf8')
prefix=source.split('old=copy.deepcopy(d.d);')[0].replace("'highlight-bottom-chart-space-'","'highlight-bottom-chart-repair-'")
exec(compile(prefix,'backup-current-resource','exec'))
old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
previous=R/'highlight-bottom-chart-space-20261025-125511'
pm=json.loads((previous/'manifest.json').read_text('utf8'))
assert sha(before[GAME/G])==pm['after_sha256'][G]
base_env=UnityPy.load(str(previous/'backup-game'/G));base_objs={o.path_id:o for o in base_env.objects}
base=base_objs[d.obj.path_id].read_typetree();br=refs(base);bs=base_objs[d.sid].read_typetree()
for k,v in bs.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v,('Baseline style pool changed',k)
 else:assert d.s[k]==v
assert set(br)==set(d.r)
allowed=set(pm['layout']['modified_style_nodes']);class_changes=set(pm['layout']['removed_background_class_nodes'])
for i in allowed:d.a(i)['m_RuleIndex']=br[i]['data']['m_RuleIndex']
for i in class_changes:d.a(i)['m_Classes']=copy.deepcopy(br[i]['data']['m_Classes'])
AUTO={'m_ValueType':1,'valueIndex':2}
def style(i,props):d.st(i,props);allowed.add(i)
def spacing(i):style(i,[(p,d.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
def transparent(i):style(i,[(458752,d.val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),(458753,{'m_ValueType':1,'valueIndex':3})])
modules=json.loads((R/'highlight-4x4-75-dividers-transparent-20261024-141806/verification.json').read_text('utf8'))['module_style']
for module in modules:
 title=module['title'];scroller=d.a(title)['m_Parent']['rid'];frame=d.a(scroller)['m_Parent']['rid'];parent=d.a(frame)['m_Parent']['rid']
 i=parent
 while i!=d.a(module['wrapper'])['m_Parent']['rid']:
  spacing(i);i=d.a(i)['m_Parent']['rid']
 spacing(frame);spacing(scroller);spacing(title)
 # Only the header's column-axis allocation is fixed. Its row-axis children
 # retain an automatic basis and can occupy the complete module width.
 style(frame,[(131087,d.px(16)),(131096,d.px(16)),(131094,d.px(16)),(131082,d.px(16)),(131084,d.num(0)),(131085,d.num(0)),(131083,d.enum('row')),(131105,d.pct(100)),(131073,d.enum('center')),(131088,d.enum('center'))])
 style(scroller,[(131082,AUTO),(131105,d.pct(100)),(131087,d.px(16)),(131084,d.num(1)),(131085,d.num(1)),(131074,d.enum('stretch'))])
 style(title,[(65537,d.px(12)),(65546,d.enum('middle-center')),(131105,d.pct(100)),(131082,AUTO),(131087,d.px(16)),(131074,d.enum('stretch'))])
 # Preserve the working native chart height/basis and orientation throughout.
 content=next(c['rid'] for c in d.a(parent)['m_Children'] if d.a(c['rid']).get('m_TemplateAlias')=='states-templates-tile-content')
 spacing(content)
for i in [3204,3197]:
 d.a(i)['m_Classes']=[c for c in d.a(i)['m_Classes'] if c!='graph_datavis_accent_background']
 transparent(i);spacing(i)
for i in [3199,3193,3211,3201]:spacing(i)

# All plot and switch sizing is byte-for-byte the known working baseline.
height_properties={131082,131087,131094,131096,131084,131085,131083}
def effective_inline(i,sheet,rr):
 idx=rr[i]['data'].get('m_RuleIndex',-1)
 props=sheet['m_Rules'][idx]['m_Properties'] if idx>=0 else []
 return {p['m_Id']:p for p in props if p['m_Id'] in height_properties}
plot_chains=[3453,3136,3140,3143,3148,3475,3180,3184,3186,3188,3191,3195,3199,3204,3211,3221,3189,3193,3197,3201,3206,3497,3276,3281,3285]
for i in plot_chains:assert effective_inline(i,d.s,d.r)==effective_inline(i,bs,br),('Working chart sizing changed',i)
for rid,record in oldr.items():
 if rid not in allowed and rid not in class_changes:assert d.r[rid]==record,('Unrelated node changed',rid)
 else:
  expected=copy.deepcopy(record)
  if rid in allowed:expected['data']['m_RuleIndex']=d.r[rid]['data']['m_RuleIndex']
  if rid in class_changes:expected['data']['m_Classes']=d.r[rid]['data']['m_Classes']
  assert d.r[rid]==expected,('Unexpected structure/binding change',rid)
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
assert set(d.r)==set(oldr)
suffix=source.split('d.save()\n',1)[1].split("report={'title_font_px'",1)[0]
d.save();exec(compile(suffix,'roundtrip-and-resource-validation','exec'))
report={'title_font_px':12,'title_height_px':16,'title_alignment':'full-width centered','native_chart_sizing_restored_and_checked':plot_chains,'activity_backdrop_transparent':[3204,3197],'other_text_and_all_bindings_unchanged':True,'modified_style_nodes':sorted(allowed),'removed_background_class_nodes':sorted(class_changes),'serialization_roundtrip':True,'runtime_verified':False}
tail=source.split("manifest={'installed':False",1)[1]
tail="manifest={'installed':False"+tail
tail=tail.replace('标题12px、行高16px，清除顶部留白；绘图区使用释放的空间。','修复上一版图表零高度与标题截断问题。恢复全部图表祖先的已知可显示尺寸；仅标题框16px、字号12px，标题容器基准宽度自动并占满整列居中。清除顶部及活动区域外围多余间距。')
exec(compile(tail,'write-reversible-repair','exec'))
