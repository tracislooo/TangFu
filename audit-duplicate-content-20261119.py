from pathlib import Path
import sys,json,ast,collections,gc
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=sorted((R/'saved-progress').glob('FM27-current-state-audit-*'))[-1];read=lambda p:json.loads(p.read_text('utf8'))
src=ast.parse((R/'review-updated-main-skin.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='canon'],type_ignores=[]),'style-canon','exec'))
results=[]
def strip(v):
 if isinstance(v,dict):return {k:strip(x) for k,x in v.items() if k not in {'m_ContentHash','inlineSheet','m_RuleIndex'}}
 if isinstance(v,list):return [strip(x) for x in v]
 return v
for record in read(O/'contract-path-trace.json')[:2]:
 mode=record['mode'];root=O/'snapshot'/mode/'StandaloneWindows64';env=UnityPy.load(str(root/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));oo={o.path_id:o for o in env.objects};rows=[]
 for d in record['duplicate_visualtree_guids']:
  candidates=d['candidates'];trees=[oo[x['pid']].read_typetree() for x in candidates];styles=[canon(oo[t['inlineSheet']['m_PathID']].read_typetree(),oo[t['inlineSheet']['m_PathID']].assets_file) if t['inlineSheet']['m_PathID'] else [] for t in trees]
  equivalent=all(strip(t)==strip(trees[0]) for t in trees[1:]);style_equal=all(s==styles[0] for s in styles[1:])
  rows.append({**d,'serialized_tree_equal_ignoring_contenthash_and_style_indices':equivalent,'entire_inline_stylesheet_equal':style_equal,'raw_sha256s':[__import__('hashlib').sha256(oo[x['pid']].get_raw_data()).hexdigest() for x in candidates]})
 results.append({'mode':mode,'duplicate_guid_count':len(rows),'different_tree_fields':sum(not x['serialized_tree_equal_ignoring_contenthash_and_style_indices'] for x in rows),'different_inline_stylesheets':sum(not x['entire_inline_stylesheet_equal'] for x in rows),'duplicates':rows});del env,oo;gc.collect()
(O/'duplicate-template-content.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf8');print(json.dumps([{k:v for k,v in x.items() if k!='duplicates'} for x in results]),flush=True)
