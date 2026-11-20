"""Append native Data Hub/Medical Centre routes and reorder the shortcuts."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
setup=(R/'change-staff-shortcut-to-recruitment-database.py').read_text('utf8').split('nav=UnityPy.load')[0]
exec(compile(setup,'resource-initialization-only','exec'))
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'ui-validator','exec'))
nav=UnityPy.load(str(GAME/'ui-globalnavigation_assets_all.bundle'))
trees={o.peek_name():o.read_typetree() for o in nav.objects if o.type.name=='MonoBehaviour'}
specs=[]
for name,navname,title in [('DataHub','TacticsSubtabs','Data Hub'),('MedicalCentre','TrainingSubtabs','Medical Centre')]:
 tree=trees[navname];root=next(x for x in tree['m_submenus'] if x['name']=='Overview');target=next(x for x in tree['m_submenus'] if x['name']==title)
 assert not target['PropertyValue']['m_translationArgs']
 specs.append({'name':name,'title':title,'root':root,'target':target,'label_id':target['PropertyValue']['m_displayValue']['GameID']})
assert [s['label_id'] for s in specs]==[35815,35712]
spec=importlib.util.spec_from_file_location('data_medical_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};reports=[]
order=['ManagingClubButtons','PrimaryNavMessagesButton','PrimaryNavCompetitionsButton','PrimaryNavFixtureScheduleButton','PrimaryNavDataHubButton','PrimaryNavMedicalCentreButton','PrimaryNavYouthButton','PrimaryNavStaffButton']
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 menu=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MenuBar');doc=menu.read_typetree();old=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']}
 def serial(i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
 def named(name):return next(i for i,r in rr.items() if r.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(i).get('name')==name)
 button=named('PrimaryNavStaffButton');frame=named('PrimaryNavStaffFrame');label=named('PrimaryNavStaffLabel');parent=rr[button]['data']['m_Parent']['rid']
 assert len(rr[parent]['data']['m_Children'])==6
 next_rid=max(rr)+1;next_eid=1911013000;used={r['data']['m_Id'] for r in rr.values() if 'm_Id' in r.get('data',{})};added=[]
 def clone(i,p,name):
  global next_rid,next_eid
  while next_eid in used:next_eid+=1
  eid=next_eid;used.add(eid);next_eid+=1
  a=copy.deepcopy(rr[i]);s=copy.deepcopy(rr[a['data']['m_SerializedData']['rid']]);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
  a['data'].update(m_Id=eid,m_Parent={'rid':p},m_Children=[],m_SerializedData={'rid':s['rid']})
  s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1)
  for record in [a,s]:rr[record['rid']]=record;doc['references']['RefIds'].append(record);added.append(record['rid'])
  rr[p]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
 native=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PortalMessagesToolPhone');base=payloads({r['rid']:r for r in native['references']['RefIds']}[1028]['data']['Events'])[0];assert len(base)==76
 def encode_native(value):
  e=value['PropertyValue']['m_openEvent'];assert e['m_anchor']['value']=='' and e['m_panelReference']['kind']==0
  return open_panel(e['m_panelReference']['asset']['m_AssetGUID'],[(a['name'],a['path']['m_path'],a['method']) for a in e['m_argumentBindings']],e['m_rebindMethod'],e['m_checkForExistingOpenedPanel'])
 pe=UnityPy.load(str(GAME/'ui-panelids_assets_all.bundle'));po={o.path_id:o for o in pe.objects};meta=next(o.read_typetree() for o in pe.objects if o.type.name=='AssetBundle')
 catalog=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());audits=[]
 for item in specs:
  b=clone(button,parent,'PrimaryNav'+item['name']+'Button');f=clone(frame,b,'PrimaryNav'+item['name']+'Frame');l=clone(label,f,'PrimaryNav'+item['name']+'Label')
  serial(b).update(Events=event([encode_native(item['root']),encode_native(item['target'])]),Events_UxmlAttributeFlags=1)
  vf=serial(l)['TextBinding']['m_visualFunction'];assert vf['m_target']['m_guid']=='eae2be944eee9e2449baef416111a087'
  arg=string('SI.VisualScripting.GenericVisualArg`1[SI.Translation.TranslationID]')+struct.pack('<i',item['label_id'])+b'\x01'+string(item['title'])
  vf['m_inputs']['m_variable']['m_argumentBytes']=list(b'\x01'+struct.pack('<I',len(arg))+arg)
  serial(l).update(DebugDisplay=item['title'],DebugDisplay_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=1)
  audit=[]
  for value in [item['root'],item['target']]:
   guid=value['PropertyValue']['m_openEvent']['m_panelReference']['asset']['m_AssetGUID'];entry=next(v for k,v in meta['m_Container'] if k==guid);pd=po[entry['asset']['m_PathID']].read_typetree()
   locations=catalog.locations(guid);assert locations
   for loc in locations:
    info=catalog.location(loc);assert info['internal']==guid and info['dependencies']
    assert catalog.location(info['dependencies'][0])['internal'].replace('\\','/').endswith('/ui-panelids_assets_all.bundle')
   audit.append({'name':pd['m_Name'],'guid':guid,'layer':pd['m_panelDescription']['layer']['Name'],'parameters':value['PropertyValue']['m_openEvent']['m_argumentBindings']})
  assert audit[0]['layer']=='MenuBody' and audit[1]['layer']=='ReportBody'
  audits.append({'title':item['title'],'label_id':item['label_id'],'route':audit})
  for src,dst in [(button,b),(frame,f),(label,l)]:
   assert rr[src]['data']['m_RuleIndex']==rr[dst]['data']['m_RuleIndex'] and rr[src]['data']['m_Classes']==rr[dst]['data']['m_Classes']
 rr[parent]['data']['m_Children']=[{'rid':named(n)} for n in order]
 for r in old['references']['RefIds']:
  expected=copy.deepcopy(r)
  if r['rid']==parent:expected['data']['m_Children']=rr[parent]['data']['m_Children']
  assert expected==rr[r['rid']],('Existing navigation changed',r['rid'])
 sid=doc['inlineSheet']['m_PathID'];validate_ui(doc,oo[sid].read_typetree())
 assert {(rr[i]['type']['class'],rr[i]['type']['ns'],rr[i]['type']['asm']) for i in added}<={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in menu.assets_file.ref_types}
 menu.save_typetree(doc);raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==menu.path_id:assert o.read_typetree()==doc
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated asset changed',tag,i)
 validate_ui(check[menu.path_id].read_typetree(),check[sid].read_typetree())
 outputs[folder/W]=raw;reports.append({'target':str(folder/W),'order':order,'native_routes':audits,'existing_styles_and_navigation_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('primary-data-medical-fixture-order-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(raw);bak.write_bytes(before[p]);tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'changes':reports},ensure_ascii=False))
