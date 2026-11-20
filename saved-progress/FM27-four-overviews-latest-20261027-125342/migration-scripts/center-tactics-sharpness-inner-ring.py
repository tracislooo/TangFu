from pathlib import Path
import struct
source = Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig')
exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-', 'tactics-concentric-fitness-rings-'), 'backup-and-helpers', 'exec'))
CELL = -970000000001000
doc = objs[CELL].read_typetree()
rr = refs(doc)
old = copy.deepcopy(rr)
sid = doc['inlineSheet']['m_PathID']
sheet = objs[sid].read_typetree()
targets = []
for i, a in rr.items():
    s = rr.get(a.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {})
    if s.get('name', '').startswith('CombinedSharpnessRing'):
        override(a['data'], [prop(131089, px(41)), prop(131104, px(5))])
        targets.append(i)
assert len(targets) == 102
assert {i for i in old if rr[i] != old[i]} == set(targets)
def value(i, key):
    p = next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == key)
    h = p['m_Values'][0]
    return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
outer = next(i for i, a in rr.items() if rr.get(a.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == 'CombinedConditionRing100')
ox, oy, ow, oh = [value(outer, k)['value'] for k in [131089, 131104, 131105, 131087]]
for i in targets:
    x, y, w, h = [value(i, k)['value'] for k in [131089, 131104, 131105, 131087]]
    assert (x+w/2, y+h/2) == (ox+ow/2, oy+oh/2) == (48, 12)
    assert ox < x and oy < y and x+w < ox+ow and y+h < oy+oh
validate_ui(doc, sheet)
objs[CELL].save_typetree(doc)
objs[sid].save_typetree(sheet)
output = env.file.save(packer='lz4')
check = {o.path_id: o for o in UnityPy.load(output).objects}
assert check.keys() == objs.keys()
for i, h in hashes.items():
    if i not in [CELL, sid]: assert sha(check[i].get_raw_data()) == h, i
assert check[CELL].read_typetree() == doc and check[sid].read_typetree() == sheet
(OUT/W).write_bytes(output)

# Preview the corrected positions with the installed ring textures.
from PIL import Image, ImageDraw, ImageFont
bg = UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle'))
textures = {o.peek_name(): o for o in bg.objects if o.type.name == 'Texture2D' and o.peek_name().startswith('FM27StatusRingCW')}
preview = Image.new('RGBA', (400, 288), (42, 44, 48, 255))
font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 48)
for row, (a, b) in enumerate([(68, 100), (91, 92), (100, 68)]):
    for left, val0 in [(True, a), (False, b)]:
        image = textures[f'FM27StatusRingCW{val0:03}'].read().image.convert('RGBA')
        size = (22 if left else 14)*4
        preview.alpha_composite(image.resize((size, size), Image.Resampling.LANCZOS), ((37 if left else 41)*4, (row*24+(1 if left else 5))*4))
        name = f'Combined{"Condition" if left else "Sharpness"}Percent{val0}'
        textid = next(i for i, r in rr.items() if rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name)
        colour = value(textid, 65536)
        fill = tuple(round(colour[c]*255) for c in ['r','g','b']) + (255,)
        ImageDraw.Draw(preview).text(((32 if left else 64)*4, (row*24+12)*4), f'{val0}%', font=font, fill=fill, anchor='rm' if left else 'lm')
preview.convert('RGB').save(OUT/'preview.png')
restore = ['$ErrorActionPreference = "Stop"', "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer = list(restore)
for p in before:
    tag = 'backup-game' if p.parent == GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/W)+"' -Destination '"+str(p)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(before[p])+"') { throw 'Package changed since preparation.' }")
for p in before: installer.append("Copy-Item -LiteralPath '"+str(OUT/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
(OUT/'install.ps1').write_text('\n'.join(installer), 'utf-8-sig')
report = {'installed':False, 'runtime_verified':False, 'outer_ring':[37,1,22,22], 'inner_ring':[41,5,14,14], 'shared_center':[48,12], 'states_verified':len(targets), 'bindings_text_colours_other_objects_unchanged':True, 'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
for p,b in before.items(): assert p.read_bytes()==b
for p,h in protected.items(): assert sha(p.read_bytes())==h
proc = subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p in before: p.write_bytes(output); assert p.read_bytes()==output
    for p,h in protected.items(): assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'states_verified':len(targets),'shared_center':[48,12]}))
