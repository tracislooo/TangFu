from pathlib import Path
import ast, copy, json, struct

source = Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix = source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-', 'restore-second-pitch-native-landscape-ratio-')
exec(compile(prefix, 'backup-and-serialization-helpers', 'exec'))
for p in [GAME/W,SKIN/W]: protected[p] = sha(p.read_bytes())
pid,sid = -940000000008000,-940000000008001
doc = objs[G][pid].read_typetree()
rr = refs(doc)
old = copy.deepcopy(rr)
fitter = named('LargePortraitLandscapePitchAspectRatio')
data = sd(fitter)
assert data['AspectMode'] == 2
previous = data['AspectRatio']
assert abs(previous-200/140) < .00001
data['AspectRatio'] = struct.unpack('<f',struct.pack('<f',140/200))[0]
data['AspectRatio_UxmlAttributeFlags'] = 1
for i,r in old.items():
    if i != rr[fitter]['data']['m_SerializedData']['rid']:
        assert rr[i] == r
assert rr[fitter]['data']['m_Children'] == [{'rid':1022},{'rid':1023}]
styles = objs[G][sid].read_typetree()
for i,expected in [(2000,9),(2002,11)]:
    p = next(p for p in styles['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131084)
    assert styles['floats'][p['m_Values'][0]['valueIndex']] == expected
validate_ui(doc,styles)
objs[G][pid].save_typetree(doc)
output = env[G].file.save(packer='lz4')
check = {o.path_id:o for o in UnityPy.load(output).objects}
assert set(check) == set(objs[G])
for i,h in hashes[G].items():
    if i != pid: assert sha(check[i].get_raw_data()) == h, ('unrelated object altered',i)
assert check[pid].read_typetree() == doc
(OUT/G).write_bytes(output)
report = {'installed':False,'runtime_verified':False,'second_only':True,
    'native_pitch_width_height':[200,140],'aspect_parameter_before':previous,
    'aspect_parameter_after':data['AspectRatio'],'upper_lower_ratio':[45,55],
    'pitch_image_and_points_share_same_rectangle':True,'native_data_and_click_bindings_unchanged':True,
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
print(json.dumps({'installed':True,'output':str(OUT),'native_pitch_ratio':[200,140],'layout':[45,55]}))
