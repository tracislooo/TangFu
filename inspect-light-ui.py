"""Read the installed UI resources; never execute historical patch scripts."""
from pathlib import Path
import json, re, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
BASE = Path(loc['bundle_root'])
OUT = R / 'light-ui-inspection'
OUT.mkdir(exist_ok=True)
POOL = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings',
        6: 'assets', 7: 'strings', 8: 'strings'}

def values(sheet, prop):
    return [sheet[POOL[h['m_ValueType']]][h['valueIndex']]
            if h['m_ValueType'] in POOL else h for h in prop['m_Values']]

def selectors(rule):
    return ' | '.join(' '.join(
        ''.join({1: '', 2: '', 3: '.', 4: ':', 5: '?', 6: '#'}.get(p['m_Type'], '?')
                + p['m_Value'] for p in s['m_Parts'])
        for s in c['m_Selectors']) for c in rule['m_ComplexSelectors'])

names = []
for short in ['default', 'common']:
    bn = f'ui-styles_assets_{short}.bundle'
    sheets = []
    for ob in UnityPy.load(str(BASE / bn)).objects:
        if ob.type.name != 'MonoBehaviour': continue
        d = ob.read_typetree()
        if 'm_Rules' not in d: continue
        rules = []
        for i, rule in enumerate(d['m_Rules']):
            rules.append({'index': i, 'selector': selectors(rule),
                          'properties': [{'id': p['m_Id'], 'name': p.get('m_CustomName'),
                                          'value': values(d, p)} for p in rule['m_Properties']]})
        sheets.append({'name': d['m_Name'], 'id': ob.path_id, 'rules': rules})
    (OUT / (short + '-styles.json')).write_text(json.dumps(sheets, ensure_ascii=False, indent=2), 'utf8')
    print(short, [(s['name'], len(s['rules'])) for s in sheets])

for short in ['gameworld', 'global']:
    bn = f'ui-visualtreeassets_assets_{short}visualtreeassetpreload.bundle'
    en = UnityPy.load(str(BASE / bn))
    obs = {o.path_id: o for o in en.objects}
    count = 0
    for ob in obs.values():
        if ob.type.name != 'MonoBehaviour': continue
        name = ob.peek_name() or ''
        if not re.search(r'SquadScreen|TeamSquadViewCard|ClubSquad|SquadList|SquadOverview|FigmaBase|Dialog|Modal|Popup|Drop[Dd]own|dropdown|ContextMenu|VirtualisedTable|PlayerNameCell|TFReferenceBookmarkSidebar', name): continue
        d = ob.read_typetree()
        if 'inlineSheet' not in d: continue
        sh = obs.get(d['inlineSheet']['m_PathID'])
        ss = sh.read_typetree() if sh else None
        rr = {r['rid']: r for r in d['references']['RefIds']}
        nodes = []
        for r in rr.values():
            a = r.get('data', {})
            if 'm_FullTypeName' not in a: continue
            sd = rr.get(a.get('m_SerializedData', {}).get('rid'), {}).get('data', {})
            idx = a.get('m_RuleIndex', -1)
            nodes.append({'rid': r['rid'], 'type': a['m_FullTypeName'], 'name': sd.get('name'),
                          'template': sd.get('templateId'), 'classes': a.get('m_Classes'),
                          'style': [{'id': p['m_Id'], 'name': p.get('m_CustomName'), 'value': values(ss, p)}
                                    for p in ss['m_Rules'][idx]['m_Properties']] if ss and idx >= 0 else [],
                          'data': sd})
        out = {'bundle': bn, 'id': ob.path_id, 'name': name, 'nodes': nodes, 'usings': d.get('m_Usings')}
        (OUT / (short + '-' + re.sub(r'[^\w.-]', '_', name) + '.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2), 'utf8')
        names.append((short, name, ob.path_id, len(nodes)))
        count += 1
    print(short, 'templates', count)
(OUT / 'templates.json').write_text(json.dumps(names, ensure_ascii=False, indent=2), 'utf8')
