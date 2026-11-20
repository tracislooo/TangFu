from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, zlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader

oldwrite = TypeTreeHelper.write_value
tree = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'write'], type_ignores=[]), '<writer>', 'exec'))
TypeTreeHelper.write_value = write
tree = ast.parse((R / 'update-ledger-bundle-crcs.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'crc'], type_ignores=[]), '<crc>', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
cfg = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(cfg['bundle_root']), Path(cfg['skin_packages'])
native = Path(json.loads((R / 'current-game-update-comparison.json').read_text('utf8'))['archive'])
BN = 'ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
PID = 2507475884890392812
sha = lambda data: hashlib.sha256(data).hexdigest()
out = R / ('draft-reference-catalog-repair-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
nativepath, = list(native.rglob(BN))
donor = next(o.read_typetree() for o in UnityPy.load(str(nativepath)).objects if o.path_id == PID)
donorrefs = {r['rid']: r for r in donor['references']['RefIds']}
native_text, = [r for r in donorrefs.values() if r.get('type', {}).get('class') == 'SIText/UxmlSerializedData' and r['data']['uxmlAssetId'] == 749073460]
assert native_text['data']['EnableEmbeddedLinks'] == 0
tx, audits, snapshots, staged = [], [], {}, {}

def stage(path, data, tag):
    before = path.read_bytes()
    snapshots[path] = before
    backup, candidate = out / ('backup-' + tag) / path.name, out / tag / path.name
    backup.parent.mkdir(exist_ok=True)
    candidate.parent.mkdir(exist_ok=True)
    backup.write_bytes(before)
    candidate.write_bytes(data)
    tx.append(dict(target=str(path), backup=str(backup), source=str(candidate), before=sha(before), after=sha(data)))
    staged[path] = data

protected = {str(p): sha(p.read_bytes()) for root in (GAME, SKIN) for p in root.glob('*.bundle')}
names = {BN, 'ui-fonts_assets_fmuniverse.bundle', 'ui-fonts_assets_production.bundle',
         'ui-styles_assets_default.bundle', 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
         'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'}
for tag, root, aa in [('game', GAME, Path(cfg['aa_root'])), ('skin', SKIN, SKIN)]:
    path = root / BN
    raw = path.read_bytes()
    env = UnityPy.load(raw)
    objects = {o.path_id: o for o in env.objects}
    obj = objects[PID]
    doc = obj.read_typetree()
    refs = {r['rid']: r for r in doc['references']['RefIds']}
    fixed = False
    if 1009 not in refs:
        override, = [x for r in refs.values() for x in r.get('data', {}).get('m_SerializedDataOverride', []) if x['m_SerializedData']['rid'] == 1009]
        assert override['m_ElementIdsPath'] == [749073460]
        restored = copy.deepcopy(native_text)
        restored['rid'] = 1009
        original_doc = copy.deepcopy(doc)
        doc['references']['RefIds'].append(restored)
        obj.save_typetree(doc)
        packed = env.file.save(packer='lz4')
        reread = {o.path_id: o for o in UnityPy.load(packed).objects}
        assert reread.keys() == objects.keys()
        for pid, old in objects.items():
            if pid == PID:
                actual = reread[pid].read_typetree()
                assert actual == doc
                actual['references']['RefIds'] = [r for r in actual['references']['RefIds'] if r['rid'] != 1009]
                assert actual == original_doc
            else:
                assert reread[pid].get_raw_data() == old.get_raw_data(), pid
        stage(path, packed, tag)
        fixed = True
    else:
        assert refs[1009]['type']['class'] == 'SIText/UxmlSerializedData'
        assert refs[1009]['data']['uxmlAssetId'] == 749073460
    # Every positive managed reference in this document must resolve.
    ids = {r['rid'] for r in doc['references']['RefIds']}
    def verify(value):
        if isinstance(value, dict):
            if set(value) == {'rid'} and value['rid'] > 0:
                assert value['rid'] in ids, value
            for item in value.values(): verify(item)
        elif isinstance(value, list):
            for item in value: verify(item)
    verify(doc)
    catpath = aa / 'catalog.bin'
    original = catpath.read_bytes()
    cat = cm.Catalog(original)
    locations = {q: cat.location(q) for _, ls in cat.keys() for q, in cat.array(ls, 'I')}
    records = []
    for q, loc in locations.items():
        name = loc['internal'].replace('\\', '/').split('/')[-1]
        if name not in names or not (root / name).is_file() or not loc['type'][1].endswith('IAssetBundleResource'): continue
        bp = root / name
        data = staged.get(bp, bp.read_bytes())
        checksum = crc(data)
        if loc['raw'][5] == cm.NULL:
            assert tag == 'skin'
            continue
        typ, payload = cat.unpack(loc['raw'][5], '2I')
        assert cat.typename(typ)[1].endswith('AssetBundleRequestOptions')
        values = list(cat.unpack(payload, '5I'))
        if values[2:4] == [checksum, len(data)]: continue
        old = values[2:4]
        values[2:4] = [checksum, len(data)]
        # Retain provider-specific fields and replace only CRC and length.
        newpayload = cat.append(struct.pack('<5I', *values))
        extra = cat.append(struct.pack('<2I', typ, newpayload))
        entry = list(loc['raw'])
        entry[5] = extra
        struct.pack_into('<7I', cat.data, q, *entry)
        records.append(dict(bundle=name, previous_crc_size=old, crc=checksum, size=len(data)))
    updated = bytes(cat.data)
    checked = cm.Catalog(updated)
    assert checked.keys() == cm.Catalog(original).keys()
    for q, loc in locations.items():
        after = checked.location(q)
        assert all(after[k] == loc[k] for k in ('internal', 'primary', 'provider', 'dependencies', 'type'))
        name = loc['internal'].replace('\\', '/').split('/')[-1]
        if name in names and (root / name).is_file() and loc['type'][1].endswith('IAssetBundleResource') and loc['raw'][5] != cm.NULL:
            bp = root / name
            data = staged.get(bp, bp.read_bytes())
            _, p = checked.unpack(after['raw'][5], '2I')
            assert checked.unpack(p, '5I')[2:4] == (crc(data), len(data))
        else:
            assert after == loc
    if updated != original:
        stage(catpath, updated, tag)
        stage(aa / 'catalog.hash', hashlib.md5(updated).hexdigest().encode('ascii'), tag)
    audits.append(dict(target=tag, reference_restored=fixed, crc_updates=records, all_template_references_resolve=True))
for p in staged: protected.pop(str(p), None)
assert all(p.read_bytes() == before for p, before in snapshots.items())
assert all(sha(Path(p).read_bytes()) == h for p, h in protected.items())
manifest = dict(installed=False, runtime_verified=False, protected_sha256=protected, audits=audits,
                native_source=str(nativepath), template='ShuffleDraft_DraftPositionTeamNames', path_id=PID)
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(out / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
for name, arg in [('install.ps1', ''), ('restore.ps1', ' --restore')]:
    (out / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable + "' '" + str(R / 'install-independent-resource-patch.py') + "' $PSScriptRoot" + arg + "\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n", 'utf-8-sig')
(out / 'install-after-game-exits.ps1').write_text((R / 'shuffle-tile-width-smaller-values-20261103-030512/install-after-game-exits.ps1').read_text('utf-8-sig'), 'utf-8-sig')
(R / 'current-draft-reference-repair.json').write_text(json.dumps(dict(patch=str(out), manifest=str(out / 'manifest.json'), installed=False, status='prepared', runtime_verified=False), indent=2), 'utf8')
print(json.dumps(dict(output=str(out), files=len(tx), audits=audits), ensure_ascii=False), flush=True)
