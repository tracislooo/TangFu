"""Restore original header styling while retaining current shortcut/holiday logic."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
setup=(R/'disable-primary-shortcuts-hover.py').read_text('utf8').split('outputs={};reports=[]')[0]
exec(compile(setup,'current-resource-helpers','exec'))
S='ui-styles_assets_default.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,S]}
for p in before:protected.pop(p,None)
baseline=R/'primary-navigation-grey-lake-blue-20261027-234809'/'backup-game'
native_env=UnityPy.load(str(baseline/W));no={o.path_id:o for o in native_env.objects}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def sd(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(oo,n):return next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==n)
native_header=named(no,'PrimaryNavigationBar').read_typetree();native_menu=named(no,'MenuBar').read_typetree()
native_styles=UnityPy.load(str(baseline/S));native_sheet=next(o.read_typetree() for o in native_styles.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
def is_mainnav(c):return any(p['m_Type']==6 and p['m_Value']=='MainNav' for s in c['m_Selectors'] for p in s['m_Parts'])
assert not any(is_mainnav(c) for r in native_sheet['m_Rules'] for c in r['m_ComplexSelectors'])
spec=importlib.util.spec_from_file_location('header_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};expected={};changes=[]
 def import_inline(source,node,dest,target):
  source_index=source['data']['m_RuleIndex']
  if source_index<0:node['data']['m_RuleIndex']=-1;return
  rule=copy.deepcopy(dest['m_Rules'][source_index]);rule['m_ComplexSelectors']=[]
  for p in rule['m_Properties']:
   for h in p['m_Values']:
    typ=h['m_ValueType']
    if typ in poolmap:
     pool=poolmap[typ];value=copy.deepcopy(dest[pool][h['valueIndex']]);target[pool].append(value);h['valueIndex']=len(target[pool])-1
  node['data']['m_RuleIndex']=len(target['m_Rules']);target['m_Rules'].append(rule)
 for template,nd in [('PrimaryNavigationBar',native_header),('MenuBar',native_menu)]:
  ob=named(oo,template);doc=ob.read_typetree();original=copy.deepcopy(doc);rr=refs(doc);nr=refs(nd)
  sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();ns=no[nd['inlineSheet']['m_PathID']].read_typetree();restored=[]
  for rid,src in nr.items():
   if 'm_FullTypeName' not in src.get('data',{}) or src['data']['m_FullTypeName']=='UnityEngine.UIElements.UXML':continue
   assert rid in rr and src['data']['m_FullTypeName']==rr[rid]['data']['m_FullTypeName']
   assert sd(nr,rid).get('name')==sd(rr,rid).get('name'),('Different native layout',template,rid)
   # Retain the intrinsic row wrapper needed to append localized links correctly.
   if template=='MenuBar' and sd(rr,rid).get('name')=='ManagingClubButtons':continue
   rr[rid]['data']['m_Classes']=copy.deepcopy(src['data']['m_Classes'])
   import_inline(src,rr[rid],ns,sheet);restored.append(rid)
  if template=='PrimaryNavigationBar':
   # Explicitly make the original background visible despite stale deadline-theme opacity rules.
   st=Styles(sheet);st.edit(rr[1005],[st.p(458767,st.num(1))])
   binding_records=[]
   for node,keys in [(1004,['BindFunction','BindFunction_UxmlAttributeFlags']),(1011,['PrimaryColorDataLink','SecondaryColorDataLink','PrimaryColorDataLink_UxmlAttributeFlags','SecondaryColorDataLink_UxmlAttributeFlags'])]:
    for key in keys:sd(rr,node)[key]=copy.deepcopy(sd(nr,node)[key])
    binding_records.append(rr[node]['data']['m_SerializedData']['rid'])
  else:
   binding_records=[];custom=[]
   for rid,r in rr.items():
    a=r.get('data',{});name=sd(rr,rid).get('name','')
    if not (name.startswith('PrimaryNav') and name.endswith(('Button','Label')) and 'm_FullTypeName' in a):continue
    prior=copy.deepcopy(sheet['m_Rules'][a['m_RuleIndex']]['m_Properties']) if a['m_RuleIndex']>=0 else []
    paint={65536,196610,458752,458753,458767,262148,131076,131077,131078,131079}
    a['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':[p for p in prior if p['m_Id'] not in paint],'line':-1});custom.append(rid)
   assert len(custom)==14
   restored+=custom
  for rid,old in refs(original).items():
   current=copy.deepcopy(rr[rid])
   if rid in restored:
    current['data']['m_Classes']=old['data']['m_Classes'];current['data']['m_RuleIndex']=old['data']['m_RuleIndex']
   if rid in binding_records:
    for key in ['BindFunction','BindFunction_UxmlAttributeFlags','PrimaryColorDataLink','SecondaryColorDataLink','PrimaryColorDataLink_UxmlAttributeFlags','SecondaryColorDataLink_UxmlAttributeFlags']:
     if key in old['data']:current['data'][key]=old['data'][key]
   assert current==old,('Unrelated node, event or holiday setting changed',template,rid)
  validate_ui(doc,sheet);expected[ob.path_id]=doc;expected[sid]=sheet
  changes.append({'template':template,'native_visual_nodes_restored':len(restored),'ids_tree_events_localization_preserved':True})
 for pid,data in expected.items():oo[pid].save_typetree(data)
 raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for pid,o in check.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert sha(o.get_raw_data())==hashes[pid],('Unrelated world object changed',tag,pid)
 outputs[folder/W]=raw
 se=UnityPy.load(before[folder/S]);so={o.path_id:o for o in se.objects};shashes={i:sha(o.get_raw_data()) for i,o in so.items()}
 ob=named(so,'AlwaysAppliedStyleSheet');sheet=ob.read_typetree();original=copy.deepcopy(sheet);removed=[]
 for idx,rule in enumerate(sheet['m_Rules']):
  selectors=rule['m_ComplexSelectors'];matched=[c for c in selectors if is_mainnav(c)]
  if matched:
   removed.append({'rule':idx,'selectors':len(matched)});rule['m_ComplexSelectors']=[c for c in selectors if not is_mainnav(c)]
 assert removed
 # Rule indices and pools remain stable. All non-header rules are byte-for-byte equivalent.
 for idx,rule in enumerate(original['m_Rules']):
  actual=copy.deepcopy(sheet['m_Rules'][idx]);actual['m_ComplexSelectors']=rule['m_ComplexSelectors'];assert actual==rule
 for key in original:
  if key!='m_Rules':assert sheet[key]==original[key]
 ob.save_typetree(sheet);raw=se.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(so)
 for pid,o in check.items():
  if pid==ob.path_id:assert o.read_typetree()==sheet
  else:assert sha(o.get_raw_data())==shashes[pid]
 outputs[folder/S]=raw
 # Verify that retained native gradient/theme functions and templates are loadable.
 cat=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());audit=[]
 for guid in ['9f6121106098fd4478470df83d3e70ee','d47d9f6bfe419344692270d5af16c5ef']:
  locs=cat.locations(guid);assert locs
  for loc in locs:
   info=cat.location(loc);assert info['type'][-1]=='SI.VisualScripting.VisualFunction' and info['dependencies']
   owner=cat.location(info['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
   pe=UnityPy.load(str(folder/owner if (folder/owner).exists() else GAME/owner));po={o.path_id:o for o in pe.objects};meta=next(o.read_typetree() for o in pe.objects if o.type.name=='AssetBundle')
   entry=next(v for k,v in meta['m_Container'] if k==guid);function=po[entry['asset']['m_PathID']].read_typetree();audit.append({'guid':guid,'object':function['m_Name'],'owner':owner})
 reports.append({'target':str(folder),'templates':changes,'removed_custom_header_selectors':sum(x['selectors'] for x in removed),'disabled_rule_selectors':removed,'native_functions':audit,'seven_shortcuts_and_holiday_preserved':True,'secondary_tabs_pages_images_and_other_objects_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('native-header-plus-shortcuts-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/p.name;bak=out/('backup-'+tag)/p.name;src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(raw);bak.write_bytes(before[p]);tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True,'native_source_for_visual_properties_only':str(baseline)}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'variants':[{'target':r['target'],'removed_custom_header_selectors':r['removed_custom_header_selectors']} for r in reports]}))
