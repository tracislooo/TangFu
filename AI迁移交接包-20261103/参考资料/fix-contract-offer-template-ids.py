"""Align contract template element identities with its updated native consumer."""
import copy, datetime, hashlib, importlib.util, json, os, subprocess, sys, uuid
from pathlib import Path

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

original_write = TypeTreeHelper.write_value
def write_value(value, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(value, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData':
                original_write(value[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):
            writer.align_stream()
        return
    return original_write(value, node, writer, config)
TypeTreeHelper.write_value = write_value

GAME = Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
NAME = 'ContractNegotiationToolTemplate'
GUID = '5f191fc6eb99dde47a955456fecb83e6'
sha = lambda b: hashlib.sha256(b).hexdigest()
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('contract-offer-template-ids-fix-' + stamp)
OUT.mkdir()
source = next(p for p in sorted(R.glob('pinned-1-14-update-*'), reverse=True) if (p/'manifest.json').exists())
source_manifest = json.loads((source/'manifest.json').read_text('utf8'))
native_bytes = (source/'backup-game'/BN).read_bytes()
assert sha(native_bytes) == source_manifest['new_game_before_sha256'][BN]
before = {folder/BN: (folder/BN).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME/BN] == before[SKIN/BN]
protected = {p: sha(p.read_bytes()) for f in [GAME, SKIN] for p in f.glob('*.bundle') if p.name != BN}
for p in [GAME.parent/'catalog.bin', GAME.parent/'catalog.hash', SKIN/'catalog.bin', SKIN/'catalog.hash', R/'current-custom-textures.json', R/'reserved-texture-ids.json']:
    protected[p] = sha(p.read_bytes())
env = UnityPy.load(before[GAME/BN])
objects = {o.path_id: o for o in env.objects}
original_hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
target = next(o for o in objects.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == NAME)
native_env = UnityPy.load(native_bytes)
native = next(o.read_typetree() for o in native_env.objects if o.type.name == 'MonoBehaviour' and o.peek_name() == NAME)
old = target.read_typetree()
new = copy.deepcopy(old)
native_refs = {r['rid']: r for r in native['references']['RefIds']}
changes = []
for row in new['references']['RefIds']:
    data = row.get('data', {})
    nr = native_refs[row['rid']]
    assert row['type'] == nr['type']
    for field in ['m_Id', 'uxmlAssetId']:
        if field in data:
            value = nr['data'][field]
            if data[field] != value:
                changes.append({'rid': row['rid'], 'field': field, 'before': data[field], 'after': value})
                data[field] = value
assert changes
new['m_ContentHash'] = old['m_ContentHash'] + 1

# Build a type-aware GUID index: stylesheets share GUIDs with their visual trees.
index = {}
for path in GAME.glob('ui-visualtreeassets*.bundle'):
    en = env if path.name == BN else UnityPy.load(str(path))
    obs = {o.path_id: o for o in en.objects}
    meta = next(o.read_typetree() for o in en.objects if o.type.name == 'AssetBundle')
    for key, entry in meta['m_Container']:
        ptr = entry['asset']
        ob = obs.get(ptr['m_PathID']) if ptr['m_FileID'] == 0 else None
        if ob and ob.type.name == 'MonoBehaviour':
            tree = ob.read_typetree()
            if 'inlineSheet' in tree:
                index[key] = (path.name, ob.path_id, tree)
assert index[GUID][1] == target.path_id

def resolve(tree, path, replacement):
    if tree['m_Name'] == NAME:
        tree = replacement
    elements = {r['data']['m_Id']: r['data'] for r in tree['references']['RefIds'] if 'm_Id' in r.get('data', {})}
    node = elements.get(path[0])
    if node is None:
        return False
    if len(path) == 1:
        return True
    alias = node.get('m_TemplateAlias')
    using = next((u for u in tree['m_Usings'] if u['alias'] == alias), None)
    return bool(using and using['path'] in index and resolve(index[using['path']][2], path[1:], replacement))

audits = []
for bundle, pid, tree in index.values():
    aliases = {u['alias'] for u in tree['m_Usings'] if u['path'] == GUID}
    for row in tree['references']['RefIds']:
        data = row.get('data', {})
        if data.get('m_TemplateAlias') not in aliases:
            continue
        overrides = data['m_SerializedDataOverride']
        previous = sum(resolve(old, x['m_ElementIdsPath'], old) for x in overrides)
        fixed = sum(resolve(new, x['m_ElementIdsPath'], new) for x in overrides)
        assert fixed == len(overrides), (tree['m_Name'], fixed, len(overrides))
        audits.append({'consumer': tree['m_Name'], 'overrides': len(overrides), 'resolved_before': previous, 'resolved_after': fixed})
assert any(x['consumer'] == 'ContractNegotiationTool' and x['overrides'] == 66 and x['resolved_before'] == 0 for x in audits)

# Validate the runtime resource registration and the owning bundle dependency.
sp = importlib.util.spec_from_file_location('catalog', R/'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(sp); sp.loader.exec_module(cm)
for cp in [GAME.parent/'catalog.bin', SKIN/'catalog.bin']:
    cat = cm.Catalog(cp.read_bytes())
    locations = [cat.location(i) for i in cat.locations(GUID) if cat.location(i)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
    assert len(locations) == 1
    assert cat.location(locations[0]['dependencies'][0])['internal'].endswith(BN)

target.save_typetree(new)
payload = env.file.save(packer='lz4')
check = {o.path_id: o for o in UnityPy.load(payload).objects}
assert set(check) == set(objects)
assert check[target.path_id].read_typetree() == new
for pid, digest in original_hashes.items():
    if pid != target.path_id:
        assert sha(check[pid].get_raw_data()) == digest
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = OUT/('backup-'+tag)/BN
    backup.parent.mkdir(); backup.write_bytes(before[folder/BN])
(OUT/BN).write_bytes(payload)
(OUT/'element-id-changes.json').write_text(json.dumps(changes, indent=2), 'utf8')
report = {'installed': False, 'runtime_verified': False, 'desktop_control_used': False, 'cause': 'All 66 updated ContractNegotiationTool overrides target new element IDs absent from the migrated template.', 'template': NAME, 'guid': GUID, 'path_id': str(target.path_id), 'native_source': str(source/'backup-game'/BN), 'identity_fields_updated': len(changes), 'consumer_audits': audits, 'unrelated_objects_byte_identical': True, 'styles_and_custom_template_links_preserved': True, 'before_sha256': sha(before[GAME/BN]), 'after_sha256': sha(payload), 'protected_sha256': {str(p): h for p, h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
proc = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
assert not proc.stdout.strip(), 'Game must be closed before installation'
for p, data in before.items():
    assert p.read_bytes() == data
for p, digest in protected.items():
    assert sha(p.read_bytes()) == digest
def atomic(path, data):
    tmp = path.with_name(path.name+'.contract-fix-'+uuid.uuid4().hex+'.tmp')
    try:
        tmp.write_bytes(data); os.replace(tmp, path)
    finally:
        if tmp.exists(): tmp.unlink()
try:
    for p in before:
        atomic(p, payload)
        assert p.read_bytes() == payload
    for p, digest in protected.items():
        assert sha(p.read_bytes()) == digest
except BaseException:
    for p, data in before.items(): atomic(p, data)
    raise
restore = ["$ErrorActionPreference='Stop'", "if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}"]
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    restore += ["if((Get-FileHash -LiteralPath '"+str(folder/BN)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(payload)+"'){throw 'Resource changed after repair; do not overwrite newer changes.'}"]
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    restore += ["Copy-Item -LiteralPath '"+str(OUT/('backup-'+tag)/BN)+"' -Destination '"+str(folder/BN)+"' -Force"]
(OUT/'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
report.update(installed=True, installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'output': str(OUT), 'installed': True, 'identity_fields_updated': len(changes), 'consumer_audits': audits, 'runtime_verified': False}, ensure_ascii=False))
