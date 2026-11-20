"""Prepare a reversible FM27 match UI patch from the currently installed bundles."""
from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,struct,uuid,importlib.util
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
PYTHON=Path(sys.executable)
OUT=R/('match-ui-avatars-layout-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();(OUT/'templates').mkdir()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
F='ui-tablefactories_assets_all.bundle'
NAMES=[W,G,M,F]
sha=lambda b:hashlib.sha256(b).hexdigest()
before={};missing=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for n in NAMES:
  p=folder/n
  if p.exists():
   before[p]=p.read_bytes();bp=OUT/('backup-'+tag)/n;bp.parent.mkdir(exist_ok=True);bp.write_bytes(before[p])
  else:missing.append(p)
for n in NAMES:
 if SKIN/n in before:assert before[SKIN/n]==before[GAME/n],('game/skin diverged',n)
for p,tag in [(GAME.parent/'catalog.bin','game'),(GAME.parent/'catalog.hash','game'),(SKIN/'catalog.bin','skin'),(SKIN/'catalog.hash','skin')]:
 if p.exists():before[p]=p.read_bytes();(OUT/('backup-'+tag)/p.name).write_bytes(before[p])
 else:missing.append(p)
assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name not in NAMES}
env={n:UnityPy.load(before[GAME/n]) for n in NAMES}
objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in objs.items()}
changes={n:{} for n in env};documents=[];clones=[];audits=[]
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))

