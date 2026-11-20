"""Restore reviewed main resources and merge changes into the updated native catalog."""
from pathlib import Path
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import zlib

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy

read = lambda p: json.loads(p.read_text('utf8'))
sha = lambda data: hashlib.sha256(data).hexdigest()
review_root = Path(read(ROOT / 'current-game-update-comparison.json')['archive'])
review = read(review_root / 'comparison.json')
AA = Path(review['game_aa'])
out = ROOT / ('main-reviewed-update-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
(out / 'backup-game').mkdir()
spec = importlib.util.spec_from_file_location('catalog', ROOT / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
original = cm.Catalog((ROOT / 'saved-progress/FM27-original-diff-20261111-191041/original/aa/catalog.bin').read_bytes())
skin = cm.Catalog(Path(review['catalog']['old_modified_catalog_source']).read_bytes())
catalog_before = (AA / 'catalog.bin').read_bytes()
native = cm.Catalog(catalog_before)
assert catalog_before == (review_root / 'updated-native/aa/catalog.bin').read_bytes()
manifest = {'installed': False, 'runtime_verified': False, 'review': str(review_root),
            'after_sha256': {}, 'new_game_before_sha256': {}, 'sources': {},
            'catalog_before_sha256': sha(catalog_before), 'scope': 'latest main, sidebar deferred'}
for name in ['catalog.bin', 'catalog.hash']:
    (out / 'backup-game' / name).write_bytes((AA / name).read_bytes())
for row in review['main_bundles']:
    name = row['bundle']
    before = (AA / 'StandaloneWindows64' / name).read_bytes()
    assert sha(before) == row['updated_sha256'], name
    source = Path(row['modified_source'])
    data = source.read_bytes()
    assert sha(data) == row['modified_sha256'], source
    (out / 'backup-game' / name).write_bytes(before)
    manifest['new_game_before_sha256'][name] = sha(before)
    manifest['sources'][name] = str(source)
    if row['status'] == 'native_changed_rebase':
        assert name == 'ui-styles_assets_common.bundle'
        env = UnityPy.load(before)
        objects = {o.path_id: o for o in env.objects}
        source_env = UnityPy.load(data)
        source_objects = {o.path_id: o for o in source_env.objects}
        pid = -6275161654120610136
        tree = objects[pid].read_typetree()
        source_tree = source_objects[pid].read_typetree()
        pools = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets',
                 7:'strings', 8:'strings', 9:'strings', 10:'strings', 12:'scalableImages', 13:'strings'}
        def rule(index):
            result = copy.deepcopy(source_tree['m_Rules'][index])
            for prop in result['m_Properties']:
                for handle in prop['m_Values']:
                    pool = pools.get(handle['m_ValueType'])
                    if pool:
                        value = source_tree[pool][handle['valueIndex']]
                        if value not in tree[pool]:
                            tree[pool].append(copy.deepcopy(value))
                        handle['valueIndex'] = tree[pool].index(value)
            return result
        common = review['common']
        assert not common['overlapping_rules']
        for index in common['skin_changed_existing_rules']:
            tree['m_Rules'][index] = rule(index)
        for index in common['skin_added_rule_indices']:
            assert index == len(tree['m_Rules'])
            tree['m_Rules'].append(rule(index))
        before_objects = {i: sha(o.get_raw_data()) for i,o in objects.items()}
        objects[pid].save_typetree(tree)
        data = env.file.save(packer='lz4')
        check = {o.path_id:o for o in UnityPy.load(data).objects}
        assert check[pid].read_typetree() == tree
        assert all(sha(check[i].get_raw_data()) == h for i,h in before_objects.items() if i != pid)
        manifest['native_common_rules_preserved'] = common['updated_native_changed_rules']
    (out / name).write_bytes(data)
    manifest['after_sha256'][name] = sha(data)

def locations(cat):
    return {loc:cat.location(loc) for _,ls in cat.keys() for loc, in cat.array(ls,'I')}

def identity(v):
    primary = '' if v['type'][1].endswith('IAssetBundleResource') else v['primary']
    return primary, v['internal'], tuple(v['type']), v['provider']

old_locs, skin_locs, new_locs = map(locations, [original, skin, native])
old_keys, skin_keys, new_keys = map(lambda c:dict(c.keys()), [original, skin, native])
new_identity = {identity(v):loc for loc,v in new_locs.items()}
old_identity = {identity(v):loc for loc,v in old_locs.items()}
type_templates = {}
for loc,v in new_locs.items():
    type_templates.setdefault((tuple(v['type']),v['provider']), loc)
extra_native = []
for loc,v in skin_locs.items():
    ident = identity(v)
    if ident in new_identity:
        continue
    # Added GUID locations carry no provider-specific extra data.
    assert ident not in old_identity, ('native resource identity removed',ident)
    assert v['raw'][5] == cm.NULL, ('custom provider metadata',ident)
    template = new_locs[type_templates[(tuple(v['type']),v['provider'])]]
    raw = list(template['raw'])
    raw[0] = native.add_string(v['primary'])
    raw[1] = native.add_string(v['internal'])
    raw[3], raw[4], raw[5] = cm.NULL, 0, cm.NULL
    dest = native.append(struct.pack('<7I',*raw))
    new_identity[ident] = dest
    extra_native.append((dest,v))

def mapped(loc):
    return new_identity[identity(skin_locs[loc])]

def set_dependencies(loc, deps):
    raw = list(native.unpack(loc,'7I'))
    binary = b''.join(struct.pack('<I',x) for x in deps)
    raw[3] = native.append(binary,True)
    raw[4] = zlib.crc32(binary)
    struct.pack_into('<7I',native.data,loc,*raw)

for dest,v in extra_native:
    set_dependencies(dest,[mapped(dep) for dep in v['dependencies']])
changed_dependencies = 0
for loc,v in skin_locs.items():
    ident = identity(v)
    if ident not in old_identity:
        continue
    old = old_locs[old_identity[ident]]
    old_deps = [identity(old_locs[x]) for x in old['dependencies']]
    skin_deps = [identity(skin_locs[x]) for x in v['dependencies']]
    if old_deps == skin_deps:
        continue
    dest = new_identity[ident]
    deps = list(new_locs[dest]['dependencies'])
    removed = set(old_deps) - set(skin_deps)
    deps = [d for d in deps if identity(new_locs[d]) not in removed]
    additions = [new_identity[d] for d in skin_deps if d not in old_deps]
    deps = list(dict.fromkeys(deps + additions))
    set_dependencies(dest,deps)
    changed_dependencies += 1

records = list(native.key_records)
record_index = {native.object(key):i for i,(key,ls) in enumerate(records)}
string_type = next(native.unpack(k,'2I')[0] for k,ls in records if isinstance(native.object(k),str))
added_keys = 0
label_additions = {}
for key,ls in skin.keys():
    source_locations = [loc for loc, in skin.array(ls,'I')]
    if key not in old_keys:
        assert key not in new_keys and isinstance(key,str)
        value = native.add_string(key)
        payload = native.append(struct.pack('<IHH',value,0,0))
        key_object = native.append(struct.pack('<2I',string_type,payload))
        location_set = native.append(b''.join(struct.pack('<I',mapped(loc)) for loc in source_locations),True)
        records.append((key_object,location_set))
        added_keys += 1
    else:
        old_set = {identity(old_locs[loc]) for loc, in original.array(old_keys[key],'I')}
        additions = [mapped(loc) for loc in source_locations if identity(skin_locs[loc]) not in old_set]
        if additions:
            index = record_index[key]
            key_object, current = records[index]
            merged = list(dict.fromkeys([loc for loc, in native.array(current,'I')] + additions))
            records[index] = (key_object,native.append(b''.join(struct.pack('<I',loc) for loc in merged),True))
            label_additions[str(key)] = len(additions)
table = native.append(b''.join(struct.pack('<2I',*record) for record in records),True)
struct.pack_into('<I',native.data,8,table)
payload = bytes(native.data)
(out / 'catalog.bin').write_bytes(payload)
(out / 'catalog.hash').write_text(hashlib.md5(payload).hexdigest(),'ascii')
manifest.update(catalog_after_sha256=sha(payload),added_catalog_keys=added_keys,
                changed_dependency_locations=changed_dependencies,label_additions=label_additions)
(out / 'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'prepared':str(out),'added_keys':added_keys,'dependency_changes':changed_dependencies,'catalog_bytes':len(payload)}))
