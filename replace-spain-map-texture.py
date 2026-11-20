from pathlib import Path
import datetime
import hashlib
import json
import runpy
import sys
import uuid

root = Path(__file__).resolve().parent
helpers = runpy.run_path(str(root / 'build-packed-club-location.py'))
catalog_type = runpy.run_path(str(root / 'catalog-binary-v35.py'))['Catalog']
read_json, sha = helpers['read_json'], helpers['sha']
bundle, layout = helpers['BACKGROUNDS'], helpers['WORLD_VTA']
source = helpers['DATA'] / '796.png'
image = helpers['Image'].open(source).convert('RGBA')
assert image.size == (1920, 1080) and image.getchannel('A').getextrema() == (0, 255)
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = root / ('club-spain-796-texture-' + stamp)
out.mkdir()
archived = out / '796.png'
archived.write_bytes(source.read_bytes())
assert archived.read_bytes() == source.read_bytes()
print(out, flush=True)
config = read_json(root / 'current-game-location.json')
registry_path = root / 'current-custom-textures.json'
registry = read_json(registry_path)
slot = next(index for index, item in enumerate(registry['textures']) if item['name'] == '796')
old_record = registry['textures'][slot]
transactions, protected, audits = [], {}, []


def stage(tag, target, before, after):
    helpers['stage'].__globals__.update(OUT=out, transactions=transactions)
    helpers['stage'](tag, target, before, after)


for tag, folder in [('game', Path(config['bundle_root'])), ('skin', Path(config['skin_packages']))]:
    target = folder / bundle
    before = target.read_bytes()
    old_object = next(obj for obj in helpers['UnityPy'].load(before).objects if obj.path_id == int(old_record['path_id']))
    assert sha(old_object.get_raw_data()) == old_record['texture_sha256']
    after, record = helpers['add_spain'](before, archived)
    assert record['path_id'] == old_record['path_id']
    protected[str(folder / layout)] = sha((folder / layout).read_bytes())
    catalog_path = (folder.parent if tag == 'game' else folder) / 'catalog.bin'
    catalog_before = catalog_path.read_bytes()
    catalog = catalog_type(catalog_before)
    guid = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27/club-location/packed-map/796').hex
    locations = catalog.locations(guid)
    assert len(locations) == 1
    location = catalog.location(locations[0])
    assert location['type'][1] == 'UnityEngine.Texture2D' and location['internal'] == '796'
    assert bundle in catalog.location(location['dependencies'][0])['internal']
    catalog_after, crc = helpers['sync_catalog_crc'](catalog_type, catalog_before, {bundle: after}, tag == 'game')
    assert catalog_type(catalog_after).location(locations[0]) == location
    stage(tag, target, before, after)
    if catalog_after != catalog_before:
        stage(tag, catalog_path, catalog_before, catalog_after)
        hash_path = catalog_path.with_suffix('.hash')
        stage(tag, hash_path, hash_path.read_bytes(), hashlib.md5(catalog_after).hexdigest().encode())
    else:
        for path in (catalog_path, catalog_path.with_suffix('.hash')):
            protected[str(path)] = sha(path.read_bytes())
    audits.append(dict(target=tag, guid=guid, bundle_crc_size=crc, texture=record))
    print(tag, 'verified', flush=True)

assert audits[0]['texture'] == audits[1]['texture']
registry['textures'][slot] = dict(old_record, **record)
registry.update(authoritative_source_bundle=str(out / 'game' / bundle),
                source_bundle_sha256=transactions[0]['after'], manifest=str(out / 'manifest.json'))
stage('registry', registry_path, registry_path.read_bytes(), json.dumps(registry, ensure_ascii=False, indent=2).encode('utf8'))
helpers['dump'](out / 'transaction.json', transactions)
helpers['dump'](out / 'manifest.json', dict(installed=False, runtime_verified=False, texture_registry_transaction=True,
                                         source=str(source), source_sha256=sha(archived.read_bytes()), protected_sha256=protected, audits=audits))
for action, extra in [('install', ''), ('restore', ' --restore')]:
    installer = root / 'install-independent-resource-patch.py'
    script = f"$ErrorActionPreference='Stop'\n& '{sys.executable}' '{installer}' $PSScriptRoot{extra}\nif ($LASTEXITCODE -ne 0) {{throw 'Operation failed'}}\n"
    (out / (action + '.ps1')).write_text(script, 'utf-8-sig')
