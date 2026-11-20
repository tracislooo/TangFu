"""Adopt the donor layout as a unit, preserving current content and bindings."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,struct,sys
OUT=Path(__file__).resolve().parent;R=OUT.parent;V4=R/'reference-sidebar-100px-v4';REF=Path('K:/桌面/Skin files')
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 a=ast.parse((R/name).read_text('utf8'));exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),name,'exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest();f32=lambda f:struct.unpack('<f',struct.pack('<f',f))[0]
GAME=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle'
prior=V4/'management-page-scope-fix';priorrows=json.loads((prior/'transaction.json').read_text('utf8'))
for row in priorrows:assert sha(Path(row['target']).read_bytes())==row['after'],row['target']
envs={n:UnityPy.load(str(GAME/n)) for n in [W,M,D]};oo={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in oo.items()};expected={n:{} for n in envs};originaldocs={}
def named(n,name):return next(o for o in oo[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def serial(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def save(n,o,d):o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
# The bound gate now applies its active class to MainNav, enclosing sidebar AND top controls.
primary=named(W,'PrimaryNavigationBar');pd=primary.read_typetree();rr=refs(pd)
gate=next(i for i in rr if serial(rr,i).get('name')=='TFReferenceSidebarBoundScope')
data=serial(rr,gate)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'];b=bytes(data);count=b[0];offset=1;args=[]
for _ in range(count):
 size=struct.unpack_from('<I',b,offset)[0];offset+=4;args.append(b[offset:offset+size]);offset+=size
assert count==5 and offset==len(b) and args[3][-1]==0
args[3]=args[3][:-1]+b'\x01'
serial(rr,gate)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(bytes([count])+b''.join(struct.pack('<I',len(a))+a for a in args))
rr[1006]['data']['m_Classes'].append('tf-reference-header-controls')
ps=oo[W][pd['inlineSheet']['m_PathID']].read_typetree();validate_ui(pd,ps);save(W,primary,pd)

# Copy only the donor's match compensation class markers, never its page contents.
mark_report=[]
for n in [W,M]:
 for ro in UnityPy.load(str(REF/n)).objects:
  if ro.type.name!='MonoBehaviour':continue
  rd=ro.read_typetree()
  if 'references' not in rd:continue
  rrefs=refs(rd)
  for rid,rec in rrefs.items():
   marks=[c for c in rec.get('data',{}).get('m_Classes',[]) if c in ['fmet-match-page','fmet-match-card']]
   if not marks:continue
   obj=oo[n][ro.path_id];d=obj.read_typetree();before=copy.deepcopy(d);dr=refs(d)
   assert dr[rid]['data']['m_Id']==rec['data']['m_Id'],(n,rd['m_Name'])
   mapped=['tf-reference-match-page' if c=='fmet-match-page' else 'tf-reference-match-card' for c in marks]
   dr[rid]['data']['m_Classes'].extend(c for c in mapped if c not in dr[rid]['data']['m_Classes'])
   check=copy.deepcopy(d);refs(check)[rid]['data']['m_Classes']=refs(before)[rid]['data']['m_Classes'];assert check==before
   originaldocs[(n,obj.path_id)]=before;save(n,obj,d);mark_report.append({'bundle':n,'name':rd['m_Name'],'path_id':obj.path_id,'rid':rid,'classes':mapped,'origin':'reference skin'})
# Explicitly protect the current game's pre-match and post-match root pages too.
for name in ['FullScreenTeamSelection','MatchPreviewCard','MatchPreparationCard','PostMatchNewsPanel']:
 obj=named(W,name);d=obj.read_typetree();before=copy.deepcopy(d);dr=refs(d)
 roots=dr[d['m_VisualTree']['rid']]['data']['m_Children'];assert len(roots)==1;rid=roots[0]['rid']
 dr[rid]['data']['m_Classes'].append('tf-reference-match-page')
 check=copy.deepcopy(d);refs(check)[rid]['data']['m_Classes']=refs(before)[rid]['data']['m_Classes'];assert check==before
 originaldocs[(W,obj.path_id)]=before;save(W,obj,d);mark_report.append({'bundle':W,'name':name,'path_id':obj.path_id,'rid':rid,'classes':['tf-reference-match-page'],'origin':'current-version pre/post-match coverage'})
assert any(x['name']=='OverviewPrototype' for x in mark_report)

style=named(D,'AlwaysAppliedStyleSheet');dd=style.read_typetree();first=next(i for i,r in enumerate(dd['m_Rules']) if 'tf-reference-sidebar' in json.dumps(r['m_ComplexSelectors']));dd['m_Rules']=dd['m_Rules'][:first];st=Styles(dd)
rd=next(o.read_typetree() for o in UnityPy.load(str(REF/D)).objects if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
def names(rule):return [p['m_Value'] for s in rule['m_ComplexSelectors'] for q in s['m_Selectors'] for p in q['m_Parts']]
def source_rule(name):return next(r for r in rd['m_Rules'] if name in names(r) and (name!='FMETSideBar' or len(r['m_ComplexSelectors'])==1 and len(r['m_ComplexSelectors'][0]['m_Selectors'])==1))
def import_rule(rule,rename=None):
 q=copy.deepcopy(rule);ri=len(dd['m_Rules'])
 for sel in q['m_ComplexSelectors']:
  sel['ruleIndex']=ri
  for s in sel['m_Selectors']:
   for part in s['m_Parts']:
    if rename and part['m_Value'] in rename:part['m_Value']=rename[part['m_Value']]
 for p in q['m_Properties']:
  for h in p['m_Values']:
   t=h['m_ValueType']
   if t in poolmap:h.update(st.h(t,copy.deepcopy(rd[poolmap[t]][h['valueIndex']])))
 dd['m_Rules'].append(q);return q
def replace(rule,prop,handle):
 p=next(p for p in rule['m_Properties'] if p['m_Id']==prop);p['m_Values']=[handle]
def add_rule(chain,props):
 ri=len(dd['m_Rules']);sels=[{'m_Parts':[{'m_Value':name,'m_Type':typ} for name,typ in parts],'m_PreviousRelationship':0 if i==0 else 2} for i,parts in enumerate(chain)]
 dd['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':1+sum(100 if t==6 else 10 for part in chain for _,t in part),'m_Selectors':sels,'ruleIndex':ri}],'m_Properties':props,'line':-1})
add_rule([[('tf-reference-sidebar',3)]],[st.p(131081,st.en('none'))])
side=import_rule(source_rule('FMETSideBar'),{'FMETSideBar':'TFReferenceSidebar'})
# Enable the rule only under the bound management navigation gate.
for s in side['m_ComplexSelectors']:
 s['m_Selectors'].insert(0,{'m_Parts':[{'m_Value':'tf-reference-sidebar-active','m_Type':3}],'m_PreviousRelationship':0});s['m_Selectors'][1]['m_PreviousRelationship']=2;s['m_Specificity']+=10
replace(side,131104,st.px(0));replace(side,131105,st.px(100));side['m_Properties'].append(st.p(131081,st.en('flex')))
# Use precisely the reference page scheme, adapting the 210px compensation to 100px.
body_source=next(r for r in rd['m_Rules'] if names(r)==['main-menu-layer-body','main-menu-layer-body','main-card-report-body','main-card-report-body'])
body=import_rule(body_source);replace(body,131089,st.px(100))
old_margin=next(rd['dimensions'][p['m_Values'][0]['valueIndex']]['value'] for p in body_source['m_Properties'] if p['m_Id']==131092)
replace(body,131092,st.px(f32(old_margin*100/210)))
page_source=source_rule('fmet-match-page');page=import_rule(page_source,{'fmet-match-page':'tf-reference-match-page'});replace(page,131091,st.px(-100))
translate=next(p for p in page['m_Properties'] if p['m_Id']==327683);translate['m_Values'][0]=st.px(f32(-old_margin*100/210))
card_source=source_rule('fmet-match-card');card=import_rule(card_source,{'fmet-match-card':'tf-reference-match-card'})
card_translate=next(p for p in card['m_Properties'] if p['m_Id']==327683);old=rd['dimensions'][next(p for p in card_source['m_Properties'] if p['m_Id']==327683)['m_Values'][0]['valueIndex']]['value'];card_translate['m_Values'][0]=st.px(f32(old*100/210))
add_rule([[('tf-reference-sidebar-active',3)],[('tf-reference-header-controls',3)]],[st.p(131099,st.px(100))])
add_rule([[('TitleBarBindingRoot',6)],[('SecondaryNavigationBar',6)]],[st.p(131099,st.px(100))])
add_rule([[('TitleBarBindingRoot',6)],[('SecondaryNavigationBar',6)],[('Bookmarks',6)]],[st.p(131081,st.en('none'))])
save(D,style,dd)
# Verify the donor-derived transforms cancel on match pages instead of merely shifting them.
scale=next(rd['floats'][p['m_Values'][0]['valueIndex']] for p in body_source['m_Properties'] if p['m_Id']==327681)
inverse=next(rd['floats'][p['m_Values'][0]['valueIndex']] for p in page_source['m_Properties'] if p['m_Id']==327681)
delta=100+scale*(-100-f32(old_margin*100/210));assert abs(scale*inverse-1)<0.0001 and abs(delta)<0.02
geometry=[{'viewport':w,'sidebar_left':0,'sidebar_width':100,'match_combined_scale':scale*inverse,'match_left_error_px':delta} for w in [1280,1920,2560,3840]]
outputs={};reports=[]
for n,e in envs.items():
 raw=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(oo[n])
 for i,o in saved.items():
  if i in expected[n]:assert o.read_typetree()==expected[n][i],(n,i)
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
 outputs[GAME/n]=raw;reports.append({'bundle':n,'changed_objects':[{'path_id':i,'name':d.get('m_Name')} for i,d in expected[n].items()]})
base=json.loads((V4/'manifest.json').read_text('utf8'));protected={p:sha(Path(p).read_bytes()) for p in base['source_preparation_hashes'] if Path(p) not in outputs}
(OUT/'packages').mkdir(exist_ok=True);(OUT/'backup-game').mkdir(exist_ok=True);tx=[]
for target,data in outputs.items():
 src=OUT/'packages'/target.name;bak=OUT/'backup-game'/target.name;before=target.read_bytes();src.write_bytes(data);bak.write_bytes(before);tx.append({'target':str(target),'source':str(src),'backup':str(bak),'before':sha(before),'after':sha(data)})
record={'version':'V5 donor layout with full-height leftmost bookmark column','installed':False,'runtime_verified':False,'sidebar_left':0,'sidebar_top':0,'sidebar_width':100,'top_navigation_inset':100,'content':'native vertical bookmarks with labels','donor_layout_scale':scale,'donor_match_inverse_scale':inverse,'match_changes':'Only compensation class markers were added; all other fields/content/events/bindings remain unchanged','match_style_markers':mark_report,'geometry_checks':geometry,'settings_and_resolution_configuration_modified':False,'current_skin_project_modified':False,'reference_bundle_files_installed_wholesale':False,'changed_bundles':reports,'protected_sha256':protected,'known_limitations':['Only serialization and transform math have been verified. Runtime continuity, before/during/after-match geometry and resolution selection require game testing.']}
(OUT/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(V4/'installer.py',OUT/'installer.py')
for name,flag in [('install',''),('restore-previous',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
full=OUT/'full-rollback';full.mkdir(exist_ok=True);orig=json.loads((prior/'full-rollback/transaction.json').read_text('utf8'));targets={Path(row['target']) for row in orig}
for row in orig:
 if Path(row['target']) in outputs:row.update(source=str(OUT/'packages'/Path(row['target']).name),after=sha(outputs[Path(row['target'])]))
for row in tx:
 if Path(row['target']) not in targets:orig.append(copy.deepcopy(row))
targets={Path(row['target']) for row in orig};fp={p:h for p,h in protected.items() if Path(p) not in targets}
(full/'transaction.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':fp},ensure_ascii=False,indent=2),'utf8');shutil.copyfile(OUT/'installer.py',full/'installer.py')
(OUT/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
(OUT/'README.md').write_text('V5：采用参考皮肤的整体正文布局和比赛反向补偿，100px竖排书签从界面左上角贯穿到底部，顶部导航与正文位于右侧。\n\n本版采用参考的0.88正文缩放及约1.13636比赛逆向补偿。17个比赛/赛前/赛后模板只增加布局补偿样式标记，其他内容、事件、绑定、ID均保持不变。未改分辨率设置或原皮肤工程。\n\n退出游戏后restore-previous.ps1恢复安装前版本；restore-original.ps1完全恢复侧栏试装前版本。\n\n尚未验证实际游戏运行效果。\n','utf8')
print(json.dumps({'output':str(OUT),'sidebar':[0,0,100],'donor_layout_scale':scale,'match_compensation_scale':inverse,'match_marker_only_changes':len(mark_report),'runtime_verified':False},ensure_ascii=False))
