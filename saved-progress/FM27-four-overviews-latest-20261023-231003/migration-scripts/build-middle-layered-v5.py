import copy
import json
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
BASE = ROOT / '左侧偏移母队租借并排-v4'
OUT = ROOT / '中间国旗Logo叠层-v5'
SOURCE = ROOT / 'middle-icon-source'
BN = 'report-player-banner-max-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7--4194025542157271532.json'
SN = 'inlineStyle-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7-8045407476604796436.json'
b = json.loads((BASE / BN).read_text(encoding='utf-8'))
s = json.loads((BASE / SN).read_text(encoding='utf-8'))
old_b, old_s = copy.deepcopy(b), copy.deepcopy(s)
refs = {r['rid']: r for r in b['references']['RefIds']}
next_rid = max(refs) + 1
next_id = 1900100000
used_ids = {r['data']['m_Id'] for r in refs.values() if 'm_Id' in r['data']}
IDS = dict(direction=131083, width=131105, height=131087, minwidth=131097,
           grow=131084, shrink=131085, align=131073, self=131074, justify=131088,
           position=131102, left=131089, top=131104, margin=262150, padding=262151, ml=131091)

def clone(source, ids):
    global next_rid, next_id
    mapping = {}
    for rid in ids:
        mapping[rid] = next_rid
        next_rid += 1
    def remap(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == 'rid' and v in mapping:
                    value[k] = mapping[v]
                else:
                    remap(v)
        elif isinstance(value, list):
            for v in value:
                remap(v)
    for rid in ids:
        ref = copy.deepcopy(source[rid])
        remap(ref)
        refs[ref['rid']] = ref
        b['references']['RefIds'].append(ref)
    for rid in ids:
        d = refs[mapping[rid]]['data']
        if 'm_Id' in d:
            while next_id in used_ids:
                next_id += 1
            d['m_Id'] = next_id
            used_ids.add(next_id)
            next_id += 1
            sd = refs[d['m_SerializedData']['rid']]['data']
            sd['uxmlAssetId'] = d['m_Id']
    return mapping

def children(parent, items):
    refs[parent]['data']['m_Children']['Array'] = [{'rid': r} for r in items]
    for rid in items:
        refs[rid]['data']['m_Parent']['rid'] = parent

def container(name):
    m = clone(refs, [1006, 1011])
    rid = m[1006]
    d = refs[rid]['data']
    d['m_Classes']['Array'] = []
    d['m_Children']['Array'] = []
    d['m_RuleIndex'] = -1
    refs[m[1011]]['data']['name'] = name
    return rid

def style(rid, entries, keep=False):
    d = refs[rid]['data']
    props = copy.deepcopy(s['m_Rules']['Array'][d['m_RuleIndex']]['m_Properties']['Array']) if keep and d['m_RuleIndex'] >= 0 else []
    props = [p for p in props if p['m_Id'] not in {IDS[k] for k in entries}]
    for key, (kind, value) in entries.items():
        if kind == 'enum':
            pool, typ = 'strings', 7
        elif kind == 'float':
            pool, typ = 'floats', 2
            value = float(value)
        else:
            pool, typ = 'dimensions', 3
            value = {'unit': 2 if kind == '%' else 1, 'value': float(value)}
        values = s[pool]['Array']
        if value not in values:
            values.append(value)
        props.append({'m_Id': IDS[key], 'm_CustomName': '', 'm_Line': -1,
                      'm_Values': {'Array': [{'m_ValueType': typ, 'valueIndex': values.index(value)}]}})
    d['m_RuleIndex'] = len(s['m_Rules']['Array'])
    s['m_Rules']['Array'].append({'m_ComplexSelectors': {'Array': []}, 'm_Properties': {'Array': props}, 'line': -1})

px = lambda v: ('px', v)
pc = lambda v: ('%', v)
num = lambda v: ('float', v)
en = lambda v: ('enum', v)
def named(name):
    return next(rid for rid, ref in refs.items()
                if 'm_SerializedData' in ref['data']
                and refs.get(ref['data']['m_SerializedData']['rid'], {}).get('data', {}).get('name') == name)

middle = named('ReportPortraitStatusColumn')
frame = refs[middle]['data']['m_Children']['Array'][0]['rid']
stage = container('ReportPortraitLayerStage')
icons = container('ReportFlagClubBackgroundLayer')

# Reuse the existing person.nation mapping and original large-flag image binding.
flag_mapping = clone(refs, [1069, refs[1069]['data']['m_SerializedData']['rid']])
flag_root = flag_mapping[1069]
flag_doc = json.loads((SOURCE / 'NationFlag_XXLarge.json').read_text(encoding='utf-8'))
flag_refs = {r['rid']: r for r in flag_doc['references']['RefIds']}
flag_copy = clone(flag_refs, [1009, flag_refs[1009]['data']['m_SerializedData']['rid']])
flag_image = flag_copy[1009]

# Reuse the existing club selector, including its active-club fallback behavior.
club_mapping = clone(refs, [1069, refs[1069]['data']['m_SerializedData']['rid']])
club_root = club_mapping[1069]
club_sd = refs[refs[club_root]['data']['m_SerializedData']['rid']]['data']
club_sd['Mappings']['Array'] = [{'m_serialisedType': 0, 'from': 'club',
                                'to': {'m_path': 'teamtodisplay.ClubForObjectLookupData'},
                                'type': {'id': 1145176067}}]
club_doc = json.loads((SOURCE / 'ClubIcon.json').read_text(encoding='utf-8'))
club_refs = {r['rid']: r for r in club_doc['references']['RefIds']}
club_copy = clone(club_refs, [1002, club_refs[1002]['data']['m_SerializedData']['rid'],
                              1009, club_refs[1009]['data']['m_SerializedData']['rid']])
club_setter, club_image = club_copy[1002], club_copy[1009]

children(middle, [stage, 1007])
children(stage, [icons, frame])  # Last sibling paints above the common icon layer.
children(icons, [flag_root, club_root])
children(flag_root, [flag_image])
children(club_root, [club_setter])
children(club_setter, [club_image])

style(stage, dict(position=en('relative'), width=px(450), height=px(200),
                  grow=num(0), shrink=num(0), self=en('center'), margin=px(0), padding=px(0)))
style(icons, dict(position=en('absolute'), left=px(0), top=px(25), direction=en('row'),
                  width=px(450), height=px(150), align=en('center'),
                  margin=px(0), padding=px(0)))
square = dict(width=px(150), height=px(150), minwidth=px(0), grow=num(0), shrink=num(0),
              align=en('center'), justify=en('center'), margin=px(0), padding=px(0))
for rid in [flag_root, flag_image, club_root, club_image]:
    refs[rid]['data']['m_Classes']['Array'] = []
    style(rid, square)
style(club_root, dict(ml=px(150)), keep=True)
style(club_setter, dict(width=pc(100), height=pc(100), margin=px(0), padding=px(0)))
style(frame, dict(position=en('absolute'), left=px(125), top=px(0)), keep=True)
for rid in [flag_image, club_image]:
    sd = refs[refs[rid]['data']['m_SerializedData']['rid']]['data']
    sd['ScaleMode'] = 2
    sd['ScaleMode_UxmlAttributeFlags'] = 1
    sd['scaleMode'] = 2
    sd['scaleMode_UxmlAttributeFlags'] = 1

# Prove that every existing element except the middle container and portrait frame is identical.
for old in old_b['references']['RefIds']:
    if old['rid'] not in [middle, frame]:
        assert refs[old['rid']] == old, old['rid']
assert s['m_Rules']['Array'][:len(old_s['m_Rules']['Array'])] == old_s['m_Rules']['Array']
assert b['m_Usings'] == old_b['m_Usings'] and s['assets'] == old_s['assets']
assert len(refs) == len(b['references']['RefIds'])
ids = []
for rid, ref in refs.items():
    d = ref['data']
    if 'm_Id' not in d:
        continue
    ids.append(d['m_Id'])
    for child in d.get('m_Children', {}).get('Array', []):
        assert refs[child['rid']]['data']['m_Parent']['rid'] == rid
    if d['m_Parent']['rid'] >= 0:
        assert {'rid': rid} in refs[d['m_Parent']['rid']]['data']['m_Children']['Array']
    if 'm_RuleIndex' in d:
        assert -1 <= d['m_RuleIndex'] < len(s['m_Rules']['Array'])
    serial = d.get('m_SerializedData', {}).get('rid', -2)
    if serial >= 0:
        assert refs[serial]['data']['uxmlAssetId'] == d['m_Id']
assert len(ids) == len(set(ids))
seen = set()
def walk(rid):
    assert rid not in seen
    seen.add(rid)
    for child in refs[rid]['data'].get('m_Children', {}).get('Array', []):
        walk(child['rid'])
walk(b['m_VisualTree']['rid'])
assert seen == {rid for rid, ref in refs.items() if 'm_Id' in ref['data']}
OUT.mkdir(exist_ok=True)
for name, doc in [(BN, b), (SN, s)]:
    (OUT / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
readme = '''中间区域国旗/俱乐部Logo叠层 v5（基于v4，仅修改中间部分）。

仅需导入global bundle的两份JSON：
report-player-banner-max Path ID -4194025542157271532
inlineStyle Path ID 8045407476604796436

国旗在左、俱乐部Logo在右，同层，各占150×150px区域；保持图片比例。
两个区域边缘之间间隔150px，整行总宽450px。
头像保持200×200px，居中叠在图标层上方，两边各覆盖标志区域25px。
状态标记仍在头像下方。国旗使用person.nation，Logo沿用teamtodisplay及原俱乐部图片绑定。
不修改共享国旗/俱乐部图片模板，不新增Externals。

左侧右80px/下30px、母队与租借队并排、透明背景、右侧布局、栏目高度均保持v4设置。
已逐条比较所有原有引用：仅中间容器的子节点和头像框的父节点/定位样式变化。
原有样式规则完整保留，新增规则只用于中间区域。
若已经导入v4，只替换本包两份JSON即可；gameworld及俱乐部模板不需重新导入。
原始bundle未覆盖。实际图片加载和游戏内显示仍需导入后确认。
'''
(OUT / '导入说明.txt').write_text(readme, encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
print('Validated: middle-only changes; 150px squares; 150px gap; foreground portrait; two-file patch.')
