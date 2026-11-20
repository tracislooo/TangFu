from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
helpers=ast.parse((R/'build-seven-badges-v39.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['string','encode','decode']],type_ignores=[]),'<native codec>','exec'))
base=R/'hidden-attributes-four-row-panel-20261019-130113'
previous=json.loads((base/'manifest.json').read_text(encoding='utf8'))
paths={e['path']:e['path'].removesuffix('.PropertyValue')+'.AttributeMinValue' for e in previous['attributes']}
assert len(paths)==13 and all(k.endswith('.PropertyValue') for k in paths)
# Verify the real native hidden-column cell explicitly reads AttributeMinValue.
bm=next(o for o in objects.values() if o.type.name=='AssetBundle').read_typetree()
nativepid=next(v['asset']['m_PathID'] for k,v in bm['m_Container'] if k=='cd65232d2c8c59e4592f0bb85658abb4')
native=objects[nativepid].read_typetree()
mappings=[m for r in native['references']['RefIds'] for m in r.get('data',{}).get('Mappings',[])]
assert any(m['from']=='minValue' and m['to']['m_path']=='binding.AttributeMinValue' for m in mappings)
changed=[];direct_count=0;switch_count=0
BC='SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
for i,r in rr.items():
 d=r.get('data',{})
 if not d.get('name','').startswith('OverviewHidden'):continue
 old=copy.deepcopy(d)
 text=d.get('TextBinding')
 if text and text.get('m_kind')==1:
  p=text['m_direct']['Path']['m_path']
  if p in paths:text['m_direct']['Path']['m_path']=paths[p];direct_count+=1
 binding=d.get('Binding')
 if binding and binding.get('m_kind')==2:
  vf=binding['m_visualFunction']
  if vf['m_target']['m_guid']=='f6f314e9db56227459137669d87c44e9':
   args=decode(vf['m_inputs']['m_variable']['m_argumentBytes']);cls,payload=args[2]
   assert cls==BC and payload[0]==1
   p=payload[2:2+payload[1]].decode()
   if p in paths:
    args[2]=(cls,b'\x01'+string(paths[p]));vf['m_inputs']['m_variable']['m_argumentBytes']=encode(args);switch_count+=1
 if d!=old:changed.append(i)
assert direct_count==13 and switch_count==143,(direct_count,switch_count)
assert {i for i in rr if rr[i]!=old_refs[i]}==set(changed)
assert sheet==old_sheet
# Every changed record differs solely in its numeric source path/encoded input bytes.
for i in changed:
 a=copy.deepcopy(rr[i]);b=old_refs[i]
 if 'TextBinding' in a['data']:
  a['data']['TextBinding']['m_direct']['Path']['m_path']=b['data']['TextBinding']['m_direct']['Path']['m_path']
 else:a['data']['Binding']['m_visualFunction']['m_inputs']=copy.deepcopy(b['data']['Binding']['m_visualFunction']['m_inputs'])
 assert a==b,i
checks={}
for key in ['adaptability','ambition','controversy','loyalty','pressure','professionalism','sportsmanship','temperament','versatility','consistency','dirtiness','important-matches','injury-proneness']:
 root=named('OverviewHiddenImagePositive_'+key)['rid']
 def pick(i,v):
  a=rr[i]['data'];s=rr[a['m_SerializedData']['rid']]['data']
  if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
   args=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack('<i',args[1][1])[0]
   assert b'AttributeMinValue' in args[2][1]
   return pick(a['m_Children'][int(v is not None and v>limit)]['rid'],v)
  return s['name']
 checks[key]={}
 for v in [None]+list(range(-2,23)):
  result=pick(root,v)
  expected='OverviewHiddenImageUnavailable_'+key if v is None or v<=0 else f'OverviewHiddenImage_{key}_{min(10,(v+1)//2):02}'
  assert result==expected,(key,v,result)
  if v in [None,0,1,2,3,18,19,20,21]:checks[key][str(v)]=result
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i==FULL:assert saved[i].read_typetree()==doc
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('fix-hidden-integer-minvalue-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL],'numeric_path_replacements':paths,'direct_number_bindings_fixed':direct_count,'integer_switch_bindings_fixed':switch_count,'changed_records':changed,'native_minvalue_mapping_verified':True,'layout_textures_titles_and_thresholds_unchanged':True,'tier_boundary_checks':checks,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-1}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'number_bindings':direct_count,'switch_bindings':switch_count,'sha256':sha(output)},ensure_ascii=False))
