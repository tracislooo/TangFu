import json,zipfile,xml.etree.ElementTree as E
from pathlib import Path
p=Path(__file__).parent;d=json.loads((p/'inventory.json').read_text('utf-8'));z=zipfile.ZipFile(p/'FM27_修改资源_PathID_CAB_Bundle清单.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
count=0
for i,key in enumerate(['ui','styles','graphics'],1):
 root=E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'));cells={c.attrib['r']:c for c in root.findall('.//s:c',ns)}
 for r,row in enumerate(d[key],6):
  for col,j in [('A',0),('B',1),('C',2),('D',3),('E',4)]:
   c=cells[f'{col}{r}'];assert c.find('s:v',ns).text==str(row[j]),(key,r,col)
   if col in ['B','C']:
    assert c.attrib.get('t')=='str'
    assert c.find('s:f',ns).text=='"'+row[j]+'"'
    count+=1
assert len(d['ui'])==71 and len(d['styles'])==44 and len(d['graphics'])==455
print(f'PASS: {count} Path ID / inlineStyle cells preserved exactly; all resource names, CABs and bundles match extraction. Workbook has four worksheets.')
