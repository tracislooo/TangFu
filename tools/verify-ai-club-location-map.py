from pathlib import Path
import hashlib,json,struct,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
state=json.loads((R/'current-ai-club-location-map.json').read_text('utf8'));O=Path(state['patch'])
m=json.loads((O/'manifest.json').read_text('utf8'));tx=json.loads((O/'transaction.json').read_text('utf8'))
out=[]
for a in m['audits']:
 tag=a['target'];row=next(r for r in tx if Path(r['source']).parent==O/tag and Path(r['source']).suffix=='.bundle')
 ob={o.path_id:o for o in UnityPy.load(row['source']).objects};old={o.path_id:o for o in UnityPy.load(row['backup']).objects}
 body=ob[-8334206648415311334].read_typetree();rs={r['rid']:r.get('data',{}) for r in body['references']['RefIds']}
 sd=lambda i:rs[rs[i]['m_SerializedData']['rid']]
 sheet=ob[body['inlineSheet']['m_PathID']].read_typetree()
 def prop(i,key):
  q=next(q for q in sheet['m_Rules'][rs[i]['m_RuleIndex']]['m_Properties'] if q['m_Id']==key)['m_Values'][0]
  pool={2:'floats',3:'dimensions',7:'strings'}[q['m_ValueType']];v=sheet[pool][q['valueIndex']]
  return v.get('value') if isinstance(v,dict) else v
 module=next(i for i,x in rs.items() if 'm_SerializedData' in x and sd(i).get('name')=='AIClubCurrentLocationAndStadium')
 right=next(i for i,x in rs.items() if 'm_SerializedData' in x and sd(i).get('name')=='AIClubRightSquadAndTransfers')
 assert prop(module,131105)==50 and prop(right,131105)==50
 assert rs[1014]['m_Parent']['rid']==right and rs[1018]['m_Parent']['rid']==right
 assert [x['rid'] for x in rs[right]['m_Children']][::2]==[1014,1018]
 assert prop(1016,131081)=='none' and prop(1020,131081)=='none'
 assert prop(1014,131084)==prop(1018,131084)==1
 assert sd(1007)['Mappings'][0]['to']['m_path']=='club.MainTeam'
 # Player-specific body is unchanged. The shared module keeps all original native info/photo bindings.
 assert ob[-991100000000060].get_raw_data()==old[-991100000000060].get_raw_data()
 def refs(d):return {r['rid']:r.get('data',{}) for r in d['references']['RefIds']}
 st=refs(ob[-991100000000030].read_typetree());prev=refs(old[-991100000000030].read_typetree())
 gate_sd=set()
 for g in a['gates']:
  i=st[g['gate']]['m_SerializedData']['rid'];gate_sd.add(i);v=st[i]
  assert v['AlwaysInstantiate']==0 and v['AlwaysInstantiate_UxmlAttributeFlags']==1 and v['Preview']=={'Mask':1}
  assert v['Binding']==prev[i]['Binding']
  args=bytes(v['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);p=1;arr=[]
  for _ in range(args[0]):n=struct.unpack_from('<I',args,p)[0];p+=4;arr.append(args[p:p+n]);p+=n
  assert struct.unpack('<i',arr[1][-4:])[0]==g['uid'] and arr[2].endswith(b'club.UniqueId')
 for i,v in prev.items():
  if i not in gate_sd:assert st[i]==v
 assert len(gate_sd)==20 and len({g['uid'] for g in a['gates']})==20
 for uid in [667,728,602,-1]:assert sum(g['uid']==uid for g in a['gates'])==(0 if uid==-1 else 1)
 for r in [r for r in tx if Path(r['source']).parent==O/tag]:
  assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['after']
  if '--installed' in sys.argv:assert hashlib.sha256(Path(r['target']).read_bytes()).hexdigest()==r['after']
 out.append(dict(target=tag,ai_layout_half_map_quarter_squad_quarter_transfers=True,current_page_club_scope_preserved=True,native_stadium_bindings_unchanged=True,unique_uid_gates=20,default_empty_branch=True,player_page_preserved=True))
result=dict(success=True,installed_verified='--installed' in sys.argv,runtime_verified=False,checks=out)
(O/('installed-verification.json' if '--installed' in sys.argv else 'verification.json')).write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps(result))
