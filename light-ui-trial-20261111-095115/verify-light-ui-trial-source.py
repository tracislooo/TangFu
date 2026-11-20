"""Independent structural and catalog QA of the prepared or installed light trial."""
from pathlib import Path
import copy, hashlib, importlib.util, json, re, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

state = json.loads((R / 'current-light-ui-trial.json').read_text('utf8'))
out = Path(state['record'])
m = json.loads((out / 'manifest.json').read_text('utf8'))
assert m['palette']['page'] == 'E7E7E7' and m['palette']['card'] == 'F7F7F5'
tx = json.loads((out / 'transaction.json').read_text('utf8'))
installed = '--installed' in sys.argv
spec = importlib.util.spec_from_file_location('catalog_qa', R / 'catalog-binary-v35.py')
catmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catmod)
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
sha = lambda b: hashlib.sha256(b).hexdigest()
reports = []

def obs(raw):
    return {o.path_id: o for o in UnityPy.load(raw).objects}

def norm_sheet(new, old):
    sanitized = copy.deepcopy(old)
    for i, previous in enumerate(old['m_Rules']):
        actual = new['m_Rules'][i]
        if actual == previous: continue
        removed = [p for p in previous['m_Properties'] if p not in actual['m_Properties']]
        assert not previous['m_ComplexSelectors'] and len(removed) == 1
        p = removed[0]
        assert p['m_Id'] == 458752
        vals = p['m_Values']
        assert len(vals) == 3 and vals[0]['m_ValueType'] == 10
        assert vals[2]['m_ValueType'] == 8 and old['strings'][vals[2]['valueIndex']] == '--layout-modules-block-surface'
        sanitized['m_Rules'][i]['m_Properties'].remove(p)
        assert actual == sanitized['m_Rules'][i]
    assert new['m_Rules'][:len(old['m_Rules'])] == sanitized['m_Rules']
    normalized = copy.deepcopy(new)
    normalized['m_Rules'] = normalized['m_Rules'][:len(old['m_Rules'])]
    for pool in set(poolmap.values()):
        assert new[pool][:len(old[pool])] == old[pool]
        normalized[pool] = normalized[pool][:len(old[pool])]
    assert normalized == sanitized, 'Non-paint stylesheet change'
    for i, rule in enumerate(new['m_Rules']):
        for p in rule['m_Properties']:
            for h in p['m_Values']:
                if h['m_ValueType'] in poolmap:
                    assert 0 <= h['valueIndex'] < len(new[poolmap[h['m_ValueType']]])
        if i < len(old['m_Rules']): continue
        if rule['m_ComplexSelectors']:
            for p in rule['m_Properties']:
                assert p['m_Id'] in [-1, 65536, 458752, 196610, 262146]
                assert len(p['m_Values']) == 1 and p['m_Values'][0]['m_ValueType'] == 4
        for selector in rule['m_ComplexSelectors']:
            assert selector['ruleIndex'] == i
            assert not any(part['m_Value'] == 'root' for s in selector['m_Selectors'] for part in s['m_Parts']), 'Global palette change'