def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def sd(r,i):return r.get(r[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def find(n,name):return next(o for o in objs[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def pointer_remap(value,source_af,target_af):
 if isinstance(value,dict):
  if set(value)=={'m_FileID','m_PathID'} and value['m_FileID']>0:
   name=source_af.externals[value['m_FileID']-1].name
   matches=[i+1 for i,x in enumerate(target_af.externals) if x.name.lower()==name.lower()]
   if not matches:target_af.externals.append(copy.copy(source_af.externals[value['m_FileID']-1]));matches=[len(target_af.externals)]
   value['m_FileID']=matches[0]
  else:
   for x in value.values():pointer_remap(x,source_af,target_af)
 elif isinstance(value,list):
  for x in value:pointer_remap(x,source_af,target_af)

def import_types(source,target,records):
 needed={(x['type']['class'],x['type']['ns'],x['type']['asm']) for x in records if x.get('type',{}).get('class')}
 known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in target.ref_types}
 for t in source.ref_types:
  key=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
  if key in needed and key not in known:target.ref_types.append(copy.copy(t));known.add(key)
 assert needed<=known,needed-known

class Doc:
 def __init__(self,n,name=None,pid=None,tree=None,style=None):
  self.n=n;self.obj=objs[n][pid] if pid is not None else find(n,name);self.af=self.obj.assets_file
  self.d=copy.deepcopy(tree) if tree else self.obj.read_typetree();self.sid=self.d['inlineSheet']['m_PathID'];self.s=copy.deepcopy(style) if style else objs[n][self.sid].read_typetree();self.r=refs(self.d)
  self.nr=max(self.r)+1;self.nid=max(x.get('data',{}).get('m_Id',0) for x in self.r.values())+1
 def named(self,name):return next(i for i,x in self.r.items() if 'm_Parent' in x.get('data',{}) and self.data(i).get('name')==name)
 def data(self,i):return sd(self.r,i)
 def a(self,i):return self.r[i]['data']
 def val(self,t,v):
  self.s[poolmap[t]].append(v);return {'m_ValueType':t,'valueIndex':len(self.s[poolmap[t]])-1}
 def px(self,v):return self.val(3,{'unit':1,'value':float(v)})
 def pct(self,v):return self.val(3,{'unit':2,'value':float(v)})
 def enum(self,v):return self.val(7,v)
 def num(self,v):return self.val(2,float(v))
 def st(self,i,props):
  a=self.a(i);ps=copy.deepcopy(self.s['m_Rules'][a['m_RuleIndex']]['m_Properties']) if a.get('m_RuleIndex',-1)>=0 else []
  keys={k for k,v in props};ps=[p for p in ps if p['m_Id'] not in keys]+[{'m_Id':k,'m_CustomName':'','m_Line':-1,'m_Values':v if isinstance(v,list) else [v]} for k,v in props]
  self.s['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':ps,'line':-1});a['m_RuleIndex']=len(self.s['m_Rules'])-1
 def size(self,i,w,h):self.st(i,[(131105,self.px(w)),(131087,self.px(h)),(131097,self.px(w)),(131096,self.px(h)),(131095,self.px(w)),(131094,self.px(h)),(131084,self.num(0)),(131085,self.num(0))])
 def fill(self,i):self.st(i,[(131105,self.pct(100)),(131087,self.pct(100)),(131097,self.px(0)),(131096,self.px(0)),(131084,self.num(1)),(131085,self.num(1))])
 def move(self,i,parent,index=None):
  old=self.a(i)['m_Parent']['rid'];self.a(old)['m_Children'].remove({'rid':i});self.a(i)['m_Parent']={'rid':parent}
  if index is None:self.a(parent)['m_Children'].append({'rid':i})
  else:self.a(parent)['m_Children'].insert(index,{'rid':i})
 def add(self,source,sourceid,parent,name):
  a=copy.deepcopy(source.r[sourceid]);s=copy.deepcopy(source.r[source.a(sourceid)['m_SerializedData']['rid']]);a['rid']=self.nr;s['rid']=self.nr+1;self.nr+=2
  a['data'].update(m_Id=self.nid,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_SerializedData={'rid':s['rid']})
  s['data'].update(uxmlAssetId=self.nid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);self.nid+=1
  for x in [a,s]:pointer_remap(x,source.af,self.af);self.r[x['rid']]=x;self.d['references']['RefIds'].append(x)
  import_types(source.af,self.af,[a,s]);self.a(parent)['m_Children'].append({'rid':a['rid']});return a['rid']
 def using(self,source,alias):
  u=next(u for u in source.d['m_Usings'] if u['alias']==alias)
  if not any(x['alias']==alias for x in self.d['m_Usings']):self.d['m_Usings'].append(copy.deepcopy(u))
 def save(self):
  validate_ui(self.d,self.s)
  for pid,d in [(self.obj.path_id,self.d),(self.sid,self.s)]:objs[self.n][pid].save_typetree(d);changes[self.n][pid]=copy.deepcopy(d)
  (OUT/'templates'/(self.d['m_Name']+'.json')).write_text(json.dumps(self.d,ensure_ascii=False,indent=2),'utf8')
  documents.append(self)

portrait=Doc(W,pid=-4028782843705546248)
VE=next(i for i,x in portrait.r.items() if x.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement')
remapdonor=Doc(W,name='PlayerKitNameCell')
REMAP=1007
PIC=next(i for i,x in portrait.r.items() if x.get('data',{}).get('m_TemplateAlias')=='PersonPicture')
textdonor=Doc(W,name='SquadOverviewPlayerBlock')
TEXT=1068
def ve(doc,parent,name,w=None,h=None):
 i=doc.add(portrait,VE,parent,name)
 if w is not None:doc.size(i,w,h)
 return i
def mapper(doc,parent,path,name):
 i=doc.add(remapdonor,REMAP,parent,name);doc.data(i).update(Mappings=[{'m_serialisedType':0,'from':'person','to':{'m_path':path},'type':{'id':1145176065}}],Mappings_UxmlAttributeFlags=1);return i
def picture(doc,parent,path,size,name):
 m=mapper(doc,parent,path,name+'Binding');doc.size(m,size,size);p=doc.add(portrait,PIC,m,name);doc.using(portrait,'PersonPicture');doc.fill(p);return m,p
def replace_shirt(doc,shirt,path,size):
 parent=doc.a(shirt)['m_Parent']['rid'];doc.st(shirt,[(458767,doc.num(0)),(131102,doc.enum('absolute'))]);m,p=picture(doc,parent,path,size,'MatchPlayerPortrait')
 # Keep native status overlays last in paint order.
 doc.move(m,parent,0);return m,p
def boundtext(doc,parent,name,path):
 i=doc.add(textdonor,TEXT,parent,name);s=doc.data(i);s['TextBinding']={'m_kind':1,'m_direct':{'Path':{'m_path':path},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}};s['TextBinding_UxmlAttributeFlags']=1;s['DebugDisplay']='';doc.a(i)['m_Classes']=['body-sm','content-ellipsis'];return i

# 1. Prematch home and away starting and substitute rows; the native person map is retained.
for name in ['HomePlayersListRow','AwayPlayersListRow','HomeSubPlayersListRow','AwaySubPlayersListRow']:
 d=Doc(M,name=name);root=next(i for i,x in d.r.items() if x.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindingExpect')
 m,p=picture(d,root,'Player.Player',20,'PrematchPlayerPortrait');d.move(m,root,0);d.st(m,[(131090,d.px(5)),(131093,d.px(5))]);d.save()
d=Doc(M,name='TeamNewsPanel_DisplayingMatchSquad');m,p=picture(d,1065,'match.MatchReferee',28,'RefereePortrait');d.move(m,1065,0);d.st(1065,[(131083,d.enum('row')),(131073,d.enum('center'))]);d.st(m,[(131090,d.px(6))]);d.save()

# Private copies keep the interview change local even though its sender is a shared template.
def clone_doc(n,name,newname,docpid,stylepid):
 src=Doc(n,name=name);tree=copy.deepcopy(src.d);style=copy.deepcopy(src.s);tree['m_Name']=newname;tree['inlineSheet']['m_PathID']=stylepid;style['m_Name']=newname+'_Style'
 for source,pid,data in [(src.obj,docpid,tree),(objs[n][src.sid],stylepid,style)]:
  assert pid not in objs[n];o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o;objs[n][pid]=o;o.save_typetree(data)
 guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/match-ui/'+newname).hex
 clones.append({'bundle':n,'guid':guid,'source_pid':src.obj.path_id,'pid':docpid,'style':stylepid})
 return Doc(n,pid=docpid,tree=tree,style=style),guid
# 2. Isolate the team-talk name cell from individual-shout and other shared kit-name rows.
talk,tg=clone_doc(W,'PlayerKitNameCell','MatchTeamTalkPortraitNameCell',-980000000001030,-980000000001031)
replace_shirt(talk,1013,'matchplayer.Person',24);talk.save()
fo=find(F,'TeamTalkPlayerReactionTableFactory');fd=fo.read_typetree();namecol=next(c for c in fd['m_rowData'] if c['m_id']=='name');assert namecol['m_uxmlRef']['m_AssetGUID']=='70c87009add8c3047acf2b3fc12457d1';namecol['m_uxmlRef']['m_AssetGUID']=tg;fo.save_typetree(fd);changes[F][fo.path_id]=fd
sender,sg=clone_doc(G,'interaction-hub-body-message_sender-primary','MatchTunnelManagerSender',-980000000001000,-980000000001001)
sender.size(1004,100,100);sender.st(1002,[(131096,sender.px(100)),(131073,sender.enum('center'))]);sender.save()
speak,spg=clone_doc(W,'MeetingSpeakToContainer','MatchTunnelSpeakToContainer',-980000000001010,-980000000001011)
next(u for u in speak.d['m_Usings'] if u['alias']=='interaction-hub-body-message_sender-primary')['path']=sg;speak.save()
meeting,mg=clone_doc(G,'FigmaBaseMeetingTemplate','MatchTunnelMeetingTemplate',-980000000001020,-980000000001021)
next(u for u in meeting.d['m_Usings'] if u['alias']=='MeetingSpeakToContainer')['path']=spg;meeting.save()
d=Doc(M,name='TunnelInterviewPanel');next(u for u in d.d['m_Usings'] if u['alias']=='FigmaBaseMeetingTemplate')['path']=mg;d.save()

# 4. The scoreboard stays in the header, and the controls flow with the footer height.
d=Doc(M,name='OverviewHeader');d.a(1034)['m_Classes']=[c for c in d.a(1034)['m_Classes'] if c!='centre-avoid-centred']
d.st(1034,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.px(-4)),(131074,d.enum('flex-start'))]);d.st(1096,[(131081,d.enum('none'))]);d.save()
toolbar_source=Doc(M,name='MatchUITacticalOptions')
for i,x in toolbar_source.r.items():
 if x.get('data',{}).get('m_FullTypeName') in ['SI.Bindable.SIDropdown','SI.Bindable.SIFloatingPopupWidget']:
  s=toolbar_source.data(i);s.update(Anchor=5,Anchor_UxmlAttributeFlags=1)
toolbar_source.save()
d=Doc(M,name='SquadOverview');host=ve(d,1009,'MatchBottomTacticalToolbar');d.move(host,1009,0)
d.st(host,[(131074,d.enum('stretch')),(131083,d.enum('row')),(131088,d.enum('flex-end')),(131087,d.px(40)),(131085,d.num(0)),(131093,d.px(32)),(131080,d.px(6))])
rem=d.add(remapdonor,REMAP,host,'MatchBottomToolbarBindings');d.data(rem).update(Mappings=[{'m_serialisedType':0,'from':key,'to':{'m_path':value},'type':{'id':0}} for key,value in [('human','game.GameCurrentManager'),('team','match.MatchHumanTeam'),('comp','match.Competition'),('tactic','match.Tactic')]],Mappings_UxmlAttributeFlags=1)
h=Doc(M,name='OverviewHeader');inst=d.add(h,1096,rem,'MatchBottomTacticalOptions');d.using(h,'MatchUITacticalOptions');d.save()

# Existing 101-step condition tree supplies exact live values and native missing-value handling.
ringdonor=Doc(W,pid=-930000000001001);RINGROOT=ringdonor.named('OverviewFitness_Condition_Available')
def rewrite_arg(raw,old,new):
 b=bytes(raw)
 if not b:return raw
 p=1;args=[]
 for _ in range(b[0]):
  l=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+l]);p+=l
 assert p==len(b)
 old=old.encode();new=new.encode();args=[a.replace(bytes([len(old)])+old,bytes([len(new)])+new) for a in args]
 return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
