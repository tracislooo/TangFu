"""Extend the Messages row with localized native overview/staff navigation."""
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
for name,wanted in [('build-fc-player-hover-layout.py',{'write'}),('add-card-six-ratings.py',{'validate_ui'})]:
 tree=ast.parse((R/name).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted],type_ignores=[]),name+':definitions-only','exec'))
codec=ast.parse((R/'fix-primary-messages-panel-navigation.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in ast.walk(codec) if isinstance(n,ast.FunctionDef) and n.name in
 {'payloads','event','string','binding','parameter','open_panel'}],type_ignores=[]),'native-panel-event-codec:definitions-only','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
serial=lambda rr,i:rr[rr[i]['data']['m_SerializedData']['rid']]['data']
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]};protected={}
for f in [GAME,SKIN]:
 for n in [G,'ui-globalnavigation_assets_all.bundle','ui-panelids_assets_all.bundle','ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualfunctions_assets_all.bundle']:
  p=f/n
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
spec=importlib.util.spec_from_file_location('shortcut_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
navigation=UnityPy.load(str(GAME/'ui-globalnavigation_assets_all.bundle'))
navtrees={o.peek_name():o.read_typetree() for o in navigation.objects if o.type.name=='MonoBehaviour'}
def entry(tree,name):return next(x for x in tree['m_submenus'] if x['name']==name)
def child_overview(tree,parent):
 rr=refs(tree)
 return next(rr[c['rid']]['data'] for c in parent['ChildList'] if rr[c['rid']]['data']['name']=='Overview')
portal=navtrees['PortalSubtabs'];squad=navtrees['SquadSubtabs'];club=navtrees['ClubSubtabs']
competition=entry(portal,'Competitions');youth=entry(squad,'Youth Setup');staff=entry(club,'Staff')
specs=[{'name':'Competitions','parent':entry(portal,'Overview'),'target':child_overview(portal,competition),'title_game_id':competition['PropertyValue']['m_displayValue']['GameID']},
       {'name':'Youth','parent':entry(squad,'Overview (Club)'),'target':child_overview(squad,youth)},
       {'name':'Staff','parent':entry(club,'Overview'),'target':staff,'title_game_id':staff['PropertyValue']['m_displayValue']['GameID']}]
expected_targets={'Competitions':('ed5ea2b61dbc27843a5bdae84aefc91f','CompetitionsOverviewTool'),
                  'Youth':('fdc4ca40b0312734b9a99317f9d351d0','SquadYouthSetupReport'),
                  'Staff':('9ba550b513bf5144da547e7d87df80da','ClubAllStaffTool')}
def encode_route(route):
 assert route['m_panelReference']['kind']==0 and route['m_anchor']['value']==''
 return open_panel(route['m_panelReference']['asset']['m_AssetGUID'],[(a['name'],a['path']['m_path'],a['method']) for a in route['m_argumentBindings']],route['m_rebindMethod'],route['m_checkForExistingOpenedPanel'])
def decode_args(value):
 b=bytes(value);p=1;parts=[]
 for _ in range(b[0]):
  n=struct.unpack_from('<I',b,p)[0];p+=4;parts.append(b[p:p+n]);p+=n
 assert p==len(b);return parts
def encode_args(parts):return list(bytes([len(parts)])+b''.join(struct.pack('<I',len(p))+p for p in parts))
outputs={};reports=[];snapshots={}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 en=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in en.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 named=lambda n:next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==n)
 menu=named('MenuBar');doc=menu.read_typetree();old=copy.deepcopy(doc);rr=refs(doc)
 def named_node(name):return next(i for i,r in rr.items() if r.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(rr,i).get('name')==name)
 message=named_node('PrimaryNavMessagesButton');label=named_node('PrimaryNavMessagesLabel');parent=rr[message]['data']['m_Parent']['rid']
 assert [serial(rr,c['rid']).get('name') for c in rr[parent]['data']['m_Children']]==['ManagingClubButtons','PrimaryNavMessagesButton']
 assert len(payloads(serial(rr,message)['Events']))==2,'Apply the Messages panel-navigation fix first.'
 source=named('PortalMessagesToolPhone').read_typetree();base=payloads(refs(source)[1028]['data']['Events'])[0]
 assert len(base)==76 and open_panel('348f23640712e754ea77d872460b1a76')==base
 ge=UnityPy.load(str(folder/G));go={o.path_id:o for o in ge.objects};gm=next(o.read_typetree() for o in go.values() if o.type.name=='AssetBundle')
 club_node=named_node('ClubButton');alias=rr[club_node]['data']['m_TemplateAlias'];key=next(u['path'] for u in doc['m_Usings'] if u['alias']==alias)
 native=next(go[v['asset']['m_PathID']].read_typetree() for k,v in gm['m_Container'] if k==key and 'inlineSheet' in go[v['asset']['m_PathID']].read_typetree());nr=refs(native)
 native_frame=next(i for i in nr if nr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(nr,i).get('name')=='MainFrame')
 assert 'padding-right-global-padding-large' in nr[native_frame]['data']['m_Classes']
 youth_source=named('ClubFacilitiesTile_4x4').read_typetree();yr=refs(youth_source)
 youth_label=yr[1064]['data'];assert youth_label['DebugDisplay']=='Youth'
 youth_binding=copy.deepcopy(youth_label['TextBinding'])
 assert youth_binding['m_visualFunction']['m_target']['m_guid']=='f97abdf5a74842647ba921d183f4a3eb'
 args=decode_args(youth_binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
 assert args[1].count(b'\x04club')==1
 args[1]=args[1].replace(b'\x04club',string('human.Club'))
 youth_binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode_args(args)
 next_rid=max(rr)+1;next_eid=1910311000;used={r['data']['m_Id'] for r in rr.values() if 'm_Id' in r.get('data',{})};added=[]
 def add(sr,i,parent,name):
  global next_rid,next_eid
  while next_eid in used:next_eid+=1
  eid=next_eid;used.add(eid);next_eid+=1
  a=copy.deepcopy(sr[i]);s=copy.deepcopy(sr[a['data']['m_SerializedData']['rid']]);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
  a['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']})
  if sr is not rr:a['data'].update(m_RuleIndex=-1,m_Properties=[],m_StylesheetPaths=[],m_Stylesheets=[])
  s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1)
  for r in [a,s]:rr[r['rid']]=r;doc['references']['RefIds'].append(r);added.append(r['rid'])
  rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
 # Put Messages and the new labels in the identical native MainFrame used by Club.
 assert rr[message]['data']['m_Children']==[{'rid':label}]
 frame=add(nr,native_frame,message,'PrimaryNavMessagesFrame')
 rr[message]['data']['m_Children']=[{'rid':frame}];rr[frame]['data']['m_Children']=[{'rid':label}];rr[label]['data']['m_Parent']={'rid':frame}
 panel_source=folder/'ui-panelids_assets_all.bundle'
 if not panel_source.exists():panel_source=GAME/'ui-panelids_assets_all.bundle'
 pe=UnityPy.load(str(panel_source));po={o.path_id:o for o in pe.objects};pm=next(o.read_typetree() for o in pe.objects if o.type.name=='AssetBundle')
 cat=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());button_reports=[]
 for spec in specs:
  name=spec['name'];target_route=spec['target']['PropertyValue']['m_openEvent'];root_route=spec['parent']['PropertyValue']['m_openEvent']
  assert target_route['m_panelReference']['asset']['m_AssetGUID']==expected_targets[name][0]
  button=add(rr,message,parent,'PrimaryNav'+name+'Button');content=add(nr,native_frame,button,'PrimaryNav'+name+'Frame');text=add(rr,label,content,'PrimaryNav'+name+'Label')
  bs=serial(rr,button);bs['Events']=event([encode_route(root_route),encode_route(target_route)]);bs['Events_UxmlAttributeFlags']=1
  ls=serial(rr,text);ls.update(DebugDisplay=name,DebugDisplay_UxmlAttributeFlags=1)
  if name=='Youth':ls['TextBinding']=copy.deepcopy(youth_binding)
  else:
   # StaticText uses the actual native navigation TranslationID, never a hard-coded display label.
   vf=copy.deepcopy(serial(rr,label)['TextBinding']);rawargs=decode_args(vf['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
   assert len(rawargs)==1
   typename=b'SI.VisualScripting.GenericVisualArg`1[SI.Translation.TranslationID]'
   assert rawargs[0].startswith(bytes([len(typename)])+typename)
   vf['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode_args([bytes([len(typename)])+typename+struct.pack('<i',spec['title_game_id'])+b'\x01'+string(name)])
   ls['TextBinding']=vf
  ls['TextBinding_UxmlAttributeFlags']=1
  panel_audit=[]
  for route in [root_route,target_route]:
   guid=route['m_panelReference']['asset']['m_AssetGUID'];entry_meta=next(v for k,v in pm['m_Container'] if k==guid);obj=po[entry_meta['asset']['m_PathID']];pd=obj.read_typetree()
   locations=cat.locations(guid);assert locations
   for l in locations:
    inf=cat.location(l);assert inf['internal']==guid and inf['dependencies']
    assert cat.location(inf['dependencies'][0])['internal'].replace('\\','/').endswith('/ui-panelids_assets_all.bundle')
   panel_audit.append({'guid':guid,'name':pd['m_Name'],'layer':pd['m_panelDescription']['layer']['Name'],'args':route['m_argumentBindings']})
  assert panel_audit[-1]['name']==expected_targets[name][1]
  assert panel_audit[0]['layer']=='MenuBody' and panel_audit[-1]['layer']=='ReportBody'
  assert rr[content]['data']['m_Classes']==nr[native_frame]['data']['m_Classes']
  button_reports.append({'name':name,'node':button,'label':text,'panel_audit':panel_audit,'native_label_function':ls['TextBinding']['m_visualFunction']['m_target']['m_guid'],
   'translation_id':spec.get('title_game_id'),'frame_classes':rr[content]['data']['m_Classes']})
 assert [serial(rr,c['rid']).get('name') for c in rr[parent]['data']['m_Children']]==['ManagingClubButtons','PrimaryNavMessagesButton','PrimaryNavCompetitionsButton','PrimaryNavYouthButton','PrimaryNavStaffButton']
 for i,r in refs(old).items():
  expected=copy.deepcopy(r)
  if i==parent:expected['data']['m_Children']=rr[i]['data']['m_Children']
  if i==message:expected['data']['m_Children']=[{'rid':frame}]
  if i==label:expected['data']['m_Parent']={'rid':frame}
  assert rr[i]==expected,('Unrelated menu record changed',i)
 sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();validate_ui(doc,sheet)
 assert {(rr[i]['type']['class'],rr[i]['type']['ns'],rr[i]['type']['asm']) for i in added}<={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in menu.assets_file.ref_types}
 menu.save_typetree(doc);raw=en.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==menu.path_id:assert o.read_typetree()==doc
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated asset changed',tag,i)
 validate_ui(check[menu.path_id].read_typetree(),check[sid].read_typetree())
 outputs[folder/W]=raw;snapshots[tag]=doc
 reports.append({'target':str(folder/W),'buttons':button_reports,'messages_event_and_label_unchanged':True,'native_club_spacing_applied_to_messages_and_new_buttons':True,
  'new_records':added,'main_tab_group_indices_unchanged':True,'holiday_and_secondary_tabbar_unchanged':True,'unrelated_objects_verified':len(oo)-1})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('primary-competitions-youth-staff-'+stamp);out.mkdir();tx=[]
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(b);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(b)})
manifest={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for tag,doc in snapshots.items():(out/('MenuBar-'+tag+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'order':['Messages','Competitions','Youth','Staff'],'native_spacing':True,'runtime_verified':False},ensure_ascii=False))
