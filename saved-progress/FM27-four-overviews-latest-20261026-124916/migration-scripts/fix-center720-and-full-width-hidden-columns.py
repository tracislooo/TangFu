from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'add-hidden-attributes-panel.py').read_text(encoding='utf8').split('bar=named(')[0],'<current helpers>','exec'))
PAGES=[-930000000001001,-930000000001003]
def pct(value):return val(3,{'unit':2,'value':struct.unpack('<f',struct.pack('<f',value))[0]})
none={'m_ValueType':1,'valueIndex':3}
changes={};checks=[]
for pid in PAGES:
 doc=objects[pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr)
 settingsid=rr[1002]['data']['m_SerializedData']['rid'];settings=rr[settingsid]['data']['Settings']['m_settings']
 settings[2].update(PredefinedSize=720.0,UsePredefinedOnly=1)
 # Min/max width prevent the native expander or flex-grow from stretching the center beyond 720.
 st(1009,[(131105,px(720)),(131097,px(720)),(131095,px(720)),(131082,px(720)),(131084,num(0)),(131085,num(0))])
 # Identical zero bases divide all remaining space equally between the two sides.
 for i in [1007,1703]:
  st(i,[(131105,auto()),(131097,px(0)),(131095,none),(131082,px(0)),(131084,num(1)),(131085,num(1))])
 for i in [1011,named('RightHiddenAttributesPanel')['rid'],named('RightHiddenAttributesList')['rid']]:
  st(i,[(131105,pct(100)),(131097,px(0)),(131095,none),(131074,en('stretch'))])
 parent=named('RightHiddenAttributesList')['rid']
 columns=[named('RightHiddenAttributesColumn'+str(i))['rid'] for i in [1,2,3]]
 for index,i in enumerate(columns):
  # Padding sits inside each third; margins would consume extra width beyond 100%.
  st(i,[(131105,pct(100/3)),(131082,pct(100/3)),(131097,px(0)),(131095,pct(100/3)),(131084,num(0)),(131085,num(0)),(262150,px(0)),(131091,px(0)),(131092,px(0)),(262151,px(0)),(131100,px(8 if index<2 else 0))])
  for child in rr[i]['data']['m_Children']:
   row=rr[child['rid']]
   st(row['rid'],[(131105,pct(100)),(131097,px(0)),(131074,en('stretch')),(131091,px(0)),(131092,px(0))])
 assert [dimension(rr[1009],p) for p in [131105,131097,131095,131082]]==[720.,720.,720.,720.]
 assert property_value(rr[1009],131084)==property_value(rr[1009],131085)==0
 for i in [1007,1703]:
  assert property_value(rr[i],131082)=={'unit':1,'value':0.0} and property_value(rr[i],131084)==1
 for i in [1011,named('RightHiddenAttributesPanel')['rid'],parent]:assert property_value(rr[i],131105)=={'unit':2,'value':100.0}
 for i in columns:
  width=property_value(rr[i],131105);basis=property_value(rr[i],131082)
  assert width==basis and width['unit']==2 and abs(width['value']-100/3)<1e-4
 for i,r in old.items():
  if 'UxmlSerializedData' not in r.get('type',{}).get('class',''):continue
  if i==settingsid:
   restored=copy.deepcopy(rr[i]);restored['data']['Settings']=r['data']['Settings'];assert restored==r
  else:assert rr[i]==r,('binding changed',i)
 validate_ui(doc,sheet);objects[pid].save_typetree(doc);objects[sid].save_typetree(sheet);changes[pid]=doc;changes[sid]=sheet
 checks.append({'page':pid,'center_width':720,'center_min_width':720,'center_max_width':720,'center_grow':0,'center_shrink':0,'center_use_predefined_only':True,'side_flex_weights':[1,1],'side_bases':[0,0],'hidden_parent_width':'100%','hidden_column_widths':['33.333333%']*3,'column_counts':[len(rr[i]['data']['m_Children']) for i in columns]})
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for pid,h in old_hashes.items():
 if pid in changes:assert saved[pid].read_typetree()==changes[pid]
 else:assert sha(saved[pid].get_raw_data())==h,pid
for pid in PAGES:
 d=saved[pid].read_typetree();validate_ui(d,saved[d['inlineSheet']['m_PathID']].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S');out=R/('fixed-center720-full-width-hidden-thirds-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'pages':checks,'all_data_bindings_preserved':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'center_actual_constraints':[720,720,720],'equal_flexible_sides':True,'hidden_columns_percent':[100/3]*3,'pages':2},ensure_ascii=True))
