from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
assert rr[1349]['data']['m_Children']==[{'rid':1351},{'rid':1186}]
# Hide the badge block reversibly so the right-hand space stays empty for the next design.
st(1351,[(131081,en('none')),(131087,px(0)),(131096,px(0)),(131094,px(0)),(131090,px(0))])
st(1349,[(131105,px(240)),(131097,px(240)),(131087,auto()),(131096,px(0)),(131094,auto()),(131084,num(0)),(131085,num(0)),(131073,en('stretch')),(131090,px(4))])
st(1026,[(131105,px(240)),(131097,px(240)),(131095,px(240)),(131087,px(176)),(131096,px(176)),(131094,px(176))])
st(1043,[(131105,px(220)),(131097,px(220)),(131095,px(220)),(131087,px(176)),(131096,px(176)),(131094,px(176)),(458768,en('visible'))])
children=rr[1173]['data']['m_Children']
assert children[:2]==[{'rid':1026},{'rid':1349}]
rr[1173]['data']['m_Children']=[{'rid':1349},{'rid':1026}]+children[2:]
st(1173,[(131083,en('column')),(131073,en('flex-start')),(131088,en('center'))])
changed={i for i in rr if rr[i]!=old_refs[i]}
assert changed=={1173,1349,1351,1026,1043},changed
assert set(rr)==set(old_refs)
for i,r in old_refs.items():
 if i not in changed:assert rr[i]==r
for i in [1062,1186,1202,1203,1217,1031,1184,1007]:assert rr[i]==old_refs[i],i
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('scout-above-smaller-radar-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid],'scout_ability_above_radar':True,'radar_size':[220,176],'right_side_blank_badges_hidden':True,'all_serialized_bindings_unchanged':True,'changed_nodes':sorted(changed),'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-2}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:
  (folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output)},ensure_ascii=False))
