import copy
import json
import zipfile
from pathlib import Path

BASE = Path('G:/Doc/FM Skin Builder/skins/tf27-01')
OUT = Path('G:/Doc/ChatGPT/New project/三等分左侧修正版-v2')
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload'
NAMES = [
    (GLOBAL, 'report-player-banner-max-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7--4194025542157271532.json'),
    (GLOBAL, 'inlineStyle-CAB-db5c0b8ab967d8aedf4e50ce6cea36d7-8045407476604796436.json'),
    (WORLD, 'PlayerReportHeader-CAB-1ab8e16d7264cd64aba00192bdf91ea2-5775949770471550939.json'),
    (WORLD, 'inlineStyle-CAB-1ab8e16d7264cd64aba00192bdf91ea2--1940069326759809061.json'),
]
docs = [json.loads((BASE / 'original' / folder / name).read_text(encoding='utf-8-sig')) for folder, name in NAMES]
original = copy.deepcopy(docs)
b, bs, h, hs = docs
bm = {r['rid']: r for r in b['references']['RefIds']}
hm = {r['rid']: r for r in h['references']['RefIds']}

IDS = dict(direction=131083, grow=131084, shrink=131085, basis=131082,
           width=131105, height=131087, minwidth=131097, maxwidth=131095,
           minheight=131096, align=131073, self=131074, justify=131088,
           ml=131091, mr=131092, mt=131093, mb=131090,
           pl=131099, pr=131100, pt=131101, pb=131098,
           margin=262150, padding=262151, overflow=458768,
           display=131081, fontsize=65537, background=458752)

class Style:
    def __init__(self, doc):
        self.doc = doc

    def val(self, kind, value):
        if kind == 'px':
            pool, typ, value = 'dimensions', 3, {'unit': 1, 'value': float(value)}
        elif kind == '%':
            pool, typ, value = 'dimensions', 3, {'unit': 2, 'value': float(value)}
        elif kind == 'float':
            pool, typ, value = 'floats', 2, float(value)
        elif kind == 'color':
            pool, typ = 'colors', 4
        else:
            pool, typ = 'strings', 7
        a = self.doc[pool]['Array']
        if value not in a:
            a.append(value)
        return {'m_ValueType': typ, 'valueIndex': a.index(value)}

    def apply(self, refs, rid, entries, keep=False):
        d = refs[rid]['data']
        old = d['m_RuleIndex']
        props = copy.deepcopy(self.doc['m_Rules']['Array'][old]['m_Properties']['Array']) if keep and old >= 0 else []
        changed = {IDS[k] for k in entries}
        props = [p for p in props if p['m_Id'] not in changed]
        for k, (kind, v) in entries.items():
            props.append({'m_Id': IDS[k], 'm_CustomName': '', 'm_Line': -1,
                          'm_Values': {'Array': [self.val(kind, v)]}})
        a = self.doc['m_Rules']['Array']
        d['m_RuleIndex'] = len(a)
        a.append({'m_ComplexSelectors': {'Array': []}, 'm_Properties': {'Array': props}, 'line': -1})

B, H = Style(bs), Style(hs)
px = lambda v: ('px', v)
pc = lambda v: ('%', v)
num = lambda v: ('float', v)
en = lambda v: ('enum', v)

def children(refs, rid, items):
    refs[rid]['data']['m_Children']['Array'] = [{'rid': i} for i in items]
    for i in items:
        refs[i]['data']['m_Parent']['rid'] = rid

next_rid = max(bm) + 1
next_id = 1900000100

