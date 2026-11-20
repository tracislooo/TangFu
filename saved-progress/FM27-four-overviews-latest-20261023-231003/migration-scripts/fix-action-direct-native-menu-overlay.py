from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
# Match the native SIButton -> last-child PluginContextMenuBindings overlay hierarchy.
assert rr[1907]['data']['m_Children']==[{'rid':1103}]
assert rr[1103]['data']['m_Children']==[{'rid':1909}]
assert rr[1909]['data']['m_Children']==[{'rid':i} for i in [1104,1105,1106,1107]]
rr[1907]['data']['m_Children']=[{'rid':1909}]
rr[1909]['data']['m_Parent']={'rid':1907}
rr[1909]['data']['m_Children'].append({'rid':1103})
rr[1103]['data']['m_Parent']={'rid':1909}
rr[1103]['data']['m_Children']=[]
rr[1103]['data']['m_Classes']=['plugin-context-menu-bindings-overlay']
rr[1109]['data']['BindingPaths']=[{'m_path':'person'}]
rr[1109]['data']['name']='OverviewActionsDirectMenuOverlay'
rr[1109]['data']['name_UxmlAttributeFlags']=1
# Explicit hit layer: no SIButton descendant captures the mouse before the menu manipulator.
override(rr[1103]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131103,px(0)),prop(131105,{'m_ValueType':3,'valueIndex':len(sheet['dimensions'])})] if False else [prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131103,px(0)),prop(131105,val(3,{'unit':2,'value':100.0})),prop(131087,px(32)),prop(131096,px(32)),prop(131094,px(32)),prop(262150,px(0)),prop(262151,px(0)),prop(458768,en('visible'))])
assert {i for i in old_refs if rr[i]!=old_refs[i]}=={1907,1909,1103,1109}
assert set(rr)==set(old_refs)
assert all(rr[i]==old_refs[i] for i in [1910,1908,1199,1214,1215,1237])
node_count=validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4')
saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,data in before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('action-direct-native-menu-overlay-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_bundle':WN,'changed_assets':[FULL,sid],'changed_nodes':[1907,1909,1103,1109],'change':'Native menu last-child overlay receives clicks directly; binding person in inherited scope','validated_nodes':node_count,'unchanged_objects':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:
   (folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except Exception:
  for p,data in before.items():p.write_bytes(data)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':report['installed'],'sha256':sha(output),'unchanged_objects':len(old_hashes)-2},ensure_ascii=False,indent=2))
