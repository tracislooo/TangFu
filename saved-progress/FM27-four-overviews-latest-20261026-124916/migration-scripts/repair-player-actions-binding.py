import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

root = Path(__file__).parent
packages = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
name = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
original_banner = root / 'Action移入属性区-20261016-002020/backup/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
source = next(o for o in UnityPy.load(str(original_banner)).objects if o.path_id == -4194025542157271532).read_typetree()
original_menu = next(r['data'] for r in source['references']['RefIds'] if r['type']['class'] == 'PluginContextMenuBindings/UxmlSerializedData')
assert original_menu['BindingPaths'] == [{'m_path': 'Person'}]
out = root / ('Action绑定修正-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
before = (packages / name).read_bytes()
(out / ('backup-' + name)).write_bytes(before)
env = UnityPy.load(before)
hashes = {o.path_id: hashlib.sha256(o.get_raw_data()).hexdigest() for o in env.objects}
changed = {}
old_write = TypeTreeHelper.write_value
def write(v, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData': old_write(v[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag): writer.align_stream()
        return
    return old_write(v, node, writer, config)
TypeTreeHelper.write_value = write
for obj in env.objects:
    if obj.type.name != 'MonoBehaviour' or obj.peek_name() not in {
        'PlayerAttributesTooltipBlock', 'PlayerAttributesSmallBlock', 'PlayerAttributesStandardBlock',
        'PlayerAttributesLargeBlock', 'PlayerAttributesCompactBlock'}: continue
    doc = obj.read_typetree()
    menu = next(r['data'] for r in doc['references']['RefIds'] if r['type']['class'] == 'PluginContextMenuBindings/UxmlSerializedData')
    assert menu['BindingPaths'] == [{'m_path': 'person'}]
    menu['BindingPaths'] = original_menu['BindingPaths']
    assert menu == original_menu, 'The migrated menu must exactly match the original serialized menu'
    obj.save_typetree(doc)
    changed[obj.path_id] = doc
assert len(changed) == 5
data = env.file.save(packer='lz4')
(out / name).write_bytes(data)
reloaded = {o.path_id: o for o in UnityPy.load(data).objects}
assert set(reloaded) == set(hashes)
for i, obj in reloaded.items():
    if i in changed: assert obj.read_typetree() == changed[i]
    else: assert hashlib.sha256(obj.get_raw_data()).hexdigest() == hashes[i]
assert (packages / name).read_bytes() == before
(packages / name).write_bytes(data)
assert (packages / name).read_bytes() == data
manifest = {'change': 'Restore original Person menu binding in all five attribute block configurations',
            'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': hashlib.sha256(data).hexdigest(),
            'changed_objects': list(changed), 'unchanged_objects_verified': len(hashes)-5,
            'menu_matches_original': True, 'runtime_verified': False, 'installed': True}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(str(out)); print(json.dumps(manifest, indent=2))
