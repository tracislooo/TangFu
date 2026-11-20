"""Add a localized native Messages shortcut after Club and narrow holiday controls."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
location=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(location['bundle_root']);SKIN=Path(location['skin_packages'])
assert GAME==Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 source=ast.parse((R/name).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),name+':definitions-only','exec'))
TypeTreeHelper.write_value=write
navigation_codec=ast.parse((R/'fix-primary-messages-panel-navigation.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in ast.walk(navigation_codec) if isinstance(n,ast.FunctionDef) and n.name in
 {'payloads','event','string','binding','parameter','open_panel'}],type_ignores=[]),'native-panel-navigation-codec:definitions-only','exec'))
sha=lambda b:hashlib.sha256(b).hexdigest()
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
serial=lambda rr,i:rr[rr[i]['data']['m_SerializedData']['rid']]['data']
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
protected={}
for f in [GAME,SKIN]:
 for n in [G,'ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualfunctions_assets_all.bundle','ui-panelids_assets_all.bundle']:
  p=f/n
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in reserved}|{-910000000000001,-910000000000002}
spec=importlib.util.spec_from_file_location('messages_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};reports=[];templates={}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 def named(name):
  matches=[o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name]
  assert len(matches)==1,(name,len(matches));return matches[0]
 nav=named('PrimaryNavigationBar');nd=nav.read_typetree();original_nav=copy.deepcopy(nd);nr=refs(nd)
 nsid=nd['inlineSheet']['m_PathID'];ns=oo[nsid].read_typetree();old_ns=copy.deepcopy(ns);nst=Styles(ns)
 def navnode(name):return next(i for i in nr if nr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(nr,i).get('name')==name)
 root=navnode('HeaderHolidayShortcut');date=navnode('HeaderHolidayCustomDate')
 width_properties=ns['m_Rules'][nr[root]['data']['m_RuleIndex']]['m_Properties']
 width_handle=next(p for p in width_properties if p['m_Id']==131105)['m_Values'][0]
 assert width_handle['m_ValueType']==3
 dim=ns['dimensions'][width_handle['valueIndex']];assert dim['unit']==1
 old_width=dim['value'];new_width=struct.unpack('<f',struct.pack('<f',old_width*2/3))[0]
 assert old_width==210 and new_width==140,(old_width,new_width)
 for i in [root,date]:nst.edit(nr[i],[nst.p(131105,nst.px(new_width))])
 for i,r in refs(original_nav).items():
  expected=copy.deepcopy(r)
  if i in [root,date]:expected['data']['m_RuleIndex']=nr[i]['data']['m_RuleIndex']
  assert nr[i]==expected,('Unrelated header change',i)
 panel_phone=named('PortalMessagesToolPhone').read_typetree();panel_phone_refs=refs(panel_phone)
 base=payloads(panel_phone_refs[1028]['data']['Events'])[0]
 assert len(base)==76
 nav_source=folder/'ui-globalnavigation_assets_all.bundle'
 if not nav_source.exists():nav_source=GAME/'ui-globalnavigation_assets_all.bundle'
 nav_env=UnityPy.load(str(nav_source))
 portal_tabs=next(o.read_typetree() for o in nav_env.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PortalSubtabs')
 overview_route=next(x['PropertyValue']['m_openEvent'] for x in portal_tabs['m_submenus'] if x['name']=='Overview')
 messages_route=next(x['PropertyValue']['m_openEvent'] for x in portal_tabs['m_submenus'] if x['name']=='Messages')
 route=event([open_panel(overview_route['m_panelReference']['asset']['m_AssetGUID'],[],overview_route['m_rebindMethod'],overview_route['m_checkForExistingOpenedPanel']),
              open_panel(messages_route['m_panelReference']['asset']['m_AssetGUID'],[(a['name'],a['path']['m_path'],a['method']) for a in messages_route['m_argumentBindings']],messages_route['m_rebindMethod'],messages_route['m_checkForExistingOpenedPanel'])])
 phone=named('PhoneDashboardHeaderMessages').read_typetree();pr=refs(phone)
 native_label=pr[1026]['data'];assert native_label['DebugDisplay']=='Messages'
 assert native_label['TextBinding']['m_kind']==2
 assert native_label['TextBinding']['m_visualFunction']['m_target']['m_guid']=='eae2be944eee9e2449baef416111a087'
 menu=named('MenuBar');md=menu.read_typetree();original_menu=copy.deepcopy(md);mr=refs(md)
 msid=md['inlineSheet']['m_PathID'];ms=oo[msid].read_typetree();old_ms=copy.deepcopy(ms);mst=Styles(ms)
 ge=UnityPy.load(str(folder/G));go={o.path_id:o for o in ge.objects};gm=next(o.read_typetree() for o in go.values() if o.type.name=='AssetBundle')
 club=next(i for i in mr if mr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(mr,i).get('name')=='ClubButton')
 group=mr[club]['data']['m_Parent']['rid'];switch=mr[group]['data']['m_Parent']['rid']
 assert serial(mr,group)['name']=='ManagingClubButtons'
 assert mr[switch]['data']['m_FullTypeName']=='SI.Bindable.BindableSwitchElement'
 using=next(u for u in md['m_Usings'] if u['alias']==mr[club]['data']['m_TemplateAlias'])
 candidates=[go[v['asset']['m_PathID']] for k,v in gm['m_Container'] if k==using['path'] and go[v['asset']['m_PathID']].type.name=='MonoBehaviour']
 candidates=[o for o in candidates if 'inlineSheet' in o.read_typetree()];assert len(candidates)==1
 actual=candidates[0].read_typetree();ar=refs(actual)
 template_button=next(i for i,r in ar.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIButton' and serial(ar,i).get('name')=='buttons-button-navigation-default')
 template_text=next(i for i,r in ar.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText' and serial(ar,i).get('name')=='text')
 # Validate existing Club template overrides against the exact GUID-resolved template, including paths.
 for override in mr[club]['data']['m_SerializedDataOverride']:
  assert len(override['m_ElementIdsPath'])==1
  assert any(r.get('data',{}).get('m_Id')==override['m_ElementIdsPath'][0] for r in ar.values())
 ids={r['data']['m_Id'] for r in mr.values() if 'm_Id' in r.get('data',{})}
 next_rid=max(mr)+1;next_id=1910310000;added=[]
 def add(records,i,parent,name):
  global next_rid,next_id
  while next_id in ids:next_id+=1
  a=copy.deepcopy(records[i]);s=copy.deepcopy(records[a['data']['m_SerializedData']['rid']]);eid=next_id;ids.add(eid);next_id+=1
  a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
  a['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=-1,m_Stylesheets=[],m_StylesheetPaths=[],m_Properties=[])
  s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1)
  for r in [a,s]:mr[r['rid']]=r;md['references']['RefIds'].append(r);added.append(r['rid'])
  mr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
 plain=next(i for i,r in mr.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement')
 wrapper=add(mr,plain,switch,'ClubAndMessagesRow')
 mr[wrapper]['data']['m_Classes']=['row-direction-normal','align-self-stretch-class','flex-grow-class']
 mr[switch]['data']['m_Children'].remove({'rid':wrapper})
 index=next(i for i,c in enumerate(mr[switch]['data']['m_Children']) if c['rid']==group)
 mr[switch]['data']['m_Children'][index]={'rid':wrapper}
 mr[group]['data']['m_Parent']={'rid':wrapper};mr[wrapper]['data']['m_Children']=[{'rid':group}]
 # Place the shortcut outside ButtonGroup so it never assigns a nonexistent primary-tab index.
 button=add(ar,template_button,wrapper,'PrimaryNavMessagesButton')
 bs=serial(mr,button)
 bs.update(Events=route,Events_UxmlAttributeFlags=1,InputActionRef={'m_inputActionAsset':{'m_AssetGUID':'','m_SubObjectName':'','m_SubObjectType':''},'m_actionID':''},InputActionRef_UxmlAttributeFlags=1,
           StopsEventPropagation=0,StopsEventPropagation_UxmlAttributeFlags=1,OnlyAcceptsClickEvents=1,OnlyAcceptsClickEvents_UxmlAttributeFlags=1)
 label=add(ar,template_text,button,'PrimaryNavMessagesLabel');ls=serial(mr,label)
 ls.update(TextBinding=copy.deepcopy(native_label['TextBinding']),TextBinding_UxmlAttributeFlags=1,DebugDisplay='Messages',DebugDisplay_UxmlAttributeFlags=1)
 # Retain Club's native button/text USS classes, including case, typeface, and hover behavior.
 auto={'m_ValueType':1,'valueIndex':3}
 mst.edit(mr[button],[mst.p(131083,mst.en('row')),mst.p(131073,mst.en('center')),mst.p(131088,mst.en('center')),
  mst.p(131074,mst.en('stretch')),mst.p(131087,mst.pct(100)),mst.p(131096,mst.px(0)),mst.p(131094,auto),
  mst.p(131084,mst.num(0)),mst.p(131085,mst.num(0))])
 assert serial(mr,label)['TextBinding']==native_label['TextBinding']
 assert serial(mr,button)['Events']==route
 assert serial(mr,button)['StaticText']==''
 assert mr[wrapper]['data']['m_Children']==[{'rid':group},{'rid':button}]
 assert mr[group]['data']['m_Children']==refs(original_menu)[group]['data']['m_Children']
 for i,r in refs(original_menu).items():
  expected=copy.deepcopy(r)
  if i==switch:expected['data']['m_Children'][index]={'rid':wrapper}
  if i==group:expected['data']['m_Parent']={'rid':wrapper}
  assert mr[i]==expected,('Unrelated menu record change',i)
 for doc,sheet,old_sheet in [(nd,ns,old_ns),(md,ms,old_ms)]:
  validate_ui(doc,sheet);assert sheet['m_Rules'][:len(old_sheet['m_Rules'])]==old_sheet['m_Rules']
 for i in added:
  a=mr[i].get('data',{})
  if a.get('m_RuleIndex',-1)>=0:assert all(h['m_ValueType'] not in [8,10] for p in ms['m_Rules'][a['m_RuleIndex']]['m_Properties'] for h in p['m_Values'])
 needed={(mr[i]['type']['class'],mr[i]['type']['ns'],mr[i]['type']['asm']) for i in added}
 known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in menu.assets_file.ref_types};assert needed<=known
 changed={nav.path_id:nd,nsid:ns,menu.path_id:md,msid:ms}
 for i,d in changed.items():oo[i].save_typetree(d)
 raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert o.read_typetree()==changed[i]
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated object changed',tag,i)
 validate_ui(check[nav.path_id].read_typetree(),check[nsid].read_typetree());validate_ui(check[menu.path_id].read_typetree(),check[msid].read_typetree())
 meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle');cat=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes())
 audited=[]
 for obj in [nav,menu]:
  key=next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':obj.path_id})
  locs=[l for l in cat.locations(key) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert locs
  assert all(cat.location(cat.location(l)['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W) for l in locs);audited.append(key)
 for l in cat.locations('eae2be944eee9e2449baef416111a087'):
  assert cat.location(l)['type'][1]=='SI.VisualScripting.VisualFunction'
 assert banned.isdisjoint(set(check)-set(oo))
 outputs[folder/W]=raw;templates[tag]={'PrimaryNavigationBar':nd,'MenuBar':md}
 reports.append({'target':str(folder/W),'holiday_width_before':old_width,'holiday_width_after':new_width,'messages_location':'immediately after Club primary navigation group',
  'native_style_template':actual['m_Name'],'label_source':'PhoneDashboardHeaderMessages / Messages SIText binding','translation_binding_preserved':True,
  'navigation_event_source':'PortalSubtabs Overview then Messages native panel-open definitions','target_panel':'PortalMessagesTool','target_binding':'human.HumanPortalCurrentMessageToOpen','primary_tab_group_indices_preserved':True,
  'changed_bundle_objects':list(changed),'new_menu_records':added,'catalog_guids_verified':audited,'no_inline_variables_added':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('menu-messages-holiday-width140-'+stamp);out.mkdir();tx=[]
for p,data in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(data);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(data)})
manifest={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},
 'holiday_default_next_match_and_crash_fix_preserved':True,'secondary_tabbar_transparency_preserved':True,'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for tag,trees in templates.items():
 folder=out/('templates-'+tag);folder.mkdir()
 for n,d in trees.items():(folder/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'holiday_width':140,'localized_messages_button':True,'runtime_verified':False},ensure_ascii=False))
