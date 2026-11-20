"""Resolve and rebase serialized template override paths against the candidate graph."""
from pathlib import Path
import importlib.util
import sys,json,hashlib
codec=Path('diagnose-ledger-ui.py').read_text('utf8')
exec(compile(codec[:codec.index('out=Path(')],'codec','exec'))
out=Path(sys.argv[1]);read=lambda p:json.loads(p.read_text('utf8'))
m=read(out/'manifest.json');ledger=Path(read(Path('current-complete-bundle-ledger.json'))['archive'])
spec=importlib.util.spec_from_file_location('semantic','semantic-ui-update.py');semantic=importlib.util.module_from_spec(spec);spec.loader.exec_module(semantic)
names=[n for n in m['after_sha256'] if 'visualtreeassets' in n]
candidate={n:UnityPy.load(str(out/n)) for n in names}
groups=[candidate,{n:UnityPy.load(str(ledger/'snapshot/current-game/aa/StandaloneWindows64'/n)) for n in names},
        {n:UnityPy.load(str(out/'backup-game'/n)) for n in names}]
indexes=[];trees=[];object_groups=[]
for envs in groups:
    objects={n:{o.path_id:o for o in env.objects} for n,env in envs.items()}
    index={};docs={}
    for n,obs in objects.items():
        for pid,o in obs.items():
            if o.type.name=='MonoBehaviour':
                d=o.read_typetree()
                if 'm_VisualTree' in d:docs[(n,pid)]=d
        meta=next(o.read_typetree() for o in obs.values() if o.type.name=='AssetBundle')
        for key,v in meta['m_Container']:
            if v['asset']['m_FileID']==0 and (n,v['asset']['m_PathID']) in docs:index[key]=(n,v['asset']['m_PathID'])
    indexes.append(index);trees.append(docs);object_groups.append(objects)

def target(tree,alias,group):
    u=next((u for u in tree['m_Usings'] if u['alias']==alias),None)
    if u is None:return None
    ptr=u.get('asset',{})
    if ptr.get('m_PathID'):
        owner=next((key for key,d in trees[group].items() if d is tree),None)
        if owner:
            af=object_groups[group][owner[0]][owner[1]].assets_file
            fid=ptr['m_FileID'];cab=(af.name if not fid else af.externals[fid-1].name).lower()
            for n,obs in object_groups[group].items():
                ob=obs.get(ptr['m_PathID'])
                if ob and ob.assets_file.name.lower()==cab and (n,ob.path_id) in trees[group]:return trees[group][(n,ob.path_id)]
    return trees[group].get(indexes[group].get(u['path']))

def resolve(tree,path,group=0):
    if not path:return None
    rr={r['rid']:r for r in tree['references']['RefIds']}
    node=next((r for r in rr.values() if r.get('data',{}).get('m_Id')==path[0]),None)
    if node is None:return None
    if len(path)==1:return node,rr
    nested=target(tree,node['data'].get('m_TemplateAlias'),group)
    return resolve(nested,path[1:],group) if nested else None

mapping_cache={}
def translated(before,after,path,group):
    if not path:return []
    rr={r['rid']:r for r in before['references']['RefIds']}
    cachekey=(id(before),id(after))
    if cachekey not in mapping_cache:mapping_cache[cachekey]=semantic.match_nodes(before,after)
    ar={r['rid']:r for r in after['references']['RefIds']}
    r=next((r for r in rr.values() if r.get('data',{}).get('m_Id')==path[0]),None)
    if r is not None:rid=mapping_cache[cachekey].get(r['rid'])
    else:
        current=next((r for r in ar.values() if r.get('data',{}).get('m_Id')==path[0]),None)
        if current is None:return None
        prior=next((k for k,v in mapping_cache[cachekey].items() if v==current['rid']),None)
        if prior is None:return None
        r=rr[prior];rid=current['rid']
    if rid not in ar:return None
    new=ar[rid]['data']['m_Id']
    if len(path)==1:return [new]
    old_nested=target(before,r['data'].get('m_TemplateAlias'),group)
    new_nested=target(after,ar[rid]['data'].get('m_TemplateAlias'),0)
    if not old_nested or not new_nested:return None
    tail=translated(old_nested,new_nested,path[1:],group)
    return [new]+tail if tail else None

