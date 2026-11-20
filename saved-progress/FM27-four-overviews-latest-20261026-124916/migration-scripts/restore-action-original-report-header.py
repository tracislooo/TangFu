from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<card bundle loader>','exec'))
changes={}
# Remove the active Action subtree from the inline attribute overview.
removed=set()
def collect(i):
 removed.add(i);d=rr[i]['data'];removed.add(d['m_SerializedData']['rid'])
 for c in d.get('m_Children',[]):collect(c['rid'])
collect(1103)
assert rr[1103]['data']['m_Parent']=={'rid':1102}
rr[1102]['data']['m_Children'].remove({'rid':1103})
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
rr={r['rid']:r for r in doc['references']['RefIds']}
validate_ui(doc,sheet)
changes[FULL]=doc
# Build the original report header as a 32px native action strip.
HP=5775949770471550939
doc=objects[HP].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']}
hsid=doc['inlineSheet']['m_PathID'];sheet=objects[hsid].read_typetree()
original_header=copy.deepcopy(doc)
src_path=R/'Action点击区域修正-20261016-003713'/WN
src=UnityPy.load(str(src_path));srcobs={o.path_id:o for o in src.objects}
st=next(o for o in src.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerAttributesLargeBlock').read_typetree()
sr={r['rid']:r for r in st['references']['RefIds']};ss=srcobs[st['inlineSheet']['m_PathID']].read_typetree()
source_nodes=[]
def walk(i):
 source_nodes.append(i)
 for c in sr[i]['data'].get('m_Children',[]):walk(c['rid'])
walk(1102)
source_ids=source_nodes+[sr[i]['data']['m_SerializedData']['rid'] for i in source_nodes]
start=max(rr)+1;mapping={i:start+k for k,i in enumerate(source_ids)}
maxeid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())
eids={i:maxeid+1+k for k,i in enumerate(source_nodes)}
def remap(v):
 if isinstance(v,dict):
  if set(v)=={'rid'} and v['rid'] in mapping:v['rid']=mapping[v['rid']]
  else:
   for a in v.values():remap(a)
 elif isinstance(v,list):
  for a in v:remap(a)
for i in source_ids:
 r=copy.deepcopy(sr[i]);r['rid']=mapping[i];remap(r['data'])
 if i in source_nodes:
  r['data']['m_Id']=eids[i]
  if i==1102:r['data']['m_Parent']={'rid':1002}
  ix=r['data']['m_RuleIndex']
  if ix>=0:
   newrule=copy.deepcopy(ss['m_Rules'][ix])
   for p in newrule['m_Properties']:
    for h in p['m_Values']:
     if h['m_ValueType']==1:continue
     pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]))
     h['valueIndex']=len(sheet[pool])-1
   r['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(newrule)
 else:
  ni=next(n for n in source_nodes if sr[n]['data']['m_SerializedData']['rid']==i)
  r['data']['uxmlAssetId']=eids[ni]
 rr[r['rid']]=r;doc['references']['RefIds'].append(r)
rr[1002]['data']['m_Children'].append({'rid':mapping[1102]})
def edit(i,ps):override(rr[i]['data'],ps)
def fixh(i,h):
 edit(i,[prop(131087,px(h)),prop(131096,px(h)),prop(131094,px(h)),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0)),prop(262151,px(0)),prop(131090,px(0)),prop(131093,px(0)),prop(131101,px(0)),prop(131098,px(0))])
# The old gradient, portrait, banner and all nested content remain hidden at zero height.
for i,r in list(rr.items()):
 if i in mapping.values() or i in [1000,1001,1002]:continue
 if 'm_Parent' in r.get('data',{}):
  fixh(i,0);edit(i,[prop(131081,en('none')),prop(458768,en('hidden'))])
for i in [1001,1002,mapping[1102]]:
 fixh(i,32);edit(i,[prop(131081,en('flex')),prop(458768,en('visible')),prop(131102,en('relative'))])
rr[mapping[1102]]['data']['m_Classes']=['row-direction-normal','align-self-stretch','flex-no-shrink-class']
edit(mapping[1102],[prop(131088,en('flex-end')),prop(131073,en('center')),prop(131105,val(3,{'unit':2,'value':100.0})),prop(131100,px(24))])
fixh(mapping[1103],32)
edit(mapping[1103],[prop(131102,en('relative')),prop(131089,auto()),prop(131104,auto()),prop(131103,auto()),prop(131105,px(160)),prop(131097,px(160)),prop(131095,px(160)),prop(131081,en('flex')),prop(458768,en('visible'))])
assert rr[mapping[1109]]['data']['BindingPaths']==[{'m_path':'Person'}]
assert rr[1003]=={r['rid']:r for r in original_header['references']['RefIds']}[1003]
validate_ui(doc,sheet)
changes[HP]=doc;changes[hsid]=sheet
for i,d in changes.items():objects[i].save_typetree(d)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in changes:assert saved[i].read_typetree()==changes[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
for pid in [FULL,HP]:
 d=saved[pid].read_typetree();validate_ui(d,saved[d['inlineSheet']['m_PathID']].read_typetree())
for p,data in before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('restore-action-to-original-report-header-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'header_height':32,'action_height':32,'original_header_other_content':'display:none and height/min/max=0','action_removed_from_full_attribute_overview':True,'native_action_source':str(src_path),'header_new_rids':mapping,'changed_assets':list(changes),'unchanged_assets_verified':len(old_hashes)-len(changes),'before_sha256':{str(p):sha(d) for p,d in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if '--install' in sys.argv:
 try:
  for folder in [GAME,SKIN]:
   (folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except Exception:
  for p,data in before.items():p.write_bytes(data)
  raise
 report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':report['installed'],'header_height':32,'sha256':sha(output),'changed_assets':list(changes)},ensure_ascii=False,indent=2))
