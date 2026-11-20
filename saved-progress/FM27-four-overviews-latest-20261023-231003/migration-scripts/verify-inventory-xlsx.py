import zipfile,json,xml.etree.ElementTree as E
z=zipfile.ZipFile('outputs/image-inventory/243张自定义图片资源资料表.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
root=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={c.attrib['r']:c for c in root.findall('.//s:sheetData/s:row/s:c',ns)}
data=json.load(open('image-inventory-data.json',encoding='utf8'))
for i,r in enumerate(data['rows'],6):
 c=cells['C'+str(i)];assert c.find('s:f',ns).text=='="'+r[2]+'"'
print('All 243 Path IDs preserved exactly as text formulas.')
