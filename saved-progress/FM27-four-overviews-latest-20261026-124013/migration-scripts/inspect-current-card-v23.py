import sys
import json
import hashlib
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
paths = [Path('G:/Doc/ChatGPT/New project/卡面上移15缩放90-v22/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'),
         Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')]
for path in paths:
    env = UnityPy.load(str(path))
    objects = {o.path_id: o for o in env.objects}
    obj = objects[-910000000000003]
    tree = obj.read_typetree()
    print(json.dumps({'path': str(path), 'cab': obj.assets_file.name, 'texture_name': tree['m_Name'],
        'width': tree['m_Width'], 'height': tree['m_Height'], 'format': tree['m_TextureFormat'],
        'stream': tree['m_StreamData'], 'raw_sha256': hashlib.sha256(obj.get_raw_data()).hexdigest(),
        'type_hash': obj.serialized_type.old_type_hash.hex()}, ensure_ascii=True))
