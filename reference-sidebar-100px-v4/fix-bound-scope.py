"""Move the sidebar gate into the bound navigation hierarchy."""
from pathlib import Path
import ast,copy,hashlib,json,re,shutil,struct,sys
V=Path(__file__).resolve().parent;R=V.parent
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 a=ast.parse((R/name).read_text('utf8'));exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in wanted],type_ignores=[]),name,'exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
location=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(location['bundle_root'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
oldmanifest=json.loads((V/'manifest.json').read_text('utf8'));oldtx=json.loads((V/'transaction.json').read_text('utf8'))
for row in oldtx:assert sha(Path(row['target']).read_bytes())==row['after'],row['target']
envs={n:UnityPy.load(str(GAME/n)) for n in [W,D]};oo={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in oo.items()};expected={n:{} for n in envs}
def named(n,name):return next(o for o in oo[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def serial(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def save(n,o,d):o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
ge=UnityPy.load(str(GAME/G));gatesource=next(o.read_typetree() for o in ge.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MainUIDocument');gr=refs(gatesource)
obj=named(W,'PrimaryNavigationBar');d=obj.read_typetree();rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=oo[W][sid].read_typetree();st=Styles(sheet)
instance=next(i for i in rr if serial(rr,i).get('name')=='TFReferenceSidebar');assert rr[instance]['data']['m_Parent']['rid']==1002
gate=copy.deepcopy(gr[2000]);gs=copy.deepcopy(gr[2001]);ei=max(rr)+1;si=ei+1;eid=1910314300
gate['rid']=ei;gs['rid']=si
gate['data'].update(m_Id=eid,m_Parent={'rid':1002},m_Children=[{'rid':instance}],m_RuleIndex=-1,m_Classes=['tf-reference-sidebar-mount'],m_SerializedData={'rid':si})
gs['data'].update(uxmlAssetId=eid,name='TFReferenceSidebarBoundScope',name_UxmlAttributeFlags=1)
def s7(s):
 b=s.encode('utf8');n=len(b);x=bytearray()
 while n>=128:x.append((n&127)|128);n>>=7
 return bytes(x)+bytes([n])+b
def packargs(a):return bytes([len(a)])+b''.join(struct.pack('<I',len(v))+v for v in a)
def abool(v):return s7('SI.VisualScripting.BooleanVisualArg')+bytes([v])
args=s7('SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BooleanArg]')+b'\x02'+b''.join(b'\x01'+s7(p)+b'\x01' for p in ['game.IsViewingMatch','game.IsDuringMatch'])
enum=s7('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.VisibleFunctions+LogicOperator]')+struct.pack('<i',0)
string=s7('SI.VisualScripting.StringVisualArg')+b'\x01'+s7('tf-reference-sidebar-active')
gs['data']['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(packargs([args,enum,string,abool(False),abool(False)]))
rr[instance]['data']['m_Parent']={'rid':ei};rr[1002]['data']['m_Children']=[{'rid':ei} if x['rid']==instance else x for x in rr[1002]['data']['m_Children']]
d['references']['RefIds'].extend([gate,gs]);st.edit(gate,[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.px(0)),st.p(131105,st.px(100)),st.p(131087,st.px(3000))])
validate_ui(d,sheet);save(W,obj,d);save(W,oo[W][sid],sheet)

style=named(D,'AlwaysAppliedStyleSheet');dd=style.read_typetree();st=Styles(dd)
first=next(i for i,r in enumerate(dd['m_Rules']) if 'tf-reference-sidebar' in json.dumps(r['m_ComplexSelectors']))
assert len(dd['m_Rules'])-first==8
default=copy.deepcopy(dd['m_Rules'][first]);active=copy.deepcopy(dd['m_Rules'][first+1]);dd['m_Rules']=dd['m_Rules'][:first]
def addrule(chain,props):
 i=len(dd['m_Rules']);sels=[{'m_Parts':[{'m_Value':n,'m_Type':t} for n,t in part],'m_PreviousRelationship':0 if j==0 else 2} for j,part in enumerate(chain)];specificity=1+sum(100 if t==6 else 10 for p in chain for _,t in p)
 dd['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':specificity,'m_Selectors':sels,'ruleIndex':i}],'m_Properties':props,'line':-1})
for q in [default,active]:
 for s in q['m_ComplexSelectors']:s['ruleIndex']=len(dd['m_Rules'])
 dd['m_Rules'].append(q)
# Match pages keep their full containing-block geometry; only ordinary flow children get padding.
# The layer bounds, minimum sizes and grid-breakpoint width remain native.
for name in ['MenuBody','ReportBody','Report']:
 addrule([[(name,6)]],[st.p(131099,st.px(100))])
addrule([[('tf-reference-header-controls',3)]],[st.p(131099,st.px(100))])
addrule([[('TitleBarBindingRoot',6)],[('SecondaryNavigationBar',6)]],[st.p(131099,st.px(100))])
addrule([[('TitleBarBindingRoot',6)],[('SecondaryNavigationBar',6)],[('Bookmarks',6)]],[st.p(131081,st.en('none'))])
matchpanels={}
for bn in ['ui-panelids_assets_all.bundle','ui-match_assets_all.bundle']:
 for o in UnityPy.load(str(GAME/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  t=o.read_typetree();p=t.get('m_panelDescription',{});layer=p.get('layer',{}).get('Name');name=t.get('m_Name','')
  if layer not in ['MenuBody','ReportBody','Report']:continue
  if bn=='ui-match_assets_all.bundle' or re.search('match|onthepitch|teamtalk|shootout|penalt|fullscreenteamselection|fmmenu|ige',name,re.I):matchpanels[name]=layer
for name,layer in sorted(matchpanels.items()):
 addrule([[(layer,6)],[(name,6)]],[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131103,st.px(0)),st.p(131104,st.px(0)),st.p(131075,st.px(0)),st.p(131105,st.pct(100)),st.p(131087,st.pct(100))])
assert 'FullScreenTeamSelection' in matchpanels and 'PostMatchNewsPanel' in matchpanels
save(D,style,dd)
outputs={}
for n,e in envs.items():
 raw=e.file.save(packer='lz4');loaded={o.path_id:o for o in UnityPy.load(raw).objects};assert set(loaded)==set(oo[n])
 for i,o in loaded.items():
  if i in expected[n]:assert o.read_typetree()==expected[n][i],(n,i)
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
 outputs[GAME/n]=raw
outputs[GAME/G]=(V/'backup-game'/G).read_bytes()
out=V/'bound-scope-fix';out.mkdir(exist_ok=False);(out/'packages').mkdir();(out/'backup-game').mkdir();tx=[]
for target,b in outputs.items():
 source=out/'packages'/target.name;backup=out/'backup-game'/target.name;source.write_bytes(b);old=target.read_bytes();backup.write_bytes(old);tx.append({'target':str(target),'source':str(source),'backup':str(backup),'before':sha(old),'after':sha(b)})
protected={p:sha(Path(p).read_bytes()) for p in oldmanifest['source_preparation_hashes'] if Path(p) not in outputs}
record={'version':'V4 bound navigation scope correction','installed':False,'runtime_verified':False,'main_uidocument_restored':True,'native_bound_parent':'PrimaryNavigationBar/MainNav','sidebar_width':100,'display_conditions':['not game.IsViewingMatch','not game.IsDuringMatch'],'common_layer_bounds_and_min_sizes_unchanged':True,'page_scale_unchanged':True,'native_match_templates_unchanged':True,'match_panel_full_width_rules':matchpanels,'protected_sha256':protected,'known_limitations':['Runtime visibility, match layout and click behavior still require testing; no live game UI inspection is available.']}
(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(V/'installer.py',out/'installer.py')
for name,flag in [('install',''),('restore-v4',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
full=out/'full-rollback';full.mkdir();orig=copy.deepcopy(oldtx)
for row in orig:
 if Path(row['target']) in outputs:row.update(source=str(out/'packages'/Path(row['target']).name),after=sha(outputs[Path(row['target'])]))
targets={Path(x['target']) for x in orig};fp={p:h for p,h in protected.items() if Path(p) not in targets}
(full/'transaction.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':fp},ensure_ascii=False,indent=2),'utf8');shutil.copyfile(out/'installer.py',full/'installer.py')
(out/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
log=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log');shutil.copyfile(log,out/'Player-before-bound-scope-fix.log')
print(json.dumps({'output':str(out),'changed_files':len(tx),'bound_scope':True,'main_uidocument_restored':True,'native_match_templates_unchanged':True,'match_full_width_rules':len(matchpanels),'runtime_verified':False},ensure_ascii=False))
