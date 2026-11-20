"""Sidebar variant: native bookmark icons, manager link, group rules and 400px bookmarks."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,shutil
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for file,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'}),('fix-primary-messages-panel-navigation.py',{'payloads','event'})]:
 t=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),'<helpers>','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
before={GAME/n:(GAME/n).read_bytes() for n in [W,D]};env=UnityPy.load(before[GAME/W]);obs=env.assets[0].objects;oldraw={i:o.get_raw_data() for i,o in obs.items()};named=lambda n:next(o for o in obs.values() if o.type.name=='MonoBehaviour' and o.peek_name()==n);refs=lambda d:{r['rid']:r for r in d['references']['RefIds']};ser=lambda rr,i:rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
obj=named('TFReferenceBookmarkSidebar');doc=obj.read_typetree();rr=refs(doc);sheetobj=obs[doc['inlineSheet']['m_PathID']];sheet=sheetobj.read_typetree();st=Styles(sheet)
rowobj=named('TFReferenceBookmarkRow');row=rowobj.read_typetree();br=refs(row);rowsheetobj=obs[row['inlineSheet']['m_PathID']];rowsheet=rowsheetobj.read_typetree();bst=Styles(rowsheet)
native=UnityPy.load(str(GAME/'gamemodules_assets_gameworld.bundle')).assets[0];icons={o.peek_name():o.read_typetree()['m_iconStyle'] for o in native.objects.values() if o.type.name=='MonoBehaviour' and 'm_iconStyle' in o.read_typetree()}
labels=['消息','一线队','动态','战术','数据中心','职员','训练','医疗中心','赛程安排','比赛','球探','俱乐部','财政','青年']
sources=['MessagesBookmark','FirstTeamBookmark','DynamicsBookmark','SetPiecesBookmark','DataHubBookmark','ClubStaffBookmark','TrainingBookmark','MedicalCentreBookmark','FixtureScheduleBookmark','CompetitionStatusBookmark','PlayerRecommendationsBookmark','ClubSiteBookmark','FinancesBookmark','YouthSetupBookmark']
buttons=[rr[x['rid']] for x in rr[1001]['data']['m_Children'] if ser(rr,x['rid']).get('name','').startswith('TFSidebarFixed_')];assert len(buttons)==14
assert [ser(rr,x['rid'])['text'] for x in buttons]==labels
original_events={x['rid']:copy.deepcopy(ser(rr,x['rid'])['Events']) for x in buttons}
next_rid=max(rr)+1;next_eid=1911021000;used={x.get('data',{}).get('m_Id') for x in rr.values()}
def add(source_refs,source_id,parent,name):
 global next_rid,next_eid
 while next_eid in used:next_eid+=1
 uid=next_eid;used.add(uid);next_eid+=1
 n=copy.deepcopy(source_refs[source_id]);sd=copy.deepcopy(source_refs[n['data']['m_SerializedData']['rid']]);n['rid']=next_rid;sd['rid']=next_rid+1;next_rid+=2
 n['data'].update(m_Id=uid,m_Parent={'rid':parent},m_Children=[],m_Classes=[],m_Properties=[],m_StylesheetPaths=[],m_Stylesheets=[],m_RuleIndex=-1,m_SerializedData={'rid':sd['rid']})
 sd['data'].update(uxmlAssetId=uid,name=name,name_UxmlAttributeFlags=1)
 doc['references']['RefIds'] += [n,sd];rr[n['rid']]=n;rr[sd['rid']]=sd
 return n
manager=add(rr,buttons[0]['rid'],1001,'TFSidebarManagerCentre');ms=ser(rr,manager['rid']);ms.update(text='经理中心',Events=event([payloads(original_events[buttons[0]['rid']])[0]]));assert b'2d1049f4571df444eb050b39a5b8aaec' in bytes(ms['Events']['m_bytes'])
allbuttons=[manager]+buttons;alllabels=['经理中心']+labels;allsources=['ClubStaffBookmark']+sources
def zero_frame(style):return [style.p(i,style.px(0)) for i in [131076,131077,131078,131079]]+[style.p(458752,style.h(4,{'r':0.,'g':0.,'b':0.,'a':0.})),style.p(458753,style.en('none'))]
def button_style(style,node):
 style.edit(node,[style.p(131105,style.px(100)),style.p(131087,style.px(30)),style.p(131096,style.px(30)),style.p(131094,style.px(30)),style.p(131085,style.num(0)),style.p(131083,style.en('row')),style.p(131072,style.en('center')),style.p(131088,style.en('flex-start')),style.p(262150,style.px(0)),style.p(262151,style.px(0)),style.p(131099,style.px(6)),style.p(131100,style.px(4))]+zero_frame(style),reset=True)
audit=[]
for button,label,source in zip(allbuttons,alllabels,allsources):
 sd=ser(rr,button['rid']);sd['text']='';sd['text_UxmlAttributeFlags']=1;button['data']['m_Classes']=['sibutton','bookmarks-button'];button_style(st,button)
 icon=add(br,1012,button['rid'],'FixedIcon_'+label);icon['data']['m_Classes']=[icons[source]];ser(rr,icon['rid']).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 st.edit(icon,[st.p(131105,st.px(16)),st.p(131087,st.px(16)),st.p(131097,st.px(16)),st.p(131096,st.px(16)),st.p(131085,st.num(0)),st.p(131092,st.px(6)),st.p(458757,st.px(16),st.px(16)),st.p(458754,st.en('center')),st.p(458755,st.en('center')),st.p(458756,st.en('no-repeat'))],reset=True)
 text=add(br,1022,button['rid'],'FixedLabel_'+label);ts=ser(rr,text['rid']);ts.update(text=label,text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=0,TextCase=0,TextCase_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);ts['TextBinding']['m_kind']=0;ts['TextBinding']['m_direct']['Path']['m_path']='';ts['TextBinding']['m_visualFunction']['m_target']['m_guid']=''
 st.edit(text,[st.p(65537,st.px(12)),st.p(65536,st.h(4,{'r':1.,'g':1.,'b':1.,'a':1.})),st.p(65546,st.en('middle-left')),st.p(131097,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(196609,st.en('ellipsis')),st.p(65552,st.en('nowrap')),st.p(262150,st.px(0))],reset=True)
 button['data']['m_Children']=[{'rid':icon['rid']},{'rid':text['rid']}];audit.append({'label':label,'native_bookmark_icon':icons[source]})
sequence=[];separators=[]
after={'经理中心','消息','动态','数据中心','医疗中心','比赛','球探','财政'}
def separator(label):
 n=add(br,1012,1001,'SidebarSeparatorAfter_'+label);ser(rr,n['rid']).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 st.edit(n,[st.p(131105,st.px(92)),st.p(131087,st.px(1)),st.p(131096,st.px(1)),st.p(131094,st.px(1)),st.p(131085,st.num(0)),st.p(131091,st.px(4)),st.p(131092,st.px(4)),st.p(458752,st.h(4,{'r':0.5,'g':0.5,'b':0.5,'a':0.5}))],reset=True);separators.append(label);return {'rid':n['rid']}
for b,label in zip(allbuttons,alllabels):
 sequence.append({'rid':b['rid']})
 if label in after:sequence.append(separator(label))
sequence.append(separator('青年_书签上方'));sequence.append({'rid':1046});rr[1001]['data']['m_Children']=sequence
st.edit(rr[1229],[st.p(131087,st.px(400))]);li=ser(rr,1229);li['FixedElementSize']=30.;li['FixedElementSize_UxmlAttributeFlags']=1
# Keep original bookmark interaction/bindings, matching fixed-link height, font and alignment.
for i in [1001,1006]:bst.edit(br[i],[bst.p(131087,bst.px(30)),bst.p(131096,bst.px(30)),bst.p(131094,bst.px(30)),bst.p(131085,bst.num(0))])
button_style(bst,br[1009]);bst.edit(br[1012],[bst.p(131105,bst.pct(100)),bst.p(131083,bst.en('row')),bst.p(131088,bst.en('flex-start')),bst.p(131072,bst.en('center'))]);bst.edit(br[1015],[bst.p(131105,bst.px(16)),bst.p(131087,bst.px(16)),bst.p(131097,bst.px(16)),bst.p(131085,bst.num(0)),bst.p(131092,bst.px(6))]);bst.edit(br[1016],[bst.p(131084,bst.num(1)),bst.p(131085,bst.num(1)),bst.p(131097,bst.px(0))]);bst.edit(br[1022],[bst.p(65537,bst.px(12)),bst.p(65546,bst.en('middle-left')),bst.p(65536,bst.h(4,{'r':1.,'g':1.,'b':1.,'a':1.}))])
for b in buttons:assert ser(rr,b['rid'])['Events']==original_events[b['rid']]
validate_ui(doc,sheet);validate_ui(row,rowsheet)
expected={obj.path_id:doc,sheetobj.path_id:sheet,rowobj.path_id:row,rowsheetobj.path_id:rowsheet}
for i,d in expected.items():obs[i].save_typetree(d)
payload=env.file.save(packer='lz4');checked=UnityPy.load(payload).assets[0]
for i,o in checked.objects.items():
 if i in expected:assert o.read_typetree()==expected[i]
 else:assert o.get_raw_data()==oldraw[i]
outputs={GAME/W:payload}
de=UnityPy.load(before[GAME/D]);a=de.assets[0];o=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');d=o.read_typetree();dst=Styles(d);rules=[x for x in d['m_Rules'] if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','TFReferenceSidebar'] for sel in x['m_ComplexSelectors'])];assert len(rules)==1
rule=rules[0];rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id'] not in [131078,458762]]+[dst.p(131078,dst.px(1)),dst.p(458762,dst.h(4,{'r':0.5,'g':0.5,'b':0.5,'a':0.5}))];hashes={i:sha(x.get_raw_data()) for i,x in a.objects.items()};o.save_typetree(d);dp=de.file.save(packer='lz4');check=UnityPy.load(dp).assets[0]
for i,x in check.objects.items():
 if i==o.path_id:assert x.read_typetree()==d
 else:assert sha(x.get_raw_data())==hashes[i]
outputs[GAME/D]=dp
out=R/('sidebar-icons-groups-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx=[]
for p,data in outputs.items():
 src=out/'packages'/p.name;bak=out/'backup-game'/p.name;src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(data);bak.write_bytes(before[p]);assert p.read_bytes()==before[p];tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(data)})
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('ui-*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+[p for p in SKIN.iterdir() if p.is_file()] if p not in outputs}
(out/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'fixed_link_count':15,'icons':audit,'separators_after':separators,'right_border_px':1,'bookmark_height_px':400,'bookmark_row_height_px':30,'original_fixed_link_events_unchanged':True,'protected_sha256':protected},ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for action,flag in [('install',''),('restore-icons-groups',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+'\n','utf-8-sig')
print(str(out),flush=True)
