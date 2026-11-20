from pathlib import Path
import sys,json,struct,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
out=Path(sys.argv[1]);mf=json.loads((out/'manifest.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle';F='ui-tablefactories_assets_all.bundle'
base=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
files={n:UnityPy.load(str(out/n)) for n in [W,G,M,F]};objs={n:{o.path_id:o for o in e.objects} for n,e in files.items()}
def get(n,name):return next(o for o in objs[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name).read_typetree()
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def sd(r,i):return r.get(r[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def args(raw):
 b=bytes(raw);p=1;out=[]
 for _ in range(b[0]):l=struct.unpack_from('<I',b,p)[0];p+=4;out.append(b[p:p+l]);p+=l
 assert p==len(b);return out
def prop(d,s,rid,k):
 r=refs(d);a=r[rid]['data'];p=next(p for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties'] if p['m_Id']==k);v=p['m_Values'][0];return s[{2:'floats',3:'dimensions',6:'assets',7:'strings'}[v['m_ValueType']]][v['valueIndex']]
checks=[];live_cases=0;texture_refs=0
bg=UnityPy.load(str(base/'ui-backgrounds_assets_common.bundle'));baf=next(iter(bg.assets))
for n,name,path,compact in [(W,'SquadOverviewPlayerBlock','playerinfo.Condition',False),(W,'SquadOverviewPlayerBlockSmall','playerinfo.Condition',False),(G,'TacticsMatchPositionFilled','position.MatchPlayer.Condition',True)]:
 d=get(n,name);r=refs(d);s=objs[n][d['inlineSheet']['m_PathID']].read_typetree();root=next(i for i in r if sd(r,i).get('name')=='MatchCondition_Available')
 def select(i,raw):
  a=r[i]['data'];data=sd(r,i)
  if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
   ar=args(data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack_from('<i',ar[1],len(ar[1])-4)[0];assert ar[2].endswith(bytes([len(path)])+path.encode());return select(a['m_Children'][int(raw is not None and raw>limit)]['rid'],raw)
  return i
 for raw in [None,-2147483648]+list(range(-1,122)):
  i=select(root,raw);expected=None if raw is None or raw<0 else min(100,raw);name0=sd(r,i)['name'];assert name0==('MatchCondition_Missing' if expected is None else f'MatchCondition_Percent{expected:03}')
  children=[c['rid'] for c in r[i]['data']['m_Children']];text=next(j for j in children if r[j]['data']['m_FullTypeName']=='SI.Bindable.SIText');assert sd(r,text)['text']==('--' if expected is None else f'{expected}%');live_cases+=1
  ring=next(j for j in children if r[j]['data']['m_FullTypeName']=='UnityEngine.UIElements.VisualElement');ptr=prop(d,s,ring,458753);af=next(iter(files[n].assets));assert ptr['m_FileID']>0
  cab=af.externals[ptr['m_FileID']-1].name;assert cab.lower()==baf.name.lower();tex=baf.objects[ptr['m_PathID']];assert tex.peek_name()==('FM27StatusRingMissing000' if expected is None else f'FM27StatusRingCW{expected:03}');texture_refs+=1
 if not compact:
  named={sd(r,i).get('name'):i for i in r if 'm_Parent' in r[i].get('data',{})}
  assert prop(d,s,1022,131098)['value']==6
  assert 16+prop(d,s,1021,131087)['value']+prop(d,s,1022,131087)['value']+6+8<=prop(d,s,1016,131087)['value']
  assert 'MatchCardRoleAndDutyText' in named
  role=args(sd(r,named['MatchCardRoleAndDutyText'])['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert b'[%tactical_role#1]' in role[0]
 checks.append(name)
# Shared interview and team-talk templates must be exactly unchanged in the emitted bundles.
for n,name in [(G,'interaction-hub-body-message_sender-primary'),(G,'FigmaBaseMeetingTemplate'),(W,'MeetingSpeakToContainer'),(W,'PlayerKitNameCell')]:
 original=UnityPy.load(str(base/n));a=next(o for o in original.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);assert hashlib.sha256(a.get_raw_data()).hexdigest()==hashlib.sha256(objs[n][a.path_id].get_raw_data()).hexdigest()
d=get(G,'MatchTunnelManagerSender');s=objs[G][d['inlineSheet']['m_PathID']].read_typetree();assert prop(d,s,1004,131105)['value']==prop(d,s,1004,131087)['value']==100
toolbar=get(M,'MatchUITacticalOptions');r=refs(toolbar)
for i,x in r.items():
 if x.get('data',{}).get('m_FullTypeName') in ['SI.Bindable.SIDropdown','SI.Bindable.SIFloatingPopupWidget']:assert sd(r,i)['Anchor']==5 and sd(r,i)['Anchor_UxmlAttributeFlags']==1
assert get(F,'TeamTalkPlayerReactionTableFactory')['m_rowData'][0]['m_uxmlRef']['m_AssetGUID']==next(c['guid'] for c in mf['clones'] if c['pid']==-980000000001030)
result={'passed':True,'condition_cases':live_cases,'ring_texture_references_checked':texture_refs,'shared_templates_unchanged':4,'manager_portrait':100,'menus_open_up':True,'runtime_verified':False,'templates':checks}
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print(json.dumps(result))
