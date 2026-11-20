"""Independently compare the prepared or installed six-variant resources."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

index = json.loads((R / 'current-player-overview-six-variants.json').read_text('utf8'))
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else Path(index['manifest']).parent
installed = '--installed' in sys.argv
manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L = 'ui-tileslayouts_assets_all.bundle'
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
sha = lambda b: hashlib.sha256(b).hexdigest()


def load(path):
    env = UnityPy.load(str(path))
    return {o.path_id: o for o in env.objects}


def canonical(d, sheet, portrait_only=False, skip_portrait=False):
    rr = {r['rid']: r for r in d['references']['RefIds']}

    def serial(i):
        return rr.get(rr[i].get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {})

    def rule(idx):
        if idx < 0:
            return None
        props = []
        for p in sheet['m_Rules'][idx]['m_Properties']:
            values = []
            for h in p['m_Values']:
                pool = poolmap.get(h['m_ValueType'])
                values.append((h['m_ValueType'], sheet[pool][h['valueIndex']] if pool else h['valueIndex']))
            props.append((p['m_Id'], p.get('m_CustomName'), values))
        return sorted(props, key=lambda p: (p[0], p[1]))

    def norm(value):
        if isinstance(value, list):
            return [norm(v) for v in value]
        if isinstance(value, dict):
            if set(value) == {'rid'}:
                return expand(value['rid'])
            return {k: rule(v) if k == 'm_RuleIndex' else norm(v) for k, v in value.items()
                    if k not in ['m_Parent', 'm_Id', 'm_ParentId', 'uxmlAssetId']}
        return value

    stack = []

    def expand(i):
        if i == -2:
            return None
        assert i not in stack, ('unexpected cyclic reference', i)
        if skip_portrait and serial(i).get('name') == 'ReportPortraitStatusColumn':
            return 'PORTRAIT_REPLACEMENT'
        stack.append(i)
        out = dict(type=rr[i]['type'], data=norm(rr[i].get('data', {})))
        stack.pop()
        return out

    root = d['m_VisualTree']['rid']
    if portrait_only:
        root, = [i for i in rr if serial(i).get('name') == 'ReportPortraitStatusColumn']
    return expand(root)


results = []
for tag, live in [('game', Path(loc['bundle_root'])), ('skin', Path(loc['skin_packages']))]:
    base = live if installed else OUT / tag
    old_w, old_l = load(OUT / ('backup-' + tag) / W), load(OUT / ('backup-' + tag) / L)
    new_w, new_l = load(base / W), load(base / L)
    catfile = (live.parent if tag == 'game' else live) / 'catalog.bin' if installed else base / 'catalog.bin'
    cat = cm.Catalog(catfile.read_bytes())
    assert catfile.with_name('catalog.hash').read_bytes() == hashlib.md5(catfile.read_bytes()).hexdigest().encode('ascii')
    meta = next(o for o in new_w.values() if o.type.name == 'AssetBundle').read_typetree()
    container = dict(meta['m_Container'])
    dependencies = {W: new_w}
    for v in manifest['versions']:
        d = new_w[v['page']].read_typetree()
        s = new_w[v['style']].read_typetree()
        donor, source = old_w[v['donor']].read_typetree(), old_w[v['source']].read_typetree()
        donor_s = old_w[donor['inlineSheet']['m_PathID']].read_typetree()
        source_s = old_w[source['inlineSheet']['m_PathID']].read_typetree()
        assert canonical(d, s, portrait_only=True) == canonical(donor, donor_s, portrait_only=True)
        assert canonical(d, s, skip_portrait=True) == canonical(source, source_s, skip_portrait=True)
        entry = container[v['guid']]
        assert entry['asset'] == {'m_FileID': 0, 'm_PathID': v['page']}
        span = meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']]
        assert {'m_FileID': 0, 'm_PathID': v['style']} in span
        at, = cat.locations(v['guid'])
        assert at in cat.locations('GameWorldVisualTreeAssetPreload')
        assert cat.location(at)['type'][1].endswith('VisualTreeAsset')
        assert cat.location(cat.location(at)['dependencies'][0])['internal'].endswith(W)
        # Check every live template alias against the actual catalog and bundle,
        # including shared native image/status templates referenced by the donor.
        rr = {r['rid']: r for r in d['references']['RefIds']}
        aliases = {r.get('data', {}).get('m_TemplateAlias') for r in rr.values()} - {None, ''}
        resolved = 0
        for use in d['m_Usings']:
            if use['alias'] not in aliases or not use.get('path'):
                continue
            matches = [cat.location(i) for i in cat.locations(use['path']) if cat.location(i)['type'][1].endswith('VisualTreeAsset')]
            assert len(matches) == 1, use
            owning = cat.location(matches[0]['dependencies'][0])['internal'].split('\\')[-1].split('/')[-1]
            if owning not in dependencies:
                dependencies[owning] = load(live / owning)
            dep_obs = dependencies[owning]
            dep_meta = next(o for o in dep_obs.values() if o.type.name == 'AssetBundle').read_typetree()
            dep_entries = [e for key, e in dep_meta['m_Container'] if key == use['path']]
            vta_entries = [e for e in dep_entries if 'm_VisualTree' in dep_obs[e['asset']['m_PathID']].read_typetree()]
            assert vta_entries, (tag, v['title'], use, owning)
            for e in vta_entries:
                dep_doc = dep_obs[e['asset']['m_PathID']].read_typetree()
                assert dep_doc['inlineSheet']['m_FileID'] == 0
                assert 'm_Rules' in dep_obs[dep_doc['inlineSheet']['m_PathID']].read_typetree()
            resolved += 1
        results.append(dict(target=tag, title=v['title'], donor_region_identical=True,
                            remaining_regions_identical=True, aliases_resolved=resolved))
    for pid in [-930000000001001, -930000000001003, -940000000010000, -940000000012000]:
        assert new_w[pid].get_raw_data() == old_w[pid].get_raw_data()
        sid = old_w[pid].read_typetree()['inlineSheet']['m_PathID']
        assert new_w[sid].get_raw_data() == old_w[sid].get_raw_data()
    lm = next(o for o in new_l.values() if o.type.name == 'AssetBundle').read_typetree()
    checked_spans = 0
    for key, entry in lm['m_Container']:
        span = lm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']]
        if any(p['m_FileID'] == 0 and p['m_PathID'] in [1332213496068314481, 3901662990989568885] for p in span):
            for v in manifest['versions']:
                assert {'m_FileID': 0, 'm_PathID': v['description']} in span
            checked_spans += 1
    assert checked_spans >= 3

for row in json.loads((OUT / 'transaction.json').read_text('utf8')):
    path = Path(row['target'] if installed else row['source'])
    assert sha(path.read_bytes()) == row['after'], path
    assert sha(Path(row['backup']).read_bytes()) == row['before']
    if 'CustomGridCompositions' in row['target']:
        old, current = json.loads(Path(row['backup']).read_bytes()), json.loads(path.read_bytes())
        assert current['m_gridComponents'] == old['m_gridComponents']
        assert current['m_placementBindings'][:-2] == old['m_placementBindings']
for path, digest in manifest['protected_sha256'].items():
    assert sha(Path(path).read_bytes()) == digest, path
report = dict(verified=True, installed=installed, runtime_verified=False, results=results)
(OUT / ('verification-installed.json' if installed else 'verification-prepared.json')).write_text(
    json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=False))
