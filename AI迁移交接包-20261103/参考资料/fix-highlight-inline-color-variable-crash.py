from pathlib import Path
import json
R=Path(__file__).parent
source=(R/'build-commentary-left-toolbar-offset.py').read_text('utf8')
prefix=source.split('audits=[]')[0].replace("'commentary-left-toolbar-minus20-'","'highlight-inline-color-crash-fix-'").replace('NAMES=[M]','NAMES=[G]')
exec(compile(prefix,'backup-current-resource','exec'))
d=Doc(G,pid=-7710242645031577538);old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
defs={}
for bundle in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle']:
 for ob in UnityPy.load(str(GAME/bundle)).objects:
  if ob.type.name!='MonoBehaviour':continue
  sheet=ob.read_typetree()
  for rule in sheet.get('m_Rules',[]):
   for prop in rule['m_Properties']:
    if prop.get('m_CustomName','').startswith('--'):defs[prop['m_CustomName']]=(sheet,prop['m_Values'])
def resolve_color(name,seen=None):
 seen=set() if seen is None else seen;assert name not in seen;seen.add(name)
 sheet,handles=defs[name]
 if len(handles)==3 and handles[0]['m_ValueType']==10:return resolve_color(sheet['strings'][handles[2]['valueIndex']],seen)
 assert len(handles)==1 and handles[0]['m_ValueType']==4
 return copy.deepcopy(sheet['colors'][handles[0]['valueIndex']])
color=resolve_color('--layout-modules-block-border-colour')
nodes=[d.named('HighlightMetadataStatsSeparator'),3430,3432,3434,3436,3438,3440]
props=[458758,458761,458762,458763];removed=0
for i in nodes:
 rule=d.s['m_Rules'][d.a(i)['m_RuleIndex']]
 for pid in props:
  p=next(p for p in rule['m_Properties'] if p['m_Id']==pid)
  assert any(h['m_ValueType']==10 for h in p['m_Values']);removed+=1
 d.st(i,[(pid,d.val(4,copy.deepcopy(color))) for pid in props])
 active=d.s['m_Rules'][d.a(i)['m_RuleIndex']]
 for p in active['m_Properties']:
  if p['m_Id'] in props:assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4
assert removed==28
for rid,record in oldr.items():
 expected=copy.deepcopy(record)
 if rid in nodes:expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
 assert d.r[rid]==expected,('Unrelated layout/binding changed',rid)
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
assert set(d.r)==set(oldr)
d.save();audits=[{'fixed_nodes':nodes,'replaced_var_properties':removed,'color':color}]
validation=source.split('data=env[M]',1)[1].split("report={'commentary_alignment'",1)[0]
exec(compile(('data=env[M]'+validation).replace('env[M]','env[G]').replace('objs[M]','objs[G]').replace('hashes[M]','hashes[G]').replace('changes[M]','changes[G]').replace('(OUT/M)','(OUT/G)'),'roundtrip-and-unrelated-check','exec'))
report={'crash_exception':'0xC0000005 read address 0x18','crash_module':'GameAssembly.dll','crash_rva':'0x2217659','confirmed_native_method':'UnityEngine.UIElements.StyleVariableResolver.ResolveVariable','method_start_rva':'0x2217620','metadata_token':'0x060023E7','null_variable_context':True,'fix':'Replace new inline var() border colors with resolved Color handles','resolved_theme_color':color,'replaced_properties':removed,'metadata_and_default_stats_preserved':True,'only_active_line_color_handles_changed':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False,'preexisting_Color_Dimension_log_warnings_not_claimed_fixed':True}
tail="manifest={'installed':False"+source.split("manifest={'installed':False",1)[1]
tail=tail.replace("{M:{str(pid):tree.get('m_Name','') for pid,tree in changes[M].items()}}","{G:{str(pid):tree.get('m_Name','') for pid,tree in changes[G].items()}}")
tail=tail.replace('{M:sha(data)}','{G:sha(data)}').replace("'files':[M]","'files':[G]")
tail=tail.replace('MatchCommentaryBar：文字纵向居中、水平左对齐，保留现有文字内边距、字号、颜色以及解说条背景和尺寸。SquadOverview/MatchBottomTacticalToolbar：left= -20px、right=20px，整体左移20px，宽度及高度不变。按钮、菜单、球员与替补区域、Highlight内容和全部绑定结构均不变。','修复上一版分隔线行内var()颜色导致的崩溃。崩溃转储异常0xC0000005读0x18；GameAssembly.dll+0x2217659位于StyleVariableResolver.ResolveVariable（方法起点0x2217620，metadata token 0x060023E7），变量上下文为空。将7个分隔线节点的28个新增行内颜色变量改为当前主题解析后的实际Color值：RGBA(1,1,1,0.24)。温度/主裁判、默认主客队统计、布局、缓存和其他既有修改保持不变。旧日志既存Color/Dimension警告未在本次修复范围内，也不作为已修复项。')
exec(compile(tail,'write-reversible-hotfix','exec'))
log=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log')
if log.exists():(OUT/'Player-before-fix.log').write_bytes(log.read_bytes())
(OUT/'崩溃原因.md').write_text('''# 已确认的崩溃点

最新转储：9fd04d06-790b-4b83-9643-eda49f34c65b.dmp，2026-10-25 14:21。
异常：0xC0000005，读取地址0x18。
模块位置：GameAssembly.dll + 0x2217659。
通过该安装版本的IL2CPP metadata方法token 0x060023E7与UnityEngine.UIElementsModule.dll方法指针表交叉确认，该地址位于StyleVariableResolver.ResolveVariable，方法入口0x2217620。
崩溃指令读取[rdi+0x18]，转储中rdi=0；该函数此前从解析器对象+0x48取得变量上下文后，未作空值检查。
breadcrumbs最后打开OverviewPrototype，正是本轮新增行内颜色var()的比赛页面。

本次热修复仅将7处分隔线的28个行内颜色变量替换为原主题解析后的具体Color值（白色，alpha 0.24），不再进入变量解析路径。温度/主裁判显示、横竖线统一颜色、主客队统计默认项和缓存迁移均保留。

Player-prev.log在上次补丁安装前已存在Color/Dimension类型警告，不能把这些警告单独当作本次崩溃原因；本次不声称已消除它们。
文件回读及无关对象一致性已检查。仍需重新进入比赛验证实际运行，不以静态检查替代运行验证。
''','utf8')
