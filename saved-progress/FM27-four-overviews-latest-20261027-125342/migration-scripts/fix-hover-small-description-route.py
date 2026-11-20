from pathlib import Path
import copy, datetime, hashlib, json, sys

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
LAYOUT = 'ui-tileslayouts_assets_all.bundle'
GUID = 'd7961b53b2635ae7b8996007ff34bf6b'
OLD_PID = 6067656787038004271
NEW_PID = -960000000003002
NEW_ID = 'TooltipOnlyPlayerAttributes'
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {p / n: (p / n).read_bytes() for p in [GAME, SKIN] for n in [WORLD, LAYOUT]}
for n in [WORLD, LAYOUT]: assert before[GAME / n] == before[SKIN / n]
envs = {n: UnityPy.load(before[GAME / n]) for n in [WORLD, LAYOUT]}
obs = {n: {o.path_id: o for o in e.objects} for n, e in envs.items()}
original_hashes = {n: {i: sha(o.get_raw_data()) for i, o in objects.items()} for n, objects in obs.items()}
def named(n, name):
    matches = [o for o in obs[n].values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name]
    assert len(matches) == 1, name
    return matches[0]

oldwrite = TypeTreeHelper.write_value
def write(v, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData': oldwrite(v[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag): writer.align_stream()
        return
    return oldwrite(v, node, writer, config)
TypeTreeHelper.write_value = write

# A dedicated description prevents runtime size selection from restoring the shared asset.
source = named(LAYOUT, 'PlayerAttributesBlockTileDescription')
assert source.path_id == OLD_PID and NEW_PID not in obs[LAYOUT]
description = source.read_typetree()
description['m_Name'] = NEW_ID + 'TileDescription'
description['<Name>k__BackingField'] = NEW_ID
description['<ID>k__BackingField'] = NEW_ID
cfg = copy.deepcopy(description['<Configurations>k__BackingField'][0])
assert cfg['Size'] == {'x': 10, 'y': 4}
cfg['Description'] = {'m_FileID': 0, 'm_PathID': NEW_PID}
cfg['AssetRef']['m_AssetGUID'] = GUID
description['<Configurations>k__BackingField'] = [cfg]
description['<DefaultConfigIndex>k__BackingField'] = 0
new = copy.copy(source)
new.path_id = NEW_PID
new.data = None
new._read_until = None
new.assets_file.objects[NEW_PID] = new
new.save_typetree(description)
expected = {LAYOUT: {NEW_PID: description}, WORLD: {}}

elementset = named(LAYOUT, 'PlayerReportTooltipGridElementSet')
setdata = elementset.read_typetree()
matches = [p for p in setdata['m_gridElementDescriptions'] if p['m_FileID'] == 0 and p['m_PathID'] == OLD_PID]
assert len(matches) == 1
matches[0]['m_PathID'] = NEW_PID
elementset.save_typetree(setdata)
expected[LAYOUT][elementset.path_id] = setdata

composition = named(LAYOUT, 'PlayerReportTooltipGridComposition')
layout = composition.read_typetree()
component = next(c for c in layout['m_gridComponents'] if c['m_elementID'] == 'PlayerAttributesBlock')
component['m_elementID'] = NEW_ID
component['m_configDescriptions'] = [{'m_FileID': 0, 'm_PathID': NEW_PID}]
component['m_configDescriptionKeys'] = []
component['m_gridElementConfigs'] = [copy.deepcopy(cfg)]
for placement in layout['m_placementBindings']:
    if placement['m_elementID'] == 'PlayerAttributesBlock': placement['m_elementID'] = NEW_ID
composition.save_typetree(layout)
expected[LAYOUT][composition.path_id] = layout

preview = named(WORLD, 'PlayerReportPreviewTooltip')
previewdata = preview.read_typetree()
grids = [r['data']['Bindings'] for r in previewdata['references']['RefIds']
         if r.get('data', {}).get('Bindings', {}).get('m_gridCompositionSet', {}).get('m_PathID') == -241840581472044354]
assert len(grids) == 1
replacements = [0]
def replace_id(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str) and v == 'PlayerAttributesBlock':
                value[k] = NEW_ID
                replacements[0] += 1
            else: replace_id(v)
    elif isinstance(value, list):
        for v in value: replace_id(v)
replace_id(grids[0])
assert replacements[0] >= 3
preview.save_typetree(previewdata)
expected[WORLD][preview.path_id] = previewdata

# Register the local description's preload pointers for each affected native root.
bundle = next(o for o in obs[LAYOUT].values() if o.type.name == 'AssetBundle')
metadata = bundle.read_typetree()
roots = {elementset.path_id, composition.path_id}
for key, entry in metadata['m_Container']:
    if entry['asset']['m_FileID'] != 0 or entry['asset']['m_PathID'] not in roots: continue
    span = copy.deepcopy(metadata['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
    ptr = {'m_FileID': 0, 'm_PathID': NEW_PID}
    if ptr not in span: span.append(ptr)
    entry['preloadIndex'] = len(metadata['m_PreloadTable'])
    entry['preloadSize'] = len(span)
    metadata['m_PreloadTable'].extend(span)
bundle.save_typetree(metadata)
expected[LAYOUT][bundle.path_id] = metadata

outputs = {n: e.file.save(packer='lz4') for n, e in envs.items()}
for n, b in outputs.items():
    saved = {o.path_id: o for o in UnityPy.load(b).objects}
    assert set(saved) == set(obs[n]) | ({NEW_PID} if n == LAYOUT else set())
    for i, o in saved.items():
        if i in expected[n]:
            assert json.dumps(o.read_typetree(), sort_keys=True) == json.dumps(expected[n][i], sort_keys=True), (n, i)
        else:
            assert sha(o.get_raw_data()) == original_hashes[n][i], (n, i)

# Follow the complete saved route, including the authoritative description configuration.
savedlayout = {o.path_id: o for o in UnityPy.load(outputs[LAYOUT]).objects}
savedworld = {o.path_id: o for o in UnityPy.load(outputs[WORLD]).objects}
actualset = savedlayout[elementset.path_id].read_typetree()
assert actualset['m_gridElementDescriptions'][0] == {'m_FileID': 0, 'm_PathID': NEW_PID}
actualdesc = savedlayout[NEW_PID].read_typetree()
assert actualdesc['<ID>k__BackingField'] == NEW_ID
assert [c['AssetRef']['m_AssetGUID'] for c in actualdesc['<Configurations>k__BackingField']] == [GUID]
assert savedlayout[OLD_PID].get_raw_data() == obs[LAYOUT][OLD_PID].get_raw_data()
wrapper = next(o for o in savedworld.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'TooltipOnly_AttributesTableSmall').read_typetree()
assert [u['alias'] for u in wrapper['m_Usings']] == ['AttributesTableSmall']
assert not any('MovedHeader' in str(r) or 'MovedBanner' in str(r) for r in wrapper['references']['RefIds'])
assert 'PlayerAttributesBlock' not in json.dumps(grids[0])

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out = R / ('hover-small-description-route-' + stamp)
out.mkdir()
for tag, p in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag)
    backup.mkdir()
    for n in [WORLD, LAYOUT]: (backup / n).write_bytes(before[p / n])
for n, b in outputs.items(): (out / n).write_bytes(b)
for p, b in before.items(): assert p.read_bytes() == b
try:
    for p in [GAME, SKIN]:
        for n, b in outputs.items(): (p / n).write_bytes(b)
    for p in [GAME, SKIN]:
        for n, b in outputs.items(): assert (p / n).read_bytes() == b
except BaseException:
    for p, b in before.items(): p.write_bytes(b)
    raise
report = {'installed': True, 'runtime_verified': False, 'backup': str(out),
          'dedicated_description': NEW_ID + 'TileDescription', 'description_id': NEW_PID,
          'full_route_verified': ['PlayerReportPreviewTooltip', 'PlayerReportTooltipGridElementSet',
                                  NEW_ID + 'TileDescription', 'TooltipOnly_AttributesTableSmall', 'AttributesTableSmall'],
          'player_page_shared_description_unchanged': True,
          'only_existing_assets_changed': {n: [obs[n][i].peek_name() for i in e if i in obs[n]] for n, e in expected.items()},
          'after_sha256': {n: sha(b) for n, b in outputs.items()}}
(out / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=True, indent=2))
