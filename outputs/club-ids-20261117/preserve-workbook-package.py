"""Copy Artifact Tool's authored ID cells into the original WPS package.

The import/export round trip drops the source worksheet's native AutoFilter.
Retaining original package parts preserves that filter and the WPS extensions.
"""
from pathlib import Path
import hashlib
import copy
import io
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent
SOURCE = Path('K:/桌面/27skin/PICTURE/country-new/ALL_clubs_coordinates_latest.xlsx')
RESULT = OUT / 'ALL_clubs_coordinates_latest_球队ID.xlsx'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
original = SOURCE.read_bytes()
source_zip = zipfile.ZipFile(io.BytesIO(original))
authored_zip = zipfile.ZipFile(RESULT)

def read_cells(archive, sheet):
    strings = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        strings = [''.join(n.itertext()) for n in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    cells = {}
    for cell in ET.fromstring(archive.read(sheet)).findall('m:sheetData/m:row/m:c', NS):
        raw = cell.find('m:v', NS)
        inline = cell.find('m:is', NS)
        value = raw.text if raw is not None else ''.join(inline.itertext()) if inline is not None else ''
        if cell.get('t') == 's':
            value = strings[int(value)]
        if value:
            cells[cell.get('r')] = value
    return cells

sheet = 'xl/worksheets/sheet1.xml'
authored = read_cells(authored_zip, sheet)
matches = json.loads((OUT / 'matches.json').read_text('utf8'))
expected = {f"R{r['row']}": str(r['uid']) for r in matches if r['club']}
assert len(expected) == 824
assert all(authored.get(address) == uid for address, uid in expected.items())
assert authored['R1'] == '球队ID'
xml = source_zip.read(sheet).decode('utf8')

def add_id(match):
    row_xml = match.group(0)
    row_number = int(match.group(1))
    address = f'R{row_number}'
    if row_number == 1:
        value = authored['R1']
    else:
        value = expected.get(address)
    if value is None:
        return row_xml
    style_match = re.search(rf'<c\b[^>]*\br="E{row_number}"[^>]*\bs="(\d+)"', row_xml)
    assert style_match, row_number
    style = style_match.group(1)
    cell = f'<c r="{address}" s="{style}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
    row_xml = re.sub(r'spans="1:17"', 'spans="1:18"', row_xml)
    return row_xml.replace('</row>', cell + '</row>')

xml = re.sub(r'<row\b[^>]*\br="(\d+)"[^>]*>.*?</row>', add_id, xml, flags=re.S)
xml = re.sub(r'(<dimension\b[^>]*ref=")A1:Q857', r'\g<1>A1:R857', xml)
xml = re.sub(r'(<autoFilter\b[^>]*ref=")A1:Q857', r'\g<1>A1:R857', xml)
assert '</cols>' in xml
xml = xml.replace('</cols>', '<col min="18" max="18" width="16" customWidth="1"/></cols>')
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for entry in source_zip.infolist():
        archive.writestr(copy.copy(entry), xml.encode('utf8') if entry.filename == sheet else source_zip.read(entry.filename))
final_bytes = buffer.getvalue()
check = zipfile.ZipFile(io.BytesIO(final_bytes))
assert set(check.namelist()) == set(source_zip.namelist())
for name in source_zip.namelist():
    if name != sheet:
        assert check.read(name) == source_zip.read(name), name
before_cells = read_cells(source_zip, sheet)
after_cells = read_cells(check, sheet)
assert {key:value for key,value in after_cells.items() if not key.startswith('R')} == before_cells
assert {key:value for key,value in after_cells.items() if key.startswith('R')} == dict(expected, R1='球队ID')
assert ET.fromstring(check.read(sheet)).find('m:autoFilter', NS).get('ref') == 'A1:R857'
assert SOURCE.read_bytes() == original, 'Source changed while processing'
(OUT / 'original-before-ID-fill.xlsx').write_bytes(original)
RESULT.write_bytes(final_bytes)
temporary = SOURCE.with_name(SOURCE.name + '.codex.tmp')
try:
    temporary.write_bytes(final_bytes)
    os.replace(temporary, SOURCE)
finally:
    if temporary.exists():
        temporary.unlink()
assert SOURCE.read_bytes() == RESULT.read_bytes()
report = dict(filled_clubs=824, blank_source_rows=32, unresolved_clubs=0, original_cells_preserved=True, other_package_parts_byte_identical=True, autofilter='A1:R857', source_updated=str(SOURCE), output=str(RESULT), sha256=hashlib.sha256(final_bytes).hexdigest())
(OUT / 'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True))
