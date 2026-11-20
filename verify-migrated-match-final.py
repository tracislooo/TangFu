from pathlib import Path
import sys,json,struct,hashlib,ast
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
env={n:UnityPy.load(str(out/n)) for n in m['after_sha256']};obs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
def doc(n,name):
 o=next(o for o in obs[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name);d=o.read_typetree();s=obs[n][d['inlineSheet']['m_PathID']].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};validate_ui(d,s);return d,s,r
def data(r,i):return r.get(r[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(r,name):return next(i for i in r if 'm_Parent' in r[i].get('data',{}) and data(r,i).get('name')==name)
def prop(s,r,i,k):
 a=r[i]['data'];p=next(p for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties'] if p['m_Id']==k);v=p['m_Values'][0];return s[poolmap[v['m_ValueType']]][v['valueIndex']]
def px(s,r,i,k):return prop(s,r,i,k)['value']
def args(raw):
 b=bytes(raw);p=1;ret=[]
 for _ in range(b[0]):l=struct.unpack_from('<I',b,p)[0];p+=4;ret.append(b[p:p+l]);p+=l
 assert p==len(b);return ret
for name in ['HomePlayersListRow','HomeSubPlayersListRow']:
 d,s,r=doc(M,name);i=named(r,'PrematchPlayerPortraitBinding');p=r[i]['data']['m_Parent']['rid'];assert r[p]['data']['m_Children'][-1]['rid']==i
for name in ['AwayPlayersListRow','AwaySubPlayersListRow']:
 d,s,r=doc(M,name);i=named(r,'PrematchPlayerPortraitBinding');p=r[i]['data']['m_Parent']['rid'];assert r[p]['data']['m_Children'][0]['rid']==i
d,s,r=doc(G,'TacticsMatchPositionFilled');assert r[1005]['data']['m_Children']==[{'rid':1008},{'rid':1007}];assert prop(s,r,1005,131083)=='column';assert px(s,r,1008,131087)==px(s,r,1017,131087)==32
d,s,r=doc(M,'SquadOverview')
hosts=[i for i in r if 'm_Parent' in r[i].get('data',{}) and data(r,i).get('name','').startswith('MatchBottomTacticalToolbar')];assert len(hosts)==4
for host in hosts:
 assert prop(s,r,host,131102)=='absolute' and prop(s,r,host,131080)=={'unit':2,'value':100.0};assert px(s,r,host,131087)==px(s,r,host,131094)==px(s,r,host,131096)==32
 assert prop(s,r,host,131089)=='auto' and all(px(s,r,host,k)==0 for k in [131103,131090,131091,131092,131093])
 parent=r[host]['data']['m_Parent']['rid'];assert data(r,parent)['name'].startswith('MatchSubstitutesAnchor_');assert len(r[parent]['data']['m_Children'])==2
 sub=r[parent]['data']['m_Children'][0]['rid'];assert r[sub]['data']['m_FullTypeName']=='SI.Bindable.StreamedObjectList' and prop(s,r,sub,131105)=={'unit':2,'value':100.0}
cases=0
for n,name,icon,scope in [(W,'SquadOverviewPlayerBlock',1070,'playerinfo.Condition'),(W,'SquadOverviewPlayerBlockSmall',1083,'playerinfo.Condition'),(G,'TacticsMatchPositionFilled',None,'position.MatchPlayer.Condition')]:
 d,s,r=doc(n,name);root=named(r,'MatchCondition_Available')
 def select(i,v):
  if r[i]['data'].get('m_FullTypeName')!='SI.Bindable.BindableSwitchElement':return i
  ar=args(data(r,i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert ar[2].endswith(bytes([len(scope)])+scope.encode());limit=struct.unpack_from('<i',ar[1],len(ar[1])-4)[0];return select(r[i]['data']['m_Children'][int(v is not None and v>limit)]['rid'],v)
 for value in [None,-2147483648]+list(range(-1,122)):
  leaf=select(root,value);text=next(c['rid'] for c in r[leaf]['data']['m_Children'] if r[c['rid']]['data']['m_FullTypeName']=='SI.Bindable.SIText');expected=None if value is None or value<0 else min(100,value);assert data(r,text)['text']==('--' if expected is None else f'{expected}%');cases+=1
 if n==W:
  role=named(r,'MatchCardPositionBinding');rv=named(r,'MatchCardRoleAndDuty');children=[x['rid'] for x in r[1016]['data']['m_Children']];assert children==[1021,1022,role]
  assert px(s,r,1016,131087)==120 and 64+34+16+6==120
  assert r[root]['data']['m_Parent']['rid']==1032 and r[1032]['data']['m_Children'][0]['rid']==root and prop(s,r,root,131102)=='relative'
  assert prop(s,r,icon,131081)=='none'
  maps={v['from']:v['to']['m_path'] for v in data(r,role)['Mappings']};assert maps=={'tactic':'match.Tactic','binding':'playerinfo','teamselectionindex':'playerinfo.PlayerTeamSelectionIndex','inpossession':'const.True'}
  dynamic=json.loads(data(r,rv)['ValueVariables'][0]['m_scopeValue']['m_serializedData']);assert {v['BindingPath'] for v in dynamic['m_data']}=={'tactic.IPRole','inpossession'}
  assert len(r[1049 if icon==1070 else 1068]['data']['m_Children'])==2

print(json.dumps({'latest_match_layout_verified':True,'condition_cases':cases}))
