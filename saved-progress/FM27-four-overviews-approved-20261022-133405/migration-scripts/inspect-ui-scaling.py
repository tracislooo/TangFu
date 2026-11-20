import json
import re
import struct
import sys
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy

BASE = Path('F:/Steam/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for name in ['ui-settings_assets_all.bundle', 'settings_assets_all.bundle', 'ui-styles_assets_.bundle']:
    env = UnityPy.load(str(BASE / name))
    print('BUNDLE', name)
    for o in env.objects:
        if o.type.name in ['MonoBehaviour', 'TextAsset']:
            try:
                d = o.read_typetree()
                print('OBJECT', o.path_id, o.type.name, d.get('m_Name'), 'keys', list(d))
                def walk(value, path=''):
                    if isinstance(value, dict):
                        for key, child in value.items():
                            next_path = path + '/' + key
                            if re.search(r'resolution|scalemode|screensize|reference|dpi|panel|zoom', key, re.I):
                                print('MATCH', next_path, json.dumps(child, ensure_ascii=True)[:2500])
                            else:
                                walk(child, next_path)
                    elif isinstance(value, list):
                        for i, child in enumerate(value):
                            walk(child, path + '/' + str(i))
                walk(d)
                if 'ConfigurationProvider' in d.get('m_Name', ''):
                    for key in ['m_stringConfigValues', 'm_intConfigValues', 'm_boolConfigValues', 'm_floatConfigValues']:
                        for row in d.get(key, []):
                            if re.search(r'resolution|scal|screen|reference|dpi|panel|zoom', json.dumps(row), re.I):
                                print('CONFIG', key, json.dumps(row, ensure_ascii=True))
            except Exception as e:
                print(type(e).__name__, str(e))

DATA = BASE.parent.parent.parent
for name in ['resources.assets', 'sharedassets0.assets', 'globalgamemanagers.assets', 'level0']:
    print('DATAFILE', name)
    env = UnityPy.load(str(DATA / name))
    for o in env.objects:
        if o.type.name not in ['MonoBehaviour', 'MonoScript']:
            continue
        try:
            d = o.read_typetree()
            if o.type.name == 'MonoScript':
                if re.search(r'panelsettings|uiscal|screenscal|resolution', d.get('m_ClassName', ''), re.I):
                    print('SCRIPT', o.path_id, {k: d[k] for k in ['m_Name', 'm_ClassName', 'm_Namespace']})
            elif any(re.search(r'referenceResolution|scaleMode|referenceDpi|matchWidthOrHeight|screenMatchMode', k, re.I) for k in d):
                print('SCALING_OBJECT', o.path_id, json.dumps(d, ensure_ascii=True))
        except Exception as e:
            raw = o.get_raw_data()
            if o.type.name == 'MonoBehaviour' and len(raw) >= 32:
                n, = struct.unpack_from('<i', raw, 28)
                assetname = raw[32:32+n].decode('utf-8', errors='replace') if 0 <= n <= 200 else ''
                if re.search(r'panel|resolution|scal|screen|ui', assetname, re.I):
                    print('RAW_UI_ASSET', o.path_id, assetname, 'script', struct.unpack_from('<iq', raw, 16),
                          'size', len(raw), 'tail', raw[32+n:32+n+120].hex())
