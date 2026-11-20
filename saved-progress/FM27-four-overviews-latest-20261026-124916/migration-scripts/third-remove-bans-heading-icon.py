from pathlib import Path
import ast,copy,json

source=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix=source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-','third-remove-bans-heading-icon-')
exec(compile(prefix,'backup-and-serialization','exec'))
PAGE,STYLE=-940000000010000,-940000000010001
SELECTOR,SELECTOR_STYLE=-940000000010020,-940000000010021
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def save(n,pid,doc,sid,styles):
    validate_ui(doc,styles);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(styles)
    changed[n][pid]=doc;changed[n][sid]=styles

def remove_subtree(i):
    parent=rr[i]['data']['m_Parent']['rid']
    rr[parent]['data']['m_Children'].remove({'rid':i})
    gone=set()
    def walk(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                rid=v['rid']
                if rid in rr and rid not in gone:
                    gone.add(rid);walk(rr[rid])
            else:
                for k,x in v.items():
                    if k!='m_Parent':walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    gone.add(i);walk(rr[i])
    doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in gone]
    return gone

PAGE,STYLE=-940000000011010,-940000000011011
doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
gone=remove_subtree(1002);rr=refs(doc)
assert rr[1001]['data']['m_Children']==[{'rid':1003}]
for i,r in rr.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert r==old[i]
assert 1005 not in rr and 1006 not in rr
save(W,PAGE,doc,STYLE,sheet)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
    for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report={'installed':False,'runtime_verified':False,'third_only':True,
    'bans_heading_frame_and_flag_removed':True,'bans_table_and_bindings_preserved':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
    tag='backup-game' if p.parent==GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for n,b in outputs.items():
        for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'bans_heading_removed':True}))
