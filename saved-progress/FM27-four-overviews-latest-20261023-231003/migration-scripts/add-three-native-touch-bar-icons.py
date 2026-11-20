from pathlib import Path
R=Path(__file__).parent
source=(R/'add-touch-bar-dynamics-happiness-condition.py').read_text(encoding='utf8')
prefix=source.split('# Use the existing native player context')[0].replace("assert len(rr[wrap]['data']['m_Children'])==11","assert len(rr[wrap]['data']['m_Children'])==17")
exec(compile(prefix,'<existing read-only loader and helpers>','exec'))
for name,pid,sourceid,valuename in [('Mindset',DYN,1047,'HeaderMindsetValue'),('Hierarchy',DYN,1050,'HeaderHierarchyValue'),('OverallCondition',GO,1007,'HeaderOverallConditionValue')]:
 parent=named('HeaderStatus_'+name)['rid'];value=named(valuename)['rid']
 icon=native(pid,sourceid,parent,'Header'+name+'Icon');iconstyle(icon)
 rr[parent]['data']['m_Children'].remove({'rid':icon})
 index=rr[parent]['data']['m_Children'].index({'rid':value})
 rr[parent]['data']['m_Children'].insert(index,{'rid':icon})
assert len(newids)==6 and len(binding_copies)==3
assert all(rr[i]==r for i,r in oldrefs.items() if 'UxmlSerializedData' in r['type']['class'])
assert rr[action]==oldrefs[action]
assert len(rr[wrap]['data']['m_Children'])==17
assert all(rr[i].get('data',{}).get('m_FullTypeName')!='SI.Bindable.SIVisible' for i in newids)
for c in binding_copies:
 a=copy.deepcopy(rr[c['serialized']]['data']);b=copy.deepcopy(src[c['source_asset']][c['source_serialized']]['data'])
 for d in [a,b]:
  for k in ['uxmlAssetId','name','name_UxmlAttributeFlags']:d.pop(k,None)
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
out=R/('touch-bar-three-native-status-icons-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'added_native_icons':['Mindset','Hierarchy','Overall Condition'],'icon_size':14,'copied_bindings':binding_copies,'existing_bindings_and_action_unchanged':True,'no_new_aliases_or_visibility_branches':True,'happiness_not_added':True,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
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
