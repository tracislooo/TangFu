from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle';F='ui-tablefactories_assets_all.bundle';V='ui-tableviews_assets_all.bundle'
env={n:UnityPy.load(str(GAME/n)) for n in [W,G,M,F,V]};docs={};guidmap={};reverse={};edges={};metas={}
def guids(v):
 found=set()
 if isinstance(v,dict):
  for x in v.values():found.update(guids(x))
 elif isinstance(v,(list,tuple)):
  if v and all(isinstance(x,int) and 0<=x<256 for x in v):found.update(x.decode() for x in re.findall(rb'[0-9a-f]{32}',bytes(v)))
  else:
   for x in v:found.update(guids(x))
 elif isinstance(v,str):found.update(re.findall(r'(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])',v))
 return found
for n,e in env.items():
 for o in e.objects:
  if o.type.name=='AssetBundle':
   metas[n]=o.read_typetree()
   for k,v in metas[n]['m_Container']:
    if v['asset']['m_FileID']==0:guidmap[k]=(n,v['asset']['m_PathID'])
  if o.type.name=='MonoBehaviour':
   d=o.read_typetree()
   if 'inlineSheet' in d or n in [F,V]:docs[n,o.path_id]=d
guidmap={g:k for g,k in guidmap.items() if k in docs}
for n,mt in metas.items():
 for g,v in mt['m_Container']:
  k=(n,v['asset']['m_PathID'])
  if v['asset']['m_FileID']==0 and k in docs:guidmap[g]=k
for key,d in docs.items():
 edges[key]={guidmap[g] for g in guids(d) if g in guidmap and guidmap[g] in docs}
 for child in edges[key]:reverse.setdefault(child,set()).add(key)
pat=re.compile(r'Match|HalfTime|FullTime|Halftime|Fulltime|Tunnel|TeamTalk|Shout|Highlight|Touchline|Dugout|PenaltyShootout',re.I)
roots={k for k,d in docs.items() if k[0]==M or pat.search(d['m_Name'].removeprefix('OutsideMatchSquare_'))}
closure=set(roots);todo=list(roots)
while todo:
 for child in edges[todo.pop()]:
  if child not in closure:closure.add(child);todo.append(child)
targets={'PlayerNameCell','PlayerNameCell14px','PlayerNameCell14pxBold','PlayerNameCell16px','PlayerNameCell16pxBold','PlayerCell'}
base={k for k,d in docs.items() if (k[0]==W and d['m_Name'] in targets) or (k[0]==G and d['m_Name'] in ['PersonPicture','thumbnails-alt-person-picture'])}
affected=set(base);todo=list(base)
while todo:
 for parent in reverse.get(todo.pop(),set()):
  if parent in roots:continue
  if parent not in affected:affected.add(parent);todo.append(parent)
clones={k for k in affected if k in closure or k in base}
safe=affected-clones
out={'bases':[(k[0],k[1],docs[k]['m_Name']) for k in sorted(base)],'clones':[(k[0],k[1],docs[k]['m_Name']) for k in sorted(clones)],'safe':[(k[0],k[1],docs[k]['m_Name']) for k in sorted(safe)],'match_closure':len(closure),'match_roots':len(roots)}
(R/'list-portrait-inspection'/'plan.json').write_text(json.dumps(out,indent=2),'utf8')
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in out.items()}))
print('GUID samples',list(guidmap.items())[:3]);print('alias target',guidmap.get('a3126e03e5bea6348ba86f23b5c5d7de'));print('reverse',[(docs[k]['m_Name'],len(reverse.get(k,[]))) for k in base])
for g in ['a3126e03e5bea6348ba86f23b5c5d7de','d894b159c6d0cba49bd51def7f05e85c','1dc44d3bb16aa43478da6d62db835467']:
 for n,mt in metas.items():
  oo={o.path_id:o for o in env[n].objects}
  for k,v in mt['m_Container']:
   if k==g:print(g,n,v,oo[v['asset']['m_PathID']].peek_name())
