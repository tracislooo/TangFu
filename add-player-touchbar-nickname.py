"""Expose the native nickname action in PlayerReportHeader, on current independent bundles."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys
R=Path(__file__).resolve().parent
setup=(R/'disable-primary-shortcuts-hover.py').read_text('utf8').split('outputs={};reports=[]')[0]
exec(compile(setup,'current-resource-helpers','exec'))
S='ui-styles_assets_default.bundle'
before.update({f/S:(f/S).read_bytes() for f in [GAME,SKIN]})
for p in before: protected.pop(p,None)
tree=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'selector-helper','exec'))
spec=importlib.util.spec_from_file_location('nickname_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
ACTION=0x4d36365a
CLASS='player-touchbar-nickname-button'
# Independently establish the action identifier from this installed native build.
import pefile
plugin=next((GAME.parents[2]/'Plugins').rglob('game_plugin.dll'))
native=plugin.read_bytes();pe=pefile.PE(data=native,fast_load=True);base=pe.OPTIONAL_HEADER.ImageBase
descriptor=pe.get_rva_from_offset(native.index(b'.?AVNICKNAME_ACTION@@')-16)
offset=0;verified=False
while True:
 offset=native.find(struct.pack('<I',descriptor),offset)
 if offset<0:break
 col=offset-12;offset+=4
 if struct.unpack_from('<I',native,col)[0]!=1:continue
 vp=native.find(struct.pack('<Q',base+pe.get_rva_from_offset(col)))
 if vp<0:continue
 getter=struct.unpack_from('<Q',native,vp+16)[0]-base
 code=native[pe.get_offset_from_rva(getter):pe.get_offset_from_rva(getter)+6]
 if code==b'\xb8'+struct.pack('<I',ACTION)+b'\xc3':verified=True;break
assert verified,'Installed NICKNAME_ACTION identifier differs'
protected[plugin]=sha(native)
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 obj=oo[5775949770471550939];doc=obj.read_typetree();old=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']}
 sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();oldsheet=copy.deepcopy(sheet);st=Styles(sheet)
 def sd(i):return rr.get(rr[i]['data']['m_SerializedData']['rid'],{}).get('data',{})
 find=lambda name:next(i for i,r in rr.items() if 'm_SerializedData' in r.get('data',{}) and sd(i).get('name')==name)
 frame=find('FrameActions');wrap=find('HeaderFitnessSixMetrics')
 action=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
 assert rr[frame]['data']['m_Children']==[{'rid':wrap},{'rid':action}]
 assert not any(r.get('data',{}).get('name')=='PlayerTouchbarNickname' for r in rr.values())
 source=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerPraiseTrainingDevelopmentTextWithIconCell')
 sr={r['rid']:r for r in source['references']['RefIds']}
 node=copy.deepcopy(sr[1002]);data=copy.deepcopy(sr[1004]);nid=max(rr)+1;did=nid+1
 eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 node['rid']=nid;data['rid']=did
 node['data'].update(m_Id=eid,m_Parent={'rid':frame},m_Children=[],m_SerializedData={'rid':did},m_RuleIndex=-1,m_Classes=[CLASS])
 data['data'].update(uxmlAssetId=eid,name='PlayerTouchbarNickname',name_UxmlAttributeFlags=1,
  RecordsBinding={'m_path':'Person'},RecordsBinding_UxmlAttributeFlags=1,
  ActionId=ACTION,ActionId_UxmlAttributeFlags=1,ActionIdBinding={'m_path':''},ActionIdBinding_UxmlAttributeFlags=1,
  ActionsListWidget={'m_AssetGUID':'23461237760028345adfc0d8d53a3f7b','m_SubObjectName':'','m_SubObjectType':''},ActionsListWidget_UxmlAttributeFlags=1,
  ShowOnlyFirstButton=1,ShowOnlyFirstButton_UxmlAttributeFlags=1,
  StyleAsPrimaryButton=0,StyleAsPrimaryButton_UxmlAttributeFlags=1,
  GrowToWidth=1,GrowToWidth_UxmlAttributeFlags=1,
  SkipInstantiationWhenActionIsNull=1,SkipInstantiationWhenActionIsNull_UxmlAttributeFlags=1)
 rr[nid]=node;rr[did]=data;doc['references']['RefIds'].extend([node,data])
 rr[frame]['data']['m_Children'].insert(1,{'rid':nid})
 st.edit(node,[st.p(131105,st.px(104)),st.p(131097,st.px(104)),st.p(131095,st.px(104)),
  st.p(131087,st.px(26)),st.p(131096,st.px(26)),st.p(131094,st.px(26)),
  st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131074,st.en('center')),st.p(131092,st.px(4))])
 changed={frame};pillids=[];sepids=[]
 for c in rr[wrap]['data']['m_Children']:
  i=c['rid'];name=sd(i).get('name','')
  if 'Separator' in name:
   st.edit(rr[i],[st.p(131091,st.px(2)),st.p(131092,st.px(2))]);sepids.append(i)
  else:
   st.edit(rr[i],[st.p(131099,st.px(3)),st.p(131100,st.px(3))]);pillids.append(i)
  changed.add(i)
 assert len(pillids)==10 and len(sepids)==9
 st.edit(rr[wrap],[st.p(131092,st.px(4))]);changed.add(wrap)
 # Existing text/data/events and the original operation menu are preserved exactly.
 for r in old['references']['RefIds']:
  actual=copy.deepcopy(rr[r['rid']])
  if r['rid'] in changed:actual['data']['m_RuleIndex']=r['data']['m_RuleIndex']
  if r['rid']==frame:actual['data']['m_Children']=r['data']['m_Children']
  assert actual==r,('Unrelated header data changed',r['rid'])
 assert sheet['m_Rules'][:len(oldsheet['m_Rules'])]==oldsheet['m_Rules']
 validate_ui(doc,sheet)
 needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in [node,data]}
 assert needed<={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in obj.assets_file.ref_types}
 expected={obj.path_id:doc,sid:sheet}
 for i,d in expected.items():oo[i].save_typetree(d)
 raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in expected:assert o.read_typetree()==expected[i]
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated world asset changed',i)
 outputs[folder/W]=raw
 # Limit generated native button height to this one touchbar instance.
 se=UnityPy.load(before[folder/S]);so={o.path_id:o for o in se.objects};sh={i:sha(o.get_raw_data()) for i,o in so.items()}
 ob=next(o for o in so.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
 ss=ob.read_typetree();oldss=copy.deepcopy(ss);sty=Styles(ss);idx=len(ss['m_Rules'])
 ss['m_Rules'].append({'m_ComplexSelectors':[selector('.'+CLASS+' .button-size-medium',idx)],'m_Properties':[
  sty.p(131087,sty.px(26)),sty.p(131096,sty.px(26)),sty.p(131094,sty.px(26)),sty.p(65537,sty.px(12))],'line':-1})
 assert ss['m_Rules'][:-1]==oldss['m_Rules']
 ob.save_typetree(ss);raw=se.file.save(packer='lz4');chk={o.path_id:o for o in UnityPy.load(raw).objects};assert set(chk)==set(so)
 for i,o in chk.items():
  if i==ob.path_id:assert o.read_typetree()==ss
  else:assert sha(o.get_raw_data())==sh[i],('Unrelated style asset changed',i)
 outputs[folder/S]=raw
 cat=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
 audit=[]
 for guid in ['23461237760028345adfc0d8d53a3f7b','ebf6856dc4a5c514ca77e904dff7b186']:
  locations=[l for l in cat.locations(guid) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert locations
  entry=next(v for k,v in meta['m_Container'] if k==guid and oo[v['asset']['m_PathID']].peek_name()!='inlineStyle')
  assert all(cat.location(cat.location(l)['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W) for l in locations)
  audit.append({'guid':guid,'name':oo[entry['asset']['m_PathID']].peek_name(),'catalog_owner_verified':True})
 reports.append({'target':str(folder),'native_action_id':ACTION,'native_action_fourcc':'M66Z','binding':'Person',
  'placement':'immediately before original operation menu','width':104,'height':26,'pill_padding_before_after':[5,3],
  'separator_margin_before_after':[3,2],'existing_header_bindings_and_menu_unchanged':True,
  'only_header_vta_inline_style_and_one_scoped_stylesheet_rule_changed':True,'native_widgets':audit})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out=R/('player-touchbar-nickname-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/p.name;bak=out/('backup-'+tag)/p.name
 src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(raw);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'native_action_id_verified_against_installed_plugin':True,
 'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
(R/'prepared-player-touchbar-nickname.json').write_text(json.dumps({'patch':str(out)},indent=2),'utf8')
print(json.dumps({'prepared':True,'output':str(out),'files':len(tx),'native_action_id':ACTION}))
