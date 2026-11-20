from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<native helpers>','exec'))

changed=[]
for key in ['controversy','injury-proneness']:
 gate=named('OverviewHiddenImagePositive_'+key)
 reference=named('OverviewHiddenImagePositive_consistency')
 for pid in [131104,131105,131087]:assert dimension(gate,pid)==dimension(reference,pid)
 for tier in range(1,11):
  node=named(f'OverviewHiddenImage_{key}_{tier:02}')
  # A negative scale on both axes rotates around the default central pivot by 180 degrees.
  # Transform the image leaf only, retaining the exact original layout rectangle.
  sheet['assets'].append({'m_FileID':fileid,'m_PathID':textures[f'HIDEstats{tier:02}']})
  override(node['data'],[prop(458753,{'m_ValueType':6,'valueIndex':len(sheet['assets'])-1}),prop(327681,num(-1),num(-1))])
  changed.append(node['rid'])
  assert property_value(node,458753)=={'m_FileID':fileid,'m_PathID':textures[f'HIDEstats{tier:02}']}
  node_rule=sheet['m_Rules'][node['data']['m_RuleIndex']]
  scale=next(p for p in node_rule['m_Properties'] if p['m_Id']==327681)
  assert [sheet['floats'][h['valueIndex']] for h in scale['m_Values']]==[-1.,-1.]
  other=named(f'OverviewHiddenImage_consistency_{tier:02}')
  for pid in [131089,131104,131105,131087]:assert dimension(node,pid)==dimension(other,pid)
assert set(rr)==set(old_refs)
assert {i for i in rr if rr[i]!=old_refs[i]}==set(changed)
assert len(changed)==20
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for pid,h in old_hashes.items():
 if pid in [FULL,sid]:assert saved[pid].read_typetree()=={FULL:doc,sid:sheet}[pid]
 else:assert sha(saved[pid].get_raw_data())==h,pid
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('two-hidden-bars-rotate180-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'attributes':['controversy','injury-proneness'],'texture_mapping':'tier N -> HIDEstatsNN, restored original tiers','image_rotation_degrees':180,'image_transform_scale':[-1,-1],'image_box':[5,20],'image_gate_y':dimension(named('OverviewHiddenImagePositive_controversy'),131104),'alignment_verified_against':'consistency','changed_image_nodes':changed,'all_other_nodes_and_bindings_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'rotation':180,'restored_tiers':True,'aligned':True,'changed_nodes':len(changed)},ensure_ascii=True))
