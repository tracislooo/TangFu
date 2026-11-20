from pathlib import Path
import re

root = Path('G:/Doc/ChatGPT/New project')
source = (root / 'set-header-240-v16.py').read_text(encoding='utf-8')
replacements = {
    "BASE = ROOT / '头部与report-max高度300-v15'": "BASE = ROOT / '头部与report-max高度195-v19'",
    "OUT = ROOT / '头部与report-max高度240-v16'": "OUT = ROOT / '头部与report-max高度190-v20'",
    "assert before == [{'unit': 1, 'value': 300.0}]": "assert before == [{'unit': 1, 'value': 195.0}]",
    "dimension(sheet, 240)": "dimension(sheet, 190)",
    "[{'unit': 1, 'value': 240.0}]": "[{'unit': 1, 'value': 190.0}]",
    '统一高度240px v16': '统一高度190px v20',
    '基于v15': '基于v19',
    '300px → 240px': '195px → 190px',
    '之前交付的v15': '之前交付的v19',
    "'height': 240": "'height': 190",
}
for old in replacements:
    assert old in source, old
pattern = re.compile('|'.join(re.escape(s) for s in sorted(replacements, key=len, reverse=True)))
patched = pattern.sub(lambda match: replacements[match.group(0)], source)
exec(compile(patched, str(root / 'set-header-190-v20.py'), 'exec'))
