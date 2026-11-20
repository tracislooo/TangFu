from pathlib import Path
import sys,json,gc
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=sorted((R/'saved-progress').glob('FM27-current-state-audit-*'))[-1];read=lambda p:json.loads(p.read_text('utf8'))
native=Path(read(R/'current-game-update-comparison.json')['archive'])/'updated-native/aa/StandaloneWindows64'
result=[]
for mode,folder in [('game',O/'snapshot/game/StandaloneWindows64'),('skin',O/'snapshot/skin/StandaloneWindows64'),('native-20261117',native)]:
 obs={};index={};named={};envs=[]
 for p in folder.glob('ui-visualtreeassets*.bundle'):
  e=UnityPy.load(str(p));envs.append(e);oo={o.path_id:o for o in e.objects};obs[p.name]=oo
  for o in oo.values():
   if o.type.name=='MonoBehaviour':named[o.peek_name()]=(p.name,o.path_id)
   elif o.type.name=='AssetBundle':
    for key,v in o.read_typetree()['m_Container']:
     ptr=v['asset'];ob=oo.get(ptr['m_PathID']) if ptr['m_FileID']==0 else None
     if ob and ob.type.name=='MonoBehaviour':index.setdefault(key,[]).append((p.name,ob.path_id))
 trees={};duplicates=[]
 def tr(n,p):
  if (n,p) not in trees:trees[n,p]=obs[n][p].read_typetree()
  return trees[n,p]
 def trace(t,path):
  nodes={r['data']['m_Id']:r['data'] for r in t['references']['RefIds'] if 'm_Id' in r.get('data',{})};nd=nodes.get(path[0]);base={'template':t['m_Name'],'element_id':path[0],'node_present':nd is not None}
  if nd is None:return [base]
  if len(path)==1:return [dict(base,success=True)]
  using=next((u for u in t['m_Usings'] if u['alias']==nd.get('m_TemplateAlias')),None);base['using']=using
  if not using:return [base]
  candidates=[tr(*x) for x in index.get(using['path'],[]) if 'm_VisualTree' in tr(*x)]
  base['candidate_count']=len(candidates)
  return [base]+(trace(candidates[0],path[1:]) if len(candidates)==1 else [])
 for key,entries in index.items():
  nonstyle=[(n,p) for n,p in set(entries) if obs[n][p].peek_name()!='inlineStyle']
  if len(nonstyle)<2:continue
  candidates=[(n,p) for n,p in nonstyle if 'm_VisualTree' in tr(n,p)]
  if len(candidates)>1:duplicates.append({'guid':key,'candidates':[{'bundle':n,'pid':p,'name':tr(n,p)['m_Name']} for n,p in candidates]})
 t=tr(*named['ContractNegotiationToolTemplate']);consumer=tr(*named['ContractNegotiationTool']);aliases={u['alias'] for u in consumer['m_Usings'] if u['path']=='5f191fc6eb99dde47a955456fecb83e6'};rows=[]
 for r in consumer['references']['RefIds']:
  d=r.get('data',{})
  if d.get('m_TemplateAlias') in aliases:
   for x in d['m_SerializedDataOverride']:
    steps=trace(t,x['m_ElementIdsPath']);rows.append({'path':x['m_ElementIdsPath'],'resolved':steps[-1].get('success',False),'trace':steps})
 result.append({'mode':mode,'uniquely_resolved':sum(x['resolved'] for x in rows),'total':len(rows),'paths':rows,'duplicate_visualtree_guids':duplicates});print(mode,result[-1]['uniquely_resolved'],len(rows),'duplicate VTA guids',len(duplicates),flush=True)
 del envs,obs,index,named,trees;gc.collect()
(O/'contract-path-trace.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
