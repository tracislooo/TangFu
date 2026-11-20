from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
HP=5775949770471550939
doc=objects[HP].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};oldrefs=copy.deepcopy(rr)
sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree()
m={int(k):v for k,v in json.loads((R/'header-six-native-fitness-metrics-20261018-013417/manifest.json').read_text())['new_node_mapping'].items()}
row=named('FrameActions')['rid'];wrap=named('HeaderFitnessSixMetrics')['rid']
action=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
def edit(i,ps):override(rr[i]['data'],ps)
# Native USS styling only; no textures or runtime bindings need to change.
edit(row,[prop(458752,color(8,8,10)),prop(262147,px(9)),prop(262148,px(1)),prop(262146,color(65,65,70)),prop(131099,px(6)),prop(131100,px(6)),prop(131073,en('center')),prop(458768,en('visible'))])
edit(wrap,[prop(131092,px(8)),prop(131073,en('center'))])
for i in [1028,1032,1029,1030,1033,1034]:
 edit(m[i],[prop(131087,px(26)),prop(131096,px(26)),prop(131094,px(26)),prop(131074,en('center')),prop(458752,color(31,31,34)),prop(262147,px(6)),prop(262148,px(1)),prop(262146,color(49,49,53)),prop(131099,px(7)),prop(131100,px(7))])
for i in [1174,1107,1113,1119,1126,1131]:
 edit(m[i],[prop(131087,px(24)),prop(65536,color(173,173,181)),prop(65537,px(11)),prop(131092,px(6))])
for i in [1178,1109,1115,1123,1191,1133]:edit(m[i],[prop(131087,px(24)),prop(65537,px(12))])
for i in [1053,1056,1060,1065,1128,1072,1068]:edit(m[i],[prop(131087,px(24))])
for i,r in rr.items():
 sd=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if sd.get('name','').startswith('HeaderFitnessSeparator'):
  edit(i,[prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(131091,px(5)),prop(131092,px(5)),prop(458752,color(124,124,132,95))])
# Action gets the same dark key treatment, keeping native click/menu bindings.
edit(action,[prop(131087,px(26)),prop(131096,px(26)),prop(131094,px(26)),prop(131074,en('center')),prop(458752,color(48,48,53)),prop(262147,px(6)),prop(262148,px(1)),prop(262146,color(83,83,91)),prop(131099,px(10)),prop(131100,px(10))])
for c in rr[action]['data']['m_Children']:
 i=c['rid'];d=rr[i]['data']
 if d.get('m_FullTypeName')=='SI.Bindable.SIGradient':edit(i,[prop(131081,en('none'))])
 elif d.get('m_FullTypeName')=='SI.Bindable.SIText':edit(i,[prop(65537,px(12)),prop(65536,color(244,244,247))])
changed=[i for i in oldrefs if rr[i]!=oldrefs[i]]
for i in changed:
 a=copy.deepcopy(rr[i]);a['data']['m_RuleIndex']=oldrefs[i]['data']['m_RuleIndex'];assert a==oldrefs[i],('Non-style change',i)
assert set(rr)==set(oldrefs)
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
out=R/('header-touch-bar-style-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'style':'Touch Bar inspired black housing, dark rounded keys, subtle light borders and dividers','header_height':32,'key_height':26,'style_only':True,'bindings_hierarchy_data_and_textures_unchanged':True,'changed_nodes':changed,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
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
