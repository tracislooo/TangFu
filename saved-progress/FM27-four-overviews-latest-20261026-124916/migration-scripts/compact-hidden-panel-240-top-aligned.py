from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def nst(name,ps):st(named(name)['rid'],ps)
panel=named('OverviewHiddenAttributesPanel')['rid']
assert rr[panel]['data']['m_Parent']=={'rid':1026}
rr[1026]['data']['m_Children'].remove({'rid':panel})
rr[1349]['data']['m_Children'].append({'rid':panel});rr[panel]['data']['m_Parent']={'rid':1349}
# Anchoring to the native scout group's wrapper gives an exact shared top without changing its layout.
st(1349,[(131102,en('relative')),(458768,en('visible'))])
st(panel,[(131102,en('absolute')),(131089,px(252)),(131104,px(0)),(131105,px(240)),(131097,px(240)),(131095,px(240)),(131087,px(168)),(131096,px(168)),(131091,px(0))])
st(1026,[(131105,px(240)),(131095,px(240))])
for name in ['OverviewHiddenSummaryLine','OverviewHiddenBarLine']:nst(name,[(131105,px(240))])
for prefix,x in [('CA',0),('PA',74)]:
 nst('Overview'+prefix+'WhiteDot',[(131089,px(x)),(131105,px(6)),(131087,px(6)),(131104,px(9)),(262147,px(3))])
 nst('Overview'+prefix+'NativeTitle',[(131089,px(x+9)),(131105,px(40)),(65537,px(9))])
 nst('Overview'+prefix+'NativeNumberAvailable',[(131089,px(x+49)),(131105,px(22))])
 for suffix in ['Missing','Value']:nst('Overview'+prefix+'NativeNumber'+suffix,[(131105,px(22))])
nst('OverviewCurrentReputationTitle',[(131089,px(148)),(131105,px(56)),(65537,px(9))])
nst('OverviewCurrentReputationAvailable',[(131089,px(204)),(131105,px(36))])
for suffix in ['Missing','Value']:nst('OverviewCurrentReputation'+suffix,[(131105,px(36)),(65537,px(11))])
nst('OverviewCAPALayeredBar',[(131089,px(44))])
rows=[['adaptability','ambition','controversy','loyalty','pressure','professionalism','sportsmanship'],['temperament','versatility','consistency','dirtiness','important-matches','injury-proneness']]
cw=f32(240/7)
for rowindex,keys in enumerate(rows):
 nst('OverviewHiddenAttributeRow'+str(rowindex+1),[(131089,px(f32(cw/2) if rowindex else 0)),(131104,px(48+60*rowindex)),(131105,px(f32(cw*len(keys)))),(131087,px(60))])
 for index,key in enumerate(keys):
  nst('OverviewHiddenCell_'+key,[(131089,px(f32(index*cw))),(131105,px(cw)),(131087,px(60))])
  nst('OverviewHiddenNumber_'+key+'Available',[(131105,px(cw))])
  for suffix in ['Missing','Value']:nst('OverviewHiddenNumber_'+key+suffix,[(131105,px(cw))])
  # Two-line native titles keep longer translations readable inside the narrower cells.
  nst('OverviewHiddenTitle_'+key,[(131105,px(cw)),(131087,px(22)),(65537,px(9)),(65552,en('normal'))])
  nst('OverviewHiddenImagePositive_'+key,[(131089,px(f32((cw-5)/2)))])
  if index<len(keys)-1:nst('OverviewHiddenDivider_'+key,[(131089,px(f32(cw-1))),(131087,px(52))])
# All native values, translations and image switches retain their exact serialized data.
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('binding changed',i)
assert set(rr)==set(old_refs)
assert dimension(rr[panel],131105)==240 and dimension(rr[panel],131104)==0
assert rr[panel]['data']['m_Parent']==rr[1186]['data']['m_Parent']=={'rid':1349}
assert dimension(named('OverviewCAPALayeredBar'),131105)==196
assert dimension(named('OverviewCAPALayeredBar'),131089)+196==240
for i in [1186,1202,1203,1217,1043]:assert rr[i]==old_refs[i],i
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
out=R/('hidden-panel-width240-top-aligned-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid],'panel_size':[240,168],'panel_anchor':'native scout group wrapper top','panel_left':252,'column_width':cw,'native_titles_wrap_two_lines':True,'bindings_thresholds_images_unchanged':True,'scout_card_radar_and_second_version_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-2}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output)},ensure_ascii=False))
