from pathlib import Path
R=Path(__file__).parent
source=(R/'add-touch-bar-dynamics-happiness-condition.py').read_text(encoding='utf8')
prefix=source.split('# Use the existing native player context')[0].replace("assert len(rr[wrap]['data']['m_Children'])==11","assert len(rr[wrap]['data']['m_Children'])==19")
exec(compile(prefix,'<current bundle and pure helpers>','exec'))
TP=-8181614945060108653;td=objects[TP].read_typetree();tr={r['rid']:r for r in td['references']['RefIds']}
assert tr[1007]['data']['DebugDisplay']=='Fitness'
condition=named('HeaderStatus_OverallCondition')['rid']
templ=named('HeaderOverallHappinessTitle')
title=addpair(templ,tr[1007],condition,'HeaderFitnessTitle');textstyle(title,True)
rr[condition]['data']['m_Children'].remove({'rid':title});rr[condition]['data']['m_Children'].insert(0,{'rid':title})
# Preserve the original Fitness translation ID/function bytes exactly.
a=copy.deepcopy(rr[rr[title]['data']['m_SerializedData']['rid']]['data']);b=copy.deepcopy(tr[1007]['data'])
for d in [a,b]:
 for k in ['uxmlAssetId','name','name_UxmlAttributeFlags']:d.pop(k,None)
assert a==b
order=[m[1029],m[1030],m[1033],m[1034],condition,m[1028],m[1032],named('HeaderStatus_Mindset')['rid'],named('HeaderStatus_Hierarchy')['rid'],named('HeaderStatus_OverallHappiness')['rid']]
oldchildren=rr[wrap]['data']['m_Children'];separators=[c['rid'] for c in oldchildren if c['rid'] not in order]
assert len(order)==10 and len(set(order))==10 and len(separators)==9
children=[]
for index,i in enumerate(order):
 if index:children.append({'rid':separators[index-1]})
 children.append({'rid':i})
rr[wrap]['data']['m_Children']=children
assert all(rr[c['rid']]['data']['m_Parent']['rid']==wrap for c in children)
for i,r in oldrefs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('Existing binding changed',i)
assert rr[action]==oldrefs[action]
assert not any(r.get('data',{}).get('name') in ['HeaderMindsetIcon','HeaderHierarchyIcon'] for r in rr.values())
assert len(newids)==2
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
out=R/('touch-bar-native-fitness-title-reorder-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
labels=['比赛负荷','伤病可能','训练负荷','伤病风险','体能','比赛状态','精力','心态','层级','个人情绪']
report={'installed':False,'runtime_verified':False,'order':labels,'ordered_nodes':order,'fitness_title':{'source_asset':TP,'source_serialized':1007,'new_node':title,'native_translation_binding_preserved':True},'mindset_hierarchy_icons_absent':True,'existing_dynamic_bindings_and_action_preserved':True,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(path):sha(data) for path,data in before.items()},'after_sha256':sha(output),'protected_sha256':{str(path):h for path,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for path,h in protected.items():assert sha(path.read_bytes())==h
except Exception:
 for path,data in before.items():path.write_bytes(data)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'order':labels,'native_fitness_title_added':True,'sha256':sha(output)},ensure_ascii=False,indent=2))
