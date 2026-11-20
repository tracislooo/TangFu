from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
HP=5775949770471550939
doc=objects[HP].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};oldrefs=copy.deepcopy(rr)
sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree()
m={int(k):v for k,v in json.loads((R/'header-six-native-fitness-metrics-20261018-013417/manifest.json').read_text())['new_node_mapping'].items()}
wrap=named('HeaderFitnessSixMetrics')['rid']
order=[1028,1032,1029,1030,1033,1034]
assert set(c['rid'] for c in rr[wrap]['data']['m_Children'])=={m[i] for i in order}
def edit(i,ps):override(rr[m[i]]['data'],ps)
# Content-sized values and rows prevent the flexible text box pushing each bar away.
for i in [1178,1109,1115,1123,1191,1133]:
 edit(i,[prop(131084,num(0)),prop(131082,auto()),prop(131105,auto()),prop(131085,num(1)),prop(131074,en('center'))])
for i in [1053,1056,1060,1065,1128,1072,1068]:
 edit(i,[prop(131084,num(0)),prop(131082,auto()),prop(131105,auto()),prop(131088,en('flex-start')),prop(131073,en('center')),prop(131074,en('center'))])
for i in order:edit(i,[prop(131073,en('center')),prop(131088,en('flex-start')),prop(131100,px(0))])
for i in [1174,1107,1113,1119,1126,1131]:edit(i,[prop(131074,en('center'))])
for i,width in [(1110,49),(1116,88),(1192,75),(1134,36)]:
 edit(i,[prop(131074,en('center')),prop(131073,en('center')),prop(131105,px(width)),prop(131097,px(width)),prop(131095,px(width)),prop(131087,px(4)),prop(131096,px(4)),prop(131094,px(4)),prop(131091,px(4)),prop(131104,auto())])
for i in [1176,1121]:edit(i,[prop(131074,en('center'))])
# Five 1px separators between the six modules.
newids=[];children=[];nextid=max(rr)+1;eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
for index,i in enumerate(order):
 children.append({'rid':m[i]})
 if index==len(order)-1:continue
 node=copy.deepcopy(rr[m[1028]]);sd=copy.deepcopy(rr[node['data']['m_SerializedData']['rid']])
 node['rid']=nextid;sd['rid']=nextid+1
 node['data'].update(m_Id=eid,m_Parent={'rid':wrap},m_Children=[],m_SerializedData={'rid':nextid+1},m_Classes=[],m_RuleIndex=-1)
 sd['data'].update(uxmlAssetId=eid,name='HeaderFitnessSeparator'+str(index+1),name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
 rr[nextid]=node;rr[nextid+1]=sd;doc['references']['RefIds'].extend([node,sd])
 override(node['data'],[prop(131105,px(1)),prop(131097,px(1)),prop(131095,px(1)),prop(131087,px(16)),prop(131096,px(16)),prop(131094,px(16)),prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('center')),prop(131091,px(8)),prop(131092,px(8)),prop(458752,color(220,226,235,80))])
 children.append({'rid':nextid});newids.extend([nextid,nextid+1]);nextid+=2;eid+=1
rr[wrap]['data']['m_Children']=children
for i,r in oldrefs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('Binding changed',i)
assert [c['rid'] for c in children if c['rid'] not in newids]==[m[i] for i in order]
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
out=R/('align-header-fitness-separators-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'order':['Match Sharpness','Energy','Match Load','Injury Susceptibility','Training Load','Injury Risk'],'value_to_bar_gap_px':4,'separators':5,'vertical_alignment':'center','native_bindings_unchanged':True,'changed_assets':[HP,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
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
