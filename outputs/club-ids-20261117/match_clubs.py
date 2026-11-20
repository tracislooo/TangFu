from pathlib import Path
import collections
import difflib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import struct

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = Path('K:/桌面/27skin/PICTURE/country-new/ALL_clubs_coordinates_latest.xlsx')
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def normalize(name):
    name = unicodedata.normalize('NFKD', name).casefold()
    return ''.join(c for c in name if c.isalnum() and not unicodedata.combining(c))

def short_name(name):
    name = unicodedata.normalize('NFKD', name).casefold()
    words = re.findall(r'\w+', ''.join(c for c in name if not unicodedata.combining(c)))
    return ''.join(w for w in words if w not in {'fc', 'cf', 'sc', 'afc', 'ac', 'fk', 'sk', 'club', 'football', 'futbol', 'calcio', 'de', 'the'})

with zipfile.ZipFile(SOURCE) as archive:
    strings = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        strings = [''.join(n.itertext()) for n in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    rows = []
    for node in ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row', NS)[1:]:
        values = {}
        for cell in node:
            value = cell.find('m:v', NS)
            inline = cell.find('m:is', NS)
            value = value.text if value is not None else ''.join(inline.itertext()) if inline is not None else ''
            if cell.get('t') == 's':
                value = strings[int(value)]
            values[re.sub(r'\d+', '', cell.get('r'))] = value
        rows.append(dict(row=int(node.get('r')), country=values.get('B'), country_key=values.get('A'), club=values.get('F'), club_zh=values.get('G')))

database = json.loads((ROOT / 'analysis/comeback-stadium-20261115/clubs-client.json').read_text('utf8'))
club_data = (OUT / 'clubs-frame.bin').read_bytes()
nation_data = (ROOT / 'analysis/fm27-lang_db-0.bin').read_bytes()
nations = []
position = 12
while position < len(nation_data):
    nation_uid = struct.unpack_from('<I', nation_data, position)[0]
    position += 4
    names = []
    for field in range(4):
        size = struct.unpack_from('<I', nation_data, position)[0]
        position += 4
        names.append(nation_data[position:position+size].decode())
        position += size + (field != 2)
    nations.append(dict(uid=nation_uid, names=names))
country_aliases = {'efl':'England','southkorea':'South Korea','saudi':'Saudi Arabia','usa':'USA','turkey':'Türkiye'}
country_indexes = {}
for key in {r['country_key'] for r in rows if r['country_key']}:
    name = country_aliases.get(key, key)
    country_indexes[key] = {i for i,n in enumerate(nations) if any(normalize(name)==normalize(v) for v in n['names'][:2])}
    assert country_indexes[key], key
country_indexes['efl'].update(i for i,n in enumerate(nations) if n['names'][0] == 'Wales')
def eligible(uid, country):
    club = by_id[uid]
    nation = struct.unpack_from('<I',club_data,club['start']+1)[0]
    gender = club_data[club['end']-13]
    return nation in country_indexes[country] and gender == 0
index = collections.defaultdict(set)
short_index = collections.defaultdict(set)
by_id = {c['id']: c for c in database}
for club in database:
    for name in club['names']:
        index[normalize(name)].add(club['id'])
        short_index[short_name(name)].add(club['id'])
china = json.loads((ROOT / 'china-transparent-map-20261117-194423/club-coordinates.json').read_text('utf8'))['clubs']
aliases = {normalize(c['club']): c['uid'] for c in china}
for c in china:
    aliases[normalize(c['club_zh'])] = c['uid']
unresolved = []
overrides = json.loads((OUT / 'overrides.json').read_text('utf8'))
country_names = {}
for key in country_indexes:
    names = collections.defaultdict(set)
    for uid, club in by_id.items():
        if eligible(uid, key):
            for name in club['names']:
                names[normalize(name)].add(uid)
    country_names[key] = names
for row in rows:
    if not row['club']:
        row.update(uid=None, method='blank_source_row')
        continue
    if str(row['row']) in overrides:
        uid = overrides[str(row['row'])]
        nation = struct.unpack_from('<I', club_data, by_id[uid]['start']+1)[0]
        assert eligible(uid, row['country_key']) or nation == 0xffffffff, (row, uid)
        row.update(uid=uid, method='reviewed_local_database_alias', database_names=by_id[uid]['names'])
        continue
    candidates = index.get(normalize(row['club']), set())
    candidates = {uid for uid in candidates if eligible(uid, row['country_key'])}
    method = 'exact_normalized_name'
    if row['country_key'] == 'china':
        uid = aliases.get(normalize(row['club'])) or aliases.get(normalize(row['club_zh']))
        if uid:
            candidates = {uid}
            method = 'previous_china_identity_mapping'
    if not candidates:
        candidates = {uid for uid in short_index.get(short_name(row['club']), set()) if eligible(uid, row['country_key'])}
        method = 'name_without_club_designators'
    if len(candidates) == 1:
        row.update(uid=next(iter(candidates)), method=method)
    else:
        row.update(uid=None, method='ambiguous' if candidates else 'unmatched')
        if not candidates:
            names = country_names[row['country_key']]
            close = difflib.get_close_matches(normalize(row['club']), names.keys(), n=4, cutoff=.65)
            candidates = {uid for n in close for uid in names[n]}
        row['candidates'] = [dict(uid=uid, names=by_id[uid]['names']) for uid in sorted(candidates)]
        unresolved.append(row)

(OUT / 'matches.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'unresolved.json').write_text(json.dumps(unresolved, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(rows=len(rows), matched=len(rows)-len(unresolved), unresolved=len(unresolved), countries=collections.Counter(r['country_key'] for r in unresolved)), ensure_ascii=True))
for r in unresolved:
    print(json.dumps(r, ensure_ascii=True))