for target, source in tx['sources'].items():
    p = Path(target)
    raw = p.read_bytes() if installed else Path(source).read_bytes()
    assert sha(raw) == m['after_sha256'][target]
    oldraw = Path(tx['before'][target]).read_bytes()
    assert sha(oldraw) == m['before_sha256'][target]
    current, baseline = obs(raw), obs(oldraw)
    assert set(current) == set(baseline)
    modified = {pid for pid in current if current[pid].get_raw_data() != baseline[pid].get_raw_data()}
    assert modified == {int(pid) for pid in m['objects'][target]['changed_ids']}
    docs = []
    for pid in modified:
        a, b = current[pid].read_typetree(), baseline[pid].read_typetree()
        if 'm_Rules' in a:
            norm_sheet(a, b)
            if a['m_Name'] == 'AlwaysAppliedStyleSheet':
                defaults = [p for r in a['m_Rules'] for p in r['m_Properties']
                            if p.get('m_CustomName') == '--layout-modules-block-surface'
                            and any(len(sel['m_Selectors']) == 1 and
                                    sel['m_Selectors'][0]['m_Parts'] == [{'m_Value': 'root', 'm_Type': 4}]
                                    for sel in r['m_ComplexSelectors'])]
                assert defaults
                bg = defaults[-1]['m_Values']
                assert len(bg) == 1 and bg[0]['m_ValueType'] == 4
                native = a['colors'][bg[0]['valueIndex']]
                assert all(abs(native[k] - v / 255) < 1e-6 for k, v in [('r', 38), ('g', 52), ('b', 69)])
            continue
        assert 'inlineSheet' in a
        rr = {r['rid']: r for r in a['references']['RefIds']}
        oldrr = {r['rid']: r for r in b['references']['RefIds']}
        assert set(rr) == set(oldrr)
        normal = copy.deepcopy(a)
        nr = {r['rid']: r for r in normal['references']['RefIds']}
        sh = current[a['inlineSheet']['m_PathID']].read_typetree()
        oldsh = baseline[b['inlineSheet']['m_PathID']].read_typetree()
        marked = 0
        for rid, rec in rr.items():
            aa, bb = rec.get('data', {}), oldrr[rid].get('data', {})
            if 'm_Parent' not in aa: continue
            oldclasses, newclasses = bb.get('m_Classes', []), aa.get('m_Classes', [])
            if oldclasses != newclasses:
                assert newclasses[:-1] == oldclasses and newclasses[-1] in ['tf-light-squad-trial', 'tf-light-dialog-trial', 'tf-light-adaptive-card-surface']
                nr[rid]['data']['m_Classes'] = copy.deepcopy(oldclasses)
                marked += 1
            if aa.get('m_RuleIndex') != bb.get('m_RuleIndex'):
                props = sh['m_Rules'][aa['m_RuleIndex']]['m_Properties']
                oldprops = oldsh['m_Rules'][bb['m_RuleIndex']]['m_Properties'] if bb['m_RuleIndex'] >= 0 else []
                assert [v for v in props if v['m_Id'] != 458752] == [v for v in oldprops if v['m_Id'] != 458752]
                assert len([v for v in props if v['m_Id'] == 458752]) == 1
                nr[rid]['data']['m_RuleIndex'] = bb['m_RuleIndex']
            if 'tf-light-adaptive-card-surface' in newclasses:
                rule = sh['m_Rules'][aa['m_RuleIndex']]
                assert not any(p['m_Id'] == 458752 for p in rule['m_Properties'])
        assert marked in [0, 1]
        assert normal == b, 'Binding, hierarchy, serialized field, or ID changed'
        docs.append((pid, a['m_Name']))
    registrations = []
    if docs:
        meta = next(o.read_typetree() for o in current.values() if o.type.name == 'AssetBundle')
        catpath = Path(tx['game']).parent / 'catalog.bin' if p.parent == Path(tx['game']) else Path(tx['skin']) / 'catalog.bin'
        cat = catmod.Catalog(catpath.read_bytes())
        for pid, name in docs:
            keys = [k for k, v in meta['m_Container'] if v['asset']['m_PathID'] == pid and re.fullmatch('[0-9a-f]{32}', k)]
            assert keys, ('Missing bundle container registration', name)
            for key in keys:
                locations = [cat.location(i) for i in cat.locations(key)]
                matches = [l for l in locations if l['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
                assert matches, ('Missing catalog VTA registration', name, key)
                for l in matches:
                    assert l['internal'] == key and l['dependencies']
                    assert cat.location(l['dependencies'][0])['internal'].replace('\\', '/').endswith('/' + p.name)
                registrations.append({'name': name, 'guid': key, 'type_and_owning_bundle_verified': True})
    reports.append({'target': target, 'changed_objects': len(modified), 'untouched_objects': len(current) - len(modified),
                    'layout_ids_bindings_and_object_inventory_preserved': True, 'catalog': registrations})

def luminance(code):
    vals = [int(code[i:i+2], 16) / 255 for i in [0, 2, 4]]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in vals]
    return sum(c * w for c, w in zip(linear, [.2126, .7152, .0722]))

ratios = []
for ink in ['text', 'secondary']:
    for bg in ['page', 'card', 'control', 'odd', 'hover', 'selected', 'pressed']:
        a, b = sorted([luminance(m['palette'][ink]), luminance(m['palette'][bg])])
        ratio = (b + .05) / (a + .05)
        assert ratio >= 4.5, (ink, bg, ratio)
        ratios.append({'text': ink, 'background': bg, 'ratio': round(ratio, 2)})
result = {'passed': True, 'mode': 'installed' if installed else 'prepared', 'files': reports,
          'contrast': ratios, 'runtime_verified': False}
(out / ('qa-installed.json' if installed else 'qa-prepared.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'passed': True, 'mode': result['mode'], 'files': len(reports),
                  'contrast_minimum': min(r['ratio'] for r in ratios), 'runtime_verified': False}))
