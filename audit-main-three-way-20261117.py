"""Audit overlapping native and skin edits without modifying the installation."""
from pathlib import Path
import collections
import hashlib
import json
import sys
import importlib.util

ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'.codex-deps'))
import UnityPy
spec=importlib.util.spec_from_file_location('semantic','semantic-ui-update.py');semantic=importlib.util.module_from_spec(spec);spec.loader.exec_module(semantic)
record=Path(json.loads((ROOT/'current-complete-bundle-ledger.json').read_text('utf8'))['archive'])
manifest=json.loads((record/'manifest.json').read_text('utf8'))
baseline={r['bundle']:r for r in json.loads((record/'baseline-index.json').read_text('utf8'))['bundles']}
game=Path(json.loads((ROOT/'current-game-location.json').read_text('utf8'))['bundle_root'])
out=ROOT/'main-update-audit-20261117'
out.mkdir(exist_ok=True)
conflicts=[]
counts=collections.Counter()
missing=object()

def audit(a,b,c,path,context):
    if a==b or b==c:return
    if a==c:
        counts['nonoverlapping_edits']+=1
        return
    if isinstance(a,dict) and isinstance(b,dict) and isinstance(c,dict):
        for key in set(a)|set(b)|set(c):
            if key in {'m_Script','m_ContentHash','m_Id','uxmlAssetId'}:continue
            audit(a.get(key,missing),b.get(key,missing),c.get(key,missing),path+'/'+key,context)
        return
    if isinstance(a,list) and isinstance(b,list) and isinstance(c,list):
        if a and all(isinstance(x,dict) and 'rid' in x for seq in [a,b,c] for x in seq):
            maps=[{str(x['rid']):x for x in seq} for seq in [a,b,c]]
            if all(len(m)==len(s) for m,s in zip(maps,[a,b,c])):
                audit(*maps,path+'/by-rid',context)
                return
        if len(a)==len(b)==len(c):
            for i,(x,y,z) in enumerate(zip(a,b,c)):audit(x,y,z,path+'/'+str(i),context)
            return
    def sample(v):
        if v is missing:return '<absent>'
        if isinstance(v,(list,dict,bytes,bytearray)):return {'type':type(v).__name__,'length':len(v)}
        return v
    conflicts.append(dict(**context,path=path,original=sample(a),skin=sample(b),updated=sample(c)))

for bundle in manifest['bundles']:
    if bundle['mode']!='current-game' or not bundle['objects']:continue
    name=bundle['bundle']
    paths=[record/baseline[name]['materialized_native'],record/bundle['snapshot'],game/name]
    pools=[{o.path_id:o for o in UnityPy.load(str(p)).objects} for p in paths]
    for row in bundle['objects']:
        pid=int(row['path_id'])
        context=dict(bundle=name,path_id=pid,name=row['name'],type=row['type'])
        if row['type']=='AssetBundle':
            counts['assetbundle_metadata_to_rebuild']+=1
            continue
        if row['status']=='added':
            if pid in pools[2]:conflicts.append(dict(**context,path='/',reason='new_native_id_collision'))
            else:counts['additions']+=1
            continue
        if pid not in pools[2]:
            conflicts.append(dict(**context,path='/',reason='native_identity_removed_or_changed'))
            continue
        if row['status']=='deleted':
            counts['deletions']+=1
            continue
        if row['type']=='MonoBehaviour':
            trees=[pool[pid].read_typetree() for pool in pools]
            if 'm_VisualTree' in trees[0]:
                trees[1]=semantic.normalize_refs(trees[0],trees[1],100000)[0]
                trees[2]=semantic.normalize_refs(trees[0],trees[2],200000)[0]
            audit(*trees,'',context)
        elif pools[0][pid].get_raw_data()!=pools[2][pid].get_raw_data():
            conflicts.append(dict(**context,path='/',reason='binary_resource_three_way_required'))
    print(name,'audited',flush=True)
result={'record':str(record),'game_untouched':True,'counts':dict(counts),'conflict_count':len(conflicts),'conflicts':conflicts}
(out/'conflicts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'counts':dict(counts),'conflicts':len(conflicts),'report':str(out/'conflicts.json')}))
