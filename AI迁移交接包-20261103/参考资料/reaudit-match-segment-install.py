from pathlib import Path
import json
R=Path.cwd();s=(R/'patch-preferences-lake-gradient.py').read_text('utf8');exec(compile(s[:s.index("W='ui-visualtree")],'<reaudit>','exec'))
out=R/'match-segment-lake-20261101-103000';m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'));targets=set(tx['sources'])
for p,h in m['before_sha256'].items():assert sha(Path(p).read_bytes())==h,p
m['protected_sha256']={p:h for p,h in protected.items() if p not in targets};m['catalog_audits']=audits
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
