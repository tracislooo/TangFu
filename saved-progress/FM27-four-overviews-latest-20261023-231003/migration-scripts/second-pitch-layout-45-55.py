from pathlib import Path
import ast, copy, json

source = Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix = source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-', 'second-pitch-layout-45-55-')
exec(compile(prefix, 'backup-and-serialization-helpers', 'exec'))
for p in [GAME/W, SKIN/W]: protected[p] = sha(p.read_bytes())
pid, sid = -940000000008000, -940000000008001
doc = objs[G][pid].read_typetree()
rr = refs(doc)
original = copy.deepcopy(rr)
sheet = objs[G][sid].read_typetree()
for i, grow in [(2000,9),(2002,11)]:
    override(rr[i]['data'],[prop(131084,num(grow))])
# The selected-position caption inherited the native vertical-gap class. Reduce its
# margins so the enlarged upper region is used by the pitch rather than blank space.
override(rr[1011]['data'],[prop(131093,px(2)),prop(131090,px(2))])
for i,r in original.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i] == r, ('native binding altered',i)
assert 9/(9+11) == .45 and 11/(9+11) == .55
validate_ui(doc,sheet)
objs[G][pid].save_typetree(doc)
objs[G][sid].save_typetree(sheet)
output = env[G].file.save(packer='lz4')
check = {o.path_id:o for o in UnityPy.load(output).objects}
assert set(check) == set(objs[G])
for i,h in hashes[G].items():
    if i not in [pid,sid]: assert sha(check[i].get_raw_data()) == h, ('unrelated object altered',i)
assert check[pid].read_typetree() == doc and check[sid].read_typetree() == sheet
(OUT/G).write_bytes(output)
report = {'installed':False,'runtime_verified':False,'second_only':True,
    'upper_lower_ratio':[45,55],'section_gap':8,'position_caption_vertical_margins':2,
    'pitch_and_position_points_share_native_aspect_fitter':True,'native_data_and_click_bindings_unchanged':True,
    'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore = ['$ErrorActionPreference = "Stop"']
for p in before:
    tag = 'backup-game' if p.parent == GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items(): assert p.read_bytes() == b
for p,h in protected.items(): assert sha(p.read_bytes()) == h
proc = subprocess.run(['powershell','-NoProfile','-Command',
    'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}))
    sys.exit(0)
try:
    for folder in [GAME,SKIN]:
        (folder/G).write_bytes(output)
        assert (folder/G).read_bytes() == output
    for p,h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p,b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'ratio':[45,55],'bindings_unchanged':True}))
