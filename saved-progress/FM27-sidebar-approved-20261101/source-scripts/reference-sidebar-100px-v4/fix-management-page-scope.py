"""Use the donor location and offset only named ordinary management panel containers."""
from pathlib import Path
import ast,copy,hashlib,json,re,shutil,struct,sys
V=Path(__file__).resolve().parent;R=V.parent;REF=Path('K:/桌面/Skin files')
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 a=ast.parse((R/name).read_text('utf8'));exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in wanted],type_ignores=[]),name,'exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
GAME=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle'
prior=V/'bound-scope-fix';ptx=json.loads((prior/'transaction.json').read_text('utf8'))
for row in ptx:assert sha(Path(row['target']).read_bytes())==row['after'],row['target']
envs={n:UnityPy.load(str(GAME/n)) for n in [W,D]};oo={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in oo.items()};expected={n:{} for n in envs}
def named(n,name):return next(o for o in oo[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def save(n,o,d):o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
# Top controls revert to native placement; the reference sidebar starts underneath them.
primary=named(W,'PrimaryNavigationBar');pd=primary.read_typetree();rr={x['rid']:x for x in pd['references']['RefIds']}
assert 'tf-reference-header-controls' in rr[1006]['data']['m_Classes']
rr[1006]['data']['m_Classes'].remove('tf-reference-header-controls')
ps=oo[W][pd['inlineSheet']['m_PathID']].read_typetree();validate_ui(pd,ps);save(W,primary,pd)
style=named(D,'AlwaysAppliedStyleSheet');dd=style.read_typetree();st=Styles(dd)
first=next(i for i,r in enumerate(dd['m_Rules']) if 'tf-reference-sidebar' in json.dumps(r['m_ComplexSelectors']))
olddefault=copy.deepcopy(dd['m_Rules'][first]);dd['m_Rules']=dd['m_Rules'][:first]
def addrule(chain,props):
 i=len(dd['m_Rules']);sels=[{'m_Parts':[{'m_Value':n,'m_Type':t} for n,t in part],'m_PreviousRelationship':0 if j==0 else 2} for j,part in enumerate(chain)]
 dd['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':1+sum(100 if t==6 else 10 for part in chain for _,t in part),'m_Selectors':sels,'ruleIndex':i}],'m_Properties':props,'line':-1})
