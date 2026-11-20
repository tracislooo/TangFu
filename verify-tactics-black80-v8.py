from pathlib import Path
import sys,json,hashlib,struct
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1])
m=json.loads((out/'manifest.json').read_text('utf8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in m['after_sha256'].items():assert sha(p)==h,p
for p,h in m['protected_files'].items():assert sha(p)==h,p
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
target=next(Path(p) for p in m['after_sha256'] if p.endswith(W))
now={o.path_id:o for o in UnityPy.load(str(target)).objects}
old={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/W)).objects}
assert now.keys()==old.keys()
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def tree(pid):
 d=now[pid].read_typetree();r={a['rid']:a for a in d['references']['RefIds']};s=now[d['inlineSheet']['m_PathID']].read_typetree()
 def sd(i):return r[r[i]['data']['m_SerializedData']['rid']]['data']
 def v(i,k):
  p=next(p for p in s['m_Rules'][r[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==k)
  return [s[pool[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']]
 return d,r,sd,v
changed=set(m['changed_world_objects'])
for pid,o in now.items():
 if pid not in changed:assert o.get_raw_data()==old[pid].get_raw_data()
 elif o.type.name=='MonoBehaviour':
  d=o.read_typetree();prev=old[pid].read_typetree()
  if 'references' not in d:continue
  a={v['rid']:v for v in prev['references']['RefIds']};b={v['rid']:v for v in d['references']['RefIds']}
  assert a.keys()==b.keys()
  for i,z in a.items():
   if 'UxmlSerializedData' not in z.get('type',{}).get('class',''):continue
   if pid==-966834888143150418 and 'BindGradientFunc' in z.get('data',{}):
    za=z['data'].copy();zb=b[i]['data'].copy();fa=za.pop('BindGradientFunc');fb=zb.pop('BindGradientFunc')
    assert za==zb and fa['m_target']==fb['m_target']
   else:assert z==b[i],(pid,i,'binding changed')
fitness=0
for pid,root in [(3127595210179668386,1173),(-8273082868742719783,1077)]:
 d,r,sd,v=tree(pid)
 for i,z in r.items():
  if z.get('data',{}).get('m_FullTypeName')!='SI.Bindable.SIText':continue
  if not sd(i).get('name','').startswith('PitchFitnessPercent'):continue
  assert v(i,131089)[0]['value']==-12 and v(i,131099)[0]['value']==4
  for c in z['data']['m_Children']:assert v(c['rid'],131089)[0]['value']==12
 for pct in [None,-1]+list(range(111)):
  i=root
  while not sd(i).get('name','').startswith('PitchFitnessPercent'):
   data=bytes(sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
   count=data[0];offset=1;args=[]
   for _ in range(count):
    size=struct.unpack_from('<I',data,offset)[0];offset+=4;args.append(data[offset:offset+size]);offset+=size
   assert args[2].endswith(b'position.Player.Condition')
   limit=struct.unpack_from('<i',args[1],len(args[1])-4)[0]
   i=r[i]['data']['m_Children'][int(pct is not None and pct>limit)]['rid']
  n=None if pct is None or pct<0 else min(pct,100)
  assert sd(i)['text']==('--' if n is None else str(n)+'%');fitness+=1
for pid,node,stars in [(3127595210179668386,1037,1036),(-970000000009000,1016,1022),(-970000000010000,1061,1027)]:
 d,r,sd,v=tree(pid)
 assert v(node,131104)[0]['value']==60 and v(node,131087)[0]['value']==11
 assert v(stars,327681)==[1.5,1.5] and v(stars,131104)[0]['value']==3
d,r,sd,v=tree(-970000000012000)
assert v(1004,131105)[0]['value']==v(1004,131087)[0]['value']==12
assert v(1004,196610)[0]=={'r':1.,'g':1.,'b':1.,'a':1.}
m.update(independent_installed_verification=True,fitness_inputs_verified=fitness)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed_verified':True,'fitness_inputs':fitness,'native_bindings_preserved':True,'protected_files_unchanged':len(m['protected_files']),'runtime_verified':False}))
