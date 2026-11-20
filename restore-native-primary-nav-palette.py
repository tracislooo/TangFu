"""Restore native header/menu colors, preserving all right-side action controls."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
# Load only current-resource initialization and serialization helpers.
setup=(R/'disable-primary-shortcuts-hover.py').read_text('utf8').split('outputs={};reports=[]')[0]
exec(compile(setup,'current-resources-and-helpers','exec'))
baseline=R/'primary-navigation-grey-lake-blue-20261027-234809'/'backup-game'/W
native_env=UnityPy.load(str(baseline))
native_doc=next(o.read_typetree() for o in native_env.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PrimaryNavigationBar')
native_refs={r['rid']:r for r in native_doc['references']['RefIds']}
def sd(rr,i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
spec=importlib.util.spec_from_file_location('native_nav_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};expected={}
 header=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='PrimaryNavigationBar')
 doc=header.read_typetree();old=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']}
 sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
 def remove_inline(node,keys):
  data=node['data'];prior=copy.deepcopy(sheet['m_Rules'][data['m_RuleIndex']]['m_Properties']) if data['m_RuleIndex']>=0 else []
  data['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':[p for p in prior if p['m_Id'] not in keys],'line':-1})
 # Preserve current sizing, classes used by Continue/holiday styles, and all control bindings.
 assert sd(rr,1002)['name']=='MainNav' and sd(rr,1040)['name']=='MenuBar'
 remove_inline(rr[1002],{458752})
 remove_inline(rr[1005],{131081})
 remove_inline(rr[1013],{458767})
 rr[1002]['data']['m_Classes']=[c for c in rr[1002]['data']['m_Classes'] if c not in ['nav-on-light','nav-on-dark']]
 rr[1040]['data']['m_Classes']=[c for c in rr[1040]['data']['m_Classes'] if c!='fm27-fixed-nav-ink']
 binding_changes=set()
 for node,keys in [(1004,['BindFunction','BindFunction_UxmlAttributeFlags']),(1011,['PrimaryColorDataLink','SecondaryColorDataLink','PrimaryColorDataLink_UxmlAttributeFlags','SecondaryColorDataLink_UxmlAttributeFlags'])]:
  current=sd(rr,node);native=sd(native_refs,node)
  for key in keys:
   if current[key]!=native[key]:current[key]=copy.deepcopy(native[key]);binding_changes.add(rr[node]['data']['m_SerializedData']['rid'])
 allowed={1002,1005,1013,1040}|binding_changes
 for r in old['references']['RefIds']:
  if r['rid'] not in allowed:assert rr[r['rid']]==r,('Right control or unrelated header record changed',r['rid'])
 assert sd(rr,1004)['BindFunction']==sd(native_refs,1004)['BindFunction']
 assert sd(rr,1011)['PrimaryColorDataLink']=={'m_path':'human.team.club.TitlebarTextColour'}
 assert sd(rr,1011)['SecondaryColorDataLink']=={'m_path':'human.team.club.TitlebarBackgroundColour'}
 validate_ui(doc,sheet);expected[header.path_id]=doc;expected[sid]=sheet
 menu=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='MenuBar');md=menu.read_typetree();oldmenu=copy.deepcopy(md);mr={r['rid']:r for r in md['references']['RefIds']}
 msid=md['inlineSheet']['m_PathID'];ms=oo[msid].read_typetree();labels=[]
 for rid,r in mr.items():
  a=r.get('data',{})
  if a.get('m_FullTypeName')!='SI.Bindable.SIText':continue
  name=sd(mr,rid).get('name','')
  if not (name.startswith('PrimaryNav') and name.endswith('Label')):continue
  assert 'portal-text' in a['m_Classes']
  oldprops=copy.deepcopy(ms['m_Rules'][a['m_RuleIndex']]['m_Properties']) if a['m_RuleIndex']>=0 else []
  a['m_RuleIndex']=len(ms['m_Rules']);ms['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':[p for p in oldprops if p['m_Id']!=65536],'line':-1})
  assert not any(p['m_Id']==65536 for p in ms['m_Rules'][a['m_RuleIndex']]['m_Properties'])
  labels.append({'name':name,'rid':rid})
 assert len(labels)==7
 changed={x['rid'] for x in labels}
 for r in oldmenu['references']['RefIds']:
  prior=copy.deepcopy(r)
  if r['rid'] in changed:prior['data']['m_RuleIndex']=mr[r['rid']]['data']['m_RuleIndex']
  assert mr[r['rid']]==prior,('Menu events, translation or layout changed',r['rid'])
 validate_ui(md,ms);expected[menu.path_id]=md;expected[msid]=ms
 # No source templates are restored wholesale; all other objects remain the latest versions.
 for pid,data in expected.items():oo[pid].save_typetree(data)
 raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for pid,o in check.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert sha(o.get_raw_data())==hashes[pid],('Unrelated object changed',tag,pid)
 meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle');cat=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());audit=[]
 for obj in [header,menu]:
  guids=[k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':obj.path_id}];assert len(guids)==1
  locs=[loc for loc in cat.locations(guids[0]) if cat.location(loc)['type'][-1]=='UnityEngine.UIElements.VisualTreeAsset'];assert locs
  for loc in locs:
   info=cat.location(loc);assert info['dependencies'] and cat.location(info['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
  audit.append({'name':obj.peek_name(),'guid':guids[0],'typed_owner_verified':True})
 outputs[folder/W]=raw;reports.append({'target':str(folder/W),'native_header_background_and_decorations_restored':True,'native_theme_binding_restored':True,'native_titlebar_text_background_bindings':True,'custom_labels_follow_native_portal_text':labels,'continue_holiday_clock_search_and_other_header_records_unchanged':True,'all_events_localization_and_layout_unchanged':True,'changed_objects':list(expected),'catalog_audit':audit})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('primary-nav-native-palette-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/W;bak=out/('backup-'+tag)/W;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(raw);bak.write_bytes(before[p])
 tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True,'native_source_used_for_binding_fields_only':str(baseline)}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'labels_per_variant':7,'right_action_controls_unchanged':True}))
