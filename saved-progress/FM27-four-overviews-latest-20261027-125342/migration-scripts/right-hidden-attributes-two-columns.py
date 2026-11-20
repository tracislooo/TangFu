from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<existing helpers>','exec'))
PAGES=[-930000000001001,-930000000001003]
keys=['adaptability','ambition','loyalty','pressure','professionalism','sportsmanship','temperament','versatility','dirtiness','consistency','important-matches','controversy','injury-proneness']
changed={};checks=[]
for pid in PAGES:
 doc=objects[pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr)
 next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;new=[]
 zero=[prop(262150,px(0)),prop(262151,px(0)),prop(131084,num(0)),prop(131085,num(0))]
 parent=named('RightHiddenAttributesList')['rid'];panel=named('RightHiddenAttributesPanel')['rid']
 rowids=[named('RightHiddenRow_'+k)['rid'] for k in keys]
 assert rr[parent]['data']['m_Children']==[{'rid':i} for i in rowids]
 st(parent,[(131083,en('row')),(131073,en('flex-start')),(131088,en('flex-start')),(131087,auto()),(131096,px(0))])
 columns=[]
 for index,ids in enumerate([rowids[:7],rowids[7:]]):
  col=make(parent,'RightHiddenAttributesColumn'+str(index+1),zero+[prop(131102,en('relative')),prop(131083,en('column')),prop(131073,en('stretch')),prop(131088,en('flex-start')),prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),prop(131097,px(0)),prop(131087,auto()),prop(131096,px(0)),prop(131092,px(8 if index==0 else 0))])
  rr[col]['data']['m_Children']=[{'rid':i} for i in ids]
  for i in ids:rr[i]['data']['m_Parent']={'rid':col}
  columns.append(col)
 rr[parent]['data']['m_Children']=[{'rid':i} for i in columns]
 st(panel,[(131096,px(220)),(131087,auto())])
 doc['references']['RefIds'].extend(new)
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('binding changed',i)
  if i in rowids:
   restored=copy.deepcopy(rr[i]);restored['data']['m_Parent']=r['data']['m_Parent'];assert restored==r
 for ix,col in enumerate(columns):
  expected=rowids[:7] if ix==0 else rowids[7:]
  assert rr[col]['data']['m_Children']==[{'rid':i} for i in expected]
  for i in expected:assert rr[i]['data']['m_Parent']=={'rid':col} and dimension(rr[i],131087)==24
 validate_ui(doc,sheet)
 objects[pid].save_typetree(doc);objects[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet
 checks.append({'page':pid,'columns':columns,'column_rows':[keys[:7],keys[7:]],'row_counts':[7,6]})
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for pid,h in old_hashes.items():
 if pid in changed:assert saved[pid].read_typetree()==changed[pid]
 else:assert sha(saved[pid].get_raw_data())==h,pid
for pid in PAGES:
 d=saved[pid].read_typetree();validate_ui(d,saved[d['inlineSheet']['m_PathID']].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S');out=R/('right-hidden-two-columns-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'pages':checks,'row_height':24,'column_gap':8,'read_order':'down left column then down right column','native_row_styles_and_all_bindings_preserved':True,'top_content_and_summary_and_bans_preserved':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'pages':2,'columns':[7,6],'bindings_preserved':True},ensure_ascii=True))
