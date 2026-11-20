"""Validate staged/installed native map bindings and UID-switch layout."""
from pathlib import Path
import hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
state=json.loads((R/'current-club-location-map.json').read_text('utf8'));O=Path(state['patch'])
m=json.loads((O/'manifest.json').read_text('utf8'));tx=json.loads((O/'transaction.json').read_text('utf8'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
mapping=json.loads((O/'uid-coordinates.json').read_text('utf8'))
checks=[]
for tag in ['game','skin']:
 folder=O/tag;cat=cm.Catalog((folder/'catalog.bin').read_bytes())
 assert hashlib.md5(bytes(cat.data)).hexdigest()==(folder/'catalog.hash').read_text('ascii')
 row=next(r for r in tx if Path(r['source'])==folder/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
 stage=UnityPy.load(row['source']);before=UnityPy.load(row['backup']);obs={o.path_id:o for o in stage.objects};old={o.path_id:o for o in before.objects}
 pid=-991100000000030;d=obs[pid].read_typetree();r={a['rid']:a.get('data',{}) for a in d['references']['RefIds']};oldr={a['rid']:a.get('data',{}) for a in old[pid].read_typetree()['references']['RefIds']}
 data=lambda i:r[r[i]['m_SerializedData']['rid']]
 sheet=obs[d['inlineSheet']['m_PathID']].read_typetree()
 def style(i,prop):
  q=next(q for q in sheet['m_Rules'][r[i]['m_RuleIndex']]['m_Properties'] if q['m_Id']==prop)['m_Values'][0]
  pool={2:'floats',3:'dimensions',7:'strings'}[q['m_ValueType']];v=sheet[pool][q['valueIndex']]
  return v['value'] if isinstance(v,dict) else v
 for a in m['audits']:
  if a['target']!=tag:continue
  assert len(a['markers'])==20
  for marker in a['markers']:
   rr=next(c for c in mapping if c['uid']==marker['uid']);g=data(marker['gate'])
   raw=bytes(g['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);p=1;args=[]
   for _ in range(raw[0]):
    n=struct.unpack_from('<I',raw,p)[0];p+=4;args.append(raw[p:p+n]);p+=n
   assert p==len(raw) and raw[0]==3
   assert struct.unpack('<i',args[0][-4:])[0]==2
   assert struct.unpack('<i',args[1][-4:])[0]==marker['uid']
   assert args[2].endswith(b'club.UniqueId')
   assert abs(style(marker['anchor'],131089)-rr['x']/1920*100)<.00001
   assert abs(style(marker['anchor'],131104)-rr['y']/1080*100)<.00001
  cases={str(uid):[q['uid'] for q in a['markers'] if q['uid']==uid] for uid in [728,602,680,99999999]}
  assert cases=={'728':[728],'602':[602],'680':[680],'99999999':[]}
  for i,x in oldr.items():
   if x.get('m_FullTypeName')=='SI.Bindable.SIText':assert data(i)==oldr[x['m_SerializedData']['rid']]
  assert data(1250)['Binding']==oldr[oldr[1250]['m_SerializedData']['rid']]['Binding']
  mapimg=next(i for i,x in r.items() if 'm_SerializedData' in x and data(i).get('name')=='TFUKMapBackground')
  assert data(mapimg)['Binding']['m_kind']==0
  fit=r[mapimg]['m_Parent']['rid'];assert data(fit)['AspectMode']==0 and data(fit)['AspectRatio']==.5625
  assert style(fit,131105)==100
  added={i:x for i,x in r.items() if i not in oldr}
  assert not any(x.get('m_FullTypeName')=='SI.Bindable.SIText' and data(i).get('name','').startswith('TFLocation') for i,x in added.items() if 'm_SerializedData' in x)
  checks.append(dict(target=tag,uid_cases=cases,marker_percentages_match=True,native_info_bindings_preserved=True,native_photo_binding_preserved=True,single_map_width_aspect=.5625,location_labels_and_leaders=False))
 for row in [r for r in tx if Path(r['source']).parent==folder]:
  assert hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()==row['after']
  if '--installed' in sys.argv:assert hashlib.sha256(Path(row['target']).read_bytes()).hexdigest()==row['after']
result=dict(success=True,installed_files_checked='--installed' in sys.argv,runtime_verified=False,checks=checks)
(O/('installed-verification.json' if '--installed' in sys.argv else 'verification.json')).write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps(result))
