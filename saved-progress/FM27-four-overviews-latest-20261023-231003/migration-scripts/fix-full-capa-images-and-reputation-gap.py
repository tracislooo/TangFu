from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def nst(name,ps):st(named(name)['rid'],ps)
bar=named('OverviewCAPALayeredBar')['rid']
# Remove the vertical squash and show the complete aspect-fitted 196x19 source textures.
override(rr[bar]['data'],[prop(327681,num(1),num(1)),prop(131087,px(19)),prop(131096,px(19)),prop(458768,en('visible'))])
bar_nodes=[]
def show_complete(i):
 bar_nodes.append(i);a=rr[i]['data'];st(i,[(458768,en('visible'))])
 if a.get('m_RuleIndex',-1)>=0:
  ids={p['m_Id'] for p in sheet['m_Rules'][a['m_RuleIndex']]['m_Properties']}
  if 458753 in ids:st(i,[(262153,en('scale-to-fit')),(131105,px(178)),(131087,px(19))])
 for c in a.get('m_Children',[]):show_complete(c['rid'])
show_complete(bar)
nst('OverviewHiddenBarLine',[(458768,en('visible'))])
# Native flex sizing puts the number immediately after the translated title, regardless of its length.
title=named('OverviewCurrentReputationTitle')['rid'];value=named('OverviewCurrentReputationAvailable')['rid']
parent=rr[title]['data']['m_Parent']['rid'];assert rr[value]['data']['m_Parent']=={'rid':parent}
template=copy.deepcopy(rr[1297]);sd=copy.deepcopy(rr[template['data']['m_SerializedData']['rid']])
rid=max(rr)+1;did=rid+1;uid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
template['rid']=rid;sd['rid']=did
template['data'].update(m_Id=uid,m_Parent={'rid':parent},m_Children=[{'rid':title},{'rid':value}],m_SerializedData={'rid':did},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
sd['data'].update(uxmlAssetId=uid,name='OverviewCurrentReputationCompactGroup',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
rr[rid]=template;rr[did]=sd;doc['references']['RefIds'].extend([template,sd])
rr[parent]['data']['m_Children']=[c for c in rr[parent]['data']['m_Children'] if c['rid'] not in [title,value]]+[{'rid':rid}]
for i in [title,value]:rr[i]['data']['m_Parent']={'rid':rid}
st(rid,[(131102,en('absolute')),(131089,px(124)),(131104,px(0)),(131105,px(86)),(131087,px(24)),(131083,en('row')),(131073,en('center')),(131088,en('flex-start')),(262150,px(0)),(262151,px(0))])
st(title,[(131102,en('relative')),(131089,auto()),(131104,auto()),(131105,auto()),(131084,num(0)),(131085,num(0)),(262150,px(0)),(262151,px(0)),(131092,px(2))])
st(value,[(131102,en('relative')),(131089,auto()),(131104,auto()),(131105,px(36)),(131084,num(0)),(131085,num(0)),(262150,px(0)),(262151,px(0))])
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('binding changed',i)
def protect(i):
 assert rr[i]==old_refs[i],i
 for c in rr[i]['data'].get('m_Children',[]):protect(c['rid'])
for name in ['OverviewHiddenAttributeRow1','OverviewHiddenAttributeRow2']:protect(named(name)['rid'])
assert dimension(rr[bar],131089)+dimension(rr[bar],131105)==210
assert dimension(rr[bar],131104)+dimension(rr[bar],131087)<=24
assert property_value(rr[title],65536)==property_value(named('OverviewCurrentReputationValue'),65536)
assert dimension(rr[title],65537)==dimension(named('OverviewCurrentReputationValue'),65537)==9
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
out=R/('fix-full-capa-and-compact-reputation-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid],'bar_box':[178,19],'bar_scale':[1,1],'full_images_scale_to_fit':True,'overflow_visible':True,'reputation_layout':'native flex row, content-sized translated title followed by number','reputation_gap_px':2,'existing_bindings_and_third_fourth_rows_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-2}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output)},ensure_ascii=False))
