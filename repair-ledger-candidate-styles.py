"""Materialize merged inline sheets after all VTA owners have been processed."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]);read=lambda p:json.loads(p.read_text('utf8'))
m=read(out/'manifest.json');ledger=Path(read(ROOT/'current-complete-bundle-ledger.json')['archive'])
sp=importlib.util.spec_from_file_location('merge',ROOT/'merge-main-fields.py');merge=importlib.util.module_from_spec(sp);sp.loader.exec_module(merge)
names=[n for n in m['after_sha256'] if 'visualtreeassets' in n]
source_env={n:UnityPy.load(str(ledger/'snapshot/current-game/aa/StandaloneWindows64'/n)) for n in names}
target_env={n:UnityPy.load(str(out/n)) for n in names}
source={n:{o.path_id:o for o in e.objects} for n,e in source_env.items()}
target={n:{o.path_id:o for o in e.objects} for n,e in target_env.items()}
cab_to_bundle={a.name.lower():n for n,e in target_env.items() for a in e.assets}
mapping={}
for row in m['stage_assets']:
    if row['bundle'] in target:
        af=source[row['source_bundle']][row['source_id']].assets_file
        mapping[(af.name.lower(),row['source_id'])]=(target[row['bundle']][row['id']].assets_file.name.lower(),row['id'])
def remap(value,srcaf,dstaf):
    if isinstance(value,dict):
        if set(value)=={'m_FileID','m_PathID'}:
            if not value['m_PathID']:return copy.deepcopy(value)
            fid=value['m_FileID'];cab=(srcaf.name if not fid else srcaf.externals[fid-1].name).lower()
            cab,pid=mapping.get((cab,value['m_PathID']),(cab,value['m_PathID']))
            if cab==dstaf.name.lower():fid=0
            else:fid=next(i+1 for i,e in enumerate(dstaf.externals) if e.name.lower()==cab)
            return {'m_FileID':fid,'m_PathID':pid}
        return {k:remap(v,srcaf,dstaf) for k,v in value.items() if k!='m_Script'}
    if isinstance(value,list):return [remap(v,srcaf,dstaf) for v in value]
    return copy.deepcopy(value)
for n in names:
    base={o.path_id:o for o in UnityPy.load(str(ledger/'native-baseline/aa/StandaloneWindows64'/n)).objects}
    native={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/n)).objects}
    fixed=0
    for row in m['stage_assets']:
        if row['bundle']!=n or row['source_id'] not in base or row['id'] not in native:continue
        old=source[n][row['source_id']];a=base[row['source_id']].read_typetree();b=old.read_typetree();c=native[row['id']].read_typetree()
        if 'm_VisualTree' not in a or 'm_VisualTree' not in b or 'm_VisualTree' not in c:continue
        af=target[n][row['id']].assets_file
        ash=remap(base[a['inlineSheet']['m_PathID']].read_typetree(),base[row['source_id']].assets_file,af)
        bsh=remap(source[n][b['inlineSheet']['m_PathID']].read_typetree(),old.assets_file,af)
        csh=native[c['inlineSheet']['m_PathID']].read_typetree()
        merged,sheet=merge.merge_ui(remap(a,base[row['source_id']].assets_file,af),remap(b,old.assets_file,af),c,ash,bsh,csh)
        actual=target[n][row['id']].read_typetree()
        expected={r['rid']:r.get('data',{}).get('m_RuleIndex') for r in merged['references']['RefIds'] if 'm_RuleIndex' in r.get('data',{})}
        indices={r['rid']:r.get('data',{}).get('m_RuleIndex') for r in actual['references']['RefIds'] if 'm_RuleIndex' in r.get('data',{})}
        assert expected==indices,('Recomputed node/style identities differ',n,row['name'])
        sid=actual['inlineSheet']['m_PathID']
        template=target[n][sid].read_typetree()
        sheet['m_Script']=template['m_Script']
        target[n][sid].save_typetree(sheet);fixed+=1
    data=target_env[n].file.save(packer='lz4');(out/n).write_bytes(data)
    m['after_sha256'][n]=hashlib.sha256(data).hexdigest()
    print(n,fixed,flush=True)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