def rewrite_binding(v,old,new):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='m_argumentBytes' and x:v[k]=rewrite_arg(x,old,new)
   elif isinstance(x,str):v[k]=x.replace(old,new)
   else:rewrite_binding(x,old,new)
 elif isinstance(v,list):
  for x in v:rewrite_binding(x,old,new)
def condition(doc,parent,path,compact=False):
 ring=22;height=ring if compact else 36;width=ring if compact else 28
 def cp(old,par):
  i=doc.add(ringdonor,old,par,ringdonor.data(old).get('name','').replace('OverviewFitness_Condition','MatchCondition'));doc.fill(i);s=doc.data(i);rewrite_binding(s,'person.Condition',path)
  name=s.get('name','')
  if 'Binding' in s:doc.st(i,[(131083,doc.enum('column'))])
  if '_Percent' in name or '_Missing' in name:
   doc.st(i,[(131083,doc.enum('column')),(131073,doc.enum('center')),(131088,doc.enum('flex-start'))])
  if '_Ring' in name or name.endswith('MissingRing'):
   props=ringdonor.s['m_Rules'][ringdonor.a(old)['m_RuleIndex']]['m_Properties'];pr=next(p for p in props if p['m_Id']==458753);ptr=copy.deepcopy(ringdonor.s['assets'][pr['m_Values'][0]['valueIndex']]);pointer_remap(ptr,ringdonor.af,doc.af)
   doc.size(i,ring,ring);doc.st(i,[(458753,doc.val(6,ptr)),(262153,doc.enum('scale-to-fit')),(131102,doc.enum('relative')),(131089,doc.px(0)),(131104,doc.px(0))])
  if '_Number' in name or name.endswith('MissingNumber'):
   doc.size(i,width,12 if not compact else ring);doc.a(i)['m_Classes']=['body-sm','text-middle-center'];doc.st(i,[(65537,doc.px(10 if not compact else 8)),(65546,doc.enum('middle-center')),(131102,doc.enum('absolute' if compact else 'relative')),(131089,doc.px(0)),(131104,doc.px(0))])
  for c in ringdonor.a(old)['m_Children']:cp(c['rid'],i)
  return i
 root=cp(RINGROOT,parent);doc.size(root,width,height)
 if compact:doc.size(root,ring,ring)
 # All switch paths must use the live match-player scope.
 return root