for s in olddefault['m_ComplexSelectors']:s['ruleIndex']=len(dd['m_Rules'])
dd['m_Rules'].append(olddefault)
# Copy the actual donor's FMETSideBar positioning/decorative rule, changing only width.
refenv=UnityPy.load(str(REF/D));refsheet=next(o.read_typetree() for o in refenv.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
ref_rule=next(r for r in refsheet['m_Rules'] if any(s['m_Selectors']==[{'m_Parts':[{'m_Value':'FMETSideBar','m_Type':6}],'m_PreviousRelationship':0}] for s in r['m_ComplexSelectors']))
def importprop(p):
 p=copy.deepcopy(p)
 for h in p['m_Values']:
  typ=h['m_ValueType']
  if typ in poolmap:
   value=copy.deepcopy(refsheet[poolmap[typ]][h['valueIndex']]);h.update(st.h(typ,value))
 return p
props=[importprop(p) for p in ref_rule['m_Properties'] if p['m_Id']!=131105]
props.extend([st.p(131105,st.px(100)),st.p(131081,st.en('flex'))])
addrule([[('tf-reference-sidebar-active',3)],[('tf-reference-sidebar',3)]],props)
assert next(refsheet['dimensions'][p['m_Values'][0]['valueIndex']]['value'] for p in ref_rule['m_Properties'] if p['m_Id']==131104)==54
# Never offset a shared layer. Only named ordinary management panel containers move.
auto={'m_ValueType':1,'valueIndex':3}
matchguids=set()
for bn in ['ui-match_assets_all.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
 for o in UnityPy.load(str(GAME/bn)).objects:
  if o.type.name=='MonoBehaviour':matchguids.update(re.findall(r'[0-9a-f]{32}',json.dumps(o.read_typetree())))
management={};excluded={}
for o in UnityPy.load(str(GAME/'ui-panelids_assets_all.bundle')).objects:
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree();p=d.get('m_panelDescription',{});layer=p.get('layer',{}).get('Name');name=d.get('m_Name','');guid=p.get('uxml',{}).get('m_AssetGUID','')
 if layer not in ['MenuBody','ReportBody']:continue
 if guid in matchguids or re.search('match|highlight|onthepitch|teamtalk|shootout|penalt|fullscreenteamselection|fulltime|halftime|fmmenu|ige|draft|store',name,re.I):excluded[name]=layer
 else:management[name]=layer
assert management['SquadScreen']=='MenuBody' and management['PortalScreen']=='MenuBody' and management['PlayerReport']=='ReportBody'
for name,layer in sorted(management.items()):
 addrule([[(layer,6)],[(name,6)]],[st.p(131102,st.en('absolute')),st.p(131089,st.px(100)),st.p(131103,st.px(0)),st.p(131104,st.px(0)),st.p(131080,st.px(0)),st.p(131105,auto),st.p(131087,st.pct(100))])
addrule([[('TitleBarBindingRoot',6)],[('SecondaryNavigationBar',6)],[('Bookmarks',6)]],[st.p(131081,st.en('none'))])
matchpanels=excluded
geometry=[]
for width in [1280,1920,2560,3840]:
 geometry.append({'viewport':width,'management_panel_left':100,'management_panel_width':width-100,'shared_layer_left':0,'shared_layer_width':width,'match_offset_rules':0})
for rule in dd['m_Rules'][first:]:
 assert all(p['m_Id'] not in [327681,327682,327683,131096,131097,131094,131095] for p in rule['m_Properties'])
 if any(p['m_Id']==131089 and p['m_Values'][0]['m_ValueType']==3 and dd['dimensions'][p['m_Values'][0]['valueIndex']]['value']==100 for p in rule['m_Properties']):
  for sel in rule['m_ComplexSelectors']:
   assert len(sel['m_Selectors'])==2
   assert sel['m_Selectors'][1]['m_Parts'][0]['m_Value'] in management
   assert sel['m_Selectors'][1]['m_Parts'][0]['m_Value'] not in excluded
save(D,style,dd)
outputs={}
for n,e in envs.items():
 raw=e.file.save(packer='lz4');loaded={o.path_id:o for o in UnityPy.load(raw).objects};assert set(loaded)==set(oo[n])
 for i,o in loaded.items():
  if i in expected[n]:assert o.read_typetree()==expected[n][i],(n,i)
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
 outputs[GAME/n]=raw
out=V/'management-page-scope-fix';out.mkdir(exist_ok=False);(out/'packages').mkdir();(out/'backup-game').mkdir();tx=[]
for target,data in outputs.items():
 src=out/'packages'/target.name;bak=out/'backup-game'/target.name;before=target.read_bytes();src.write_bytes(data);bak.write_bytes(before);tx.append({'target':str(target),'source':str(src),'backup':str(bak),'before':sha(before),'after':sha(data)})
protected={p:sha(Path(p).read_bytes()) for p in json.loads((V/'manifest.json').read_text('utf8'))['source_preparation_hashes'] if Path(p) not in outputs}
reference_hashes={str(p):sha(p.read_bytes()) for p in REF.glob('*.bundle')}
record={'version':'V4 named management panel scope correction','installed':False,'runtime_verified':False,'reference_sidebar_top_px':54,'sidebar_left_px':0,'sidebar_width_px':100,'content_source':'native selected bookmarks, vertical, with labels','reference_sidebar_position_rule_copied':True,'body_bounds_offset_used_instead_of_padding':False,'named_management_panel_offsets':management,'shared_layer_offsets':False,'match_offset_rules':False,'page_scaling_imported':False,'native_match_templates_unchanged':True,'settings_and_resolution_config_unchanged':True,'excluded_match_panels':matchpanels,'horizontal_geometry_checks':geometry,'reference_hashes':reference_hashes,'protected_sha256':protected,'known_limitations':['Actual rendering, layer stacking and match transitions still require in-game testing; geometry checks are static.']}
(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(V/'installer.py',out/'installer.py')
for name,flag in [('install',''),('restore-previous',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
full=out/'full-rollback';full.mkdir();orig=json.loads((prior/'full-rollback/transaction.json').read_text('utf8'))
for row in orig:
 if Path(row['target']) in outputs:row.update(source=str(out/'packages'/Path(row['target']).name),after=sha(outputs[Path(row['target'])]))
targets={Path(x['target']) for x in orig};fp={p:h for p,h in protected.items() if Path(p) not in targets}
(full/'transaction.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':fp},ensure_ascii=False,indent=2),'utf8');shutil.copyfile(out/'installer.py',full/'installer.py')
(out/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
shutil.copyfile('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log',out/'Player-before-management-scope-fix.log')
print(json.dumps({'output':str(out),'sidebar_top':54,'sidebar_width':100,'management_panels':len(management),'shared_layer_offset':False,'match_offset_rules':False,'native_match_templates_unchanged':True,'runtime_verified':False},ensure_ascii=False))
