from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def pct(x):return val(3,{'unit':2,'value':float(x)})
def style(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def move(i,parent,index=None):
 old=rr[i]['data']['m_Parent']['rid']
 rr[old]['data']['m_Children'].remove({'rid':i})
 rr[i]['data']['m_Parent']={'rid':parent}
 if index is None:rr[parent]['data']['m_Children'].append({'rid':i})
 else:rr[parent]['data']['m_Children'].insert(index,{'rid':i})
removed=set()
def remove(i):
 a=rr[i]['data']
 for c in list(a.get('m_Children',[])):remove(c['rid'])
 sd=a.get('m_SerializedData',{}).get('rid')
 if sd in rr:removed.add(sd)
 removed.add(i)
 parent=a.get('m_Parent',{}).get('rid')
 if parent in rr and {'rid':i} in rr[parent]['data'].get('m_Children',[]):rr[parent]['data']['m_Children'].remove({'rid':i})
# Put the existing badge grid above the complete native scout/ability template.
move(1351,1349,0)
move(1026,1173,0)
style(1173,[(131083,en('row')),(131073,en('center')),(131088,en('space-between')),(131097,px(0))])
style(1349,[(131105,px(190)),(131097,px(190)),(131087,px(238)),(131083,en('column')),(131073,en('center')),(131088,en('flex-start'))])
style(1351,[(131082,auto()),(131085,num(0)),(131092,px(0)),(131090,px(6)),(131074,en('center'))])
style(1186,[(131105,pct(100)),(131085,num(0)),(131093,px(0))])
# Reuse the actual native chart, including its player/goalkeeper binding and label templates.
rr[1026]['data']['m_Classes']=[]
style(1026,[(131105,px(240)),(131097,px(240)),(131095,px(240)),(131087,px(230)),(131096,px(230)),(131094,px(230)),(131084,num(0)),(131085,num(0)),(131083,en('column')),(131073,en('center')),(131088,en('center')),(262150,px(0)),(262151,px(0))])
style(1043,[(131105,px(240)),(131097,px(240)),(131095,px(240)),(131087,px(230)),(131096,px(230)),(131094,px(230)),(131084,num(0)),(131085,num(0)),(131074,en('center'))])
assert rr[1062]==old_refs[1062]
# The attribute columns now always show the table. Remove the old toggle and both old chart slots.
remove(1046)
remove(1013)
remove(1012)
rr[1009]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
rr[1027]['type']=copy.deepcopy(rr[1042]['type'])
rr[1027]['data']=copy.deepcopy(rr[1042]['data'])
rr[1027]['data']['uxmlAssetId']=rr[1009]['data']['m_Id']
assert rr[1009]['data']['m_Children']==[{'rid':1025}]
settings=rr[1014]['data']['Settings']['m_settings']
assert len(settings)==7
rr[1014]['data']['Settings']['m_settings']=settings[:5]
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed:del rr[i]
# All data/ratings/functions, native scout group and left identity details stay byte-for-byte equal.
allowed_sd={1014,1027}
for i,r in old_refs.items():
 if i not in removed and 'UxmlSerializedData' in r['type']['class'] and i not in allowed_sd:assert rr[i]==r,('binding changed',i)
for i in [1291,1297,1171,1295,1182,1180,1193,1184,1199,1202,1203,1217]:assert rr[i]==old_refs[i],i
assert rr[1349]['data']['m_Children']==[{'rid':1351},{'rid':1186}]
assert rr[1173]['data']['m_Children'][0]=={'rid':1026}
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4')
saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('banner-right-badges-native-radar-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid],'radar_size':[240,230],'radar_native_binding_unchanged':True,'native_scout_template_unchanged':True,'second_version_unchanged':True,'removed_records':sorted(removed),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-2}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  (folder/WN).write_bytes(output)
  assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output),'unchanged_assets':len(old_hashes)-2},ensure_ascii=False))
