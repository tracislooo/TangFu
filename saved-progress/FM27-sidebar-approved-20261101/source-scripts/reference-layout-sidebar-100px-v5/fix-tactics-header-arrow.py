"""Fix shared tactics compensation, header inset and bookmark edit icon size."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,struct,sys
V=Path(__file__).resolve().parent;R=V.parent
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
v5rows=json.loads((V/'transaction.json').read_text('utf8'))
for row in v5rows:assert sha(Path(row['target']).read_bytes())==row['after'],row['target']
envs={n:UnityPy.load(str(GAME/n)) for n in [W,D]};oo={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in os.items()} for n,os in oo.items()};expected={n:{} for n in envs}
def named(n,name):return next(o for o in oo[n].values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def serial(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def save(n,o,d):o.save_typetree(d);expected[n][o.path_id]=copy.deepcopy(d)
primary=named(W,'PrimaryNavigationBar');pd=primary.read_typetree();pr=refs(pd)
gate=next(i for i in pr if serial(pr,i).get('name')=='TFReferenceSidebarBoundScope')
source_el=copy.deepcopy(pr[gate]);source_sd=copy.deepcopy(pr[source_el['data']['m_SerializedData']['rid']])
def s7(s):
 b=s.encode('utf8');n=len(b);a=bytearray()
 while n>=128:a.append((n&127)|128);n>>=7
 return bytes(a)+bytes([n])+b
def packargs(args):return bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args)
def abool(b):return s7('SI.VisualScripting.BooleanVisualArg')+bytes([b])
conditions=s7('SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BooleanArg]')+b'\x02'+b''.join(b'\x01'+s7(p)+b'\x00' for p in ['game.IsViewingMatch','game.IsDuringMatch'])
operator=s7('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.VisibleFunctions+LogicOperator]')+struct.pack('<i',1)
style_name=s7('SI.VisualScripting.StringVisualArg')+b'\x01'+s7('tf-reference-match-page')
function=copy.deepcopy(source_sd['data']['BindFunction']);function['m_inputs']['m_variable']['m_argumentBytes']=list(packargs([conditions,operator,style_name,abool(True),abool(False)]))
tactics=[]
for ordinal,name in enumerate(['OnThePitchSetPiecesTool','OnThePitchPenaltiesTool','OnThePitchOppositionInstructionsTool']):
 obj=named(W,name);d=obj.read_typetree();rr=refs(d);oldrefs=copy.deepcopy(rr);sid=d['inlineSheet']['m_PathID'];sheet=oo[W][sid].read_typetree();st=Styles(sheet)
 root=d['m_VisualTree']['rid'];children=rr[root]['data']['m_Children'];assert len(children)==1;parent=children[0]['rid']
 assert 'tf-reference-match-page' in rr[parent]['data']['m_Classes']
 rr[parent]['data']['m_Classes'].remove('tf-reference-match-page')
 ei=max(rr)+1;si=ei+1;eid=1911011000+ordinal
 assert eid not in {x.get('data',{}).get('m_Id') for x in rr.values()}
 el=copy.deepcopy(source_el);sd=copy.deepcopy(source_sd);el['rid']=ei;sd['rid']=si
 el['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_SerializedData={'rid':si})
 sd['data'].update(uxmlAssetId=eid,name='TFMatchOnlyCompensation',name_UxmlAttributeFlags=1,BindFunction=copy.deepcopy(function),BindFunction_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 st.edit(el,[st.p(131102,st.en('absolute')),st.p(131105,st.px(0)),st.p(131087,st.px(0))])
 d['references']['RefIds'].extend([el,sd]);rr[parent]['data']['m_Children'].append({'rid':ei})
 # All original element IDs, events, bindings and template paths remain intact.
 for i,old in oldrefs.items():
  if i==parent:
   old['data']['m_Classes']=rr[parent]['data']['m_Classes'];old['data']['m_Children']=rr[parent]['data']['m_Children']
  assert rr[i]==old,(name,i)
 validate_ui(d,sheet);save(W,obj,d);save(W,oo[W][sid],sheet);tactics.append({'name':name,'mode':'compensate only when viewing or during match','root_type':rr[parent]['data']['m_FullTypeName']})
# Move the inset to the actual left controls, outside SISafeAreaElement's padding logic.
assert 'tf-reference-header-controls' in pr[1006]['data']['m_Classes']
pr[1006]['data']['m_Classes'].remove('tf-reference-header-controls')
pr[1010]['data']['m_Classes'].append('tf-reference-header-controls')
assert serial(pr,1014)['name']=='BackForwardVisible' and pr[1014]['data']['m_Parent']['rid']==1010
validate_ui(pd,oo[W][pd['inlineSheet']['m_PathID']].read_typetree());save(W,primary,pd)
style=named(D,'AlwaysAppliedStyleSheet');dd=style.read_typetree();old_dd=copy.deepcopy(dd)
matches=[q for q in dd['m_Rules'] if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','tf-reference-header-controls'] for sel in q['m_ComplexSelectors'])]
assert len(matches)==1;rule=matches[0]
assert len(rule['m_Properties'])==1 and rule['m_Properties'][0]['m_Id']==131099
rule['m_Properties'][0]['m_Id']=131091
check=copy.deepcopy(dd)
for q in check['m_Rules']:
 if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','tf-reference-header-controls'] for sel in q['m_ComplexSelectors']):q['m_Properties'][0]['m_Id']=131099
assert check==old_dd
save(D,style,dd)
# The popup is 100px wide, but its chevron image must remain 16px square.
sidebar=named(W,'TFReferenceBookmarkSidebar');sd=sidebar.read_typetree();sr=refs(sd);sid=sd['inlineSheet']['m_PathID'];ss=oo[W][sid].read_typetree();st=Styles(ss)
assert serial(sr,1073)['name']=='BookmarksPopupWidget'
popup_before=copy.deepcopy(serial(sr,1073))
st.edit(sr[1073],[st.p(458757,st.px(16),st.px(16)),st.p(458754,st.en('center')),st.p(458755,st.en('center')),st.p(458756,st.en('no-repeat'))])
assert serial(sr,1073)==popup_before
props={p['m_Id']:p['m_Values'] for p in ss['m_Rules'][sr[1073]['data']['m_RuleIndex']]['m_Properties']}
assert ss['dimensions'][props[131105][0]['valueIndex']]['value']==100
assert [ss['dimensions'][h['valueIndex']]['value'] for h in props[458757]]==[16,16]
validate_ui(sd,ss);save(W,sidebar,sd);save(W,oo[W][sid],ss)
outputs={};reports=[]
for n,e in envs.items():
 raw=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(oo[n])
 for i,o in saved.items():
  if i in expected[n]:assert o.read_typetree()==expected[n][i],(n,i)
  else:assert sha(o.get_raw_data())==hashes[n][i],(n,i)
 outputs[GAME/n]=raw;reports.append({'bundle':n,'changed_objects':[{'path_id':i,'name':d.get('m_Name')} for i,d in expected[n].items()]})
out=V/'tactics-header-arrow-fix';out.mkdir(exist_ok=False);(out/'packages').mkdir();(out/'backup-game').mkdir();tx=[]
for target,data in outputs.items():
 src=out/'packages'/target.name;bak=out/'backup-game'/target.name;old=target.read_bytes();src.write_bytes(data);bak.write_bytes(old);tx.append({'target':str(target),'source':str(src),'backup':str(bak),'before':sha(old),'after':sha(data)})
baseline=json.loads((R/'reference-sidebar-100px-v4/manifest.json').read_text('utf8'))['source_preparation_hashes']
protected={p:sha(Path(p).read_bytes()) for p in baseline if Path(p) not in outputs}
record={'version':'V5 tactics context, history controls and chevron fix','installed':False,'runtime_verified':False,'tactics_pages':tactics,'match_conditions_operator':'OR','header_inset':'100px margin on left BindingRemapper group containing BackForwardVisible','bookmark_popup_click_width':100,'bookmark_popup_icon_size':[16,16],'bookmark_popup_events_unchanged':True,'matches_bundle_unchanged_from_installed_v5':True,'page_scale_unchanged':True,'settings_resolution_unchanged':True,'changed_bundles':reports,'protected_sha256':protected,'mode_checks':[{'viewing_match':a,'during_match':b,'compensation':a or b} for a in [False,True] for b in [False,True]]}
(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(V/'installer.py',out/'installer.py')
for name,flag in [('install',''),('restore-v5',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
full=out/'full-rollback';full.mkdir();orig=json.loads((V/'full-rollback/transaction.json').read_text('utf8'))
for row in orig:
 if Path(row['target']) in outputs:row.update(source=str(out/'packages'/Path(row['target']).name),after=sha(outputs[Path(row['target'])]))
targets={Path(x['target']) for x in orig};fp={p:h for p,h in protected.items() if Path(p) not in targets}
(full/'transaction.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':fp},ensure_ascii=False,indent=2),'utf8');shutil.copyfile(out/'installer.py',full/'installer.py')
(out/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
(out/'README.md').write_text('V5定点修订：普通战术页的点球、定位球及复用的对手指令，仅在比赛状态启用逆向布局补偿；前进后退所在左侧控件组以100px外边距留位；书签编辑按钮仍100px宽，箭头固定16×16。未改当前正文缩放、原生事件、比赛包及分辨率设置。\n\nrestore-v5.ps1恢复本次修改前；restore-original.ps1完全撤销侧栏。先退出游戏再运行。\n\n静态与序列化验证完成，实际显示和模式切换尚需游戏内检查。\n','utf8')
shutil.copyfile('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log',out/'Player-before-tactics-header-arrow-fix.log')
print(json.dumps({'output':str(out),'tactics_contexts':len(tactics),'header_inset':'left controls margin 100px','popup_image':[16,16],'changed_files':len(tx),'runtime_verified':False},ensure_ascii=False))
