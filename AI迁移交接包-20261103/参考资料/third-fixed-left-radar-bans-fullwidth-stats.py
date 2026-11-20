from pathlib import Path
import ast,copy,json

source=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix=source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-','third-fixed-left-radar-bans-fullwidth-stats-')
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
# Replace the left scroll view with an ordinary bounded container.
left_sd=rr[1102]['data']['m_SerializedData']['rid']
replacement=copy.deepcopy(serial(old,1291));replacement['rid']=left_sd
replacement['data'].update(uxmlAssetId=rr[1102]['data']['m_Id'],name='ThirdOverviewLeftBoundedNoScroll',name_UxmlAttributeFlags=1)
rr[left_sd].clear();rr[left_sd].update(replacement)
rr[1102]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
override(rr[1102]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),
    prop(458768,en('hidden')),prop(131101,px(0)),prop(131098,px(0))])
override(rr[1114]['data'],[prop(131094,pct(100)),prop(131085,num(1)),prop(458768,en('hidden'))])
# Preserve the native chart and its player binding; only move its container.
rr[1173]['data']['m_Children'].remove({'rid':1026})
rr[1026]['data']['m_Parent']={'rid':6298}
remove_subtree(6230);rr=refs(doc)
rr[6298]['data']['m_Children'].append({'rid':1026})
remove_subtree(6336);rr=refs(doc)
assert rr[6298]['data']['m_Children']==[{'rid':6228},{'rid':1026}]
assert rr[1173]['data']['m_Children']==[{'rid':2242}]
override(rr[1026]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
    prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(160)),
    prop(131096,px(160)),prop(131094,px(160)),prop(131074,en('flex-start'))])
override(rr[1173]['data'],[prop(131083,en('column')),prop(131073,en('stretch'))])
override(rr[2242]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
    prop(131083,en('column')),prop(131073,en('stretch')),prop(131091,px(0)),prop(131092,px(0))])
next_rid=max(max(rr),max(old))+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
line=add_pair(old[6286],serial(old,6286),2242,'ThirdOverviewFitnessStatsDivider')
rr[line]['data']['m_RuleIndex']=old[6286]['data']['m_RuleIndex']
override(rr[line]['data'],[prop(131087,px(1)),prop(131096,px(1)),prop(131094,px(1)),
    prop(131093,px(3)),prop(131090,px(3)),prop(131105,pct(100)),prop(131084,num(0)),prop(131085,num(0))])
rr[2242]['data']['m_Children']=[{'rid':1186},{'rid':6286},{'rid':2986},{'rid':line},{'rid':6304}]
# Only the scroll wrapper's serialized type and new separator are changed.
for i,r in old.items():
    if i in rr and i!=left_sd and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('unexpected binding change',i)
save(W,PAGE,doc,STYLE,sheet)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
    for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report={'installed':False,'runtime_verified':False,'third_only':True,
    'left_bounded_no_scroll':True,'tactics_removed':True,'radar_beside_bans':True,
    'bottom_right_report_fitness_stats_full_width':True,'section_separators':True,
    'native_chart_stats_bans_bindings_preserved':True,
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
print(json.dumps({'installed':True,'output':str(OUT),'left_scroll_removed':True,'radar_relocated':True}))

