from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<current native helpers>','exec'))
PAGES=[-930000000001001,-930000000001003]
keys=['adaptability','ambition','loyalty','pressure','professionalism','sportsmanship','temperament','versatility','dirtiness','consistency','important-matches','controversy','injury-proneness']
groups=[keys[:5],keys[5:9],keys[9:]]
changed={};checks=[]
for pid in PAGES:
 doc=objects[pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr)
 next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;new=[]
 zero=[prop(262150,px(0)),prop(262151,px(0)),prop(131084,num(0)),prop(131085,num(0))]
 bodyid=rr[1002]['data']['m_SerializedData']['rid'];settings=rr[bodyid]['data']['Settings']['m_settings']
 before_sizes=[settings[i]['PredefinedSize'] for i in [0,2,4]]
 assert before_sizes==[380.,860.,295.],before_sizes
 for i,size in [(0,380.),(2,720.),(4,380.)]:
  settings[i]['PredefinedSize']=size;settings[i]['Priority']=0;settings[i]['UsePredefinedOnly']=0
 assert settings[0]==settings[4]
 # Remove the old right-side 312px cap so the native sizing control can give both sides equal room.
 for i in [1011,1703]:st(i,[(131095,{'m_ValueType':1,'valueIndex':3}),(131097,px(0)),(131105,auto())])
 parent=named('RightHiddenAttributesList')['rid'];panel=named('RightHiddenAttributesPanel')['rid']
 columns=[named('RightHiddenAttributesColumn'+str(i))['rid'] for i in [1,2]]
 assert rr[parent]['data']['m_Children']==[{'rid':i} for i in columns]
 third=make(parent,'RightHiddenAttributesColumn3',zero+[prop(131102,en('relative')),prop(131083,en('column')),prop(131073,en('stretch')),prop(131088,en('flex-start')),prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),prop(131097,px(0)),prop(131087,auto()),prop(131096,px(0))])
 columns.append(third)
 for index,(col,group) in enumerate(zip(columns,groups)):
  st(col,[(131092,px(8 if index<2 else 0)),(131084,num(1)),(131085,num(1)),(131082,px(0)),(131097,px(0))])
  rr[col]['data']['m_Children']=[{'rid':named('RightHiddenRow_'+key)['rid']} for key in group]
  for key in group:
   row=named('RightHiddenRow_'+key);row['data']['m_Parent']={'rid':col}
   # Give the labels enough room in the narrower cells while retaining the native 24px rows and badges.
   st(row['rid'],[(131091,px(0)),(131092,px(0)),(131097,px(0))])
 rr[parent]['data']['m_Children']=[{'rid':i} for i in columns]
 st(panel,[(131096,px(172)),(131087,auto())])
 doc['references']['RefIds'].extend(new)
 for i,r in old.items():
  if 'UxmlSerializedData' not in r.get('type',{}).get('class',''):continue
  if i==bodyid:
   restored=copy.deepcopy(rr[i]);restored['data']['Settings']=r['data']['Settings'];assert restored==r
  else:assert rr[i]==r,('data binding changed',pid,i)
 assert settings[2]['PredefinedSize']==720
 assert settings[0]['PredefinedSize']==settings[4]['PredefinedSize']==380
 for ix,col in enumerate(columns):
  assert rr[col]['data']['m_Children']==[{'rid':named('RightHiddenRow_'+k)['rid']} for k in groups[ix]]
  for key in groups[ix]:assert dimension(named('RightHiddenRow_'+key),131087)==24
 validate_ui(doc,sheet)
 objects[pid].save_typetree(doc);objects[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet
 checks.append({'page':pid,'before_predefined_widths':before_sizes,'after_predefined_widths':[380,720,380],'equal_side_settings':settings[0]==settings[4],'columns':groups,'column_counts':[5,4,4],'right_width_cap_removed':True})
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for pid,h in old_hashes.items():
 if pid in changed:assert saved[pid].read_typetree()==changed[pid]
 else:assert sha(saved[pid].get_raw_data())==h,pid
for pid in PAGES:
 d=saved[pid].read_typetree();validate_ui(d,saved[d['inlineSheet']['m_PathID']].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S');out=R/('center720-equal-sides-hidden-three-columns-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'pages':checks,'adaptive_sizing_preserved':True,'all_data_bindings_preserved':True,'native_row_height':24,'hidden_column_gap':8,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'predefined_widths':[380,720,380],'hidden_columns':[5,4,4],'pages':2,'bindings_preserved':True},ensure_ascii=True))
