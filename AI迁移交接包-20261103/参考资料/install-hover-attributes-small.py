from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, struct, sys, uuid

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
LAYOUT = 'ui-tileslayouts_assets_all.bundle'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/TooltipOnly_AttributesTableSmall/v1').hex
PID = -960000000003001
NAME = 'TooltipOnly_AttributesTableSmall'
SMALL_GUID = '3fd3642a7a1e65c44a46d4db296e615f'
sha = lambda b: hashlib.sha256(b).hexdigest()

spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
before = {GAME / n: (GAME / n).read_bytes() for n in [WORLD, LAYOUT]}
for n in [WORLD, LAYOUT]:
    before[SKIN / n] = (SKIN / n).read_bytes()
    assert before[SKIN / n] == before[GAME / n], ('skin/game differ', n)
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin']:
    before[p] = p.read_bytes()
assert before[GAME.parent / 'catalog.bin'] == before[SKIN / 'catalog.bin']
cat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
assert GUID not in dict(cat.keys()), 'Already installed; inspect the existing installation first.'
envs = {n: UnityPy.load(before[GAME / n]) for n in [WORLD, LAYOUT]}
objects = {n: {o.path_id: o for o in e.objects} for n, e in envs.items()}
hashes = {n: {i: sha(o.get_raw_data()) for i, o in obs.items()} for n, obs in objects.items()}
def named(bundle, name):
    matches = [o for o in objects[bundle].values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name]
    assert len(matches) == 1, name
    return matches[0]

# Use the game's own person -> player remapper and nullable rolemask setup.
source = named(WORLD, 'PlayerAttributesSmallBlock')
data = source.read_typetree()
refs = {r['rid']: r for r in data['references']['RefIds']}
template = next(r for r in refs.values() if r['type']['class'] == 'TemplateAsset' and r['data'].get('m_TemplateAlias') == 'AttributesTableSmall')
template_sd = refs[template['data']['m_SerializedData']['rid']]
assert template['rid'] == 1031 and template_sd['rid'] == 1049
keep = {-2, 1000, 1001, 1002, 1003, 1004, 1013, 1014, 1015, 1006, 1031, 1049}
data['references']['RefIds'] = [r for r in data['references']['RefIds'] if r['rid'] in keep]
data['m_Name'] = NAME
data['inlineSheet'] = {'m_FileID': 0, 'm_PathID': 0}
data['m_Usings'] = [copy.deepcopy(next(u for u in data['m_Usings'] if u['alias'] == 'AttributesTableSmall'))]
assert data['m_Usings'][0]['path'] == SMALL_GUID
data['m_Usings'][0]['asset'] = {'m_FileID': 0, 'm_PathID': 0}
data['m_AssetEntries'] = []
data['m_Slots'] = []
data['m_ContentContainerId'] = 0
data['m_ContentHash'] = struct.unpack('<i', bytes.fromhex(GUID[:8]))[0]
root = refs[1001]['data']
root['m_Children'] = [{'rid': i} for i in [1002, 1003, 1004, 1031]]
root['m_RuleIndex'] = -1
root['m_Classes'] = ['flex-grow-class', 'column-direction-normal']
template['data']['m_Parent'] = {'rid': 1001}
template['data']['m_RuleIndex'] = -1
template['data']['m_AttributeOverrides'] = []
template['data']['m_SerializedDataOverride'] = []
refs[1015]['data']['ValueVariables'] = []
refs[1015]['data']['ReferenceVariables'] = [v for v in refs[1015]['data']['ReferenceVariables'] if v['m_name'] == 'rolemask']
refs[1004]['data']['m_Properties'] = [{'name': 'reference-vars', 'value': 'rolemask:roleabilityrow:True'}]
assert refs[1015]['data']['ReferenceVariables'][0]['m_initToNull'] == 1
assert refs[1013]['data']['Parameters'][0]['name'] == 'person'
assert refs[1014]['data']['Mappings'][0]['from'] == 'player'

# Validate every managed reference before serialization.
def validate_refs(value):
    if isinstance(value, dict):
        if set(value) == {'rid'}:
            assert value['rid'] in keep, value
        else:
            for v in value.values(): validate_refs(v)
    elif isinstance(value, list):
        for v in value: validate_refs(v)
validate_refs(data)
assert all(r.get('data', {}).get('m_RuleIndex', -1) == -1 for r in data['references']['RefIds'])

