from pathlib import Path
R=Path(__file__).parent
source=(R/'add-touch-bar-dynamics-happiness-condition.py').read_text(encoding='utf8')
exec(compile(source.split('# Use the existing native player context')[0],'<restored baseline and pure helpers>','exec'))
# Build on the rolled-back version. Reuse its existing player scope unchanged.
modules=[]
for name,titleid,valueid in [('Mindset',1058,1059),('Hierarchy',1062,1063)]:
 p=pill(name);modules.append(p)
 textstyle(native(DYN,titleid,p,'Header'+name+'Title'),True)
 textstyle(native(DYN,valueid,p,'Header'+name+'Value'))
p=pill('OverallCondition');modules.append(p)
textstyle(native(FIT,1217,p,'HeaderOverallConditionValue'))
# Give tenured content its natural width as three text pills join the bar.
for i in [1028,1032,1029,1030,1033,1034]:edit(m[i],[prop(131082,auto()),prop(131099,px(5)),prop(131100,px(5))])
for i,r in rr.items():
 sd=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if sd.get('name','').startswith('HeaderFitnessSeparator'):edit(i,[prop(131091,px(3)),prop(131092,px(3))])
# Existing bindings and controls are exact matches to the rollback baseline.
for i,r in oldrefs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('Existing binding changed',i)
assert rr[action]==oldrefs[action]
assert len(rr[wrap]['data']['m_Children'])==17
assert len(binding_copies)==5
assert all('OverallHappiness' not in rr[i].get('data',{}).get('name','') for i in newids)
assert not any(rr[i].get('data',{}).get('m_FullTypeName') in ['SI.Bindable.SIImage','SI.Bindable.SIVisible','SI.Bindable.BindingRemapper'] for i in newids)
for c in binding_copies:
 a=copy.deepcopy(rr[c['serialized']]['data']);b=copy.deepcopy(src[c['source_asset']][c['source_serialized']]['data'])
 for d in [a,b]:
  for key in ['uxmlAssetId','name','name_UxmlAttributeFlags']:d.pop(key,None)
 assert a==b
count=validate_ui(doc,sheet)
objects[HP].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [HP,sid]:assert saved[i].read_typetree()=={HP:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[HP].read_typetree(),saved[sid].read_typetree())
for p,d in before.items():assert p.read_bytes()==d
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('touch-bar-three-status-text-only-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'baseline':'Rolled back to pre-four-status version','added_metrics':['Mindset','Hierarchy','Overall Condition'],'happiness_omitted':True,'native_text_bindings_only':True,'new_images_visibility_and_aliases':False,'copied_bindings':binding_copies,'new_module_nodes':modules,'native_bindings_preserved':True,'action_preserved':True,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except Exception:
  for p,d in before.items():p.write_bytes(d)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':report['installed'],'sha256':sha(output),'validated_nodes':count},ensure_ascii=False,indent=2))