def clone_group(source, ids):
    global next_rid, next_id
    mapping = {}
    for rid in ids:
        mapping[rid] = next_rid
        next_rid += 1
    def remap(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'rid' and v in mapping:
                    obj[k] = mapping[v]
                else:
                    remap(v)
        elif isinstance(obj, list):
            for v in obj:
                remap(v)
    for rid in ids:
        r = copy.deepcopy(source[rid])
        remap(r)
        b['references']['RefIds'].append(r)
        bm[r['rid']] = r
    for rid in ids:
        d = bm[mapping[rid]]['data']
        if 'm_Id' in d:
            next_id += 1
            d['m_Id'] = next_id
            serial = d['m_SerializedData']['rid']
            if serial >= 0:
                bm[serial]['data']['uxmlAssetId'] = next_id
    return mapping

def container(name):
    m = clone_group(bm, [1006, 1011])
    rid = m[1006]
    bm[rid]['data']['m_Classes']['Array'] = []
    bm[rid]['data']['m_Children']['Array'] = []
    bm[m[1011]]['data']['name'] = name
    return rid

# Preserve the existing portrait template and its data remapper as a local instance.
portrait = clone_group(hm, [1010, 1014, 1013, 1018, 1017, 1022])
frame = portrait[1010]
b['m_Usings']['Array'].append(copy.deepcopy(next(x for x in h['m_Usings']['Array'] if x['alias'] == 'PersonPicture')))
left = container('ReportIdentityColumn')
middle = container('ReportPortraitStatusColumn')
affiliations = container('ReportNationClubRow')

# Keep each binding wrapper with its descendants; only move whole bound groups.
children(bm, left, [1006, affiliations])
children(bm, affiliations, [1018, 1016])
children(bm, middle, [frame, 1007])
children(bm, 1007, [1012])
children(bm, 1008, [1013, 1022, 1020, 1015, 1017, 1019, 1021])
children(bm, 1004, [left, middle, 1008])
# Age follows the position and its tooltip. Hide the former nationality-only row.
children(bm, 1044, [1066, 1067, 1070])
children(bm, 1045, [1069])

# Identical basis/grow/shrink and padding give three equal outer widths.
column = dict(grow=num(1), shrink=num(1), basis=px(0), minwidth=px(0),
              direction=en('column'), self=en('stretch'), align=en('stretch'),
              justify=en('flex-start'), margin=px(0), padding=px(0),
              pl=px(12), pr=px(12), pt=px(2), pb=px(2))
B.apply(bm, 1004, dict(direction=en('row'), align=en('stretch'), width=pc(100),
                      height=px(148), minwidth=px(0), minheight=px(0),
                      margin=px(0), padding=px(0)))
for rid in [left, middle, 1008]:
    B.apply(bm, rid, column)

# Compact identity: name / squad number / ID; position / age.
for rid in [1006, 1010, 1024]:
    B.apply(bm, rid, dict(direction=en('column'), width=pc(100), minwidth=px(0),
                         grow=num(0), shrink=num(0), align=en('stretch'),
                         margin=px(0), padding=px(0)))
B.apply(bm, 1043, dict(direction=en('row'), align=en('center'), height=px(48),
                       minwidth=px(0), width=pc(100), shrink=num(0), mb=px(0)))
B.apply(bm, 1062, dict(fontsize=px(40), grow=num(0), shrink=num(1), minwidth=px(0),
                       mr=px(10), self=en('center')), keep=True)
for rid in [1063, 1064]:
    B.apply(bm, rid, dict(shrink=num(0), self=en('center')))
B.apply(bm, 1044, dict(direction=en('row'), align=en('center'), height=px(24),
                       minwidth=px(0), shrink=num(0), self=en('stretch'), margin=px(0)))
B.apply(bm, 1045, dict(display=en('none'), height=px(0), margin=px(0), padding=px(0)))
B.apply(bm, 1070, dict(shrink=num(0), minwidth=px(0), ml=px(12), self=en('center')), keep=True)
B.apply(bm, 1066, dict(shrink=num(1), minwidth=px(0)), keep=True)

# Nation on the left, club badge/name/playing time on the right, below identity.
B.apply(bm, affiliations, dict(direction=en('row'), align=en('stretch'), width=pc(100),
                               minwidth=px(0), shrink=num(0), minheight=px(72), mt=px(0)))
card = dict(direction=en('column'), align=en('stretch'), justify=en('center'),
            minwidth=px(0), shrink=num(1), margin=px(0), padding=px(0), pl=px(6), pr=px(6))
B.apply(bm, 1018, dict(card, basis=pc(32), grow=num(0),
                       background=('color', {'r': 0.08, 'g': 0.12, 'b': 0.15, 'a': 0.7})))
B.apply(bm, 1016, dict(card, basis=px(0), grow=num(1), ml=px(2),
                       background=('color', {'r': 0.04, 'g': 0.16, 'b': 0.27, 'a': 0.65})))
for rid in [1031, 1034, 1055, 1078]:
    B.apply(bm, rid, dict(minwidth=px(0), width=pc(100), shrink=num(1)), keep=True)
B.apply(bm, 1077, dict(mb=px(0)), keep=True)
B.apply(bm, 1101, dict(mb=px(0)), keep=True)

# A bounded portrait inside the equal middle column; flags sit directly below it.
for rid in [frame, portrait[1013], portrait[1017]]:
    bm[rid]['data']['m_Classes']['Array'] = [] if rid != portrait[1017] else ['thumbnails-alt-person-picture-player-report']
B.apply(bm, frame, dict(width=px(120), maxwidth=pc(100), height=px(120), grow=num(0),
                       shrink=num(0), align=en('center'), justify=en('center'),
                       self=en('center'), margin=px(0), padding=px(0)))
for rid in [portrait[1013], portrait[1017]]:
    B.apply(bm, rid, dict(width=pc(100), height=pc(100), minwidth=px(0),
                         align=en('center'), justify=en('center'), margin=px(0), padding=px(0)))
for rid in [1007, 1012, 1026, 1047]:
    B.apply(bm, rid, dict(direction=en('column'), align=en('center'), justify=en('center'),
                         self=en('center'), minwidth=px(0), grow=num(0), shrink=num(0),
                         margin=px(0), padding=px(0)))
B.apply(bm, 1007, dict(mt=px(0)), keep=True)

# Right: actions, ability/potential, then value and contract.
for rid in [1013, 1022, 1020]:
    B.apply(bm, rid, dict(direction=en('column'), width=pc(100), minwidth=px(0),
                         grow=num(0), shrink=num(0), self=en('stretch'), align=en('flex-start'),
                         margin=px(0), padding=px(0), mb=px(12 if rid != 1020 else 0)))
for rid in [1037, 1041, 1058]:
    B.apply(bm, rid, dict(width=pc(100), minwidth=px(0), margin=px(0), padding=px(0)), keep=True)
B.apply(bm, 1057, dict(ml=px(0), mr=px(0), self=en('flex-start')), keep=True)
B.apply(bm, 1083, dict(ml=px(0), mr=px(0)), keep=True)
for rid in [1015, 1017, 1019, 1021]:
    B.apply(bm, rid, dict(display=en('none'), width=px(0), margin=px(0), padding=px(0)))

# The old left portrait must occupy no width so the new center is the whole header center.
H.apply(hm, 1010, dict(width=px(0), minwidth=px(0), maxwidth=px(0), grow=num(0),
                      shrink=num(0), basis=px(0), margin=px(0), padding=px(0),
                      display=en('none'), overflow=en('hidden')))
for rid in [1002, 1004, 1006, 1008, 1011, 1015, 1019, 1023, 1027]:
    H.apply(hm, rid, dict(width=pc(100), minwidth=px(0), ml=px(0), mr=px(0),
                         pl=px(0), pr=px(0)), keep=True)
H.apply(hm, 1011, dict(grow=num(1), shrink=num(1), basis=px(0)), keep=True)
# Match the established 148px header and align its body at the top.
H.apply(hm, 1008, dict(height=px(148), minheight=px(0), align=en('stretch'),
                      mt=px(0), mb=px(0), pt=px(0), pb=px(0)), keep=True)
H.apply(hm, 1011, dict(height=pc(100), justify=en('flex-start'),
                      mt=px(0), mb=px(0), pt=px(0), pb=px(0)), keep=True)

def validate(tree, sheet):
    refs = {r['rid']: r for r in tree['references']['RefIds']}
    assert len(refs) == len(tree['references']['RefIds'])
    ids = []
    for rid, r in refs.items():
        d = r['data']
        if 'm_Id' not in d:
            continue
        ids.append(d['m_Id'])
        for child in d.get('m_Children', {}).get('Array', []):
            assert refs[child['rid']]['data']['m_Parent']['rid'] == rid
        parent = d['m_Parent']['rid']
        if parent >= 0:
            assert {'rid': rid} in refs[parent]['data']['m_Children']['Array']
        if 'm_RuleIndex' in d:
            assert -1 <= d['m_RuleIndex'] < len(sheet['m_Rules']['Array'])
        sd = d.get('m_SerializedData', {}).get('rid', -2)
        if sd >= 0:
            assert refs[sd]['data']['uxmlAssetId'] == d['m_Id']
    assert len(ids) == len(set(ids))
    for rule in sheet['m_Rules']['Array']:
        for p in rule['m_Properties']['Array']:
            for v in p['m_Values']['Array']:
                pool = {2: 'floats', 3: 'dimensions', 4: 'colors', 6: 'assets', 7: 'strings'}.get(v['m_ValueType'])
                if pool:
                    assert 0 <= v['valueIndex'] < len(sheet[pool]['Array'])

validate(b, bs)
validate(h, hs)
# Check the requested grouping and equal-width settings independently of serialization.
assert [x['rid'] for x in bm[1004]['data']['m_Children']['Array']] == [left, middle, 1008]
assert [x['rid'] for x in bm[affiliations]['data']['m_Children']['Array']] == [1018, 1016]
assert bm[1012]['data']['m_Parent']['rid'] == 1007
assert bm[1013]['data']['m_Parent']['rid'] == 1008
assert bm[1022]['data']['m_Parent']['rid'] == 1008
assert bm[1020]['data']['m_Parent']['rid'] == 1008
assert [x['rid'] for x in bm[1044]['data']['m_Children']['Array']] == [1066, 1067, 1070]
assert [x['rid'] for x in bm[1045]['data']['m_Children']['Array']] == [1069]
rules = bs['m_Rules']['Array']
assert all(rules[bm[rid]['data']['m_RuleIndex']] == rules[bm[left]['data']['m_RuleIndex']]
           for rid in [middle, 1008])
def walk(rid, seen):
    assert rid not in seen, 'Cycle or repeated child in visual hierarchy'
    seen.add(rid)
    for child in bm[rid]['data'].get('m_Children', {}).get('Array', []):
        walk(child['rid'], seen)
seen = set()
walk(b['m_VisualTree']['rid'], seen)
assert seen == {rid for rid, ref in bm.items() if 'm_Id' in ref['data']}
# All original serialized binding data and original template aliases remain byte-for-byte equivalent as JSON values.
for old, new in [(original[0], b), (original[2], h)]:
    refs = {r['rid']: r for r in new['references']['RefIds']}
    for r in old['references']['RefIds']:
        if 'm_Id' not in r['data']:
            assert refs[r['rid']] == r
assert bs['assets'] == original[1]['assets'] and hs['assets'] == original[3]['assets']
OUT.mkdir(parents=True, exist_ok=True)
for (folder, name), doc in zip(NAMES, docs):
    (OUT / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    assert json.loads((OUT / name).read_text(encoding='utf-8')) == doc
readme = '''球员报告头部：三等分左侧修正版 v2。

global bundle：
report-player-banner-max Path ID -4194025542157271532
inlineStyle Path ID 8045407476604796436

gameworld bundle：
PlayerReportHeader Path ID 5775949770471550939
inlineStyle Path ID -1940069326759809061

将本目录四份 JSON 分别导入对应条目，保存两个 bundle。本版本不需要新增 Externals。
整体三个外层区域继续等宽。取消260px最小高度，与原头部148px高度匹配，内容顶部对齐。
左侧第一行：40px 原字体姓名、号码、ID；第二行：位置、年龄/生日。
删除原年龄行前的国旗/国籍显示，原第三行不再占位。
左侧底部：国家队信息在左，俱乐部徽章/名称/队内地位在右；保留现有国家队出场与进球信息。
国家队和俱乐部紧接第二行，去掉上方10px间隔及多余纵向内边距。
国家队保留三行信息，取消行间多余空隙；左侧总高度148px（顶部2+姓名48+位置/年龄24+国家队/俱乐部72+底部2）。
中间：头像调整为120 × 120以适应原头部高度，下方保留原状态标记。
右侧从上到下：原操作按钮、能力/潜力模块、身价及合同信息。
原外层左侧头像隐藏，防止重复头像及左侧占位；共享 PersonPicture 文件未修改。
背景和纹理引用保留，左侧底部新增半透明信息底色。

保留所有原有数据绑定。已检查 JSON、引用、父子结构、样式索引及绑定完整性。
原始文件未覆盖。本包只修改上述四个 JSON，不需要导入其他版本的样式文件。
本次修改针对 report-player-banner-max；小屏/手机的 min 与 mid 横幅模板仍用原布局。
尚未导入游戏。实际字体宽度、共享模板内部排版和分辨率效果需游戏内确认。
'''
(OUT / '导入说明.txt').write_text(readme, encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
print('Validated four JSON files; original bindings and texture references preserved.')
print(OUT)
