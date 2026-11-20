from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
import importlib.util
BN='ui-backgrounds_assets_common.bundle'
bgbytes=(GAME/BN).read_bytes();be=UnityPy.load(bgbytes);bgaf=be.assets[0]
names={o.peek_name():o for o in be.objects if o.type.name=='Texture2D'}
required=['CAPAbg']+[f'{p}{i:02}' for p in ['PA','CA'] for i in range(1,21)]
assert all(n in names for n in required)
textures={n:names[n].path_id for n in required}
for n in required:
 o=names[n];d=o.read_typetree();im=o.read().image
 assert im.size==(196,19) and (d['m_Width'],d['m_Height'])==(196,19)
 assert im.mode=='RGBA' and im.getextrema()[3][0]==0
af=objects[FULL].assets_file
extpath=f'archive:/{bgaf.name}/{bgaf.name}'
fileid=next(i+1 for i,e in enumerate(af.externals) if e.path==extpath)
bundle=next(o for o in objects.values() if o.type.name=='AssetBundle')
meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta)
assert bgaf.name.lower() in meta['m_Dependencies']
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog((GAME.parent/'catalog.bin').read_bytes())
fullguid='1f6ebbeeaeba50cbbb57ef2d123b47dc'
assert all(any(cat.location(dep)['internal'].endswith('\\'+BN) for dep in cat.location(loc)['dependencies']) for loc in cat.locations(fullguid))
# Reuse the established native integer comparison switch: false=child0, true=child1.
swtemplate=copy.deepcopy(rr[1303]);sdtemplate=copy.deepcopy(rr[swtemplate['data']['m_SerializedData']['rid']])
visualtemplate=copy.deepcopy(rr[1297]);visualsd=copy.deepcopy(rr[visualtemplate['data']['m_SerializedData']['rid']])
helpers=ast.parse((R/'build-seven-badges-v39.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['string','encode','decode']],type_ignores=[]),'<native arg codec>','exec'))
comparison_args=decode(sdtemplate['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
assert struct.unpack('<i',comparison_args[0][1])[0]==4
BC='SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
new=[]
def make(parent,name,properties,sw=False,limit=None,path=None):
 global next_rid,next_id
 n,s=copy.deepcopy(swtemplate if sw else visualtemplate),copy.deepcopy(sdtemplate if sw else visualsd)
 n['rid'],s['rid']=next_rid,next_rid+1;next_rid+=2
 n['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);next_id+=1
 if sw:
  args=copy.deepcopy(comparison_args);args[1]=(args[1][0],struct.pack('<i',limit));args[2]=(BC,b'\x01'+string(path))
  s['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
  s['data']['BindDirectAsMask']=0;s['data']['InvertDirectBinding']=0
 override(n['data'],properties)
 rr[n['rid']]=n;rr[s['rid']]=s;new.extend([n,s]);rr[parent]['data']['m_Children'].append({'rid':n['rid']})
 return n['rid']
def pct(x):return val(3,{'unit':2,'value':float(x)})
zero=[prop(262150,px(0)),prop(262151,px(0)),prop(131084,num(0)),prop(131085,num(0))]
overlay=zero+[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,px(196)),prop(131087,px(19))]
def image(parent,name,texture):
 sheet['assets'].append({'m_FileID':fileid,'m_PathID':textures[texture]})
 handle={'m_ValueType':6,'valueIndex':len(sheet['assets'])-1}
 return make(parent,name,overlay+[prop(458753,handle),prop(262153,en('scale-to-fit'))])
# Expand only the graph row. The native scout/ability group above is untouched.
override(rr[1026]['data'],[prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('flex-start')),prop(131105,px(448)),prop(131097,px(0)),prop(131095,px(448)),prop(131085,num(1))])
override(rr[1043]['data'],[prop(131091,px(10)),prop(131092,px(0))])
bar=make(1026,'OverviewCAPALayeredBar',zero+[prop(131102,en('relative')),prop(131105,px(196)),prop(131097,px(196)),prop(131087,px(19)),prop(131096,px(19)),prop(131091,px(12)),prop(131074,en('center'))])
image(bar,'OverviewCAPABackground','CAPAbg')
layer_roots={}
for prefix,path in [('PA','person.PlayerPotentialAbility'),('CA','person.PlayerCurrentAbility')]:
 gate=make(bar,'Overview'+prefix+'Positive',overlay,True,0,path);layer_roots[prefix]=gate
 make(gate,'Overview'+prefix+'Unavailable',overlay)
 parent=gate
 for tier in range(1,20):
  switch=make(parent,f'Overview{prefix}Above{tier*10}',overlay,True,tier*10,path)
  image(switch,f'Overview{prefix}{tier:02}',f'{prefix}{tier:02}')
  parent=switch
 image(parent,f'Overview{prefix}20',f'{prefix}20')
doc['references']['RefIds'].extend(new)
# Add external textures to this VTA's preload span; leave all other asset entries intact.
entry=next(v for k,v in meta['m_Container'] if k==fullguid)
span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for n in required:
 ptr={'m_FileID':fileid,'m_PathID':textures[n]}
 if ptr not in span:span.append(ptr)
entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span);meta['m_PreloadTable'].extend(span)
# Evaluate the serialized switches, rather than merely testing a parallel formula.
def selected(i,value):
 d=rr[i]['data']
 if d.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  s=rr[d['m_SerializedData']['rid']]['data'];args=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
  limit=struct.unpack('<i',args[1][1])[0]
  return selected(d['m_Children'][int(value is not None and value>limit)]['rid'],value)
 s=rr[d['m_SerializedData']['rid']]['data'];return s['name']
checks={}
for prefix in ['PA','CA']:
 checks[prefix]={}
 for value in [None]+list(range(-10,222)):
  result=selected(layer_roots[prefix],value)
  expected='Overview'+prefix+('Unavailable' if value is None or value<=0 else f'{min(20,(value+9)//10):02}')
  assert result==expected,(prefix,value,result,expected)
  if value in [None,0,1,10,11,190,191,200,201]:checks[prefix][str(value)]=result
assert rr[bar]['data']['m_Children'][1:]==[{'rid':layer_roots['PA']},{'rid':layer_roots['CA']}]
assert all(rr[i]==old_refs[i] for i in old_refs if i not in [1026,1043])
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet);bundle.save_typetree(meta)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid,bundle.path_id]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet,bundle.path_id:meta}[i]
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
resolved=UnityPy.load(output,bgbytes);wf=next(a for a in resolved.assets if a.name==af.name)
for ptr in sheet['assets'][-41:]:
 from UnityPy.classes import PPtr
 assert PPtr(m_FileID=ptr['m_FileID'],m_PathID=ptr['m_PathID'],assetsfile=wf).deref().read_typetree()['m_Name'] in required
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
# Mirror the user's freshly updated background bundle if the skin copy is older.
skinbg=SKIN/BN;skinbg_before=skinbg.read_bytes() if skinbg.exists() else None
syncbg=skinbg_before!=bgbytes
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('capa-layered-bar-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
 if syncbg:
  data=bgbytes if tag=='game' else skinbg_before
  if data is not None:(bp/BN).write_bytes(data)
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid,bundle.path_id],'texture_ids':textures,'bar_size':[196,19],'layer_order':['CAPAbg','PA','CA'],'tier_boundary_checks':checks,'values_tested_per_layer':233,'native_scout_and_stars_unchanged':True,'second_version_unchanged':True,'catalog_unchanged':True,'skin_background_synced':syncbg,'background_source_sha256':sha(bgbytes),'skin_background_before_sha256':sha(skinbg_before) if skinbg_before else None,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-3}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 if syncbg:skinbg.write_bytes(bgbytes);assert skinbg.read_bytes()==bgbytes
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 if syncbg:
  if skinbg_before is None:skinbg.unlink(missing_ok=True)
  else:skinbg.write_bytes(skinbg_before)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output),'skin_background_synced':syncbg},ensure_ascii=False))
