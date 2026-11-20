from pathlib import Path
import re

root = Path('G:/Doc/ChatGPT/New project')
source = (root / 'set-header-240-v16.py').read_text(encoding='utf-8')
replacements = {
    "BASE = ROOT / '头部与report-max高度300-v15'": "BASE = ROOT / '头部与report-max高度190-v20'",
    "OUT = ROOT / '头部与report-max高度240-v16'": "OUT = ROOT / '头部与report-max高度185-v21'",
    "assert before == [{'unit': 1, 'value': 300.0}]": "assert before == [{'unit': 1, 'value': 190.0}]",
    "dimension(sheet, 240)": "dimension(sheet, 185)",
    "[{'unit': 1, 'value': 240.0}]": "[{'unit': 1, 'value': 185.0}]",
    '统一高度240px v16': '统一高度185px v21',
    '基于v15': '基于v20',
    '300px → 240px': '190px → 185px',
    '之前交付的v15': '之前交付的v20',
    "'height': 240": "'height': 185",
}
for old in replacements:
    assert old in source, old
pattern = re.compile('|'.join(re.escape(s) for s in sorted(replacements, key=len, reverse=True)))
patched = pattern.sub(lambda match: replacements[match.group(0)], source)
exec(compile(patched, str(root / 'set-header-185-v21.py'), 'exec'))
