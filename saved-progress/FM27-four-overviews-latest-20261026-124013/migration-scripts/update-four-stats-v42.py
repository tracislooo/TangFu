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
WIN = AA / 'StandaloneWindows64'
N = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
BG = WIN / 'ui-backgrounds_assets_common.bundle'
GW = WIN / 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT = R / '下方四项90stats背景与原生标题-V42'
B, S = -4194025542157271532, 8045407476604796436
sha = lambda b: hashlib.sha256(b).hexdigest()
source = (WIN / N).read_bytes()
assert sha(source) == '35b106588ff194c6b48edf5163d7a994d3c5690b96dc5589a2c9df5c9ee9e8e7'
protected_files = {p: sha(p.read_bytes()) for p in [BG, GW, AA / 'catalog.bin', WIN / 'ui-visualfunctions_assets_all.bundle']}

# UnityPy does not handle Unity's null managed-reference sentinel by default.
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

e = UnityPy.load(str(WIN / N))
obs = {o.path_id: o for o in e.objects}
af = obs[B].assets_file
hashes = {i: sha(o.get_raw_data()) for i, o in obs.items()}
doc, sheet = obs[B].read_typetree(), obs[S].read_typetree()
old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
refs = {r['rid']: r for r in doc['references']['RefIds']}
oldrefs = copy.deepcopy(refs)
bundle = next(o for o in obs.values() if o.type.name == 'AssetBundle')
meta = bundle.read_typetree()
old_meta = copy.deepcopy(meta)

native = next(o for o in UnityPy.load(str(GW)).objects if o.path_id == -648337528654704265).read_typetree()
nr = {r['rid']: r for r in native['references']['RefIds']}
bg = {o.path_id: o for o in UnityPy.load(str(BG)).objects}
template = obs[-910000000000003]

def val(pool, typ, value):
    if value not in sheet[pool]:
        sheet[pool].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[pool].index(value)}
def px(v): return val('dimensions', 3, {'unit': 1, 'value': float(v)})
def pct(v): return val('dimensions', 3, {'unit': 2, 'value': float(v)})
def en(v): return val('strings', 7, v)
def prop(k, v): return {'m_Id': k, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [v]}
zero = [prop(262150, px(0)), prop(262151, px(0))]
changed_rules = set()
allowed_refs = set()

def node(name):
    sd = next(r for r in refs.values() if r.get('data', {}).get('name') == name)
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])
def replace_rule(n, ps):
    ri = n['data']['m_RuleIndex']
    sheet['m_Rules'][ri]['m_Properties'] = ps
    changed_rules.add(ri)

specs = [(1188, 1190, 1192, 1370, -910000000000088),
         (1194, 1196, 1198, 1323, -910000000000089),
         (1200, 1202, 1204, 1335, -910000000000090),
         (1206, 1208, 1210, 1409, -910000000000091)]
