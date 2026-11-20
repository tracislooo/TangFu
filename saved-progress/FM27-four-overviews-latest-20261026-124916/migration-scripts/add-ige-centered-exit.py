import ast, copy, datetime, hashlib, json, sys, struct
from pathlib import Path
R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GN = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {p / WN: (p / WN).read_bytes() for p in [GAME, SKIN]}
assert len({sha(b) for b in before.values()}) == 1
env = UnityPy.load(before[GAME / WN]); objects = {o.path_id: o for o in env.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
pid = -7201274251439515232
doc = objects[pid].read_typetree(); original = copy.deepcopy(doc)
assert doc['m_Name'] == 'IGEEditDetailsBlock'
sid = doc['inlineSheet']['m_PathID']; sheet = objects[sid].read_typetree()
rr = {r['rid']: r for r in doc['references']['RefIds']}
ge = UnityPy.load(str(GAME / GN))
donor = next(o for o in ge.objects if o.type.name == 'MonoBehaviour' and o.peek_name() == 'buttons-controls-back-default').read_typetree()
dr = {r['rid']: r for r in donor['references']['RefIds']}
oldwrite = TypeTreeHelper.write_value
src = ast.parse((R / 'redesign-card-top-info-foot.py').read_text('utf8'))
names = {'write', 'val', 'px', 'en', 'num', 'color', 'prop', 'rule', 'override'}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[]), '<helpers>', 'exec'))
TypeTreeHelper.write_value = write
n = max(rr) + 1; eid = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
button = copy.deepcopy(dr[1006]); sd = copy.deepcopy(dr[1009])
button['rid'] = n; sd['rid'] = n + 1
button['data'].update(m_Id=eid, m_Parent={'rid': 1005}, m_Children=[], m_SerializedData={'rid': n + 1}, m_RuleIndex=-1,
    m_Classes=['buttons-controls-pc-default--active-true'], m_Properties=[])
sd['data'].update(uxmlAssetId=eid, name='IGEExitBackButton', name_UxmlAttributeFlags=1,
    text='X  退出 Exit', text_UxmlAttributeFlags=1, pickingMode=0, pickingMode_UxmlAttributeFlags=1,
    InputActionRef={'m_inputActionAsset': {'m_AssetGUID': '', 'm_SubObjectName': '', 'm_SubObjectType': ''}, 'm_actionID': ''},
    InputActionRef_UxmlAttributeFlags=1)
override(button['data'], [prop(131102, en('absolute')), prop(131089, val(3, {'unit': 2, 'value': 50.0})),
    prop(131091, px(-85)), prop(131104, px(0)), prop(131105, px(170)), prop(131087, px(36)),
    prop(131096, px(36)), prop(131094, px(36)), prop(131084, num(0)), prop(131085, num(0)),
    prop(131099, px(12)), prop(131100, px(12)), prop(65537, px(16)), prop(65543, en('bold')),
    prop(65536, color(255,255,255)), prop(65546, en('middle-center')), prop(65552, en('nowrap')),
    prop(458752, color(105,27,185)), prop(262147, px(5)), prop(262148, px(1)), prop(262146, color(185,132,238))])
rr[1005]['data']['m_Children'].append({'rid': n})
doc['references']['RefIds'].extend([button, sd])
assert sd['data']['Events'] == dr[1009]['data']['Events']
assert not sd['data']['InputActionRef']['m_actionID']
for r in original['references']['RefIds']:
    actual = copy.deepcopy(rr[r['rid']])
    if r['rid'] == 1005: actual['data']['m_Children'] = r['data']['m_Children']
    assert actual == r
seen = set()
allrefs = {r['rid']: r for r in doc['references']['RefIds']}
def visit(i):
    assert i not in seen; seen.add(i)
    for c in allrefs[i].get('data', {}).get('m_Children', []):
        assert allrefs[c['rid']]['data']['m_Parent']['rid'] == i
        visit(c['rid'])
visit(doc['m_VisualTree']['rid'])
objects[pid].save_typetree(doc); objects[sid].save_typetree(sheet)
output = env.file.save(packer='lz4')
for o in UnityPy.load(output).objects:
    if o.path_id in [pid, sid]: assert o.read_typetree() == {pid:doc, sid:sheet}[o.path_id]
    else: assert sha(o.get_raw_data()) == hashes[o.path_id]
out = R / ('ige-centered-exit-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    (out / ('backup-' + tag)).mkdir(); (out / ('backup-' + tag) / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
for p,b in before.items(): assert p.read_bytes() == b
try:
    for p in before: p.write_bytes(output); assert p.read_bytes() == output
except Exception:
    for p,b in before.items(): p.write_bytes(b)
    raise
report = {'installed':True, 'runtime_verified':False, 'asset':doc['m_Name'], 'button':'X  退出 Exit',
    'width':170, 'height':36, 'top':0, 'left':'50% minus 85px', 'native_back_event_preserved':True,
    'original_records_preserved':True, 'unrelated_objects_unchanged':len(objects)-2,
    'before_sha256':sha(before[GAME/WN]), 'after_sha256':sha(output)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore = ["$ErrorActionPreference = 'Stop'"]
for tag,folder in [('game',GAME),('skin',SKIN)]:
    restore.append("Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'backup-"+tag+"/"+WN+"') -Destination '"+str(folder/WN)+"' -Force")
(out/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
print(str(out)); print(json.dumps(report,ensure_ascii=True,indent=2))
