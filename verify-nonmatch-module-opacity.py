from pathlib import Path
import json, sys, struct
R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
out = Path(json.loads((R / 'pending-nonmatch-module-opacity.json').read_text('utf8'))['patch'])
tx = json.loads((out / 'transaction.json').read_text('utf8'))
MARK = 'tf27-nonmatch-module-alpha30'
reports = []
def read_string(raw, pos):
    n = 0; shift = 0
    while True:
        b = raw[pos]; pos += 1; n |= (b & 127) << shift
        if b < 128: break
        shift += 7
    return raw[pos:pos+n].decode(), pos+n
for target, source in tx['sources'].items():
    if not target.endswith('.bundle'): continue
    old = {o.path_id:o for o in UnityPy.load(tx['before'][target]).objects}
    new = {o.path_id:o for o in UnityPy.load(source).objects}
    assert set(old) == set(new)
    count = 0; nodes = 0; sheets = 0
    for pid, ob in new.items():
        if ob.get_raw_data() == old[pid].get_raw_data(): continue
        a = old[pid].read_typetree(); b = ob.read_typetree()
        if 'm_Rules' in a:
            assert b['m_Rules'][:len(a['m_Rules'])] == a['m_Rules']
            for key in a:
                if key == 'm_Rules': continue
                if isinstance(a[key], list): assert b[key][:len(a[key])] == a[key], key
                else: assert a[key] == b[key], key
            if a['m_Name'] == 'AlwaysAppliedStyleSheet':
                for rule in b['m_Rules'][len(a['m_Rules']):]:
                    assert [p['m_Id'] for p in rule['m_Properties']] == [458752]
                    for sel in rule['m_ComplexSelectors']:
                        if any(p['m_Value'] == MARK for s in sel['m_Selectors'] for p in s['m_Parts']):
                            h = rule['m_Properties'][0]['m_Values'][0]
                            assert h['m_ValueType'] == 4 and abs(b['colors'][h['valueIndex']]['a']-.3) < 1e-6
                            count += 1
            sheets += 1
        elif 'inlineSheet' in a:
            ar = {r['rid']:r for r in a['references']['RefIds']}
            br = {r['rid']:r for r in b['references']['RefIds']}
            for key in a:
                if key != 'references': assert a[key] == b[key], key
            for rid, r in ar.items():
                n = br[rid]
                if r == n: continue
                assert r['type'] == n['type']
                for key in r['data']:
                    if key not in ['m_Classes', 'm_Children', 'm_RuleIndex']: assert r['data'][key] == n['data'][key], (a['m_Name'], key)
                nc = n['data'].get('m_Classes', []); oc = r['data'].get('m_Classes', [])
                assert nc[:len(oc)] == oc
                assert all(c.startswith('tf27-module-bg-') for c in nc[len(oc):])
                children = n['data'].get('m_Children', []); oldchildren = r['data'].get('m_Children', [])
                assert children[:len(oldchildren)] == oldchildren
                for child in children[len(oldchildren):]:
                    helper = br[child['rid']]
                    assert helper['data']['m_Parent']['rid'] == rid and child['rid'] not in ar
            for rid in set(br) - set(ar):
                helper = br[rid]
                if helper.get('data', {}).get('m_FullTypeName') != 'SI.Bindable.SIStyleSetter': continue
                sd = br[helper['data']['m_SerializedData']['rid']]['data']
                assert sd['name'] == 'TFNonMatchModuleBackgroundState' and sd['pickingMode'] == 1
                f = sd['BindFunction']; assert f['m_target']['m_guid'] == 'd47d9f6bfe419344692270d5af16c5ef'
                raw = bytes(f['m_inputs']['m_variable']['m_argumentBytes']); assert raw[0] == 5
                vals = []; pos = 1
                for i in range(5):
                    size = struct.unpack_from('<i', raw, pos)[0]; pos += 4
                    block = raw[pos:pos+size]; pos += size
                    kind, p = read_string(block, 0)
                    if kind.endswith('BooleanVisualArg'): vals.append(bool(block[p])); assert p+1 == len(block)
                    else:
                        assert block[p] == 1
                        value, end = read_string(block, p+1); assert end == len(block); vals.append(value)
                assert pos == len(raw)
                assert vals == ['game.IsDuringMatch', 'tf27-match-module-original', MARK, True, False]
                nodes += 1
        else: raise AssertionError(('Unexpected change', a.get('m_Name')))
    reports.append({'target':target, 'background_rules':count, 'state_helpers':nodes, 'stylesheets':sheets})
assert sum(x['background_rules'] for x in reports) == sum(x['state_helpers'] for x in reports)
(out / 'verification.json').write_text(json.dumps({'passed':True, 'runtime_verified':False, 'reports':reports}, indent=2), 'utf8')
print(json.dumps(reports, indent=2))
