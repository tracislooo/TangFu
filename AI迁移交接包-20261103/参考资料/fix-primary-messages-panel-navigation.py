"""Use the real PortalSubtabs panel-open definition for the primary Messages button."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages'])
assert GAME==Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'serialization-helper','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]};protected={}
for f in [GAME,SKIN]:
 for n in [G,'ui-globalnavigation_assets_all.bundle','ui-panelids_assets_all.bundle','ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle','ui-visualfunctions_assets_all.bundle']:
  p=f/n
  if p.exists():protected[p]=sha(p.read_bytes())
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
for n in ['AGENTS.md','current-game-location.json','reserved-texture-ids.json','current-custom-textures.json']:protected[R/n]=sha((R/n).read_bytes())
def payloads(event):
 b=bytes(event['m_bytes']);assert b[:3]==b'\x01\x01\x01';p=4;out=[]
 for _ in range(b[3]):
  assert b[p]==1;n=struct.unpack_from('<I',b,p+1)[0];p+=5;out.append(b[p:p+n]);p+=n
 assert p==len(b);return out
def event(parts):return {'m_bytes':list(b'\x01\x01\x01'+bytes([len(parts)])+b''.join(b'\x01'+struct.pack('<I',len(p))+p for p in parts))}
def string(v):
 b=v.encode('utf8');assert len(b)<128;return bytes([len(b)])+b
def binding(path):return b'\x01\x01'+string(path)
def parameter(name,path,method):
 b=binding(path);data=binding(name)+struct.pack('<I',len(b))+b+bytes([method]);return struct.pack('<I',len(data))+data
outputs={};reports=[]
spec=importlib.util.spec_from_file_location('messages_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for tag,folder in [('game',GAME),('skin',SKIN)]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 named=lambda name:next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 menu=named('MenuBar');doc=menu.read_typetree();old=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']}
 target=next(r for r in rr.values() if r.get('data',{}).get('name')=='PrimaryNavMessagesButton')
 native=named('PortalMessagesToolPhone').read_typetree();nr={r['rid']:r for r in native['references']['RefIds']}
 base=payloads(nr[1028]['data']['Events'])[0]
 assert len(base)==76 and base[:5]==struct.pack('<I',0x076665d3)+b'\x02'
 assert base[30:62]==b'348f23640712e754ea77d872460b1a76' and base[73:]==b'\x00\x00\x00'
 def open_panel(guid,args=(),rebind=0,check_existing=0):
  p=bytearray(base[:73]);p[30:62]=guid.encode('ascii')
  p.extend(bytes([len(args)]))
  for name,path,method in args:p.extend(parameter(name,path,method))
  p.extend(bytes([rebind,check_existing]));return bytes(p)
 assert open_panel('348f23640712e754ea77d872460b1a76')==base
 ge=UnityPy.load(str(folder/G));go={o.path_id:o for o in ge.objects}
 example=next(o.read_typetree() for o in go.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='speakto-messages-navigator-button')
 er={r['rid']:r for r in example['references']['RefIds']}
 # Byte-for-byte check against a native panel event with the same parameter list encoding.
 expected=payloads(er[1013]['data']['Events'])[2]
 assert open_panel('b557c0aee6f6fcb4eb20a1212a26b388',[
  ('newsitem','newsitem',0),('portalsourceid','portalsourceid',0),('DynamicCardReference','portalsourceid',0)])==expected
 navigation_source=folder/'ui-globalnavigation_assets_all.bundle'
 if not navigation_source.exists():navigation_source=GAME/'ui-globalnavigation_assets_all.bundle'
 ne=UnityPy.load(str(navigation_source))
 subtabs=next(o.read_typetree() for o in ne.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PortalSubtabs')
 message=next(x['PropertyValue'] for x in subtabs['m_submenus'] if x['name']=='Messages')
 overview=next(x['PropertyValue'] for x in subtabs['m_submenus'] if x['name']=='Overview')
 route=message['m_openEvent'];args=[(a['name'],a['path']['m_path'],a['method']) for a in route['m_argumentBindings']]
 assert args==[('portalsourceid','const.One',0),('team','human.Team',0),('newsitem','human.HumanPortalCurrentMessageToOpen',0)]
 assert route['m_panelReference']['asset']['m_AssetGUID']=='b557c0aee6f6fcb4eb20a1212a26b388'
 portal_route=overview['m_openEvent'];portal=portal_route['m_panelReference']['asset']['m_AssetGUID']
 new_event=event([open_panel(portal,[],portal_route['m_rebindMethod'],portal_route['m_checkForExistingOpenedPanel']),
                  open_panel(route['m_panelReference']['asset']['m_AssetGUID'],args,route['m_rebindMethod'],route['m_checkForExistingOpenedPanel'])])
 assert len(payloads(new_event))==2
 target['data'].update(Events=new_event,Events_UxmlAttributeFlags=1,StopsEventPropagation=0,StopsEventPropagation_UxmlAttributeFlags=1,
                       OnlyAcceptsClickEvents=1,OnlyAcceptsClickEvents_UxmlAttributeFlags=1,
                       OnlyAcceptsSubmitEvents=0,OnlyAcceptsSubmitEvents_UxmlAttributeFlags=1)
 for r in old['references']['RefIds']:
  if r['rid']!=target['rid']:assert rr[r['rid']]==r,('Unrelated menu record changed',r['rid'])
 panel_source=folder/'ui-panelids_assets_all.bundle'
 if not panel_source.exists():panel_source=GAME/'ui-panelids_assets_all.bundle'
 pe=UnityPy.load(str(panel_source));po={o.path_id:o for o in pe.objects};meta=next(o.read_typetree() for o in pe.objects if o.type.name=='AssetBundle')
 panel_audit=[];c=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes())
 for key in [portal,route['m_panelReference']['asset']['m_AssetGUID']]:
  entries=[v for k,v in meta['m_Container'] if k==key];assert len(entries)==1
  obj=po[entries[0]['asset']['m_PathID']];tree=obj.read_typetree()
  assert tree['m_Name'] in ['PortalScreen','PortalMessagesTool']
  assert c.locations(key)
  for l in c.locations(key):
   info=c.location(l);assert info['internal']==key and info['dependencies']
   assert c.location(info['dependencies'][0])['internal'].replace('\\','/').endswith('/ui-panelids_assets_all.bundle')
  panel_audit.append({'name':tree['m_Name'],'guid':key,'layer':tree['m_panelDescription']['layer']['Name']})
 menu.save_typetree(doc);raw=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==menu.path_id:assert o.read_typetree()==doc
  else:assert sha(o.get_raw_data())==hashes[i],('Unrelated bundle object changed',tag,i)
 outputs[folder/W]=raw
 reports.append({'target':str(folder/W),'changed_asset':'MenuBar','changed_record':target['rid'],
  'event_source':'PortalSubtabs native Overview then Messages m_openEvent definitions','parameters':args,
  'native_event_codec_roundtrip_verified':True,'panel_audit':panel_audit,'label_and_styles_unchanged':True,
  'holiday_width_and_secondary_tabbar_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('primary-messages-panel-navigation-fix-'+stamp);out.mkdir();tx=[]
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W
 src.parent.mkdir();bak.parent.mkdir();src.write_bytes(b);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(b)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for n,flag in [('install',''),('restore',' --restore')]:
 (out/(n+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'explicit_native_panel_events':2,'native_parameter_codec_verified':True},ensure_ascii=False))
