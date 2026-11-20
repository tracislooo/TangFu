import copy
import json
import zipfile
from pathlib import Path

BASE = Path('G:/Doc/FM Skin Builder/skins/tf27-01')
OUT = BASE / 'edited/PlayerReportHeader-reference-layout'
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
           display=131081, fontsize=65537)

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
club = container('ReportClubNationColumn')
stats = container('ReportValueAbilityColumn')

children(bm, left, [1006])
children(bm, club, [1007, 1016, 1018])
children(bm, stats, [1020, 1022])
# Keep divider assets in the hierarchy but remove their former horizontal spacing.
children(bm, 1008, [club, stats, 1015, 1017, 1019, 1021])
children(bm, 1004, [left, frame, 1008])

side = dict(grow=num(1), shrink=num(1), basis=px(0), minwidth=px(0),
            self=en('stretch'), margin=px(0), padding=px(0))
B.apply(bm, 1004, dict(direction=en('row'), align=en('stretch'), width=pc(100),
                      minwidth=px(0), minheight=px(260), margin=px(0), padding=px(0)))
B.apply(bm, left, dict(side, direction=en('column'), justify=en('center'), pr=px(16)))
B.apply(bm, 1008, dict(side, direction=en('row'), align=en('stretch'), pl=px(16)))

for rid in [frame, portrait[1013], portrait[1017]]:
    bm[rid]['data']['m_Classes']['Array'] = [] if rid != portrait[1017] else ['thumbnails-alt-person-picture-player-report']
B.apply(bm, frame, dict(width=px(240), height=px(260), grow=num(0), shrink=num(0),
                       align=en('center'), justify=en('center'), self=en('center'), margin=px(0), padding=px(0)))
for rid in [portrait[1013], portrait[1017]]:
    B.apply(bm, rid, dict(width=pc(100), height=pc(100), minwidth=px(0),
                         align=en('center'), justify=en('center'), margin=px(0), padding=px(0)))

# Identity remains vertically centered on the left.
B.apply(bm, 1006, dict(direction=en('column'), grow=num(0), shrink=num(1), width=pc(100),
                      minwidth=px(0), margin=px(0), padding=px(0)))
for rid in [1010, 1024, 1043]:
    B.apply(bm, rid, dict(minwidth=px(0), width=pc(100)), keep=True)

# Club and nation are stacked; statuses/actions retain their bindings above them.
B.apply(bm, club, dict(direction=en('column'), grow=num(1), shrink=num(1), basis=px(0),
                      minwidth=px(0), justify=en('center'), align=en('stretch'), mr=px(16)))
for rid in [1007, 1016, 1018]:
    B.apply(bm, rid, dict(direction=en('column'), width=pc(100), minwidth=px(0),
                         grow=num(0), shrink=num(1), margin=px(0), mb=px(10), padding=px(0)))

# Price/contract and scouting ratings share a fixed right column and left edge.
B.apply(bm, stats, dict(direction=en('column'), width=px(260), minwidth=px(260),
                       grow=num(0), shrink=num(0), justify=en('center'), align=en('stretch'),
                       margin=px(0), padding=px(0)))
for rid in [1020, 1022]:
    B.apply(bm, rid, dict(direction=en('column'), width=pc(100), minwidth=px(0),
                         grow=num(0), shrink=num(0), self=en('stretch'),
                         align=en('flex-start'), margin=px(0), padding=px(0),
                         mb=px(16 if rid == 1020 else 0)))
for rid in [1037, 1041, 1058]:
    B.apply(bm, rid, dict(width=pc(100), minwidth=px(0), margin=px(0), padding=px(0)), keep=True)
B.apply(bm, 1057, dict(ml=px(0), mr=px(0), self=en('flex-start')), keep=True)
B.apply(bm, 1083, dict(ml=px(0), mr=px(0)), keep=True)
for rid in [1015, 1017, 1019, 1021]:
    B.apply(bm, rid, dict(display=en('none'), width=px(0), margin=px(0), padding=px(0)))

# The old left portrait must occupy no width so the new center is the whole header center.
H.apply(hm, 1010, dict(width=px(0), minwidth=px(0), maxwidth=px(0), grow=num(0),
                      shrink=num(0), basis=px(0), margin=px(0), padding=px(0), overflow=en('hidden')))
for rid in [1002, 1004, 1006, 1008, 1011, 1015, 1019, 1023, 1027]:
    H.apply(hm, rid, dict(width=pc(100), minwidth=px(0), ml=px(0), mr=px(0),
                         pl=px(0), pr=px(0)), keep=True)

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
readme = '''导入布局版：背景不变，未新增 FC 图片引用。

global bundle：
report-player-banner-max Path ID -4194025542157271532
inlineStyle Path ID 8045407476604796436

gameworld bundle：
PlayerReportHeader Path ID 5775949770471550939
inlineStyle Path ID -1940069326759809061

将本目录四份 JSON 分别导入对应条目，保存两个 bundle。本版本不需要新增 Externals。
左侧：姓名、号码、位置、国籍、年龄。
中间：独立头像区 240 × 260，两侧等宽可伸缩，保证相对整个头部居中。
右侧：状态/操作、俱乐部、国家队上下排列。
最右：身价/合同在上，原能力潜力评分模块在下，统一 260 像素列宽和左边界。
原左侧头像宽度归零；共享 PersonPicture 文件未修改。

保留所有原有数据绑定。已检查 JSON、引用、父子结构、样式索引及绑定完整性。
尚未导入游戏，实际字号、评分模板内部排布和不同分辨率效果需游戏内确认。
'''
(OUT / '导入说明.txt').write_text(readme, encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
print('Validated four JSON files; original bindings and texture references preserved.')
print(OUT)
