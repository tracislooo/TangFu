from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<current bundle loader>','exec'))
base=R/'gk-no-title-left-stars-horizontal-loans-20261019-011613'
rep=json.loads((base/'manifest.json').read_text(encoding='utf8'))
left,right=rep['inline_imports'][:2]
assert left['prefix']=='IdentityAbility_' and right['prefix']=='RightScout_'
source_env=UnityPy.load(str(base/'backup-game'/WN));source_objects={o.path_id:o for o in source_env.objects}
source_doc=source_objects[FULL].read_typetree();sr={r['rid']:r for r in source_doc['references']['RefIds']}
source_sheet=source_objects[source_doc['inlineSheet']['m_PathID']].read_typetree()
# Old inline styles are unchanged prefixes; original native template can reuse its exact rule index.
for pool in ['m_Rules','floats','dimensions','colors','strings','assets']:
 assert sheet[pool][:len(source_sheet[pool])]==source_sheet[pool],('Source style pool prefix changed',pool)
star=rep['star_holder'];holder_sd=rr[star]['data']['m_SerializedData']['rid']
assert rr[1297]['data']['m_Children'].count({'rid':star})==1
rr[1297]['data']['m_Children'].remove({'rid':star})
removed={star,holder_sd}
for imp in [left,right]:
 removed.update(int(v) for k,v in imp['mapping'].items() if int(k)!=1000)
assert not any(i in removed for i in [1203,1217,1193,1297,1184])
# Reuse the original right-hand native ScoutSection template and its original current-player context.
for i in [1203,1217]:rr[i]=copy.deepcopy(sr[i])
assert rr[1203]['data']['m_TemplateAlias']=='MovedBanner_PlayerReportHeaderScoutSection'
assert rr[1217]['data']['templateId']=='MovedBanner_PlayerReportHeaderScoutSection'
assert rr[1203]['data']['m_Parent']==old_refs[1203]['data']['m_Parent']
for i in removed:del rr[i]
doc['references']['RefIds']=[rr[r['rid']] for r in doc['references']['RefIds'] if r['rid'] not in removed]
old_using_count=len(doc['m_Usings'])
doc['m_Usings']=[u for u in doc['m_Usings'] if not u['alias'].startswith(('IdentityAbility_','RightScout_'))]
assert old_using_count-len(doc['m_Usings'])==10
assert rr[1297]['data']['m_Children']==[{'rid':1171},{'rid':1295},{'rid':1184}]
assert {i for i in old_refs if i not in removed and rr[i]!=old_refs[i]}=={1297,1203,1217}
assert rr[1203]==sr[1203] and rr[1217]==sr[1217]
# Keep tighter country/club/loan spacing and native vertical contract layout exactly as installed.
assert rr[1184]==old_refs[1184] and rr[1199]==old_refs[1199]
clubmap={int(k):v for k,v in rep['inline_imports'][2]['mapping'].items()}
for old,new in clubmap.items():
 if old!=1000:assert rr[new]==old_refs[new]
assert property_value(rr[1199],131083)=='column'
assert property_value(rr[clubmap[1007]],131083)=='row'
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i==FULL:assert saved[i].read_typetree()==doc
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,data in before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('restore-ability-stars-native-right-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'native_right_scout_template_restored':True,'native_template_records_exact_source_matches':[1203,1217],'left_star_block_removed':True,'removed_inline_records':sorted(removed),'left_country_club_gap_and_horizontal_loans_preserved':True,'native_vertical_contract_preserved':True,'goalkeeping_heading_removal_preserved':True,'card_numeric_CA_PA_preserved':True,'changed_assets':[FULL],'unchanged_assets_verified':len(old_hashes)-1,'before_sha256':{str(p):sha(data) for p,data in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,data in before.items():p.write_bytes(data)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'stars_restored_to_native_right_module':True,'other_layout_changes_preserved':True,'sha256':sha(output)},ensure_ascii=False,indent=2))