oldwrite = TypeTreeHelper.write_value
def write(value, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(value, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData': oldwrite(value[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag): writer.align_stream()
        return
    return oldwrite(value, node, writer, config)
TypeTreeHelper.write_value = write

assert PID not in objects[WORLD]
new = copy.copy(source)
new.path_id = PID
new.data = None
new._read_until = None
new.assets_file.objects[PID] = new
new.save_typetree(data)

# Register the new VTA without changing any shared player page resource.
ab = next(o for o in objects[WORLD].values() if o.type.name == 'AssetBundle')
meta = ab.read_typetree()
span = []
def pointers(v):
    if isinstance(v, dict):
        if set(v) == {'m_FileID', 'm_PathID'}:
            if v['m_PathID'] and v not in span: span.append(copy.deepcopy(v))
        else:
            for x in v.values(): pointers(x)
    elif isinstance(v, list):
        for x in v: pointers(x)
pointers(data)
rootptr = {'m_FileID': 0, 'm_PathID': PID}
span.append(rootptr)
meta['m_Container'].append((GUID, {'preloadIndex': len(meta['m_PreloadTable']), 'preloadSize': len(span), 'asset': rootptr}))
meta['m_Container'].sort(key=lambda item: item[0])
meta['m_PreloadTable'].extend(span)
ab.save_typetree(meta)

composition = named(LAYOUT, 'PlayerReportTooltipGridComposition')
layout = composition.read_typetree()
attribute = next(c for c in layout['m_gridComponents'] if c['m_elementID'] == 'PlayerAttributesBlock')
assert len(attribute['m_gridElementConfigs']) == 1
config = attribute['m_gridElementConfigs'][0]
assert config['AssetRef']['m_AssetGUID'] == '6377cf8f9948a924d87a497f02adf653'
assert config['Size'] == {'x': 10, 'y': 4}
config['AssetRef']['m_AssetGUID'] = GUID
composition.save_typetree(layout)

source_guid = next(k for k, v in meta['m_Container'] if v['asset'] == {'m_FileID': 0, 'm_PathID': source.path_id})
base_loc = cat.locations(source_guid)[0]
assert cat.location(base_loc)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset'
deps = cat.location(base_loc)['dependencies']
assert cat.location(deps[0])['internal'].replace('\\', '/').endswith('/' + WORLD)
assert any(cat.location(p)['internal'].replace('\\', '/').endswith('/' + GLOBAL) for p in deps)
cat = cm.Catalog(cat.add_key_location(GUID, base_loc, base_loc))
label = 'GameWorldVisualTreeAssetPreload'
idx = next(i for i, (k, _) in enumerate(cat.keys()) if k == label)
keyobj, locset = cat.key_records[idx]
locations = [v[0] for v in cat.array(locset, 'I')]
locations.append(cat.locations(GUID)[0])
newset = cat.append(b''.join(struct.pack('<I', p) for p in locations), True)
records = list(cat.key_records)
records[idx] = (keyobj, newset)
table = cat.append(b''.join(struct.pack('<2I', *r) for r in records), True)
struct.pack_into('<I', cat.data, 8, table)
cat = cm.Catalog(bytes(cat.data))

outputs = {n: e.file.save(packer='lz4') for n, e in envs.items()}
expected = {WORLD: {PID: data, ab.path_id: meta}, LAYOUT: {composition.path_id: layout}}
unchanged = {}
for n, output in outputs.items():
    saved = {o.path_id: o for o in UnityPy.load(output).objects}
    assert set(saved) == set(objects[n]) | ({PID} if n == WORLD else set())
    for i, o in saved.items():
        if i in expected[n]:
            actual = o.read_typetree()
            # UnityPy may normalize tuple pairs to lists on save.
            assert json.dumps(actual, sort_keys=True) == json.dumps(expected[n][i], sort_keys=True), (n, i)
        else:
            assert sha(o.get_raw_data()) == hashes[n][i], (n, i)
    unchanged[n] = len(saved) - len(expected[n])
oldcat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
assert set(dict(cat.keys())) == set(dict(oldcat.keys())) | {GUID}
oldkeys, newkeys = dict(oldcat.keys()), dict(cat.keys())
custom_locations = cat.locations(GUID)
for key, locset in oldkeys.items():
    oldlocs = [v[0] for v in oldcat.array(locset, 'I')]
    newlocs = [v[0] for v in cat.array(newkeys[key], 'I')]
    if key == label:
        assert newlocs == oldlocs + custom_locations
    else:
        assert newlocs == oldlocs
        for loc in oldlocs: assert oldcat.location(loc) == cat.location(loc)
assert cat.location(cat.locations(GUID)[0])['dependencies'] == deps

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out = R / ('hover-attributes-small-' + stamp)
out.mkdir()
for tag, directory in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag)
    backup.mkdir()
    for n in [WORLD, LAYOUT]: (backup / n).write_bytes(before[directory / n])
    cp = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    (backup / 'catalog.bin').write_bytes(before[cp])
(out / 'backup-game' / 'catalog.hash').write_bytes(before[GAME.parent / 'catalog.hash'])
for n, output in outputs.items(): (out / n).write_bytes(output)
(out / (NAME + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf8')
catalog_output = bytes(cat.data)
(out / 'catalog.bin').write_bytes(catalog_output)
(out / 'catalog.hash').write_bytes(hashlib.md5(catalog_output).hexdigest().encode('ascii'))
install = {directory / n: output for directory in [GAME, SKIN] for n, output in outputs.items()}
install.update({GAME.parent / 'catalog.bin': catalog_output, SKIN / 'catalog.bin': catalog_output,
                GAME.parent / 'catalog.hash': (out / 'catalog.hash').read_bytes()})
for p, b in before.items(): assert p.read_bytes() == b, ('concurrent modification', str(p))
try:
    for p, b in install.items(): p.write_bytes(b)
    for p, b in install.items(): assert p.read_bytes() == b
except BaseException:
    for p in install: p.write_bytes(before[p])
    raise
report = {'installed': True, 'runtime_verified': False, 'guid': GUID, 'asset': NAME,
          'module': 'AttributesTableSmall', 'grid_size': [10, 4], 'shared_player_assets_unchanged': True,
          'unchanged_objects_verified': unchanged, 'after_sha256': {str(p): sha(b) for p, b in install.items()},
          'backup': str(out), 'only_layout_changed': 'PlayerReportTooltipGridComposition/PlayerAttributesBlock/AssetRef'}
(out / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=True, indent=2))
