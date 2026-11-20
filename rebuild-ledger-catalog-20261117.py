
from pathlib import Path
import sys,json,hashlib,importlib.util,struct,zlib
ROOT=Path.cwd();out=Path(sys.argv[1])
read=lambda p:json.loads(p.read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=read(out/'manifest.json')
ledger=Path(read(ROOT/'current-complete-bundle-ledger.json')['archive'])
spec=importlib.util.spec_from_file_location('catalog',ROOT/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
original=cm.Catalog((ledger/'native-baseline/aa/catalog.bin').read_bytes())
skin=cm.Catalog((ledger/'snapshot/current-game/aa/catalog.bin').read_bytes())
native=cm.Catalog((out/'backup-game/catalog.bin').read_bytes())
def locations(cat):
    return {loc:cat.location(loc) for _,ls in cat.keys() for loc, in cat.array(ls,'I')}

def identity(v):
    bundle = v['type'][1].endswith('IAssetBundleResource')
    primary = '' if bundle else v['primary']
    return primary, v['internal'].replace('\\','/'), tuple(v['type']), '' if bundle else v['provider']

old_locs, skin_locs, new_locs = map(locations, [original, skin, native])
old_keys, skin_keys, new_keys = map(lambda c:dict(c.keys()), [original, skin, native])
forced_keys=set(manifest['registered_custom_guids'])-set(new_keys)
forced_identities={identity(skin_locs[loc]) for key in forced_keys if key in skin_keys for loc, in skin.array(skin_keys[key],'I')}
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
    if ident in old_identity and ident not in forced_identities:continue
    assert v['raw'][5] == cm.NULL, ('custom provider metadata',ident)
    template_id = type_templates.get((tuple(v['type']),v['provider']))
    if template_id is None:
        assert v['provider']=='SI.Core.LocalAssetProvider',v
        assert Path(v['internal']).is_file(),v['internal']
        template_id=next(loc for (typ,provider),loc in type_templates.items() if typ==tuple(v['type']))
    template = new_locs[template_id]
    raw = list(template['raw'])
    raw[0] = native.add_string(v['primary'])
    raw[1] = native.add_string(v['internal'])
    raw[2] = native.add_string(v['provider'])
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
    if ident not in old_identity or ident not in new_identity or new_identity[ident] not in new_locs:
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
    if key not in old_keys or key in forced_keys:
        assert key not in new_keys and isinstance(key,str)
        value = native.add_string(key)
        payload = native.append(struct.pack('<IHH',value,0,0))
        key_object = native.append(struct.pack('<2I',string_type,payload))
        location_set = native.append(b''.join(struct.pack('<I',mapped(loc)) for loc in source_locations),True)
        records.append((key_object,location_set))
        added_keys += 1
    else:
        old_set = {identity(old_locs[loc]) for loc, in original.array(old_keys[key],'I')}
        additions = [mapped(loc) for loc in source_locations if (identity(skin_locs[loc]) not in old_set or identity(skin_locs[loc]) in forced_identities) and identity(skin_locs[loc]) in new_identity]
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
