from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, subprocess, sys

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

config = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(config['bundle_root']), Path(config['skin_packages'])
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
oldwrite = TypeTreeHelper.write_value
helpers = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name == 'write'], type_ignores=[]), '<write-helper>', 'exec'))
TypeTreeHelper.write_value = write
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = R / ('shuffle-draft-current-hover-' + stamp)
out.mkdir()
transactions, audits, protected = [], [], {}

for tag, root in [('game', GAME), ('skin', SKIN)]:
    path = root / W
    before = path.read_bytes()
    env = UnityPy.load(before)
    obs = {o.path_id: o for o in env.objects}
    hashes = {i: sha(o.get_raw_data()) for i, o in obs.items()}
    obj = next(o for o in obs.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'PlayerReportPreviewTooltip')
    doc = obj.read_typetree()
    refs = {r['rid']: r for r in doc['references']['RefIds']}
    tooltip = next(r for r in refs.values() if r.get('data', {}).get('m_FullTypeName') == 'SI.Bindable.Tooltip')
    switch = refs[tooltip['data']['m_Children'][0]['rid']]
    assert switch['data']['m_FullTypeName'] == 'SI.Bindable.BindableSwitchElement'
    branches = [refs[c['rid']] for c in switch['data']['m_Children']]
    fixed = next(r for r in branches if r['data']['m_FullTypeName'] == 'SI.Bindable.BindingRemapper')
    legacy = next(r for r in branches if r['data']['m_FullTypeName'] == 'SI.Bindable.ScalableBindableGridLayoutElement')
    assert not legacy['data']['m_Children'] and len(branches) == 2
    original_fixed = copy.deepcopy(fixed)
    fixed['data']['m_Parent'] = {'rid': tooltip['rid']}
    tooltip['data']['m_Children'] = [{'rid': fixed['rid']}]
    removed = {r['rid'] for r in [switch, legacy]} | {r['data']['m_SerializedData']['rid'] for r in [switch, legacy]}
    doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]
    refs = {r['rid']: r for r in doc['references']['RefIds']}
    seen = set()
    def walk(i):
        assert i not in seen
        seen.add(i)
        v = refs[i]['data']
        sd = v.get('m_SerializedData', {}).get('rid', -2)
        if sd != -2: assert refs[sd]['data']['uxmlAssetId'] == v['m_Id']
        for c in v.get('m_Children', []):
            assert refs[c['rid']]['data']['m_Parent']['rid'] == i
            walk(c['rid'])
    walk(doc['m_VisualTree']['rid'])
    assert all(r['rid'] in seen for r in refs.values() if 'm_Parent' in r.get('data', {}))
    checkfixed = copy.deepcopy(fixed)
    checkfixed['data']['m_Parent'] = original_fixed['data']['m_Parent']
    assert checkfixed == original_fixed
    assert all('FantasyDraftScalableBindableGridLayoutElement' not in str(r) for r in refs.values())
    obj.save_typetree(doc)
    output = env.file.save(packer='lz4')
    saved = {o.path_id: o for o in UnityPy.load(output).objects}
    assert set(saved) == set(obs)
    for i, o in saved.items():
        if i == obj.path_id: assert o.read_typetree() == doc
        else: assert sha(o.get_raw_data()) == hashes[i], (tag, i)

    # Validate the reused VTA and function GUIDs against actual bundle objects and catalog locations.
    catpath = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    cat = cm.Catalog(catpath.read_bytes())
    keys = {k for k, _ in cat.keys() if isinstance(k, str)}
    bundles = {}
    for bn in [W, 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
        e = UnityPy.load(output if bn == W else (root / bn).read_bytes())
        os = {o.path_id: o for o in e.objects}
        meta = next(o.read_typetree() for o in os.values() if o.type.name == 'AssetBundle')
        for key, entry in meta['m_Container']:
            if entry['asset']['m_FileID'] == 0 and entry['asset']['m_PathID'] in os:
                candidate = os[entry['asset']['m_PathID']]
                if candidate.type.name == 'MonoBehaviour':
                    tree = candidate.read_typetree()
                    if 'inlineSheet' in tree or 'm_nodes' in tree:
                        bundles[key] = (bn, candidate)
    verified, pending = {}, [u['path'] for u in doc['m_Usings']]
    while pending:
        guid = pending.pop()
        if not guid or guid in verified: continue
        assert guid in keys, ('Missing catalog GUID', tag, guid)
        locations = [cat.location(l) for l in cat.locations(guid)]
        assert locations
        if guid not in bundles:
            verified[guid] = {'catalog_only_external': True}
            continue
        bn, actual = bundles[guid]
        data = actual.read_typetree()
        typ = 'UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in data else 'SI.VisualScripting.VisualFunction'
        assert any(l['type'][1] == typ and l['internal'] == guid and l['dependencies'] and cat.location(l['dependencies'][0])['internal'].endswith(bn) for l in locations), (tag, guid, bn)
        verified[guid] = {'bundle': bn, 'name': actual.peek_name(), 'path_id': str(actual.path_id), 'type': typ}
        pending.extend(u['path'] for u in data.get('m_Usings', []))
        def functions(v):
            if isinstance(v, dict):
                if 'm_target' in v and isinstance(v['m_target'], dict): pending.append(v['m_target'].get('m_guid', ''))
                for x in v.values(): functions(x)
            elif isinstance(v, list):
                for x in v: functions(x)
        functions(data)
    assert '64033a72b9925c8dad3b08826077c328' in verified
    for n in ['catalog.bin', 'catalog.hash']:
        p = catpath.parent / n
        if p.exists(): protected[str(p)] = sha(p.read_bytes())
    for n in ['ui-backgrounds_assets_common.bundle', 'ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle', 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle', 'ui-tileslayouts_assets_all.bundle', 'ui-styles_assets_default.bundle']:
        p = root / n
        protected[str(p)] = sha(p.read_bytes())
    backup, source = out / ('backup-' + tag) / W, out / tag / W
    backup.parent.mkdir(); source.parent.mkdir()
    backup.write_bytes(before); source.write_bytes(output)
    transactions.append({'target': str(path), 'backup': str(backup), 'source': str(source), 'before': sha(before), 'after': sha(output)})
    audits.append({'target': tag, 'changed_object': str(obj.path_id), 'unchanged_objects': len(obs)-1, 'removed_legacy_refs': sorted(removed), 'catalog_checks': verified})

manifest = {'installed': False, 'runtime_verified': False, 'cause': 'Fantasy Draft selected the legacy scalable grid instead of the existing pinned-5 fixed popup', 'change': 'Reuse the exact current fixed player hover content for Fantasy Draft and standard modes', 'audits': audits, 'protected_sha256': protected}
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(transactions, ensure_ascii=False, indent=2), 'utf8')
python = sys.executable
for name, arg in [('install.ps1', ''), ('restore.ps1', ' --restore')]:
    (out / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + python + "' '" + str(R / 'install-independent-resource-patch.py') + "' $PSScriptRoot" + arg + "\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n", 'utf-8-sig')
print('Prepared:', out)
subprocess.run([python, str(R / 'install-independent-resource-patch.py'), str(out)], check=True)
