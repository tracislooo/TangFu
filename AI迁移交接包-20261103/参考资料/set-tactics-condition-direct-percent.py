from pathlib import Path
import struct
source=Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig')
exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-','tactics-condition-direct-percent-'),'backup-and-helpers','exec'))
CELL=-970000000001000;doc=objs[CELL].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[sid].read_typetree()
def sd(i):return serial(rr,i)['data']
def args(raw):
 b=bytes(raw);p=1;out=[]
 for _ in range(b[0]):n=struct.unpack_from('<I',b,p)[0];p+=4;out.append(bytearray(b[p:p+n]));p+=n
 assert p==len(b);return out
def encode(a):return list(bytes([len(a)])+b''.join(struct.pack('<I',len(x))+x for x in a))
gate=next(i for i,r in rr.items() if 'm_SerializedData' in r.get('data',{}) and r['data']['m_SerializedData']['rid']!=-2 and sd(i).get('name')=='TacticsConditionAbove-1')
oldtree=rr[gate]['data']['m_Children'][1]['rid'];switchproto=copy.deepcopy(rr[oldtree]);switchsd=copy.deepcopy(serial(rr,oldtree));leafid=next(i for i,r in rr.items() if 'm_SerializedData' in r.get('data',{}) and r['data']['m_SerializedData']['rid']!=-2 and sd(i).get('name')=='TacticsConditionPercent0');leafproto=copy.deepcopy(rr[leafid]);leafsd=copy.deepcopy(serial(rr,leafid))
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;removed=set()
def discard(i):
 for c in rr[i]['data'].get('m_Children',[]):discard(c['rid'])
 removed.add(i);removed.add(rr[i]['data']['m_SerializedData']['rid'])
discard(oldtree)
rr[gate]['data']['m_Children']=rr[gate]['data']['m_Children'][:1]
for i in removed:rr.pop(i)
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
def add(node,serial,parent,name):
 global next_rid,next_id
 a=copy.deepcopy(node);s=copy.deepcopy(serial);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']})
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1);next_id+=1;rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
values={}
def tree(parent,lo,hi):
 if lo==hi:
  i=add(leafproto,leafsd,parent,'TacticsConditionPercent'+str(lo));sd(i)['text']=str(lo)+'%';values[i]=lo;return i
 mid=(lo+hi)//2;i=add(switchproto,switchsd,parent,'TacticsConditionAbove'+str(mid));a=args(sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);struct.pack_into('<i',a[1],len(a[1])-4,mid);sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(a);tree(i,lo,mid);tree(i,mid+1,hi);return i
root=tree(gate,0,100)
def selected(i,value):
 if i in values:return str(values[i])+'%'
 if rr[i]['data']['m_FullTypeName']!='SI.Bindable.BindableSwitchElement':return sd(i)['text']
 a=args(sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack_from('<i',a[1],len(a[1])-4)[0];return selected(rr[i]['data']['m_Children'][int(value is not None and value>limit)]['rid'],value)
cases=[None,-2147483648]+list(range(-1,151))
for value in cases:assert selected(gate,value)==('--' if value is None or value<0 else str(min(100,value))+'%'),value
for i,r in old.items():
 if i not in removed and i!=gate:assert rr[i]==r,('unrelated reference changed',i)
validate_ui(doc,sheet);objs[CELL].save_typetree(doc);output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs)
for i,h in hashes.items():
 if i!=CELL:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
assert check[CELL].read_typetree()==doc
(OUT/W).write_bytes(output);(OUT/'cell.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
report={'installed':False,'runtime_verified':False,'formula':'clamp(player.Condition,0,100)%','examples':{str(v):selected(gate,v) for v in [0,25,50,75,100]},'missing':'--','cases_verified':len(cases),'changed_object':CELL,'portrait_sizes_unchanged':True,'catalog_factory_styles_and_other_objects_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p in before:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'examples':report['examples'],'cases_verified':len(cases)}))
