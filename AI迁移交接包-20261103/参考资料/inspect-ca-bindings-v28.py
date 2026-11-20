import json
import sys
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
ROOT = Path('G:/Doc/ChatGPT/New project')
BASE = ROOT / '卡面98总上移10头像70-v27'
report = []
for name in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle', 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
    env = UnityPy.load(str(BASE / name))
    for o in env.objects:
        if o.type.name != 'MonoBehaviour':
            continue
        raw = o.get_raw_data()
        if not any(t in raw for t in [b'CurrentAbility', b'currentability', b'CA000']):
            continue
        try:
            tree = o.read_typetree()
        except Exception:
            continue
        rows = []
        for r in tree.get('references', {}).get('RefIds', []):
            if any(t in json.dumps(r).lower() for t in ['currentability', 'sistylesetter', 'sishow', 'siconditional', 'sibinding']):
                rows.append(r)
        item = {'bundle': name, 'pid': o.path_id, 'name': tree.get('m_Name'), 'records': rows,
                'usings': tree.get('m_Usings', [])}
        report.append(item)
        print(json.dumps(item, ensure_ascii=True))
(ROOT / 'ca-binding-inspection-v28.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
