from pathlib import Path
import csv
import json
import runpy
import struct
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy

out = Path(sys.argv[1])
manifest = json.loads((out / 'manifest.json').read_text('utf8'))
groups = json.loads((out / 'coordinates.json').read_text('utf8'))['groups']
source = Path('K:/桌面/27skin/PICTURE/country-new/club-coordinates.csv')
with source.open(encoding='utf-8-sig', newline='') as file:
    for row in csv.DictReader(file):
        point = groups['110'][row['uid']]
        assert (point['x'], point['y']) == (float(row['x']), float(row['y']))
assert [len(groups[name]) for name in ('110', '796', '219003')] == [32, 40, 92]
Catalog = runpy.run_path(str(ROOT / 'catalog-binary-v35.py'))['Catalog']

for audit in manifest['audits']:
    folder = out / audit['target']
    catalog = Catalog((folder / 'catalog.bin').read_bytes())
    mapping = audit['nation_to_map']
    assert mapping['765'] == '219003' and mapping['796'] == '796' and len(mapping) == 35
    actual = {}
    for offset in {loc for _, offsets in catalog.keys() for loc, in catalog.array(offsets, 'I')}:
        loc = catalog.location(offset)
        bundle = Path(loc['internal'].replace(chr(92), '/')).name
        if bundle in audit['bundle_crc_size'] and loc['type'][1].endswith('IAssetBundleResource') and loc['raw'][5] != 0xffffffff:
            payload = catalog.unpack(loc['raw'][5], '2I')[1]
            actual[bundle] = list(catalog.unpack(payload, '5I')[2:4])
    assert actual == audit['bundle_crc_size']
    path = next(folder.glob('ui-visualtreeassets_*.bundle'))
    objects = {obj.path_id: obj for obj in UnityPy.load(str(path)).objects}
    data = objects[-991100000000030].read_typetree()
    style = objects[data['inlineSheet']['m_PathID']].read_typetree()
    refs = {item['rid']: item.get('data', {}) for item in data['references']['RefIds']}

    def serialized(rid):
        return refs.get(refs[rid].get('m_SerializedData', {}).get('rid'), {})

    def children(rid):
        return [child['rid'] for child in refs[rid]['m_Children']]

    def value(rid, key):
        prop = next(prop for prop in style['m_Rules'][refs[rid]['m_RuleIndex']]['m_Properties'] if prop['m_Id'] == key)
        return style['dimensions'][prop['m_Values'][0]['valueIndex']]['value']

    fit = next(rid for rid in refs if serialized(rid).get('name') == 'TFUKMapWidthAspect')
    siblings = children(fit)
    surface = refs[fit]['m_Parent']['rid']
    props = style['m_Rules'][refs[surface]['m_RuleIndex']]['m_Properties']
    background = next(prop for prop in props if prop['m_Id'] == 458752)
    assert style['colors'][background['m_Values'][0]['valueIndex']]['a'] == 0
    world_gate = siblings[0]
    for nation in sorted(mapping, key=int):
        assert serialized(world_gate)['name'] == 'TFMapWorldUnlessNation' + nation
        proceed, blocked = children(world_gate)
        assert not children(blocked)
        world_gate, = children(proceed)
    assert serialized(world_gate)['name'] == 'TFPackedMapworld'
    nation_gates = [rid for rid in siblings[1:] if serialized(rid)['name'].startswith('TFMapNation')]
    assert len(nation_gates) == len(mapping)
    checked = set()
    for rid in nation_gates:
        gate = serialized(rid)
        nation = gate['name'].removeprefix('TFMapNation')
        raw = bytes(gate['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        argsize = struct.unpack_from('<I', raw, 1)[0]
        uid_size = struct.unpack_from('<I', raw, 5 + argsize)[0]
        assert raw.endswith(b'club.nation.UniqueId') and struct.unpack_from('<i', raw, 5 + argsize + uid_size)[0] == int(nation)
        assert nation not in checked
        checked.add(nation)
        off, match = children(rid)
        assert not children(off)
        assert all(p['m_Id'] != 458752 for p in style['m_Rules'][refs[match]['m_RuleIndex']]['m_Properties'])
        background, *markers = children(match)
        map_name = mapping[nation]
        asset = audit['maps'][map_name]
        assert serialized(background)['StaticImage']['m_AssetGUID'] == asset['guid']
        assert len(markers) == len(groups[map_name])
        for marker in markers:
            uid = serialized(marker)['name'].removeprefix('TFMapClubUID')
            point = groups[map_name][uid]
            empty, pin = children(marker)
            assert not children(empty)
            assert abs(value(pin, 131089) - asset['scale'] * point['x'] / 19.2) < 1e-5
            assert abs(value(pin, 131104) - (asset['top'] * 100 + asset['scale'] * point['y'] / 10.8)) < 1e-5
    assert checked == mapping.keys()
    print(audit['target'], '35 nation IDs, coordinates, blank marker branches and bundle metadata verified')
