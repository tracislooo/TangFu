from pathlib import Path
import sys,json,ast
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=next(p for p in sorted(R.glob('main-1-14-rebuild-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((O/'manifest.json').read_text('utf8'));index={}
for bn in m['after_sha256']:
 if 'visualtree' not in bn:continue
 e=UnityPy.load(str(O/bn));obs={o.path_id:o for o in e.objects};meta=next(o.read_typetree() for o in obs.values() if o.type.name=='AssetBundle')
 for key,entry in meta['m_Container']:
  ptr=entry['asset'];o=obs.get(ptr['m_PathID']) if ptr['m_FileID']==0 else None
  if o and o.type.name=='MonoBehaviour':
   d=o.read_typetree()
   if 'inlineSheet' in d:index[key]=(bn,o.path_id,d)
NAME='ContractNegotiationToolTemplate';GUID='5f191fc6eb99dde47a955456fecb83e6';new=index[GUID][2]
a=ast.parse((R/'fix-contract-offer-template-ids.py').read_text('utf8'));exec(compile(ast.Module(body=[x for x in a.body if isinstance(x,ast.FunctionDef) and x.name=='resolve'],type_ignores=[]),'resolve','exec'))
audit=[]
for bundle,pid,tree in index.values():
 aliases={u['alias'] for u in tree['m_Usings'] if u['path']==GUID}
 for row in tree['references']['RefIds']:
  d=row.get('data',{})
  if d.get('m_TemplateAlias') not in aliases:continue
  ovs=d['m_SerializedDataOverride'];count=sum(resolve(new,x['m_ElementIdsPath'],new) for x in ovs);assert count==len(ovs),(tree['m_Name'],count,len(ovs));audit.append({'consumer':tree['m_Name'],'resolved':count})
assert any(x['consumer']=='ContractNegotiationTool' and x['resolved']==66 for x in audit)
print(json.dumps(audit));(O/'contract-override-verification.json').write_text(json.dumps(audit,indent=2),'utf8')
