from pathlib import Path
R=Path(__file__).parent
source=(R/'add-touch-bar-dynamics-happiness-condition.py').read_text(encoding='utf8')
prefix=source.split('# Use the existing native player context')[0].replace("assert len(rr[wrap]['data']['m_Children'])==11","assert len(rr[wrap]['data']['m_Children'])==17")
exec(compile(prefix,'<existing loader and pure helpers>','exec'))
# Roll back the newly failing Mindset icon; Hierarchy's icon remains absent.
assert rr[1141]['data']['m_FullTypeName']=='SI.Bindable.SIImage'
assert rr[1142]['data']['name']=='HeaderMindsetIcon'
parent=rr[1141]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':1141})
removed={1141,1142}
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed:del rr[i]
assert 1143 not in rr and 1144 not in rr
assert rr[1145]['data']['m_FullTypeName']=='SI.Bindable.SIImage'
# Add native Overall Happiness as text, reusing the already working player scope.
p=pill('OverallHappiness')
textstyle(native(HT,1006,p,'HeaderOverallHappinessTitle'),True)
textstyle(native(HAP,1015,p,'HeaderOverallHappinessValue'))
assert len(binding_copies)==2
for c in binding_copies:
 a=copy.deepcopy(rr[c['serialized']]['data']);b=copy.deepcopy(src[c['source_asset']][c['source_serialized']]['data'])
 for d in [a,b]:
  for key in ['uxmlAssetId','name','name_UxmlAttributeFlags']:d.pop(key,None)
 assert a==b
for i,r in oldrefs.items():
 if i not in removed and 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r
assert rr[action]==oldrefs[action]
assert len(rr[wrap]['data']['m_Children'])==19
assert all(rr[i].get('data',{}).get('m_FullTypeName') not in ['SI.Bindable.SIImage','SI.Bindable.SIVisible','SI.Bindable.BindingRemapper'] for i in newids)
assert not any(r.get('data',{}).get('name') in ['HeaderMindsetIcon','HeaderHierarchyIcon'] for r in rr.values())
assert sum(r.get('data',{}).get('name')=='HeaderOverallConditionIcon' for r in rr.values())==1
count=validate_ui(doc,sheet)
objects[HP].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [HP,sid]:assert saved[i].read_typetree()=={HP:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[HP].read_typetree(),saved[sid].read_typetree())
for path,data in before.items():assert path.read_bytes()==data
for path,h in protected.items():assert sha(path.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('rollback-mindset-icon-add-happiness-text-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
tested=(R/'isolate-touch-bar-icons-20261019-002114/only-OverallCondition'/WN).read_bytes()
assert sha(tested)=='0c80951534506ad15a3e2f78cd4e74d474015d4abea4c4b807d6662cce597350'
(out/'tested-condition-only.bundle').write_bytes(tested)
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'removed_failing_icon':'Mindset','hierarchy_icon_omitted':True,'tested_overall_condition_icon_preserved':True,'added_metric':'Overall Happiness','new_happiness_icon_added':False,'copied_native_bindings':binding_copies,'new_aliases_or_visibility_branches':False,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(path):sha(data) for path,data in before.items()},'after_sha256':sha(output),'protected_sha256':{str(path):h for path,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for path,h in protected.items():assert sha(path.read_bytes())==h
except Exception:
 for path,data in before.items():path.write_bytes(data)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'removed_icons':['Mindset','Hierarchy'],'overall_condition_icon_preserved':True,'added':'Overall Happiness text','sha256':sha(output)},ensure_ascii=False,indent=2))