expanded_cache={}
def expanded(tree,trail=()):
    if id(tree) in trail:return []
    if id(tree) in expanded_cache:return expanded_cache[id(tree)]
    refs={r['rid']:r for r in tree['references']['RefIds']};out=[]
    for r in refs.values():
        d=r.get('data',{});sid=d.get('m_SerializedData',{}).get('rid',-2)
        if 'm_Id' not in d:continue
        if sid in refs and 'data' in refs[sid]:out.append(([d['m_Id']],refs[sid],d))
        if d.get('m_TemplateAlias'):
            nested=target(tree,d['m_TemplateAlias'],0)
            if nested:
                out.extend(([d['m_Id']]+path,sd,node) for path,sd,node in expanded(nested,trail+(id(tree),)))
    expanded_cache[id(tree)]=out
    return out

errors=[];fixed=[];total=0;changed=set()
for (n,pid),tree in trees[0].items():
    source=trees[1].get((n,pid));native=trees[2].get((n,pid))
    rr={r['rid']:r for r in tree['references']['RefIds']}
    for record in rr.values():
        d=record.get('data',{})
        if not d.get('m_SerializedDataOverride'):continue
        alias=d.get('m_TemplateAlias');dest=target(tree,alias,0)
        for override in d['m_SerializedDataOverride']:
            total+=1;path=override['m_ElementIdsPath'];resolved=resolve(dest,path) if dest else None
            if resolved is None and dest:
                for group,consumer in [(1,source),(2,native)]:
                    if consumer is None:continue
                    prior=target(consumer,alias,group)
                    if not prior:continue
                    newpath=translated(prior,dest,path,group)
                    if newpath and resolve(dest,newpath):
                        override['m_ElementIdsPath']=newpath;override['m_ElementId']=newpath[-1]
                        changed.add(n);fixed.append(dict(bundle=n,name=tree['m_Name'],alias=alias,before=path,after=newpath))
                        resolved=resolve(dest,newpath);break
            if resolved is None and dest:
                expected=rr.get(override['m_SerializedData']['rid'],{})
                scope=dest;prefix=[]
                for item in path[:-1]:
                    sr={r['rid']:r for r in scope['references']['RefIds']}
                    node=next((r['data'] for r in sr.values() if r.get('data',{}).get('m_Id')==item),None)
                    nested=target(scope,node.get('m_TemplateAlias'),0) if node else None
                    if not nested:break
                    prefix.append(item);scope=nested
                options=[(prefix+x[0],x[1],x[2]) for x in expanded(scope) if x[1]['type']==expected.get('type')]
                ename=expected.get('data',{}).get('name','')
                named=[x for x in options if ename and x[1].get('data',{}).get('name')==ename]
                if len(named)==1:options=named
                branch=[x for x in options if len(path)>1 and path[-2] in x[0][:-1]]
                if len(branch)==1:options=branch
                tid=expected.get('data',{}).get('templateId','')
                typed=[x for x in options if tid and x[2].get('m_TemplateAlias')==tid]
                if len(typed)==1:options=typed
                if len(options)==1:
                    newpath=options[0][0]
                    override['m_ElementIdsPath']=newpath;override['m_ElementId']=newpath[-1]
                    changed.add(n);fixed.append(dict(bundle=n,name=tree['m_Name'],alias=alias,before=path,after=newpath,method='unique_serialized_control_identity'))
                    resolved=resolve(dest,newpath)
            if resolved is None:
                errors.append(dict(bundle=n,name=tree['m_Name'],alias=alias,path=path));continue
            override['m_ElementId']=override['m_ElementIdsPath'][-1]
            sid=override['m_SerializedData']['rid']
            if sid in rr and 'uxmlAssetId' in rr[sid].get('data',{}):
                if rr[sid]['data']['uxmlAssetId']!=override['m_ElementId']:
                    rr[sid]['data']['uxmlAssetId']=override['m_ElementId'];changed.add(n)
    if n in changed:object_groups[0][n][pid].save_typetree(tree)
for n in changed:
    data=candidate[n].file.save(packer='lz4');(out/n).write_bytes(data)
    m['after_sha256'][n]=hashlib.sha256(data).hexdigest()
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'all-template-overrides.json').write_text(json.dumps(dict(total=total,fixed=fixed,errors=errors),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(total=total,fixed=len(fixed),unresolved=len(errors),examples=errors[:12]),ensure_ascii=False))
