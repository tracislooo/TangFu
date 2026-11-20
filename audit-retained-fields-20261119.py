"""Check selected historical edits at field level, resolving inline stylesheet values."""
from pathlib import Path
import sys,json,ast,collections,gc
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=sorted((R/'saved-progress').glob('FM27-current-state-audit-*'))[-1]
read=lambda p:json.loads(p.read_text('utf8'))
source=ast.parse((R/'review-updated-main-skin.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='canon'],type_ignores=[]),'style-canon','exec'))
selected=['inmatch-tactics-tabs-centred-20261116-110343','old-left-fc-competition-radar-divider-20261116-093607','old-left-portrait-compact-details-20261116-095721','old-left-portrait-nonhidden-20261116-191955','middle-nonhidden-career-match-fc-20261116-101358','middle-portrait-hidden-career-match-fc-20261116-102953','lake-controls-progress-repair-20261117-221018','continue-preference-key-fix-20261110-203659']
rows=read(O/'transaction-object-comparison.json');out=[];missing=object()
def transform(v):
 if isinstance(v,dict):return {k:transform(x) for k,x in v.items() if k not in {'m_ContentHash','m_Script'}}
 if isinstance(v,list):
  if v and all(isinstance(x,dict) and 'rid' in x for x in v):return {str(x['rid']):transform(x) for x in v}
  return [transform(x) for x in v]
 return v
def delta(a,b,path=()):
 if a==b:return
 if isinstance(a,dict) and isinstance(b,dict):
  for k in a.keys()|b.keys():yield from delta(a.get(k,missing),b.get(k,missing),path+(k,))
 elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
  for i,(x,y) in enumerate(zip(a,b)):yield from delta(x,y,path+(i,))
 else:yield path,a,b
def at(t,path):
 try:
  for p in path:t=t[p]
  return t
 except (KeyError,TypeError,IndexError):return missing
def short(v):
 if v is missing:return '<absent>'
 if isinstance(v,(list,dict)):return {'kind':type(v).__name__,'length':len(v)}
 return v
for r in rows:
 if Path(r['patch']).name not in selected or r['status']!='object_review_required':continue
 print(Path(r['patch']).name,r['mode'],flush=True)
 paths=[Path(r['backup']),Path(r['source']),O/'snapshot'/r['mode']/'StandaloneWindows64'/Path(r['target']).name]
 envs=[UnityPy.load(str(p)) for p in paths];pools=[{o.path_id:o for o in e.objects} for e in envs]
 def canonical(o,pool):
  t=o.read_typetree()
  if 'm_Rules' in t:return {'rules':canon(t,o.assets_file)}
  if 'm_VisualTree' in t:
   sheet=pool.get(t.get('inlineSheet',{}).get('m_PathID'))
   rules=canon(sheet.read_typetree(),sheet.assets_file) if sheet else []
   for rr in t.get('references',{}).get('RefIds',[]):
    d=rr.get('data',{});i=d.get('m_RuleIndex')
    if i is not None:
     d['resolved_inline_style']=rules[i] if 0<=i<len(rules) else None;d.pop('m_RuleIndex')
  return transform(t)
 for ob in r.get('objects',[]):
  if ob['status']!='changed_since_patch' or ob['type']!='MonoBehaviour':continue
  pid=int(ob['pid'])
  if not all(pid in p for p in pools):continue
  ts=[canonical(p[pid],p) for p in pools];changes=[]
  for path,a,b in delta(ts[0],ts[1]):
   c=at(ts[2],path);status='retained' if c==b else 'back_to_before' if c==a else 'changed_again'
   changes.append({'path':'/'.join(map(str,path)),'status':status,'before':short(a),'patch_after':short(b),'current':short(c)})
  out.append({'patch':r['patch'],'mode':r['mode'],'object':ob['name'],'pid':pid,'counts':dict(collections.Counter(x['status'] for x in changes)),'changes':changes})
 (O/'retained-field-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
 del envs,pools;gc.collect()
print('done',len(out),flush=True)
