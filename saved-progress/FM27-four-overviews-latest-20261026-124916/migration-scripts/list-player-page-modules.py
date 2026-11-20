from pathlib import Path
import sys,json,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
files=[GAME/n for n in ['ui-tileslayouts_assets_all.bundle','ui-dynamiccardcollections_assets_all.bundle','ui-panelids_assets_all.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']]
files.append(GAME/'ui-tactics_assets_all.bundle')
env=UnityPy.load(*[str(p) for p in files]);af=next(a for a in env.assets if any(o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerReportOverviewTileSet' for o in a.objects.values()))
names={'PlayerReportOverviewTileSet':'球员概览','PlayerReportPersonalTileSet':'个人页面','PlayerReportPerformanceTileSet':'表现页面','PlayerDynamicsCardTileSet':'球员动态','PersonOverviewTileset':'人物通用概览','DebugPlayerReportOverviewTileSet':'调试概览'}
cn={'Nationality':'国籍／资格','Biography':'生平','CareerStats':'职业生涯数据','Happiness':'个人情绪','Player Hierarchy':'队内层级','PlayerOffThePitchSocialGroup':'社交群体','PlayerTransferStatus':'转会状态','Favoured People':'喜爱的人物','PlayerContractNegotiationTile':'合同','PlayerPromises':'承诺','PlayerHomegrownStatus':'青训资格','PlayerWorkPermit':'劳工证','PersonPersonal':'个人资料大模块','PlayerDynamics':'球员动态','NationalTeam':'国家队','PlayerSeasonStats':'赛季统计','PlayerRoleSelector':'位置与角色','PlayerCoachReport':'教练／球探报告','PlayerPlans':'球员计划','PlayerTraits':'习惯／特质','PlayerTrainingOverview':'训练概览','FItness':'体能','Playing Time':'出场时间','Discipline':'纪律与禁赛','PlayerPerformanceData':'表现数据','PlayerTargets':'目标','PlayerForm':'近期状态','PlayerLoanReport':'租借报告','PlayerBansAndDiscipline':'禁赛与纪律','PlayerDynamicsCard':'球员动态卡','PlayerOverviewFull':'自定义完整球员概览','PlayerOverviewSimple':'自定义头像与属性版'}
sets=[]
for o in af.objects.values():
 if o.type.name!='MonoBehaviour' or o.peek_name() not in names:continue
 d=o.read_typetree();rows=[]
 for ptr in d.get('m_gridElementDescriptions',[]):
  obj=PPtr(**ptr,assetsfile=af).deref();t=obj.read_typetree()
  name=t.get('<Name>k__BackingField',t.get('m_Name'))
  configs=t.get('<Configurations>k__BackingField',[])
  sizes=list(dict.fromkeys(f"{c['Size']['x']}×{c['Size']['y']}" for c in configs))
  rows.append({'name':name,'chinese':cn.get(name,name),'resource':t['m_Name'],'path_id':obj.path_id,'sizes':sizes,'configurations':configs})
 sets.append({'name':d['m_Name'],'page':names[d['m_Name']],'modules':rows})
sets.sort(key=lambda s:list(names).index(s['name']))
extra_cn={'PlayerAttributesBlock':'属性区','PlayerInfo':'资料／习惯／禁赛','Summary':'概览摘要','TacticalEffectiveness':'战术熟练度'}
cn.update(extra_cn)
for s in sets:
 for r in s['modules']:r['chinese']=cn.get(r['name'],r['name'])
registered={r['resource'] for s in sets for r in s['modules']};extras=[]
for a in env.assets:
 for o in a.objects.values():
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  if not n or n in registered or not n.startswith(('Player','Person','Fatigue','MatchSharpness','Energy','Injury')):continue
  if any(k in n for k in ['Search','Recommendations','Tooltip','Database','Staff','AwayTeam','HomeTeam','OppositionTeam','HumanTeam']):continue
  t=o.read_typetree();configs=t.get('<Configurations>k__BackingField',[])
  if not configs:continue
  registered.add(n);name=t.get('<Name>k__BackingField',n)
  extras.append({'name':name,'chinese':cn.get(name,name),'resource':n,'path_id':o.path_id,'sizes':list(dict.fromkeys(f"{c['Size']['x']}×{c['Size']['y']}" for c in configs)),'configurations':configs})
if extras:sets.append({'name':'OtherPackagedPlayerModules','page':'其他已打包球员模块（不代表已注册到当前概览菜单）','modules':sorted(extras,key=lambda r:r['resource'])})
out=R/'球员页面模块与尺寸清单';out.mkdir(exist_ok=True)
(out/'模块原始配置.json').write_text(json.dumps({'source':str(files[0]),'sha256':hashlib.sha256(files[0].read_bytes()).hexdigest(),'sets':sets},ensure_ascii=False,indent=2),encoding='utf8')
lines=['# 当前游戏球员页面模块与尺寸','', '尺寸表示网格列×行，不是像素。以下直接读取当前F盘游戏包；可见性还受页面、球员状态和模块条件限制。','']
for s in sets:
 lines+=['## '+s['page']+'（'+s['name']+'）','', '| 模块 | 内部名称 | 支持尺寸 |','|---|---|---|']
 for r in s['modules']:lines.append('| '+r['chinese']+' | `'+r['resource']+'` | '+ '、'.join(r['sizes'])+' |')
 lines.append('')
(out/'球员页面模块清单.md').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps([{'page':s['page'],'count':len(s['modules']),'rows':[(r['chinese'],r['name'],','.join(r['sizes'])) for r in s['modules']]} for s in sets],ensure_ascii=False))
