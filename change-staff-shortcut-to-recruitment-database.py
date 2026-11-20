"""Retarget the existing Staff shortcut to the native staff recruitment database."""
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
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'serialization-helper','exec'))
source=ast.parse((R/'fix-primary-messages-panel-navigation.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in ast.walk(source) if isinstance(n,ast.FunctionDef) and n.name in
 {'payloads','event','string','binding','parameter','open_panel'}],type_ignores=[]),'native-panel-codec:definitions-only','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]};protected={}
for f in [GAME,SKIN]:
 for name in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-globalnavigation_assets_all.bundle','ui-panelids_assets_all.bundle','ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualfunctions_assets_all.bundle']:
  p=f/name
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
nav=UnityPy.load(str(GAME/'ui-globalnavigation_assets_all.bundle'))
tree=next(o.read_typetree() for o in nav.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='RecruitmentSubtabs')
rr={r['rid']:r for r in tree['references']['RefIds']}
root=next(x for x in tree['m_submenus'] if x['name']=='Overview (Club)')
parent=next(x for x in tree['m_submenus'] if x['name']=='Staff Recruitment')
target=next(rr[c['rid']]['data'] for c in parent['ChildList'] if rr[c['rid']]['data']['name']=='Staff Database')
title_id=parent['PropertyValue']['m_displayValue']['GameID'];assert title_id==35789
route=target['PropertyValue']['m_openEvent'];assert route['m_panelReference']['asset']['m_AssetGUID']=='a6331fde9dbe9fa47a9da59a7fc09715'
assert [(a['name'],a['path']['m_path']) for a in route['m_argumentBindings']]==[('team','human.Team'),('type','const.Two'),('isplayerrecruitment','const.False')]
spec=importlib.util.spec_from_file_location('staff_db_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 menu=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MenuBar');doc=menu.read_typetree();old=copy.deepcopy(doc);refs={r['rid']:r for r in doc['references']['RefIds']}
 button=next(r for r in refs.values() if r.get('data',{}).get('name')=='PrimaryNavStaffButton')
 label=next(r for r in refs.values() if r.get('data',{}).get('name')=='PrimaryNavStaffLabel')
 native=next(o.read_typetree() for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PortalMessagesToolPhone')
 base=payloads({r['rid']:r for r in native['references']['RefIds']}[1028]['data']['Events'])[0]
 assert len(base)==76
 def encode_native(value):
  e=value['PropertyValue']['m_openEvent'];assert e['m_anchor']['value']=='' and e['m_panelReference']['kind']==0
  return open_panel(e['m_panelReference']['asset']['m_AssetGUID'],[(a['name'],a['path']['m_path'],a['method']) for a in e['m_argumentBindings']],e['m_rebindMethod'],e['m_checkForExistingOpenedPanel'])
 button['data']['Events']=event([encode_native(root),encode_native(target)]);button['data']['Events_UxmlAttributeFlags']=1
 vf=label['data']['TextBinding']['m_visualFunction'];assert vf['m_target']['m_guid']=='eae2be944eee9e2449baef416111a087'
 typename='SI.VisualScripting.GenericVisualArg`1[SI.Translation.TranslationID]'
 arg=string(typename)+struct.pack('<i',title_id)+b'\x01'+string('Staff Recruitment')
 vf['m_inputs']['m_variable']['m_argumentBytes']=list(b'\x01'+struct.pack('<I',len(arg))+arg)
 label['data'].update(DebugDisplay='Staff Recruitment',DebugDisplay_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=1)
 changed={button['rid'],label['rid']}
 for r in old['references']['RefIds']:
  if r['rid'] not in changed:assert refs[r['rid']]==r,('Unrelated navigation record changed',r['rid'])
 # All existing inline styles, dimensions, hover pins, and other button events are untouched.
 assert all({k:v for k,v in refs[r['rid']]['data'].items() if k not in ['Events','Events_UxmlAttributeFlags']}==
            {k:v for k,v in r['data'].items() if k not in ['Events','Events_UxmlAttributeFlags']}
            for r in old['references']['RefIds'] if r['rid']==button['rid'])
 panelpath=folder/'ui-panelids_assets_all.bundle'
 if not panelpath.exists():panelpath=GAME/'ui-panelids_assets_all.bundle'
 pe=UnityPy.load(str(panelpath));po={o.path_id:o for o in pe.objects};meta=next(o.read_typetree() for o in pe.objects if o.type.name=='AssetBundle')
 catalog=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());audit=[]
 for value in [root,target]:
  guid=value['PropertyValue']['m_openEvent']['m_panelReference']['asset']['m_AssetGUID']
  entry=next(v for k,v in meta['m_Container'] if k==guid);obj=po[entry['asset']['m_PathID']];pd=obj.read_typetree()
  locations=catalog.locations(guid);assert locations
  for l in locations:
   info=catalog.location(l);assert info['internal']==guid and info['dependencies']
   assert catalog.location(info['dependencies'][0])['internal'].replace('\\','/').endswith('/ui-panelids_assets_all.bundle')
  audit.append({'name':pd['m_Name'],'guid':guid,'layer':pd['m_panelDescription']['layer']['Name']})
 menu.save_typetree(doc);raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==menu.path_id:assert o.read_typetree()==doc
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated bundle asset changed',tag,i)
 outputs[folder/W]=raw;reports.append({'target':str(folder/W),'native_label_game_id':title_id,'label':'Staff Recruitment','destination':'Recruitment / Staff Recruitment / Staff Database',
  'native_target_parameters':route['m_argumentBindings'],'panel_audit':audit,'changed_serialized_records':sorted(changed),
  'styles_layout_hover_and_other_shortcuts_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('primary-staff-recruitment-database-'+stamp);out.mkdir();tx=[]
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(b);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(b)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'native_label':'Staff Recruitment','target':'Staff Database','other_controls_unchanged':True},ensure_ascii=False))
