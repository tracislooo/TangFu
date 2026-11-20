import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
N = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT = R / ('卡面放大10百分比-头像下移10-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {folder / N: (folder / N).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME / N] == before[SKIN / N]
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    (OUT / ('backup-' + tag + '.bundle')).write_bytes(before[folder / N])
env = UnityPy.load(before[GAME / N]); objects = {o.path_id: o for o in env.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
doc = objects[-930000000001001].read_typetree()
refs = {r['rid']: r for r in doc['references']['RefIds']}
sid = doc['inlineSheet']['m_PathID']; sheet = objects[sid].read_typetree(); old = copy.deepcopy(sheet)
def name(r):
    return refs.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name', '')
stage = next(r for r in refs.values() if name(r) == 'ReportPortraitLayerStage')
card = next(r for r in refs.values() if name(r) == 'ReportMiddleCA000Layer')
portrait = next(r for r in refs.values() if name(r) == 'PersonPictureFrame' and r['data']['m_Parent']['rid'] == stage['rid'])
cr = card['data']['m_RuleIndex']; pr = portrait['data']['m_RuleIndex']
for rule, node in [(cr, card), (pr, portrait)]:
    assert [r['rid'] for r in refs.values() if r.get('data', {}).get('m_RuleIndex') == rule] == [node['rid']]
def get(rule, pid):
    p = next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == pid)
    assert len(p['m_Values']) == 1 and p['m_Values'][0]['m_ValueType'] == 3
    d = sheet['dimensions'][p['m_Values'][0]['valueIndex']]
    assert d['unit'] == 1
    return d['value']
def set_px(rule, pid, value):
    p = next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == pid)
    sheet['dimensions'].append({'unit': 1, 'value': float(value)})
    p['m_Values'] = [{'m_ValueType': 3, 'valueIndex': len(sheet['dimensions']) - 1}]
w, h, left, top = [get(cr, p) for p in [131105, 131087, 131089, 131104]]
assert w == h == 260
new_w, new_h = round(w * 1.1, 6), round(h * 1.1, 6)
new_left, new_top = left + (w - new_w) / 2, top + (h - new_h) / 2
for pid, value in [(131105, new_w), (131087, new_h), (131089, new_left), (131104, new_top)]:
    set_px(cr, pid, value)
portrait_top = get(pr, 131104)
set_px(pr, 131104, portrait_top + 10)
assert get(cr, 131089) + get(cr, 131105) / 2 == left + w / 2
assert get(cr, 131104) + get(cr, 131087) / 2 == top + h / 2
assert get(pr, 131105) == get(pr, 131087) == 160
assert get(pr, 131104) - portrait_top == 10
assert {i for i, (a, b) in enumerate(zip(old['m_Rules'], sheet['m_Rules'])) if a != b} == {cr, pr}
for key in sheet:
    if key not in ['m_Rules', 'dimensions']: assert sheet[key] == old[key]
objects[sid].save_typetree(sheet)
data = env.file.save(packer='lz4'); (OUT / N).write_bytes(data)
saved = {o.path_id: o for o in UnityPy.load(data).objects}
assert set(saved) == set(objects)
for i, hsh in hashes.items():
    if i == sid: assert saved[i].read_typetree() == sheet
    else: assert sha(saved[i].get_raw_data()) == hsh, ('Unrelated asset changed', i)
for path, original in before.items(): assert path.read_bytes() == original
try:
    for path in before:
        path.write_bytes(data); assert path.read_bytes() == data
except Exception:
    for path, original in before.items(): path.write_bytes(original)
    raise
report = {'installed': True, 'runtime_verified': False, 'card_size': [new_w, new_h],
          'card_position': [new_left, new_top], 'card_center_preserved': True,
          'portrait_top_before': portrait_top, 'portrait_top_after': portrait_top + 10,
          'portrait_size': [160, 160], 'changed_style_asset': sid,
          'stats_and_texture_assets_unchanged': True,
          'unrelated_objects_verified': len(hashes) - 1,
          'before_sha256': {str(p): sha(b) for p, b in before.items()}, 'after_sha256': sha(data)}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), **report}, ensure_ascii=False, indent=2))
