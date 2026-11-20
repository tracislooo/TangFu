"""只读校验交接包，不导入历史脚本，也不访问游戏目录。"""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root / '文件校验清单.json').read_text(encoding='utf-8'))
failures = []
for row in manifest['files']:
    path = (root / row['path']).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        failures.append(row['path'])
    elif hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
        failures.append(row['path'])
print(json.dumps({'checked': len(manifest['files']), 'passed': not failures, 'failures': failures}, ensure_ascii=False))
sys.exit(bool(failures))
