from pathlib import Path
import sys,json,re
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
OUT=R/'match-ui-research';OUT.mkdir(exist_ok=True)
names={'match':{'OverviewHeader','OverviewPrototype','SquadOverview','TeamNewsPanel_DisplayingMatchSquad','TeamTalkPanel','TunnelInterviewPanel','MatchUITacticalOptions','MatchUITacticalOptionsCompact','MatchCommentary'},'gameworld':{'SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall','SquadOverviewPlayerBlock-Compact','PlayerPortraitCell','PlayerShirtAndNameCell','TeamTalkBlock','FigmaBaseMeetingTemplate','MeetingSpeakToContainer','MeetingSpeakTo','MeetingPerson','PlayerTeamTalkPositionCell'},'global':{'TacticsMatchPositionFilled','TeamFormationAdaptiveBlock'}}
allnames=set().union(*names.values())|{'PlayerPickedRoleCellInMatch','PlayerPickedRoleCell','PlayerKitNameCell','FigmaBaseMeetingTemplate','interaction-hub-body-message_sender-primary','interaction-hub-body-message_sender-secondary','PersonPicture','PersonPictureWithCircleAndBG','thumbnails-alt-person-picture','PlayerShirtAndNameCell','PlayerShirtNameCell','PlayerShirtNameCellInMatch','HomePlayersListRow','AwayPlayersListRow','HomeSubPlayersListRow','AwaySubPlayersListRow'}
for key,ns in names.items():
 ns=allnames|{'MeetingJournalistHeader','MeetingStaffHeader','JournalistPressConferenceCell'}
 e=UnityPy.load(str(GAME/f'ui-visualtreeassets_assets_{key}visualtreeassetpreload.bundle'));obs={o.path_id:o for o in e.objects}
 for o in obs.values():
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  if n not in ns:continue
  d=o.read_typetree();s=obs[d['inlineSheet']['m_PathID']].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
  (OUT/f'{n}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  def style(a):
   if a.get('m_RuleIndex',-1)<0:return []
   ret=[]
   for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']:
    vals=[]
    for v in p['m_Values']:
     pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(v['m_ValueType'])
     vals.append(s[pool][v['valueIndex']] if pool else v)
    ret.append((p['m_Id'],vals))
   return ret
  lines=[f'{key} {n} PathID={o.path_id} Style={d["inlineSheet"]["m_PathID"]}',f'USINGS {d["m_Usings"]}']
  def clean(v):
   if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
   if isinstance(v,list):
    if len(v)>20 and all(isinstance(x,int) for x in v):return re.findall(r'[ -~]{4,}',bytes(v).decode('latin1'))
    return [clean(x) for x in v]
   return v
  def walk(i,dep=0):
   a=r[i].get('data',{});sd=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   vals={k:v for k,v in sd.items() if not k.endswith('UxmlAttributeFlags') and k not in ['uxmlAssetId','dataSourceUnityObject','dataSourcePathString','dataSourceTypeString','bindings'] and v not in [None,'',0,[],{},False]}
   lines.append(' '*dep+f'{i} {a.get("m_FullTypeName") or a.get("m_TemplateAlias")} CLASS={a.get("m_Classes")} '+json.dumps(clean(vals),ensure_ascii=False))
   lines.append(' '*dep+'STYLE '+json.dumps(style(a),ensure_ascii=False))
   for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
  walk(d['m_VisualTree']['rid']);(OUT/f'{n}.txt').write_text('\n'.join(lines),'utf8')
print(str(OUT))