checks = []
new_ids = []
for index, (cell, title, value, native_sd, pid) in enumerate(specs, 1):
    src = bg[pid]
    td = src.read_typetree()
    assert td['m_Name'] == f'90stats{index:02}'
    assert not td.get('m_StreamData', {}).get('size', 0)
    assert pid not in af.objects
    texture = copy.copy(src)
    texture.path_id = pid
    texture.assets_file = af
    texture.type_id = template.type_id
    texture.serialized_type = template.serialized_type
    texture.set_raw_data(src.get_raw_data())
    af.objects[pid] = texture
    new_ids.append(pid)

    holder = node('ReportStatDiamondFrame' + str(cell))
    outline = node('ReportStatDiamondOutline' + str(cell))
    panel = node('ReportStatTitleBanner' + str(cell))
    hd, pd = holder['data'], panel['data']
    assert pd['m_Parent']['rid'] == cell
    refs[cell]['data']['m_Children'].remove({'rid': panel['rid']})
    hd['m_Children'].append({'rid': panel['rid']})
    pd['m_Parent'] = {'rid': holder['rid']}
    allowed_refs.update([cell, holder['rid'], panel['rid']])

    # Use the complete source image, without the old rotated border or artificial plaque.
    replace_rule(outline, zero + [prop(131102, en('absolute')), prop(131089, px(0)),
        prop(131104, px(0)), prop(131105, pct(100)), prop(131087, pct(100)),
        prop(458753, val('assets', 6, {'m_FileID': 0, 'm_PathID': pid})),
        prop(262153, en('scale-to-fit'))])
    replace_rule(panel, zero + [prop(131102, en('absolute')), prop(131089, pct(12)),
        prop(131104, pct(71)), prop(131105, pct(76)), prop(131087, pct(18))])
    tri = refs[title]['data']['m_RuleIndex']
    for p in sheet['m_Rules'][tri]['m_Properties']:
        if p['m_Id'] == 65537:
            p['m_Values'] = [px(5)]
    changed_rules.add(tri)

    tsid = refs[title]['data']['m_SerializedData']['rid']
    tsd, nsd = refs[tsid]['data'], nr[native_sd]['data']
    assert refs[tsid]['type'] == nr[native_sd]['type']
    for k in ['text', 'text_UxmlAttributeFlags', 'DebugDisplay', 'DebugDisplay_UxmlAttributeFlags',
              'TextBinding', 'TextBinding_UxmlAttributeFlags']:
        tsd[k] = copy.deepcopy(nsd[k])
    allowed_refs.add(tsid)
    assert tsd['text'] == '' and tsd['text_UxmlAttributeFlags'] == 0
    assert tsd['TextBinding'] == nsd['TextBinding']
    args = bytes(nsd['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    translation_id = struct.unpack('<i', args[-6:-2])[0]
    checks.append({'background': td['m_Name'], 'texture_path_id': pid, 'texture_sha256': sha(src.get_raw_data()),
        'native_title': nsd['DebugDisplay'], 'translation_id': translation_id,
        'native_title_serialized_data_rid': native_sd, 'title_serialized_data_rid': tsid,
        'number_serialized_data_rid': refs[value]['data']['m_SerializedData']['rid']})

# Keep each public asset's existing preload span intact, then include the new local textures.
changed_container_indices = []
for i, (_, entry) in enumerate(meta['m_Container']):
    if entry['asset']['m_PathID'] in [B, S]:
        span = copy.deepcopy(old_meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        for pid in new_ids:
            ptr = {'m_FileID': 0, 'm_PathID': pid}
            if ptr not in span:
                span.append(ptr)
        entry['preloadIndex'] = len(meta['m_PreloadTable'])
        entry['preloadSize'] = len(span)
        meta['m_PreloadTable'].extend(span)
        changed_container_indices.append(i)
assert len(changed_container_indices) == 2

# Scope checks: all unrelated managed references, rules, and numeric bindings are preserved.
for i, r in oldrefs.items():
    if i not in allowed_refs:
        assert refs[i] == r, ('unrelated reference changed', i)
for i, rule in enumerate(old_sheet['m_Rules']):
    if i not in changed_rules:
        assert sheet['m_Rules'][i] == rule, ('unrelated style changed', i)
for i in [1193, 1199, 1205, 1211, 1187]:
    assert refs[i] == oldrefs[i]
seen = set()
def visit(i):
    assert i not in seen
    seen.add(i)
    for c in refs[i].get('data', {}).get('m_Children', []):
        assert refs[c['rid']]['data']['m_Parent']['rid'] == i
        visit(c['rid'])
visit(doc['m_VisualTree']['rid'])
assert len(refs) == len(doc['references']['RefIds'])
assert len(refs) == len(oldrefs)

obs[B].save_typetree(doc)
obs[S].save_typetree(sheet)
bundle.save_typetree(meta)
OUT.mkdir(exist_ok=True)
dest = OUT / N
dest.write_bytes(e.file.save(packer='lz4'))

saved = {o.path_id: o for o in UnityPy.load(str(dest)).objects}
assert set(saved) == set(hashes) | set(new_ids)
assert saved[B].read_typetree() == doc
assert saved[S].read_typetree() == sheet
assert saved[bundle.path_id].read_typetree() == meta
for pid in new_ids:
    assert saved[pid].get_raw_data() == bg[pid].get_raw_data()
    assert saved[pid].read_typetree() == bg[pid].read_typetree()
for i, h in hashes.items():
    if i not in [B, S, bundle.path_id]:
        assert sha(saved[i].get_raw_data()) == h, ('unrelated asset changed', i)
assert (WIN / N).read_bytes() == source
for p, h in protected_files.items():
    assert sha(p.read_bytes()) == h, p

(OUT / '回退').mkdir(exist_ok=True)
(OUT / '回退' / N).write_bytes(source)
m = {'version': 42, 'source_sha256': sha(source), 'sha256': sha(dest.read_bytes()),
     'modules': checks, 'badge_size_px': 50, 'native_stat_values_unchanged': True,
     'native_competition_remapper_unchanged': True, 'unchanged_assets_verified': len(hashes) - 3,
     'new_texture_count': 4, 'changed_rule_ids': sorted(changed_rules),
     'catalog_sha256': protected_files[AA / 'catalog.bin'],
     'source_backgrounds_sha256': protected_files[BG], 'backgrounds_unchanged': True,
     'game_runtime_verified': False, 'installed': False}
(OUT / '修改记录.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf8')
(OUT / 'report-player-banner-max.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf8')
(OUT / 'inlineStyle.json').write_text(json.dumps(sheet, ensure_ascii=False, indent=2), encoding='utf8')
for rollback in [False, True]:
    src = '回退/' + N if rollback else N
    expected = m['sha256'] if rollback else m['source_sha256']
    script = f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{WIN / N}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
Write-Host 'Complete.'
'''
    (OUT / ('回退.ps1' if rollback else '安装.ps1')).write_text(script, encoding='utf-8-sig')
(OUT / '说明.txt').write_text(
    'V42：下方四个模块依次使用当前游戏 backgrounds bundle 中的 90stats01、90stats02、90stats03、90stats04。\n'
    '原图纹理无损复制到 global，使用本地图片引用并补全预加载；无需覆盖 backgrounds 或 catalog。\n'
    '四个标题恢复 PlayerReportSeasonStatsBlock 中的原生 TextBinding 和 TranslationID：22725、22729、22733、22738。\n'
    '分别为每90分钟预期进球、每90分钟预期助攻、每90分钟成功传球、每场成功抢断；名称由游戏当前语言提供。\n'
    '数值绑定和比赛/赛季统计来源保持不变，其他七项徽章、右侧管理模块及50px紧凑布局沿用V41。\n'
    '退出游戏后运行安装.ps1。回退.ps1恢复V41。已完成保存后重读与数据对比，游戏内显示与切换语言仍需实测。',
    encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():
            z.write(f, f.relative_to(OUT))
print(json.dumps(m, ensure_ascii=False))
