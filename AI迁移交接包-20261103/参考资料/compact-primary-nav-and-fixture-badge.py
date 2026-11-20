"""Reduce only main-menu labels to 80 percent and add the native opponent badge."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,sys
R=Path(__file__).resolve().parent
setup=(R/'change-staff-shortcut-to-recruitment-database.py').read_text('utf8').split('nav=UnityPy.load')[0]
exec(compile(setup,'resource-initialization-only','exec'))
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';S='ui-styles_assets_default.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [G,S]}
for p in before:protected.pop(p,None)
for f in [GAME,SKIN]:protected[f/W]=sha((f/W).read_bytes())
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename,names in [('build-fc-player-hover-layout.py',{'Styles'}),('add-card-six-ratings.py',{'validate_ui'}),('fix-primary-navigation-grey-lake-blue.py',{'selector'})]:
 tree=ast.parse((R/filename).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names],type_ignores=[]),filename+':definitions-only','exec'))
spec=importlib.util.spec_from_file_location('compact_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def serial(rr,i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
def argsdecode(v):
 b=bytes(v);p=1;args=[]
 for _ in range(b[0]):
  n=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+n]);p+=n
 assert p==len(b);return args
def argsencode(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
outputs={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 we=UnityPy.load(str(folder/W));team=next(o.read_typetree() for o in we.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='TeamLogo');tr=refs(team)
 image=next(i for i in tr if tr[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIImage')
 ge=UnityPy.load(before[folder/G]);go={o.path_id:o for o in ge.objects};gh={i:sha(o.get_raw_data()) for i,o in go.items()}
 obj=next(o for o in go.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='CurrentDayWidget');doc=obj.read_typetree();old=copy.deepcopy(doc);rr=refs(doc)
 parent=next(i for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(rr,i).get('name')=='HasFixture')
 assert not any(r.get('data',{}).get('name')=='NextFixtureOpponentBadge' for r in rr.values())
 a=copy.deepcopy(tr[image]);sd=copy.deepcopy(tr[a['data']['m_SerializedData']['rid']]);a['rid']=max(rr)+1;sd['rid']=a['rid']+1
 eid=1911012000;assert eid not in {r.get('data',{}).get('m_Id') for r in rr.values()}
 a['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_StylesheetPaths=[],m_Stylesheets=[],m_Properties=[],m_SerializedData={'rid':sd['rid']})
 sd['data'].update(uxmlAssetId=eid,name='NextFixtureOpponentBadge',name_UxmlAttributeFlags=1)
 vf=sd['data']['Binding']['m_visualFunction'];assert vf['m_target']['m_guid']=='7a35874b5cb0acb4d846df3f46c3a872'
 args=argsdecode(vf['m_inputs']['m_variable']['m_argumentBytes']);assert len(args)==5
 paths=[]
 for i in range(4):
  raw=args[i];size=raw[0];prefix=raw[:size+2];assert raw[size+1]==1
  path=raw[size+3:].decode('utf8');assert raw[size+2]==len(raw[size+3:]) and path.startswith('Team.')
  path='teamrequestingreport.NextFixture.TeamOpponent.'+path[5:];paths.append(path)
  args[i]=prefix+string(path)
 vf['m_inputs']['m_variable']['m_argumentBytes']=argsencode(args)
 assert argsdecode(vf['m_inputs']['m_variable']['m_argumentBytes'])==args
 for record in [a,sd]:rr[record['rid']]=record;doc['references']['RefIds'].append(record)
 rr[parent]['data']['m_Children'].insert(0,{'rid':a['rid']})
 assert {(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in [a,sd]}<={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in obj.assets_file.ref_types}
 sid=doc['inlineSheet']['m_PathID'];sheet=go[sid].read_typetree();st=Styles(sheet)
 st.edit(a,[st.p(131105,st.px(16)),st.p(131087,st.px(16)),st.p(131097,st.px(16)),st.p(131095,st.px(16)),st.p(131096,st.px(16)),st.p(131094,st.px(16)),st.p(131085,st.num(0)),st.p(262150,st.px(0)),st.p(131092,st.px(4)),st.p(262151,st.px(0))])
 # The inline rule is numeric only, avoiding the game's inline variable resolver crash.
 assert all(h['m_ValueType'] not in [8,10] for p in sheet['m_Rules'][a['data']['m_RuleIndex']]['m_Properties'] for h in p['m_Values'])
 for r in old['references']['RefIds']:
  expected=copy.deepcopy(r)
  if r['rid']==parent:expected['data']['m_Children']=rr[parent]['data']['m_Children']
  assert rr[r['rid']]==expected,('Existing date/fixture binding changed',r['rid'])
 validate_ui(doc,sheet);obj.save_typetree(doc);go[sid].save_typetree(sheet)
 se=UnityPy.load(before[folder/S]);so={o.path_id:o for o in se.objects};sh={i:sha(o.get_raw_data()) for i,o in so.items()}
 stylesheet=next(o for o in so.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');style=stylesheet.read_typetree();oldstyle=copy.deepcopy(style)
 # Resolve the current native font token rather than assuming a particular pixel size.
 prop=next(p for rule in style['m_Rules'] if any(any(part['m_Value']=='thematic-md' for sel in c['m_Selectors'] for part in sel['m_Parts']) for c in rule['m_ComplexSelectors']) for p in rule['m_Properties'] if p['m_Id']==65537)
 token=style['strings'][prop['m_Values'][-1]['valueIndex']];seen=set()
 while True:
  assert token not in seen;seen.add(token)
  values=[p['m_Values'] for r in style['m_Rules'] for p in r['m_Properties'] if p['m_CustomName']==token];assert len(values)==1
  v=values[0]
  if len(v)==1 and v[0]['m_ValueType']==3:
   dimension=style['dimensions'][v[0]['valueIndex']];assert dimension['unit']==1;native_size=dimension['value'];break
  assert v[-1]['m_ValueType']==8;token=style['strings'][v[-1]['valueIndex']]
 ss=Styles(style);idx=len(style['m_Rules']);size=f32(native_size*.8)
 style['m_Rules'].append({'m_ComplexSelectors':[selector('#MainNav #MenuBar .portal-text',idx)],'m_Properties':[ss.p(65537,ss.px(size))],'line':-1})
 assert style['m_Rules'][:-1]==oldstyle['m_Rules']
 stylesheet.save_typetree(style)
 # Existing object IDs and catalogs suffice: only a node is added to an existing registered VTA.
 cat=cm.Catalog(((GAME.parent if tag=='game' else SKIN)/'catalog.bin').read_bytes());audit=[]
 for guid,owner in [('7a35874b5cb0acb4d846df3f46c3a872',None)]:
  locs=cat.locations(guid);assert locs
  for loc in locs:
   info=cat.location(loc);assert info['internal']==guid and info['dependencies']
   owner=cat.location(info['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
   pe=UnityPy.load(str(folder/owner if (folder/owner).exists() else GAME/owner));po={o.path_id:o for o in pe.objects};meta=next(o.read_typetree() for o in pe.objects if o.type.name=='AssetBundle')
   entries=[entry for key,entry in meta['m_Container'] if key==guid];assert entries and all(x['asset']['m_PathID'] in po for x in entries)
   audit.append({'guid':guid,'owner':owner,'objects':[po[x['asset']['m_PathID']].peek_name() for x in entries]})
 gm=next(o.read_typetree() for o in go.values() if o.type.name=='AssetBundle')
 widget_guids=[key for key,entry in gm['m_Container'] if entry['asset']['m_PathID']==obj.path_id];assert widget_guids
 for guid in widget_guids:
  locs=cat.locations(guid);assert locs
  for loc in locs:
   info=cat.location(loc);assert info['internal']==guid and info['dependencies']
   dependencies=[cat.location(dep)['internal'].replace('\\','/').split('/')[-1] for dep in info['dependencies']]
   assert dependencies[0]==G
   assert info['type'][-1] in ['UnityEngine.UIElements.VisualTreeAsset','UnityEngine.UIElements.StyleSheet']
  # VisualFunction is a dynamic GUID lookup, independently registered and audited above.
  audit.append({'guid':guid,'owner':G,'object':'CurrentDayWidget','native_dependencies_preserved':True,'dynamic_function_catalog_verified':True})
 for name,en,objects,hashes,expected in [(G,ge,go,gh,{obj.path_id:doc,sid:sheet}),(S,se,so,sh,{stylesheet.path_id:style})]:
  raw=en.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(objects)
  for i,o in check.items():
   if i in expected:assert o.read_typetree()==expected[i],('Roundtrip failed',name,i)
   else:assert sha(o.get_raw_data())==hashes[i],('Unrelated asset changed',name,i)
  outputs[folder/name]=raw
 reports.append({'target':str(folder),'original_font_size':native_size,'new_font_size':size,'font_ratio':.8,'font_scope':'#MainNav #MenuBar .portal-text','badge_size':16,'badge_binding_paths':paths,'function_audit':audit,'date_and_fixture_events_unchanged':True})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('primary-nav-compact-fixture-badge-'+stamp);out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/p.name;bak=out/('backup-'+tag)/p.name
 src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(raw);bak.write_bytes(before[p]);tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
m={'installed':False,'runtime_verified':False,'changes':reports,'protected_sha256':{str(p):h for p,h in protected.items()},'no_desktop_or_game_control':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
print(json.dumps({'prepared':True,'output':str(out),'changes':reports},ensure_ascii=False))
