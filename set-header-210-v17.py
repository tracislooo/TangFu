from pathlib import Path

# Reuse the validated height-only patch workflow with the previous release as baseline.
root = Path('G:/Doc/ChatGPT/New project')
source = (root / 'set-header-240-v16.py').read_text(encoding='utf-8')
replacements = {
    "BASE = ROOT / '头部与report-max高度300-v15'": "BASE = ROOT / '头部与report-max高度240-v16'",
    "OUT = ROOT / '头部与report-max高度240-v16'": "OUT = ROOT / '头部与report-max高度210-v17'",
    "assert before == [{'unit': 1, 'value': 300.0}]": "assert before == [{'unit': 1, 'value': 240.0}]",
    "dimension(sheet, 240)": "dimension(sheet, 210)",
    "[{'unit': 1, 'value': 240.0}]": "[{'unit': 1, 'value': 210.0}]",
    '统一高度240px v16': '统一高度210px v17',
    '基于v15': '基于v16',
    '300px → 240px': '240px → 210px',
    '之前交付的v15': '之前交付的v16',
    "'height': 240": "'height': 210",
}
# Apply substitutions simultaneously so expected old values cannot be replaced twice.
import re
for old in replacements:
    assert old in source, old
pattern = re.compile('|'.join(re.escape(s) for s in sorted(replacements, key=len, reverse=True)))
patched = pattern.sub(lambda match: replacements[match.group(0)], source)
exec(compile(patched, str(root / 'set-header-210-v17.py'), 'exec'))
