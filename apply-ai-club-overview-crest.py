"""Apply the player's two-row crest layout to the AI club site header."""
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
for script, names in [
    ('add-card-six-ratings.py', {'write', 'validate_ui'}),
    ('build-match-ui-avatars-layout.py', {'refs', 'sd', 'find', 'Doc'}),
    ('build-club-stadium-overlay-local.py', {'stage'}),
]:
    for node in ast.parse((R / script).read_text('utf8')).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            exec(compile(ast.Module([node], []), script, 'exec'), globals())
TypeTreeHelper.write_value = write
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog_module)
cfg = json.loads((R / 'current-game-location.json').read_text('utf8'))
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
ai_guid = '441736359c3f87447bdebb8316ee98e9'
factory_guid = '83957ab1d9313aa42837b24e6d6fda2e'
sha = lambda data: hashlib.sha256(data).hexdigest()
out = R / ('ai-club-overview-crest-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx, audit = [], []

for tag, folder in [('game', Path(cfg['bundle_root'])), ('skin', Path(cfg['skin_packages']))]:
    path = folder / W
    before = path.read_bytes()
    env = UnityPy.load(before)
    af = env.assets[0]
    objs = {W: af.objects}
    player = Doc(W, pid=-991100000000020)
    ai = Doc(W, name='ClubSiteHeader')
    club_site = Doc(W, name='ClubSite')
    assert club_site.data(1004) is not None
    assert bytes(club_site.r[1012]['data']['VisualFuncBinding']['m_inputs']['m_variable']['m_argumentBytes']).count(factory_guid.encode()) == 1
    assert club_site.r[1012]['data']['PreviewAsset']['m_AssetGUID'] == ai_guid
    settings_path = folder / 'ui-settings_assets_all.bundle'
    if not settings_path.is_file():
        settings_path = Path(cfg['bundle_root']) / settings_path.name
    settings = UnityPy.load(str(settings_path)).assets[0]
    settings_meta = next(o.read_typetree() for o in settings.objects.values() if o.type.name == 'AssetBundle')
    factory_pid = next(e['asset']['m_PathID'] for k, e in settings_meta['m_Container'] if k == factory_guid)
    factory = settings.objects[factory_pid].read_typetree()
    assert next(item for item in factory['m_items'] if item['Id'] == 'club-site')['Asset']['m_AssetGUID'] == ai_guid

    # Keep the AI header's existing asset and stylesheet IDs. The native
    # dynamic header wrapper sizes to content, so reserve the same 180 units
    # here that the player overview reserves at its template instance.
    player_host = Doc(W, name='ClubScreenOverviewBlock')
    assert player_host.a(1231)['m_TemplateAlias'] == 'ClubSiteHeader'
    host_rule = player_host.s['m_Rules'][player_host.a(1231)['m_RuleIndex']]['m_Properties']
    height = next(x for x in host_rule if x['m_Id'] == 131087)['m_Values'][0]
    assert player_host.s['dimensions'][height['valueIndex']] == {'unit': 1, 'value': 180.0}
    for rid in (1001, 1004, 1006, 1010, 1012, 1013):
        assert ai.a(rid)['m_Id'] == player.a(rid)['m_Id']
    tree = copy.deepcopy(player.d)
    tree['m_Name'] = ai.d['m_Name']
    tree['inlineSheet'] = copy.deepcopy(ai.d['inlineSheet'])
    style = copy.deepcopy(player.s)
    style['m_Name'] = ai.s['m_Name']
    new = Doc(W, pid=ai.obj.path_id, tree=tree, style=style)
    new.st(1001, [(131087, new.px(180)), (131096, new.px(180)), (131094, new.px(180)),
                  (131084, new.num(0)), (131085, new.num(0))])
    validate_ui(new.d, new.s)

    meta_obj = next(o for o in af.objects.values() if o.type.name == 'AssetBundle')
    meta = meta_obj.read_typetree()
    ai_entry = next(e for k, e in meta['m_Container'] if k == ai_guid and e['asset']['m_PathID'] == ai.obj.path_id)
    donor_entry = next(e for k, e in meta['m_Container'] if e['asset']['m_PathID'] == player.obj.path_id)
    def span(entry):
        start = entry['preloadIndex']
        return meta['m_PreloadTable'][start:start + entry['preloadSize']]
    preload = list(span(ai_entry))
    for pointer in span(donor_entry):
        if pointer not in preload and pointer['m_PathID'] not in {player.obj.path_id, player.sid}:
            preload.append(pointer)
    if preload != span(ai_entry):
        ai_entry.update(preloadIndex=len(meta['m_PreloadTable']), preloadSize=len(preload))
        meta['m_PreloadTable'].extend(preload)

    cat_path = (folder.parent if tag == 'game' else folder) / 'catalog.bin'
    cat = catalog_module.Catalog(cat_path.read_bytes())
    def vta_location(guid):
        return next(l for l in cat.locations(guid) if cat.location(l)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset')
    assert vta_location(ai_guid) in cat.locations('GameWorldVisualTreeAssetPreload')
    ai_deps = cat.location(vta_location(ai_guid))['dependencies']
    donor_deps = cat.location(vta_location('ab552408c4415c32b16746fc332d572a'))['dependencies']
    assert ai_deps[0] == donor_deps[0] and set(donor_deps) <= set(ai_deps)
    for using in new.d['m_Usings']:
        vta_location(using['path'])

    hashes = {pid: sha(o.get_raw_data()) for pid, o in af.objects.items()}
    changes = {ai.obj.path_id: new.d, ai.sid: new.s, meta_obj.path_id: meta}
    for pid, value in changes.items():
        af.objects[pid].save_typetree(value)
    after = env.file.save(packer='lz4')
    check = UnityPy.load(after).assets[0].objects
    assert set(check) == set(hashes)
    for pid, obj in check.items():
        if pid in changes:
            assert obj.read_typetree() == changes[pid]
        else:
            assert sha(obj.get_raw_data()) == hashes[pid]
    stage(tag, path, before, after)
    audit.append({'target': tag, 'factory_key': 'club-site', 'header_guid': ai_guid,
                  'crest_size': [160, 166], 'header_height': 180, 'row_inset': 176,
                  'unrelated_objects_byte_identical': True})

for name, value in [('transaction', tx), ('manifest', dict(installed=False, runtime_verified=False, protected_sha256={}, audit=audit))]:
    (out / (name + '.json')).write_text(json.dumps(value, indent=2), 'utf8')
for action, flag in [('install', ''), ('restore', ' --restore')]:
    line = f"& '{sys.executable}' '{R / 'install-independent-resource-patch.py'}' $PSScriptRoot{flag}\nexit $LASTEXITCODE\n"
    (out / (action + '.ps1')).write_text(line, 'utf-8-sig')
print(out, flush=True)
