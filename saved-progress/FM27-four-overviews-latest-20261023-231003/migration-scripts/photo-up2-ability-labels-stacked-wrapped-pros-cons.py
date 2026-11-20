from pathlib import Path
import ast, copy, json, struct

source = Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix = source.split('ROW=-940000000006000;')[0]
prefix = prefix.replace('photo-up3-titled-pros-cons-tactics-thirds-', 'photo-up2-ability-labels-stacked-wrapped-pros-cons-')
exec(compile(prefix, 'existing-backup-and-serialization-helpers', 'exec'))

def serial(rr0, i):
    return rr0[rr0[i]['data']['m_SerializedData']['rid']]

def save(n, pid, doc, sid, sheet):
    validate_ui(doc, sheet)
    objs[n][pid].save_typetree(doc)
    objs[n][sid].save_typetree(sheet)
    changed[n][pid] = doc
    changed[n][sid] = sheet

def style_value(i, key):
    props = sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']
    v = next(p for p in props if p['m_Id'] == key)['m_Values'][0]
    return sheet[poolmap[v['m_ValueType']]][v['valueIndex']]

def gray():
    f = struct.unpack('<f', struct.pack('<f', 160 / 255))[0]
    return val(4, {'r': f, 'g': f, 'b': f, 'a': 1.0})

# Keep all native list bindings, headings, icon templates and tooltips intact.
pid = -940000000006002
doc = objs[G][pid].read_typetree()
rr = refs(doc)
original = copy.deepcopy(rr)
sid = doc['inlineSheet']['m_PathID']
sheet = objs[G][sid].read_typetree()
for i in [1001, 1002, 1004, 1005]:
    override(rr[i]['data'], [prop(131083, en('column')), prop(131105, pct(100)),
        prop(131082, auto), prop(131084, num(0)), prop(131085, num(0)),
        prop(131087, auto), prop(131096, px(0)), prop(131094, none)])
override(rr[1004]['data'], [prop(131090, px(8))])
for i in [1008, 1011]:
    rr[i]['data']['m_Classes'] = list(dict.fromkeys(rr[i]['data']['m_Classes'] + ['wrapped_list']))
    override(rr[i]['data'], [prop(131087, auto), prop(131096, px(0)),
        prop(131094, none), prop(131084, num(0)), prop(131085, num(0))])
    for k, v in {'Direction': 1, 'ScrollViewMode': 0, 'HorizontalScrollerVisibility': 2,
            'VerticalScrollerVisibility': 2, 'DynamicElements': 1, 'FixedElementSize': 24.0,
            'ClampSizeToPage': 0, 'Truncate': 0}.items():
        sd(i)[k] = v
        sd(i)[k + '_UxmlAttributeFlags'] = 1
    for k in ['Binding', 'RowTemplate', 'RowParamName']:
        assert sd(i)[k] == serial(original, i)['data'][k]
# Pin the native wrapping rule locally to these two lists, including automatic view height.
ri = rule([prop(131083, en('row')), prop(131086, en('wrap')),
    prop(131105, pct(100)), prop(131095, pct(100)), prop(131087, auto),
    prop(131096, px(0)), prop(131094, none), prop(131085, num(0))])
sheet['m_Rules'][ri]['m_ComplexSelectors'] = [{'m_Specificity': 21, 'm_Selectors': [
    {'m_Parts': [{'m_Value': 'wrapped_list', 'm_Type': 3}], 'm_PreviousRelationship': 0},
    {'m_Parts': [{'m_Value': 'virtualised-list__view', 'm_Type': 3}], 'm_PreviousRelationship': 2}], 'ruleIndex': ri}]
save(G, pid, doc, sid, sheet)

