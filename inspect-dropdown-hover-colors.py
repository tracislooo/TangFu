from pathlib import Path
import sys,json,re
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
rows=[];defs={};sheets=[]
for bn in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']:
 for o in UnityPy.load(str(G/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' in d:sheets.append((bn,d))
for bn,s in sheets:
 for r in s['m_Rules']:
  for p in r['m_Properties']:
   if p['m_Id']==-1:defs[p['m_CustomName']]=(s,p)
def val(s,p,seen=()):
 hs=p['m_Values'];out=[]
 for h in hs:
  ty=h['m_ValueType'];i=h['valueIndex'];a={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(ty)
  out.append(s[a][i] if a else {'type':ty,'i':i})
 if len(hs)>=3 and hs[0]['m_ValueType']==10:
  k=s['strings'][hs[2]['valueIndex']]
  if k in defs and k not in seen:return {'var':k,'resolved':val(*defs[k],seen+(k,))}
 return out
for bn,s in sheets:
 for r in s['m_Rules']:
  sel=json.dumps(r.get('m_ComplexSelectors',[]),ensure_ascii=False)
  if not any(k in sel.lower() for k in ['hover','dropdown','drop-down','popup','menu-item','list-item','collection-item']):continue
  ps=[{'id':p['m_Id'],'name':p.get('m_CustomName'),'value':val(s,p)} for p in r['m_Properties']]
  rows.append({'bundle':bn,'sheet':s['m_Name'],'selector':r.get('m_ComplexSelectors'),'properties':ps})
P=R/'dropdown-hover-inspection';P.mkdir(exist_ok=True);(P/'rules.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
def purple(x):
 if isinstance(x,dict):
  if all(k in x for k in ['r','g','b']):return x['b']>x['g']*1.15 and x['r']>x['g']*1.15 and x['b']>.25
  return any(purple(v) for v in x.values())
 if isinstance(x,list):return any(purple(v) for v in x)
 return False
sus=[r for r in rows if purple(r['properties'])];(P/'purple-rules.json').write_text(json.dumps(sus,ensure_ascii=False,indent=2),'utf8')
for r in sus:print(json.dumps(r,ensure_ascii=False))
print('TOTAL',len(rows),'PURPLE',len(sus))
