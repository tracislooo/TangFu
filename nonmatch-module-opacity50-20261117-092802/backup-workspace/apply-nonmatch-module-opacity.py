"""Prepare background-only alpha changes gated by native game.IsDuringMatch."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
S = 'ui-styles_assets_default.bundle'
FUNC = 'd47d9f6bfe419344692270d5af16c5ef'
MARK = 'tf27-nonmatch-module-alpha30'
HELPER = 'TFNonMatchModuleBackgroundState'
sha = lambda b: hashlib.sha256(b).hexdigest()
f32 = lambda v: struct.unpack('<f', struct.pack('<f', v))[0]
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
oldwrite = TypeTreeHelper.write_value
for filename, names in [('build-fc-player-hover-layout.py', ['write', 'Styles']),
                        ('fix-primary-navigation-grey-lake-blue.py', ['selector'])]:
    src = ast.parse((R / filename).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names], type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write

def string(s):
    raw = s.encode('utf8'); n = len(raw); prefix = bytearray()
    while n >= 128:
        prefix.append((n & 127) | 128); n >>= 7
    return bytes(prefix) + bytes([n]) + raw

def arguments():
    args = [('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]', b'\1' + string('game.IsDuringMatch')),
            ('SI.VisualScripting.StringVisualArg', b'\1' + string('tf27-match-module-original')),
            ('SI.VisualScripting.StringVisualArg', b'\1' + string(MARK)),
            ('SI.VisualScripting.BooleanVisualArg', b'\1'),
            ('SI.VisualScripting.BooleanVisualArg', b'\0')]
    blocks = [string(kind) + value for kind, value in args]
    return list(bytes([len(blocks)]) + b''.join(struct.pack('<i', len(b)) + b for b in blocks))

def add_rule(sheet, text, prop, priority):
    idx = len(sheet['m_Rules']); sel = selector(text, idx); sel['m_Specificity'] = priority
    sheet['m_Rules'].append({'m_ComplexSelectors':[sel], 'm_Properties':[prop], 'line':-1})

def move_property(prop, source, dest):
    p = copy.deepcopy(prop)
    for h in p['m_Values']:
        if h['m_ValueType'] in poolmap:
            pool = poolmap[h['m_ValueType']]
            dest[pool].append(copy.deepcopy(source[pool][h['valueIndex']]))
            h['valueIndex'] = len(dest[pool]) - 1
    return p

out = R / ('nonmatch-module-opacity30-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
out.mkdir()
before = {}; payloads = {}; protected = {}; changes = []; audit = []
spec = importlib.util.spec_from_file_location('cat', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)

for tag, folder in [('game', GAME), ('skin', SKIN)]:
    catpath = (GAME.parent if tag == 'game' else SKIN) / 'catalog.bin'
    catalog = cm.Catalog(catpath.read_bytes())
    locs = [catalog.location(i) for i in catalog.locations(FUNC)]
    assert any(x['type'][1] == 'SI.VisualScripting.VisualFunction' for x in locs)
    for p in list(folder.glob('*.bundle')) + [catpath, catpath.with_suffix('.hash')]:
        if p.exists(): protected[str(p)] = sha(p.read_bytes())
    raw = (folder / S).read_bytes(); before[folder / S] = raw
    env = UnityPy.load(raw); objects = {o.path_id:o for o in env.objects}
    sobj = next(o for o in objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'AlwaysAppliedStyleSheet')
    sheet = sobj.read_typetree(); original_sheet = copy.deepcopy(sheet)
    definitions = {}
    for rule in sheet['m_Rules']:
        for p in rule['m_Properties']:
            if p.get('m_CustomName'): definitions[p['m_CustomName']] = p
    def resolve(p, seen=None):
        seen = set() if seen is None else seen
        hs = p['m_Values']
        if len(hs) == 1 and hs[0]['m_ValueType'] == 4:
            return copy.deepcopy(sheet['colors'][hs[0]['valueIndex']])
        for h in hs:
            if h['m_ValueType'] == 8:
                name = sheet['strings'][h['valueIndex']]
                if name in definitions and name not in seen:
                    return resolve(definitions[name], seen | {name})
        return None
    candidates = []
    for rule in original_sheet['m_Rules']:
        bg = next((p for p in rule['m_Properties'] if p['m_Id'] == 458752), None)
        if bg is None: continue
        varnames = [sheet['strings'][h['valueIndex']] for h in bg['m_Values'] if h['m_ValueType'] == 8]
        for sel in rule['m_ComplexSelectors']:
            if len(sel['m_Selectors']) != 1: continue
            parts = sel['m_Selectors'][0]['m_Parts']
            if not parts or any(p['m_Type'] != 3 for p in parts): continue
            classes = {p['m_Value'] for p in parts}
            module = any(v.startswith(('--layout-modules-', '--layout-ui-tiles-interaction-surface-')) for v in varnames)
            module |= bool(classes & {'siblock-border', 'layout-tile-interaction-button-background', 'layout-tile-interaction-none', 'layout-tile-scalable-default--background-true', 'border-color-layout-modules-block-border-colour-opaque'})
            if not module: continue
            if any(c.startswith(('buttons-', 'figma-base-', 'base-component-tutorial', 'data-display-', 'control_bar_')) for c in classes): continue
            c = resolve(bg)
            if c and c['a'] > 0: candidates.append((classes, c))
    assert any('layout-tile-interaction-button-background' in cs for cs, _ in candidates)
    donor_env = UnityPy.load(str(folder / G)); donor_objects = {o.path_id:o for o in donor_env.objects}
    donor_doc = next(o.read_typetree() for o in donor_objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'MatchStatsKeyStatsBlock')
    dr = {r['rid']:r for r in donor_doc['references']['RefIds']}
    donor = next(r for r in dr.values() if r.get('data', {}).get('m_FullTypeName') == 'SI.Bindable.SIStyleSetter')
    donor_sd = dr[donor['data']['m_SerializedData']['rid']]
    assert donor_sd['data']['BindFunction']['m_target']['m_guid'] == FUNC
    # Both owning bundles already depend on and preload the native global function.
    function_path = folder / 'ui-visualfunctions_assets_all.bundle'
    if not function_path.exists(): function_path = GAME / function_path.name
    function_env = UnityPy.load(str(function_path))
    function_object = next(o for o in list(function_env.objects) + list(donor_objects.values()) if o.type.name == 'MonoBehaviour' and o.peek_name() == 'BindBoolToAorBUssClass')
    assert function_object.read_typetree()['m_inputs'][5]['m_name'] == 'ApplyToParent'
    total = 0; skipped = []
    bundle_names = [G, W] + [p.name for p in folder.glob('*visualtree*.bundle') if 'fantasydraft' in p.name or 'introvisual' in p.name]
    for bn in bundle_names:
        path = folder / bn; data = path.read_bytes(); before[path] = data
        en = UnityPy.load(data); oo = {o.path_id:o for o in en.objects}; expected = {}
        for ob in list(oo.values()):
            if ob.type.name != 'MonoBehaviour': continue
            tree = ob.read_typetree()
            if 'inlineSheet' not in tree: continue
            rr = {r['rid']:r for r in tree['references']['RefIds']}
            if any(r.get('data', {}).get('name') == HELPER for r in rr.values()): continue
            sid = tree['inlineSheet']['m_PathID']
            if sid not in oo: continue
            sh = oo[sid].read_typetree(); original_sh = copy.deepcopy(sh)
            count = 0
            for node in list(rr.values()):
                a = node.get('data', {}); classes = set(a.get('m_Classes', []))
                matches = [(cs, c) for cs, c in candidates if cs <= classes]
                if not matches: continue
                sd = rr.get(a.get('m_SerializedData', {}).get('rid'), {}).get('data', {})
                if sd.get('name') == 'Card-frame': continue
                holder = node
                if not a.get('m_FullTypeName'):
                    holder = rr.get(a.get('m_Parent', {}).get('rid'))
                    while holder and not holder.get('data', {}).get('m_FullTypeName'):
                        holder = rr.get(holder['data'].get('m_Parent', {}).get('rid'))
                if not holder or 'm_Children' not in holder['data']:
                    skipped.append([tree['m_Name'], node['rid'], sorted(classes)]); continue
                c = copy.deepcopy(matches[-1][1]); inline = None
                ri = a.get('m_RuleIndex', -1)
                if ri >= 0:
                    inline = next((p for p in sh['m_Rules'][ri]['m_Properties'] if p['m_Id'] == 458752), None)
                    if inline:
                        hs = inline['m_Values']
                        if len(hs) == 1 and hs[0]['m_ValueType'] == 4:
                            c = copy.deepcopy(sh['colors'][hs[0]['valueIndex']])
                            if c['a'] == 0: continue
                cls = 'tf27-module-bg-' + hashlib.sha1((bn + str(ob.path_id) + '/' + str(a['m_Id'])).encode()).hexdigest()[:16]
                a['m_Classes'].append(cls)
                if inline:
                    prop = move_property(inline, sh, sheet)
                    add_rule(sheet, '.' + cls, prop, 1000000)
                    newrule = copy.deepcopy(sh['m_Rules'][ri])
                    newrule['m_Properties'] = [p for p in newrule['m_Properties'] if p['m_Id'] != 458752]
                    newrule['m_ComplexSelectors'] = []
                    a['m_RuleIndex'] = len(sh['m_Rules']); sh['m_Rules'].append(newrule)
                c['a'] = f32(.3)
                st = Styles(sheet)
                scoped = '.' + cls + '.' + MARK if holder is node else '.' + MARK + ' .' + cls
                add_rule(sheet, scoped, st.p(458752, st.h(4, c)), 1000010)
                nr = max(rr) + 1; sr = nr + 1
                used = {r.get('data', {}).get('m_Id') for r in rr.values()}
                uid = 1900000000 + count * 2
                while uid in used or uid + 1 in used: uid += 2
                n = copy.deepcopy(donor); n['rid'] = nr
                n['data'].update(m_Id=uid, m_Parent={'rid':holder['rid']}, m_Children=[], m_RuleIndex=-1,
                                 m_Classes=[], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[], m_SerializedData={'rid':sr})
                s = copy.deepcopy(donor_sd); s['rid'] = sr
                s['data'].update(uxmlAssetId=uid, name=HELPER, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
                s['data']['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'] = arguments()
                st = Styles(sh)
                st.edit(n, [st.p(131102, st.en('absolute')), st.p(131105, st.px(0)), st.p(131087, st.px(0))])
                holder['data']['m_Children'].append({'rid':nr})
                tree['references']['RefIds'].extend([n, s]); rr[nr] = n; rr[sr] = s
                count += 1
            if count:
                ob.save_typetree(tree); oo[sid].save_typetree(sh)
                expected[ob.path_id] = tree; expected[sid] = sh
                changes.append({'target':str(path), 'template':tree['m_Name'], 'surfaces':count})
                total += count
        if expected:
            packed = en.file.save(packer='lz4')
            check = {o.path_id:o for o in UnityPy.load(packed).objects}
            old = {o.path_id:o for o in UnityPy.load(data).objects}
            assert set(check) == set(old)
            for pid, o in check.items():
                if pid in expected: assert o.read_typetree() == expected[pid], (bn, pid)
                else: assert o.get_raw_data() == old[pid].get_raw_data(), (bn, pid)
            payloads[path] = packed
    if sheet != original_sheet:
        assert sheet['m_Rules'][:len(original_sheet['m_Rules'])] == original_sheet['m_Rules']
        sobj.save_typetree(sheet); packed = env.file.save(packer='lz4')
        check = {o.path_id:o for o in UnityPy.load(packed).objects}
        old = {o.path_id:o for o in UnityPy.load(raw).objects}
        for pid, o in check.items():
            if pid == sobj.path_id: assert o.read_typetree() == sheet
            else: assert o.get_raw_data() == old[pid].get_raw_data()
        payloads[folder / S] = packed
    audit.append({'target':tag, 'module_backgrounds':total, 'skipped_template_instances':skipped,
                  'native_function_verified':True, 'existing_styles_preserved':True})
    print(tag, total, 'backgrounds;', len(skipped), 'template instances skipped', flush=True)

tx = {'game':str(GAME), 'skin':str(SKIN), 'workspace':str(R), 'sources':{}, 'before':{}}
for p, data in payloads.items():
    assert p.read_bytes() == before[p], ('Concurrent change', p)
    tag = 'game' if p.parent == GAME else 'skin'
    dst = out / tag / p.name; bak = out / ('backup-' + tag) / p.name
    dst.parent.mkdir(exist_ok=True); bak.parent.mkdir(exist_ok=True)
    dst.write_bytes(data); bak.write_bytes(before[p])
    tx['sources'][str(p)] = str(dst); tx['before'][str(p)] = str(bak)
    protected.pop(str(p), None)
m = {'installed':False, 'runtime_verified':False, 'background_alpha':.3, 'condition':'game.IsDuringMatch == false',
     'before_sha256':{str(p):sha(before[p]) for p in payloads}, 'after_sha256':{str(p):sha(b) for p,b in payloads.items()},
     'protected_sha256':protected, 'changes':changes, 'audits':audit, 'desktop_control_used':False}
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
for name, flag in [('install.ps1',''), ('restore.ps1','--restore')]:
    (out / name).write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '" + str(R / 'install-native-background-overrides.py') + "' '" + str(out) + "' " + flag + '\n', 'utf8')
(R / 'pending-nonmatch-module-opacity.json').write_text(json.dumps({'patch':str(out)}, indent=2), 'utf8')
print(out)