audits = []
for pid in [-930000000001001, -930000000001003]:
    doc = objs[W][pid].read_typetree()
    rr = refs(doc)
    original = copy.deepcopy(rr)
    sid = doc['inlineSheet']['m_PathID']
    sheet = objs[W][sid].read_typetree()
    if pid == -930000000001001:
        assert sd(1285)['name'] == 'PersonPictureFrame'
        assert style_value(1285, 131104)['value'] == 31
        override(rr[1285]['data'], [prop(131104, px(29))])
    line = named('RightHidden_OverviewHiddenSummaryLine')
    for suffix, title_name in [('CA', 'RightHidden_OverviewCANativeTitle'), ('PA', 'RightHidden_OverviewPANativeTitle')]:
        group = named('RightHidden' + suffix + 'FullWidthGroup')
        title = named(title_name)
        icon, number = [c['rid'] for c in rr[group]['data']['m_Children']]
        rr[line]['data']['m_Children'].remove({'rid': title})
        rr[title]['data']['m_Parent'] = {'rid': group}
        rr[group]['data']['m_Children'] = [{'rid': icon}, {'rid': title}, {'rid': number}]
        override(rr[group]['data'], [prop(131083, en('row')), prop(131073, en('center'))])
        for i in [icon, title, number]:
            override(rr[i]['data'], [prop(131102, en('relative')), prop(131089, auto),
                prop(131103, auto), prop(131104, auto), prop(131080, auto)])
        override(rr[icon]['data'], [prop(131092, px(4))])
        override(rr[title]['data'], [prop(131081, en('flex')), prop(131105, auto),
            prop(131087, px(30)), prop(131092, px(4)), prop(65537, px(9)), prop(65536, gray())])
        override(rr[number]['data'], [prop(131105, px(0)), prop(131097, px(0)),
            prop(131082, px(0)), prop(131084, num(1)), prop(131085, num(1))])
    row = named('OverviewProsConsTacticsEqualRow')
    left = named('OverviewProsConsReportMapping')
    tactic = named('RightMiddleTacticalEffectiveness')
    override(rr[row]['data'], [prop(131087, auto), prop(131096, px(160)), prop(131094, none)])
    for i in [left, tactic]:
        override(rr[i]['data'], [prop(131084, num(1)), prop(131082, px(0)),
            prop(131105, px(0)), prop(131097, px(0)), prop(131087, auto),
            prop(131096, px(0)), prop(131094, none)])
    inst = named('OverviewTitledProsConsIcons')
    override(rr[inst]['data'], [prop(131084, num(0)), prop(131085, num(0)), prop(131087, auto)])
    # Only layout and parent relationships change; all serialized bindings stay byte-for-byte equivalent.
    for i, r in original.items():
        if 'UxmlSerializedData' in r.get('type', {}).get('class', ''):
            assert rr[i] == r, ('binding changed', pid, i)
    assert style_value(1009, 131105)['value'] == 640
    assert style_value(left, 131084) == style_value(tactic, 131084) == 1
    save(W, pid, doc, sid, sheet)
    audits.append({'page': pid, 'left_fraction': 0.5, 'right_fraction': 0.5,
        'attribute_width': 640, 'binding_serialized_data_unchanged': True})

outputs = {n: e.file.save(packer='lz4') for n, e in env.items()}
for n, b in outputs.items():
    check = {o.path_id: o for o in UnityPy.load(b).objects}
    assert set(check) == set(objs[n])
    for i, h in hashes[n].items():
        if i not in changed[n]:
            assert sha(check[i].get_raw_data()) == h, ('unrelated asset changed', n, i)
    for i, d in changed[n].items():
        assert check[i].read_typetree() == d, ('roundtrip mismatch', n, i)
    (OUT / n).write_bytes(b)
report = {'installed': False, 'runtime_verified': False, 'photo_top_before': 31,
    'photo_top_after': 29, 'titles': 'icon title value', 'pros_cons': 'stacked left half',
    'tactics': 'right half', 'icon_size': 20, 'icon_cell_width': 24,
    'overflow': 'native wrapped_list, no internal scrollbars, automatic height',
    'pages': audits, 'after_sha256': {n: sha(b) for n, b in outputs.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
restore = ['$ErrorActionPreference = "Stop"']
for p in before:
    tag = 'backup-game' if p.parent == GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '" + str(OUT / tag / p.name) + "' -Destination '" + str(p) + "' -Force")
(OUT / 'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
for p, b in before.items():
    assert p.read_bytes() == b
for p, h in protected.items():
    assert sha(p.read_bytes()) == h
proc = subprocess.run(['powershell', '-NoProfile', '-Command',
    'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'output': str(OUT), 'waiting_for_game_exit': True}))
    sys.exit(0)
try:
    for n, b in outputs.items():
        for folder in [GAME, SKIN]:
            (folder / n).write_bytes(b)
            assert (folder / n).read_bytes() == b
    for p, h in protected.items():
        assert sha(p.read_bytes()) == h
except BaseException:
    for p, b in before.items():
        p.write_bytes(b)
    raise
report['installed'] = True
report['installed_verified'] = True
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': True, 'output': str(OUT), 'changed_objects': {n: list(x) for n, x in changed.items()}}))
