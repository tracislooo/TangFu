import copy
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

R = Path.cwd()
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

AA = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
N = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
TARGET = AA / 'StandaloneWindows64' / N
OUT = R / '数字下移与三行收紧-V43'
B, S = -4194025542157271532, 8045407476604796436
sha = lambda b: hashlib.sha256(b).hexdigest()
source = TARGET.read_bytes()
assert sha(source) == 'ecdb6d81244a60ddfdec385210a3c960dcb7a218649222b22298694e16eefade'
e = UnityPy.load(str(TARGET))
obs = {o.path_id: o for o in e.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in obs.items()}
doc = obs[B].read_typetree()
refs = {r['rid']: r for r in doc['references']['RefIds']}
sheet = obs[S].read_typetree()
old = copy.deepcopy(sheet)
oldwrite = TypeTreeHelper.write_value
def write(v, n, w, c):
    if n.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, c.assetsfile) is None:
        for ch in n.m_Children:
            if ch.m_Type != 'ReferencedObjectData':
                oldwrite(v[ch.m_Name], ch, w, c)
        if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):
            w.align_stream()
        return
    return oldwrite(v, n, w, c)
TypeTreeHelper.write_value = write

def px(v):
    value = {'unit': 1, 'value': struct.unpack('<f', struct.pack('<f', v))[0]}
    if value not in sheet['dimensions']:
        sheet['dimensions'].append(value)
    return {'m_ValueType': 3, 'valueIndex': sheet['dimensions'].index(value)}
def node(name):
    sd = next(r for r in refs.values() if r.get('data', {}).get('name') == name)
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])
changes = {}
def patch_rule(i, values):
    ps = sheet['m_Rules'][i]['m_Properties']
    for key, value in values.items():
        matches = [p for p in ps if p['m_Id'] == key]
        assert len(matches) == 1, (i, key)
        matches[0]['m_Values'] = [value]
    changes.setdefault(i, set()).update(values)
def patch(name, values):
    patch_rule(node(name)['data']['m_RuleIndex'], values)

patch('ReportBadgeGrid4_3_4', {131082: px(208), 131105: px(208), 131097: px(208), 131087: px(150)})
# Three rows share one style; the seven attribute cells share another.
patch('ReportAttributeBadgesFirstRow', {131087: px(50)})
patch('ReportATTBadge', {131091: px(1), 131092: px(1)})
patch_rule(refs[1188]['data']['m_RuleIndex'], {131087: px(50)})
for i in [1192, 1198, 1204, 1210]:
    patch_rule(refs[i]['data']['m_RuleIndex'], {65537: px(11), 131104: px(11.6), 131087: px(20)})

# Only the specified properties of these eight rules may differ.
for i, rule in enumerate(old['m_Rules']):
    if i not in changes:
        assert sheet['m_Rules'][i] == rule
    else:
        expected = copy.deepcopy(sheet['m_Rules'][i])
        for p in expected['m_Properties']:
            if p['m_Id'] in changes[i]:
                p['m_Values'] = next(q['m_Values'] for q in rule['m_Properties'] if q['m_Id'] == p['m_Id'])
        assert expected == rule
for key in old:
    if key not in ['m_Rules', 'dimensions']:
        assert sheet[key] == old[key]
assert sheet['dimensions'][:len(old['dimensions'])] == old['dimensions']

obs[S].save_typetree(sheet)
OUT.mkdir(exist_ok=True)
dest = OUT / N
dest.write_bytes(e.file.save(packer='lz4'))
saved = {o.path_id: o for o in UnityPy.load(str(dest)).objects}
assert saved.keys() == obs.keys()
assert saved[S].read_typetree() == sheet
for i, h in hashes.items():
    if i != S:
        assert sha(saved[i].get_raw_data()) == h, i
assert saved[B].read_typetree() == doc
assert TARGET.read_bytes() == source

(OUT / '回退').mkdir(exist_ok=True)
(OUT / '回退' / N).write_bytes(source)
manifest = {'version': 43, 'source_sha256': sha(source), 'sha256': sha(dest.read_bytes()),
    'number_font_size_px': 11, 'previous_number_font_size_px': 14,
    'number_top_px': 11.6, 'number_box_height_px': 20, 'number_center_y_px': 21.6,
    'number_center_down_px': 2.6, 'grid_width_px': 208, 'grid_height_px': 150,
    'badge_size_px': 50, 'row_height_px': 50, 'attribute_badge_horizontal_margin_px': 1,
    'only_inline_style_changed': True, 'unchanged_assets_verified': len(hashes) - 1,
    'all_data_and_translation_bindings_unchanged': True,
    'changed_rule_properties': {str(i): sorted(v) for i, v in changes.items()},
    'installed': False, 'game_runtime_verified': False}
(OUT / '修改记录.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
(OUT / 'inlineStyle.json').write_text(json.dumps(sheet, ensure_ascii=False, indent=2), encoding='utf8')
for rollback in [False, True]:
    src = '回退/' + N if rollback else N
    expected = manifest['sha256'] if rollback else manifest['source_sha256']
    script = f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{TARGET}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{manifest['source_sha256'] if rollback else manifest['sha256']}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
    (OUT / ('回退.ps1' if rollback else '安装.ps1')).write_text(script, encoding='utf-8-sig')
(OUT / '说明.txt').write_text(
    'V43：下方四个统计数字字号14→11，文本框中心从y=19移至y=21.6，对齐50px背景菱形两侧角的水平中线。\n'
    '三行图标整体256×156→208×150；每行52→50px；属性徽章左右边距各2→1px；徽章本身保持50×50。\n'
    '只修改inlineStyle。90stats背景、标题原生翻译引用、所有数值绑定及其余资源保持V42原样。\n'
    '退出游戏后运行安装.ps1；回退.ps1恢复V42。已完成保存后重读与未改资源哈希校验，游戏内效果待实测。',
    encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():
            z.write(f, f.relative_to(OUT))
print(json.dumps(manifest, ensure_ascii=False))
