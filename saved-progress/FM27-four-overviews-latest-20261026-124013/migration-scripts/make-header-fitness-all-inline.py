from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
HP=5775949770471550939
doc=objects[HP].read_typetree();old_doc=copy.deepcopy(doc);rr={r['rid']:r for r in doc['references']['RefIds']};old_refs=copy.deepcopy(rr)
sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree()
mf=json.loads((R/'header-six-native-fitness-metrics-20261018-013417/manifest.json').read_text(encoding='utf8'))
m={int(k):v for k,v in mf['new_node_mapping'].items()}
roots=[1028,1029,1030,1032,1033,1034];titles=[1174,1107,1113,1119,1126,1131];rows=[1053,1056,1060,1065,1128,1072];values=[1178,1109,1115,1123,1191,1133]
def edit(i,p):override(rr[m[i]]['data'],p)
for i in roots:
 edit(i,[prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('flex-start'))])
for i in titles:
 edit(i,[prop(131087,px(32)),prop(131105,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(131092,px(6)),prop(65552,en('nowrap'))])
for i in rows:
 edit(i,[prop(131087,px(32)),prop(131105,auto()),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131097,px(0))])
edit(1068,[prop(131087,px(32)),prop(131105,auto()),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131097,px(0))])
for i in values:edit(i,[prop(65552,en('nowrap')),prop(131087,px(32))])
# Only inline layout rule indices change; all native bindings, hierarchy, action and icons stay intact.
allowed={m[i] for i in roots+titles+rows+values+[1068]}
assert {i for i in old_refs if rr[i]!=old_refs[i]}==allowed
for i in allowed:
 a=copy.deepcopy(rr[i]);a['data']['m_RuleIndex']=old_refs[i]['data']['m_RuleIndex'];assert a==old_refs[i]
validate_ui(doc,sheet)
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
out=R/('header-fitness-all-inline-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'change':'Each fitness module title, image/value and stepper now one horizontal row','header_height':32,'native_bindings_action_icons_unchanged':True,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except Exception:
  for p,d in before.items():p.write_bytes(d)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':report['installed'],'sha256':sha(output)},ensure_ascii=False,indent=2))