role_source=Doc(W,name='PlayerPickedRoleCellInMatch')
def rolelabel(doc,parent):
 # Native tactical index lookup already observes substitutions and pending role changes.
 rem=doc.add(role_source,1006,parent,'MatchCardPositionBinding');doc.data(rem)['Mappings_UxmlAttributeFlags']=1
 rv=doc.add(role_source,1029,rem,'MatchCardRoleAndDuty');txt=doc.add(role_source,1033,rv,'MatchCardRoleAndDutyText')
 # Native full tactical-role description includes the game's role/duty wording.
 rewrite_binding(doc.data(txt),'[%tactical_role#1-short]','[%tactical_role#1]')
 doc.a(txt)['m_Classes']=['body-sm','content-ellipsis'];doc.st(txt,[(65537,doc.px(10)),(65546,doc.enum('middle-center')),(131074,doc.enum('stretch'))])
 doc.st(rem,[(131087,doc.px(16)),(131085,doc.num(0)),(131074,doc.enum('stretch'))]);return rem

# 5. Both responsive expanded card variants serve first-team and substitute lists.
for name,shirt,frame,hero,goal,assist,mid in [('SquadOverviewPlayerBlock',1084,1063,1028,1042,1044,1043),('SquadOverviewPlayerBlockSmall',1076,1061,1028,1042,1044,1043)]:
 d=Doc(W,name=name);small=name.endswith('Small');size=36 if small else 44;replace_shirt(d,shirt,'person',size);d.size(frame,size,size)
 d.st(1016,[(131087,d.px(140)),(131096,d.px(140)),(131088,d.enum('flex-start')),(262151,[d.px(0),d.px(8),d.px(8),d.px(8)]),(131085,d.num(0))])
 rr=rolelabel(d,1016);d.move(rr,1016,0)
 d.st(1021,[(131087,d.px(72)),(131073,d.enum('center')),(131088,d.enum('space-between'))])
 d.st(hero,[(131087,d.px(48)),(131074,d.enum('stretch')),(131088,d.enum('center')),(131102,d.enum('relative'))])
 for i,top in [(goal,0),(assist,26)]:d.size(i,14,16);d.st(i,[(131102,d.enum('absolute')),(131103,d.px(0)),(131104,d.px(top))])
 d.st(mid,[(131074,d.enum('center')),(131085,d.num(0))])
 root=condition(d,hero,'playerinfo.Condition');d.st(root,[(131102,d.enum('absolute')),(131089,d.px(-4 if small else 0)),(131104,d.px(4))])
 d.st(1022,[(131087,d.px(38)),(131098,d.px(6)),(131085,d.num(0))]);d.save()

