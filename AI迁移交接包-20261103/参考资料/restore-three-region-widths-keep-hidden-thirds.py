from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<current bundle>','exec'))
baseline=R/'center720-equal-sides-hidden-three-columns-20261020-015636'/'backup-game'/WN
originals={o.path_id:o for o in UnityPy.load(str(baseline)).objects}
PAGES=[-930000000001001,-930000000001003]
width_ids={131105,131097,131095,131082,131084,131085}
changed={};checks=[]
def widths(refs,style,i):
 index=refs[i]['data'].get('m_RuleIndex',-1)
 if index<0:return {}
 return {p['m_Id']:[('keyword',h['valueIndex']) if h['m_ValueType']==1 else style[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in style['m_Rules'][index]['m_Properties'] if p['m_Id'] in width_ids}
for pid in PAGES:
 doc=objects[pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr)
 original=originals[pid].read_typetree();ors={r['rid']:r for r in original['references']['RefIds']};osheet=originals[original['inlineSheet']['m_PathID']].read_typetree()
 sdid=rr[1002]['data']['m_SerializedData']['rid'];rr[sdid]['data']['Settings']=copy.deepcopy(ors[ors[1002]['data']['m_SerializedData']['rid']]['data']['Settings'])
 for i in [1007,1009,1703,1011]:
  a=rr[i]['data'];ridx=a.get('m_RuleIndex',-1)
  nr=copy.deepcopy(sheet['m_Rules'][ridx]) if ridx>=0 else {'m_ComplexSelectors':[],'m_Properties':[],'line':-1}
  nr['m_Properties']=[p for p in nr['m_Properties'] if p['m_Id'] not in width_ids]
  oldidx=ors[i]['data'].get('m_RuleIndex',-1)
  if oldidx>=0:
   for p in osheet['m_Rules'][oldidx]['m_Properties']:
    if p['m_Id'] not in width_ids:continue
    np=copy.deepcopy(p)
    for h in np['m_Values']:
     if h['m_ValueType']==1:continue
     pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(osheet[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    nr['m_Properties'].append(np)
  a['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(nr)
  assert widths(rr,sheet,i)==widths(ors,osheet,i),i
 for i,r in old.items():
  if i==sdid:
   restored=copy.deepcopy(rr[i]);restored['data']['Settings']=r['data']['Settings'];assert restored==r
  elif i not in [1007,1009,1703,1011]:assert rr[i]==r,('unrelated node changed',i)
 columns=[]
 for index in [1,2,3]:
  node=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='RightHiddenAttributesColumn'+str(index))
  assert node==old[node['rid']]
  colwidth=next(p for p in sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131105)['m_Values'][0]
  assert abs(sheet['dimensions'][colwidth['valueIndex']]['value']-100/3)<1e-4
  columns.append(len(node['data']['m_Children']))
 assert columns==[5,4,4]
 validate_ui(doc,sheet);objects[pid].save_typetree(doc);objects[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet
 checks.append({'page':pid,'region_predefined_widths':[rr[sdid]['data']['Settings']['m_settings'][i]['PredefinedSize'] for i in [0,2,4]],'original_width_rules_restored':True,'hidden_columns':columns,'hidden_column_widths':'33.333333% each, unchanged'})
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
for pid,h in old_hashes.items():
 if pid in changed:assert saved[pid].read_typetree()==changed[pid]
 else:assert sha(saved[pid].get_raw_data())==h,pid
for pid in PAGES:
 d=saved[pid].read_typetree();validate_ui(d,saved[d['inlineSheet']['m_PathID']].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S');out=R/('restored-region-widths-hidden-three-columns-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'baseline':str(baseline),'pages':checks,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output)}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert sha((folder/WN).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'installed':True,'output':str(out),'original_predefined_widths':[380,860,295],'hidden_columns':[5,4,4],'hidden_equal_thirds_preserved':True,'pages':2},ensure_ascii=True))
