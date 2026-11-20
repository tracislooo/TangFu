from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
src_path=R/'Action点击区域修正-20261016-003713'/WN
src=UnityPy.load(str(src_path));srcobs={o.path_id:o for o in src.objects}
original=next(o for o in src.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerAttributesLargeBlock').read_typetree()
srr={r['rid']:r for r in original['references']['RefIds']}
ss=srcobs[original['inlineSheet']['m_PathID']].read_typetree()
menu_id=next(i for i,r in srr.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.PluginContextMenuBindings')
assert menu_id==1103
nodes=[]
def walk(i):
 nodes.append(i)
 for c in srr[i]['data']['m_Children']:walk(c['rid'])
walk(menu_id)
ids=nodes+[srr[i]['data']['m_SerializedData']['rid'] for i in nodes]
assert nodes==[1103,1104,1105,1106,1107]
# Restore the known working native button, without added click/alias wrappers.
for i in ids:
 rec=copy.deepcopy(srr[i])
 if i in nodes:
  ridx=rec['data']['m_RuleIndex']
  if ridx>=0:
   rulecopy=copy.deepcopy(ss['m_Rules'][ridx])
   for pr in rulecopy['m_Properties']:
    for h in pr['m_Values']:
     if h['m_ValueType']==1:continue
     pool=poolmap[h['m_ValueType']]
     sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]))
     h['valueIndex']=len(sheet[pool])-1
   rec['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(rulecopy)
 rr[i]=rec
rr[1103]['data']['m_Parent']={'rid':1102}
assert rr[1102]['data']['m_Children']==[{'rid':1114},{'rid':1907}]
rr[1102]['data']['m_Children']=[{'rid':1114},{'rid':1103}]
removed={1907,1908,1909,1910}
for i in removed:del rr[i]
# Only position and fixed button size differ from the working source.
override(rr[1103]['data'],[prop(131102,en('absolute')),prop(131089,auto()),prop(131103,px(24)),prop(131104,px(48)),prop(131105,px(160)),prop(131097,px(160)),prop(131095,px(160)),prop(131087,px(32)),prop(131096,px(32)),prop(131094,px(32)),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0)),prop(131091,px(0)),prop(131092,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(458768,en('visible'))])
doc['references']['RefIds']=[rr[r['rid']] for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in nodes:
 assert rr[i]['data']['m_FullTypeName']==srr[i]['data']['m_FullTypeName']
 assert rr[rr[i]['data']['m_SerializedData']['rid']]==srr[srr[i]['data']['m_SerializedData']['rid']]
assert all(rr[i]==old_refs[i] for i in old_refs if i not in set(ids)|removed|{1102})
# All navigation, card graphics, formulas and contract nodes remain byte-identical records.
node_count=validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,data in before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('restore-working-native-action-subtree-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'source':str(src_path),'source_sha256':sha(src_path.read_bytes()),'change':'Restore working native menu subtree and serialized bindings; remove added BindingRemapper and SIButton layers; retain current right-side coordinates','removed_records':sorted(removed),'restored_records':ids,'native_serialized_data_matches_source':True,'navigation_and_other_nodes_preserved':True,'validated_nodes':node_count,'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
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
print(json.dumps({'output':str(out),'installed':report['installed'],'after_sha256':sha(output),'unchanged_assets_verified':report['unchanged_assets_verified']},ensure_ascii=False,indent=2))