# 6. Actual live match formation markers, with injuries/cards and role/rating left intact.
d=Doc(G,name='TacticsMatchPositionFilled');replace_shirt(d,1037,'position.MatchPlayer.Person',36);d.size(1017,36,36);d.st(1008,[(458768,d.enum('visible'))]);root=condition(d,1017,'position.MatchPlayer.Condition',True)
d.st(root,[(131102,d.enum('absolute')),(131089,d.px(-9)),(131104,d.px(-5))]);d.save()

# Update only the preload spans of changed templates and add the three private templates.
def allptr(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   if v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():allptr(x,out)
 elif isinstance(v,list):
  for x in v:allptr(x,out)
for n in [W,G,M]:
 mo=next(o for o in objs[n].values() if o.type.name=='AssetBundle');meta=mo.read_typetree()
 for d in [d for d in documents if d.n==n]:
  c=next((c for c in clones if c['pid']==d.obj.path_id),None)
  entries=[entry for key,entry in meta['m_Container'] if entry['asset']['m_PathID']==d.obj.path_id]
  if c:
   entry={'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':d.obj.path_id}};meta['m_Container'].append((c['guid'],entry));entries=[entry]
  for entry in entries:
   span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]) if not c else []
   allptr(d.d,span);allptr(d.s,span)
   ptr={'m_FileID':0,'m_PathID':d.obj.path_id}
   if ptr not in span:span.append(ptr)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 meta['m_Container'].sort(key=lambda kv:kv[0]);mo.save_typetree(meta);changes[n][mo.path_id]=meta

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin']
for c in clones:
 mo=next(o for o in objs[c['bundle']].values() if o.type.name=='AssetBundle');meta=mo.read_typetree();sourcekey=next(key for key,entry in meta['m_Container'] if entry['asset']['m_PathID']==c['source_pid'])
 cat=cm.Catalog(catalog);loc=cat.locations(sourcekey)[0];catalog=cat.add_key_location(c['guid'],loc,loc)
