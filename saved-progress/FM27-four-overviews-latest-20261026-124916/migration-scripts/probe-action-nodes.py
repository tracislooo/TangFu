from pathlib import Path
R=Path.cwd();s=(R/'refine-card-inner-layout.py').read_text(encoding='utf8');exec(compile(s.split('\nportrait = rr[1285]')[0],'<loader>','exec'))
for i in [1103,1909,1015,1016,1017]:print(i,json.dumps(rr[i],ensure_ascii=False))

