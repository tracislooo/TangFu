"""Check every staged UI tree and prune disconnected managed records."""
from pathlib import Path
import sys,json,hashlib,ast,traceback
sys.path.insert(0,'.codex-deps')
import UnityPy
from UnityPy.helpers import TypeTreeHelper
write_original=TypeTreeHelper.write_value
def write(value,node,writer,config):
    if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(value,config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type!='ReferencedObjectData':write_original(value[child.m_Name],child,writer,config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
        return
    return write_original(value,node,writer,config)
TypeTreeHelper.write_value=write
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'))
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse(Path('add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in src.body if isinstance(x,ast.FunctionDef) and x.name=='validate_ui'],type_ignores=[]),'validator','exec'))
errors=[];cleaned=[]
for n in m['after_sha256']:
    if 'visualtreeassets' not in n:continue
    e=UnityPy.load(str(out/n));obs={o.path_id:o for o in e.objects};changed=False
    for o in list(obs.values()):
        if o.type.name!='MonoBehaviour':continue
        d=o.read_typetree()
        if 'm_VisualTree' not in d or not d['inlineSheet']['m_PathID']:continue
        rr={r['rid']:r for r in d['references']['RefIds']};seen=set()
        def refs(v):
            if isinstance(v,dict):
                if set(v)=={'rid'}:yield v['rid']
                else:
                    for k,x in v.items():
                        if k not in ['references','m_Parent']:yield from refs(x)
            elif isinstance(v,list):
                for x in v:yield from refs(x)
        pending=list(refs(d))
        while pending:
            rid=pending.pop()
            if rid in seen or rid not in rr:continue
            seen.add(rid);pending.extend(refs(rr[rid].get('data',{})))
        removed=set(rr)-seen-{-2}
        if removed:
            d['references']['RefIds']=[r for r in d['references']['RefIds'] if r['rid'] not in removed]
            o.save_typetree(d);changed=True
            cleaned.append(dict(bundle=n,pid=o.path_id,name=d['m_Name'],removed=len(removed)))
        try:validate_ui(d,obs[d['inlineSheet']['m_PathID']].read_typetree())
        except Exception as ex:
            tb=traceback.extract_tb(ex.__traceback__)
            errors.append(dict(bundle=n,pid=o.path_id,name=d['m_Name'],error=repr(ex),line=tb[-1].lineno))
    if changed:
        data=e.file.save(packer='lz4');(out/n).write_bytes(data)
        m['after_sha256'][n]=hashlib.sha256(data).hexdigest()
    print(n,'diagnosed',flush=True)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'ui-diagnosis.json').write_text(json.dumps(dict(errors=errors,pruned=cleaned),ensure_ascii=False,indent=2),'utf8')
print('errors',len(errors),str(errors)[:4000])
