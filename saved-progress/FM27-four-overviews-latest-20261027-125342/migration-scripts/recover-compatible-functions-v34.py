import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

NAME = 'ui-visualfunctions_assets_all.bundle'
SOURCE = ROOT / '四项单图切换整体75-v32' / NAME
OLD = Path('G:/Doc/skins/27_01') / NAME
OUT = ROOT / '修复函数版本报错-v34'
PID = -2894917070210310574
GUID = '139a6658c54dcd543a94e04e35f46c9c'
TEXTURES = [-910000000000008-i for i in range(10)]

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

def sha(b):
    return hashlib.sha256(b).hexdigest()
env = UnityPy.load(str(SOURCE))
objects = {o.path_id: o for o in env.objects}
old_objects = {o.path_id: o for o in UnityPy.load(str(OLD)).objects}
snapshot = json.loads((ROOT / 'render-image-function-v32.json').read_text(encoding='utf-8'))
assert snapshot['pid'] == PID
original_tree = snapshot['tree']
assert old_objects[PID].read_typetree() == original_tree
raw_before = {pid: o.get_raw_data() for pid, o in objects.items()}
af = objects[PID].assets_file
bundle = next(o for o in objects.values() if o.type.name == 'AssetBundle')
meta = bundle.read_typetree()
old_meta = old_objects[bundle.path_id].read_typetree()
original_info = next(info for key, info in old_meta['m_Container'] if key == GUID)
info = next(info for key, info in meta['m_Container'] if key == GUID)
assert info['preloadIndex'] == len(meta['m_PreloadTable']) - 12
assert info['preloadSize'] == 12
assert meta['m_PreloadTable'][-10:] == [{'m_FileID': 0, 'm_PathID': p} for p in TEXTURES]
assert meta['m_PreloadTable'][-12:-10] == meta['m_PreloadTable'][original_info['preloadIndex']:original_info['preloadIndex']+2]
info.update(copy.deepcopy(original_info))
del meta['m_PreloadTable'][-12:]
assert meta == old_meta
bundle.set_raw_data(old_objects[bundle.path_id].get_raw_data())
objects[PID].set_raw_data(old_objects[PID].get_raw_data())
for pid in TEXTURES:
    assert af.objects[pid].type.name == 'Texture2D'
    del af.objects[pid]
assert af.types[-1].class_id == 28
assert all(o.type_id < len(af.types)-1 for o in af.objects.values())
af.types.pop()
OUT.mkdir(exist_ok=True)
(OUT / NAME).write_bytes(env.file.save(packer='lz4'))
restored = {o.path_id: o for o in UnityPy.load(str(OUT / NAME)).objects}
assert len(restored) == 397
assert set(restored) == set(old_objects)
assert restored[PID].read_typetree() == original_tree
assert restored[bundle.path_id].read_typetree() == old_meta
for pid, obj in restored.items():
    if pid not in [PID, bundle.path_id]:
        assert obj.get_raw_data() == raw_before[pid], pid
differences = []
for pid, obj in restored.items():
    if obj.get_raw_data() != old_objects[pid].get_raw_data():
        a, b = obj.read_typetree(), old_objects[pid].read_typetree()
        differences.append({'pid': pid, 'name': a.get('m_Name'),
            'compatible_inputs': [(x['m_name'], x['m_type']['m_typeString']) for x in a.get('m_inputs', [])],
            'incorrect_restore_inputs': [(x['m_name'], x['m_type']['m_typeString']) for x in b.get('m_inputs', [])]})
assert len(differences) == 9
manifest = {'recovered_file': str(OUT / NAME), 'sha256': sha((OUT / NAME).read_bytes()),
    'pre_v32_source_sha256': json.loads((ROOT / '四项单图切换整体75-v32' / '修改记录.json').read_text(encoding='utf-8'))['function_source_sha256'],
    'original_object_count': len(restored), 'added_nodes_removed': True, 'added_textures_removed': True,
    'untouched_objects_verified': True, 'preserved_existing_function_differences': differences,
    'runtime_verified': False}
(OUT / '恢复校验.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(manifest, ensure_ascii=True))