cat=cm.Catalog(catalog)
for key,n in [('GameWorldVisualTreeAssetPreload',W),('GlobalVisualTreeAssetPreload',G)]:
 additions=[cat.locations(c['guid'])[0] for c in clones if c['bundle']==n]
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==key);ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+additions;records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cat=cm.Catalog(bytes(cat.data))
catalog=bytes(cat.data);oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);newcat=cm.Catalog(catalog)
assert set(dict(newcat.keys()))==set(dict(oldcat.keys()))|{c['guid'] for c in clones}
nk=dict(newcat.keys())
for key,loc in oldcat.keys():
 expected=[x[0] for x in oldcat.array(loc,'I')]
 if key in ['GameWorldVisualTreeAssetPreload','GlobalVisualTreeAssetPreload']:
  bundle=W if key=='GameWorldVisualTreeAssetPreload' else G;expected += [newcat.locations(c['guid'])[0] for c in clones if c['bundle']==bundle]
 assert [x[0] for x in newcat.array(nk[key],'I')]==expected,('catalog location changed',key)
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changes[n]:assert sha(check[i].get_raw_data())==h,('unrelated object modified',n,i)
 for i,data in changes[n].items():assert check[i].read_typetree()==data,('roundtrip failed',n,i)
 for d in [d for d in documents if d.n==n]:validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
 (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catalog);(OUT/'catalog.hash').write_bytes(hashlib.md5(catalog).hexdigest().encode('ascii'))
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'changes':{n:{str(pid):d.get('m_Name','AssetBundle') for pid,d in ps.items()} for n,ps in changes.items()},'clones':clones,'card_order':['position','native_role_and_duty_description','portrait_with_condition_left','name','status_rating_body_language'],'condition_binding':['playerinfo.Condition','position.MatchPlayer.Condition'],'condition_scale':'same 0..100 UI value; native missing handling','manager_portrait_size':100,'reporter_reference_size':100,'bottom_rating_margin_top':6,'menus_anchor':{'TopRight':5},'unrelated_objects_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'missing_before':[str(p) for p in missing],'protected_sha256':{str(p):h for p,h in protected.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()}|{'catalog.bin':sha(catalog),'catalog.hash':sha((OUT/'catalog.hash').read_bytes())}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs)+['catalog.bin','catalog.hash'],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[str(p) for p in missing]},ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b,('installation changed during build',p)
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'output':str(OUT),'changed_objects':{n:len(v) for n,v in changes.items()},'clones':len(clones)},ensure_ascii=False))
