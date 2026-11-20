from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<bundle loader>','exec'))
HP=5775949770471550939
isodir=R/'isolate-touch-bar-icons-20261019-002114';iso=json.loads((isodir/'manifest.json').read_text(encoding='utf8'))
assert sha(before[GAME/WN])==iso['variants']['OverallCondition']['sha256']
doc=objects[HP].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};oldrefs=copy.deepcopy(rr)
assert 1145 in rr and 1141 not in rr and 1143 not in rr
# Bring only Mindset's native icon back from its already checked isolation variant.
se=UnityPy.load(str(isodir/'only-Mindset'/WN));sd=next(o for o in se.objects if o.path_id==HP).read_typetree();sr={r['rid']:r for r in sd['references']['RefIds']}
icon=copy.deepcopy(sr[1141]);dataid=icon['data']['m_SerializedData']['rid'];serialized=copy.deepcopy(sr[dataid])
assert dataid==1142
assert icon['data']['m_FullTypeName']=='SI.Bindable.SIImage'
assert serialized['data']['name']=='HeaderMindsetIcon'
parent=icon['data']['m_Parent']['rid'];value=next(i for i,r in rr.items() if r.get('data',{}).get('name')=='HeaderMindsetValue')
value_node=next(i for i,r in rr.items() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==value)
children=rr[parent]['data']['m_Children'];children.insert(children.index({'rid':value_node}),{'rid':1141})
doc['references']['RefIds'].extend([icon,serialized]);rr[1141]=icon;rr[1142]=serialized
sheetid=doc['inlineSheet']['m_PathID'];sheet=objects[sheetid].read_typetree()
assert next(o for o in se.objects if o.path_id==sheetid).read_typetree()==sheet
assert {i for i in oldrefs if rr[i]!=oldrefs[i]}=={parent}
assert set(rr)-set(oldrefs)=={1141,1142}
assert 1143 not in rr and 1144 not in rr and 1145 in rr
validate_ui(doc,sheet)
objects[HP].save_typetree(doc);output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i==HP:assert saved[i].read_typetree()==doc
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[HP].read_typetree(),saved[sheetid].read_typetree())
for p,d in before.items():assert p.read_bytes()==d
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('touch-bar-condition-plus-mindset-icons-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'enabled_icons':['Overall Condition','Mindset'],'hierarchy_icon_omitted':True,'new_records':[1141,1142],'changed_assets':[HP],'other_assets_unchanged':len(old_hashes)-1,'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output)}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,d in before.items():p.write_bytes(d)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'enabled_icons':report['enabled_icons'],'hierarchy_icon_omitted':True,'sha256':sha(output),'installed':True},ensure_ascii=False,indent=2))
