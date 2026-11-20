"""Restore screenshot-visible objects verbatim; move them with outer USS only."""
from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
for fn, names in [
    ('build-fc-player-hover-layout.py', {'write', 'Styles'}),
    ('add-two-portrait-hidden-overviews.py', {'refs', 'data', 'named', 'rid_links', 'owned_refs'}),
    ('split-season-radar-two-charts.py', {'graph'}),
    ('add-card-six-ratings.py', {'validate_ui'}),
]:
    tree = ast.parse((R / fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names], type_ignores=[]), fn, 'exec'))
TypeTreeHelper.write_value = write

W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BASE = R / 'test-four-kpis-two-radars-20261115-100951'
radar_only = '--radar-only' in sys.argv
OUT = R / (('test-visible-radar-only-' if radar_only else 'test-visible-modules-outer-only-') + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
location = json.loads((R / 'current-game-location.json').read_text('utf8'))
index = R / 'current-player-overview-test-variant.json'
previous = json.loads(index.read_text('utf8'))
roots = [('game', Path(location['bundle_root'])), ('skin', Path(location['skin_packages']))]
protected = {str(p):sha(p.read_bytes()) for _, root in roots for p in root.glob('*.bundle') if p.name != W}
for tag, root in roots:
    for name in ['catalog.bin', 'catalog.hash']:
        p = (root.parent if tag == 'game' else root) / name
        protected[str(p)] = sha(p.read_bytes())
tx, checks = [], []
restore_ids = [-941100000001050, -941100000001052, -941100000001053]
style_id = -941100000001051
for tag, root in roots:
    print('Preparing ' + tag, flush=True)
    before = (root / W).read_bytes()
    env = UnityPy.load(before)
    obs = {o.path_id:o for o in env.objects}
    oldhashes = {i:sha(o.get_raw_data()) for i,o in obs.items()}
    donor_env = UnityPy.load(str(BASE / tag / W))
    donor = {o.path_id:o for o in donor_env.objects}
    stats = donor[restore_ids[0]].read_typetree()
    rr = refs(stats)
    sheet = donor[style_id].read_typetree()
    original_sheet = copy.deepcopy(sheet)
    st = Styles(sheet)
    column = named(stats, 'WorkingNativeSeasonDataColumn')
    radar = named(stats, 'WorkingSeasonRadarGoalkeeperSwitch')
    # Replace three unique outer rules in place. Never change node/rule indices.
    updates = {
        column: [st.p(131081, st.en('none'))] if radar_only else [st.p(131087, st.px(65))],
        1046: [st.p(131081, st.en('none'))],
        1047: [st.p(131081, st.en('none'))],
    }
    changed_rules = set()
    for node, props in updates.items():
        rule = rr[node]['data']['m_RuleIndex']
        users = [i for i,r in rr.items() if r.get('data', {}).get('m_RuleIndex') == rule]
        assert users == [node], ('Shared rule', rule, users)
        keys = {p['m_Id'] for p in props}
        values = sheet['m_Rules'][rule]['m_Properties']
        sheet['m_Rules'][rule]['m_Properties'] = [p for p in values if p['m_Id'] not in keys] + props
        changed_rules.add(rule)
    assert len(changed_rules) == 3
    assert len(sheet['m_Rules']) == len(original_sheet['m_Rules'])
    for rule, value in enumerate(original_sheet['m_Rules']):
        if rule not in changed_rules:
            assert sheet['m_Rules'][rule] == value
    # All existing value pools are unchanged prefixes, preserving every inner style.
    for key, value in original_sheet.items():
        if key == 'm_Rules': continue
        if key in {'dimensions', 'strings'}:
            assert sheet[key][:len(value)] == value
        else:
            assert sheet[key] == value, key
    assert rr[1048]['data']['m_Children'] == [{'rid':i} for i in [1058,1060,1063,1065]]
    protected_nodes = set()
    for node in [1058,1060,1063,1065,radar]:
        protected_nodes.update(owned_refs(rr,node))
    for node in protected_nodes:
        rule = rr[node].get('data',{}).get('m_RuleIndex',-1)
        assert rule not in changed_rules
        if rule >= 0:
            assert sheet['m_Rules'][rule] == original_sheet['m_Rules'][rule]
    graph(stats)
    validate_ui(stats,sheet)
    for i in restore_ids:
        if radar_only:
            assert obs[i].get_raw_data() == donor[i].get_raw_data(), ('Visible source drifted', i)
        obs[i].set_raw_data(donor[i].get_raw_data())
    obs[style_id].save_typetree(sheet)
    output = env.file.save(packer='lz4')
    reread = {o.path_id:o for o in UnityPy.load(output).objects}
    assert reread.keys() == obs.keys()
    for i in restore_ids:
        assert reread[i].get_raw_data() == donor[i].get_raw_data(), ('Not exact donor', i)
    assert reread[style_id].read_typetree() == sheet
    for i, value in oldhashes.items():
        if i not in restore_ids + [style_id]:
            assert sha(reread[i].get_raw_data()) == value, ('Unrelated object changed', i)
    source, backup = OUT/tag/W, OUT/('backup-'+tag)/W
    source.parent.mkdir(); backup.parent.mkdir()
    source.write_bytes(output); backup.write_bytes(before)
    tx.append(dict(target=str(root/W), source=str(source), backup=str(backup), before=sha(before), after=sha(output)))
    checks.append(dict(
        target=tag, donor=str(BASE/tag/W),
        donor_exact_objects={str(i):sha(donor[i].get_raw_data()) for i in restore_ids},
        internal_ui_bindings_templates_exact=True,
        internal_card_and_radar_styles_exact=True,
        modified_outer_rule_nodes=list(updates), modified_outer_rules=sorted(changed_rules),
        card_row_height=64, card_wrapper_hidden=radar_only,
        card_wrapper_height=0 if radar_only else 65, radar_height_unchanged=159,
        top_stats_row_hidden_with_style_only=True,
        page_and_native_radar_unchanged=True, unrelated_objects_byte_identical=True,
    ))
    print('Verified ' + tag + ': exact working modules; only three outer style rules changed', flush=True)

manifest = json.loads(Path(previous['manifest']).read_text('utf8'))
manifest.update(installed=False, installed_verified=False, runtime_verified=False,
    donor_manifest=str(BASE/'manifest.json'), previous_manifest=previous['manifest'],
    change=('Hide the complete statistics wrapper with outer display:none; retain exact screenshot-visible radar and its internal styles' if radar_only else 'Restore screenshot-visible stats/radar objects byte-for-byte; only outer wrapper height and top-row visibility changed'),
    protected_sha256=protected, checks=checks)
for name, value in [('manifest.json', manifest), ('transaction.json',tx), ('previous-index.json', previous),
                    ('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
(R/'visible-modules-outer-only-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
