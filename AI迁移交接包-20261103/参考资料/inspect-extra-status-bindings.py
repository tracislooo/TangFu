exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
import re
for pid,ids in [(3052255369264346086,[1006,1047,1058,1059,1050,1062,1063]),(1504705285788836261,[1006]),(3508926604620743622,[1003,1012,1015,1014]),(5108509966786251923,[1005,1217,1042,1043])]:
 d=objects[pid].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};print('\n',d['m_Name'])
 for i in ids:
  r=sr[i];a=r['data'];sd=sr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',a)
  # Function bytes are summarized as printable strings; no schema/values lost on disk.
  def short(v):
   if isinstance(v,dict):return {k:([s.decode() for s in re.findall(rb'[ -~]{4,}',bytes(x))] if k in ['m_argumentBytes','m_bytes'] else short(x)) for k,x in v.items()}
   if isinstance(v,list):return [short(x) for x in v]
   return v
  fields={k:v for k,v in sd.items() if k in ['Parameters','Mappings','ValueVariables','ReferenceVariables','m_components','TextBinding','Binding','ImageKind','DebugDisplay','BindTextFunction']}
  print(i,r['type']['class'],json.dumps(short(fields),ensure_ascii=False))
