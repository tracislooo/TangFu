from pathlib import Path
import ast
import copy
import datetime
import hashlib
import json
import runpy
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

def load_definitions(filename, names):
    parsed = ast.parse((ROOT / filename).read_text('utf8'))
    selected = [node for node in parsed.body if getattr(node, 'name', None) in names]
    assert len(selected) == len(names), filename
    exec(compile(ast.Module(body=selected, type_ignores=[]), filename, 'exec'), globals())

load_definitions('redesign-card-top-info-foot.py', {'write'})
load_definitions('add-card-six-ratings.py', {'validate_ui'})
load_definitions('build-match-ui-avatars-layout.py', {'Doc', 'refs', 'sd'})
oldwrite = TypeTreeHelper.write_value
TypeTreeHelper.write_value = write
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}

paths = json.loads((ROOT / 'current-game-location.json').read_text('utf-8-sig'))
game = Path(paths['bundle_root'])
skin = Path(paths['skin_packages'])
bundle = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT = ROOT / ('tactical-complexity-icons-left5-' + stamp)
OUT.mkdir()
(OUT / 'templates').mkdir()
sha = lambda data: hashlib.sha256(data).hexdigest()
Catalog = runpy.run_path(str(ROOT / 'catalog-binary-v35.py'))['Catalog']
header_guid = '78037b43a1f746740a7dbac11358e5e3'
factor_guid = '82f8cdb8bd675085b02354d68d6a874d'
ring_guid = 'ed746cfaec145ca49adc9797155ef821'
header_id = 1593217430813700770
transaction = []
checks = []
protected = {}
documents = []

for folder, catalog_path, tag in [(game, game.parent / 'catalog.bin', 'game'),
                                   (skin, skin / 'catalog.bin', 'skin')]:
    target = folder / bundle
    original = target.read_bytes()
    environment = UnityPy.load(original)
    objects = {obj.path_id: obj for obj in environment.objects}
    objs = {bundle: objects}
    changes = {bundle: {}}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objects.items()}
    meta = next(obj.read_typetree() for obj in objects.values() if obj.type.name == 'AssetBundle')
    catalog_bytes = catalog_path.read_bytes()
    protected[str(catalog_path)] = sha(catalog_bytes)
    catalog_hash = catalog_path.with_suffix('.hash')
    if catalog_hash.exists():
        protected[str(catalog_hash)] = sha(catalog_hash.read_bytes())
    catalog = Catalog(catalog_bytes)

    for key in (header_guid, factor_guid, ring_guid):
        locations = [catalog.location(index) for index in catalog.locations(key)]
        trees = [entry for entry in locations if entry['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
        assert len(trees) == 1 and trees[0]['internal'] == key, (tag, key)
        assert catalog.location(trees[0]['dependencies'][0])['internal'].endswith(bundle), (tag, key)

    assert any(key == header_guid and entry['asset']['m_PathID'] == header_id for key, entry in meta['m_Container'])
    factor_ids = sorted({entry['asset']['m_PathID'] for key, entry in meta['m_Container'] if key == factor_guid})
    assert factor_ids, tag
    header = Doc(bundle, pid=header_id)
    assert header.d['m_Name'] == 'TacticalPlannerSubsBlock'
    for node in (1047, 1065):
        assert header.data(node)['RowTemplate']['m_AssetGUID'] == factor_guid
    targets = [(header, (1041, 1059))]
    for pid in factor_ids:
        factor = Doc(bundle, pid=pid)
        assert factor.d['m_Name'] == 'CompactComplexityFactorRow'
        targets.append((factor, (1019,)))

    for document, nodes in targets:
        prior = copy.deepcopy(document.d)
        for node in nodes:
            element = document.a(node)
            assert element['m_TemplateAlias'] == 'TacticalEffectivenessPercentageGauge'
            rule_index = element['m_RuleIndex']
            if rule_index >= 0:
                assert not any(prop['m_Id'] in (131089, 131102, 131103)
                               for prop in document.s['m_Rules'][rule_index]['m_Properties'])
            document.st(node, [(131089, document.px(-5))])
        comparison = copy.deepcopy(document.d)
        for node in nodes:
            refs(comparison)[node]['data']['m_RuleIndex'] = refs(prior)[node]['data']['m_RuleIndex']
        assert comparison == prior
        document.save()

    data = environment.file.save(packer='lz4')
    saved = {obj.path_id: obj for obj in UnityPy.load(data).objects}
    assert saved.keys() == objects.keys()
    for pid, obj in saved.items():
        if pid in changes[bundle]:
            assert obj.read_typetree() == changes[bundle][pid], (tag, pid)
        else:
            assert sha(obj.get_raw_data()) == original_hashes[pid], (tag, pid)
    backup = OUT / ('backup-' + tag) / bundle
    output = OUT / ('output-' + tag) / bundle
    for path, contents in [(backup, original), (output, data)]:
        path.parent.mkdir()
        path.write_bytes(contents)
    transaction.append({'target':str(target), 'backup':str(backup), 'source':str(output),
                        'before':sha(original), 'after':sha(data)})
    checks.append({'target':tag, 'horizontal_offset_px':-5,
                   'header_nodes':[1041,1059], 'factor_template_ids':factor_ids, 'factor_node':1019})

manifest = {'installed':False, 'runtime_verified':False, 'checks':checks,
            'scope':'Move the right column of tactic complexity gauges 5px left',
            'protected_sha256':protected}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transaction, indent=2), 'utf8')
installer = ROOT / 'install-independent-resource-patch.py'
for filename, flag in [('install.ps1', ''), ('restore.ps1', ' --restore')]:
    (OUT / filename).write_text(f"& '{sys.executable}' '{installer}' $PSScriptRoot{flag}\n", 'utf8')
print(OUT, flush=True)
