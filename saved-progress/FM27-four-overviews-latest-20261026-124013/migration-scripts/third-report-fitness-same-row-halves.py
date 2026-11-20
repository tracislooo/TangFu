from pathlib import Path
import ast,copy,json

source=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix=source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-','third-report-fitness-same-row-halves-')
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

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
row=add_pair(old[6298],serial(old,6298),2242,'ThirdOverviewScoutFitnessEqualRow')
override(rr[row]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
    prop(131087,auto),prop(131096,px(42)),prop(131094,none),prop(131082,auto),
    prop(131084,num(0)),prop(131085,num(0)),prop(131083,en('row')),
    prop(131073,en('center')),prop(131088,en('flex-start')),prop(262150,px(0)),prop(262151,px(0))])
for i in [1186,2986]:
    rr[2242]['data']['m_Children'].remove({'rid':i})
    rr[i]['data']['m_Parent']={'rid':row}
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
        prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),
        prop(131091,px(0)),prop(131092,px(0))])
rr[row]['data']['m_Children']=[{'rid':1186},{'rid':2986}]
# Report-to-fitness divider no longer separates vertically stacked sections.
remove_subtree(6286);rr=refs(doc)
line=named('ThirdOverviewFitnessStatsDivider')
rr[2242]['data']['m_Children']=[{'rid':row},{'rid':line},{'rid':6304}]
for i,r in old.items():
    if i in rr and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('unexpected binding change',i)
assert rr[row]['data']['m_Children']==[{'rid':1186},{'rid':2986}]
save(W,PAGE,doc,STYLE,sheet)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
    for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report={'installed':False,'runtime_verified':False,'third_only':True,
    'scout_report_left_fitness_right_same_row':True,'width_ratio':[1,1],
    'stats_below_with_separator':True,'native_bindings_preserved':True,
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
print(json.dumps({'installed':True,'output':str(OUT),'scout_fitness_same_row':True,'width_ratio':'50/50'}))

