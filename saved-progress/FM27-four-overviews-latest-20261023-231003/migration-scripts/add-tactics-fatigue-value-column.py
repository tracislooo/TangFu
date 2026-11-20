from pathlib import Path
import copy, datetime, hashlib, json, subprocess, sys

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
F = 'ui-tablefactories_assets_all.bundle'
V = 'ui-tableviews_assets_all.bundle'
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
FACTORY = -7014073910555419620
COLUMN = 'tactics-fatigue-value'
NUMBER_CELL = '7fb52cbb54bc0be45bb85d725b2f53b9'
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT = R / ('tactics-fatigue-value-column-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
before = {f / n: (f / n).read_bytes() for f in [GAME, SKIN] for n in [F, V]}
for n in [F, V]: assert before[GAME / n] == before[SKIN / n], n
for p, b in before.items():
    folder = OUT / ('backup-skin' if p.parent == SKIN else 'backup-game')
    folder.mkdir(exist_ok=True)
    (folder / p.name).write_bytes(b)
protected = {p: sha(p.read_bytes()) for f in [GAME, SKIN] for p in f.glob('*.bundle') if p.name not in [F, V]}
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin']:
    protected[p] = sha(p.read_bytes())
env = {n: UnityPy.load(before[GAME / n]) for n in [F, V]}
obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
hashes = {n: {i: sha(o.get_raw_data()) for i, o in os.items()} for n, os in obs.items()}
expected = {n: {} for n in env}

# Reuse the native integer-capable centered label and fatigue binding.
world = {o.path_id: o for o in UnityPy.load(str(GAME / W)).objects}
numeric = next(o for o in world.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'StandardLabelCellCentered')
nd = numeric.read_typetree()
assert any(a.get('data', {}).get('TextBinding', {}).get('m_direct', {}).get('Path', {}).get('m_path') == 'binding' for a in nd['references']['RefIds'])
meta = next(o for o in world.values() if o.type.name == 'AssetBundle').read_typetree()
assert any(k == NUMBER_CELL and v['asset']['m_PathID'] == numeric.path_id for k, v in meta['m_Container'])

factory = obs[F][FACTORY].read_typetree()
oldfactory = copy.deepcopy(factory)
rows = factory['m_rowData']
assert not any(c['m_id'] == COLUMN for c in rows), 'Fatigue value column already exists'
native = next(c for c in rows if c['m_id'] == 'fatigue-icon')
column = copy.deepcopy(native)
column.update(m_id=COLUMN, m_defaultWidth=56.0, m_minimumWidth=56.0)
column['m_uxmlRef']['m_AssetGUID'] = NUMBER_CELL
assert column['m_valueBindings'][0]['to']['m_path'] == 'binding.Player.fatigue'
assert column['m_sortBinding']['m_path'] == 'binding.Player.fatigue'
assert column['m_translationID']['GameID'] == 3251
condition_index = next(i for i, c in enumerate(rows) if c['m_id'] == 'condition')
rows.insert(condition_index + 1, column)
assert [c for c in rows if c['m_id'] != COLUMN] == oldfactory['m_rowData']
obs[F][FACTORY].save_typetree(factory)
expected[F][FACTORY] = factory

views = []
for o in obs[V].values():
    if o.type.name != 'MonoBehaviour' or not o.peek_name().startswith('TacticTeamSelection') or 'InMatch' in o.peek_name(): continue
    d = o.read_typetree()
    configs = d.get('m_tableView', {}).get('m_tableConfig', [])
    if not any(c['m_columnID'] == 'condition' for c in configs): continue
    original = copy.deepcopy(d)
    assert not any(c['m_columnID'] == COLUMN for c in configs)
    i = next(i for i, c in enumerate(configs) if c['m_columnID'] == 'condition')
    c = copy.deepcopy(configs[i])
    c['m_columnID'] = COLUMN
    c['m_columnMetadata'].update(m_widthOverride=56.0, m_minWidthOverride=56.0)
    c['m_columnMetadata']['m_titleTranslationIdOverride']['GameID'] = 0
    configs.insert(i + 1, c)
    assert configs[i + 1]['m_columnID'] == COLUMN
    assert [x for x in configs if x['m_columnID'] != COLUMN] == original['m_tableView']['m_tableConfig']
    o.save_typetree(d)
    expected[V][o.path_id] = d
    views.append(d['m_Name'])
assert len(views) == 6

outputs = {n: e.file.save(packer='lz4') for n, e in env.items()}
for n, b in outputs.items():
    check = {o.path_id: o for o in UnityPy.load(b).objects}
    assert check.keys() == obs[n].keys()
    for i, h in hashes[n].items():
        if i not in expected[n]: assert sha(check[i].get_raw_data()) == h, (n, i)
    for i, d in expected[n].items(): assert check[i].read_typetree() == d, (n, i)
    (OUT / n).write_bytes(b)

restore = ['$ErrorActionPreference = "Stop"', "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer = list(restore)
for p, b in before.items():
    tag = 'backup-skin' if p.parent == SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '" + str(OUT / tag / p.name) + "' -Destination '" + str(p) + "' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '" + str(p) + "' -Algorithm SHA256).Hash.ToLower() -ne '" + sha(b) + "') { throw 'Package changed since preparation.' }")
for p in before: installer.append("Copy-Item -LiteralPath '" + str(OUT / p.name) + "' -Destination '" + str(p) + "' -Force")
(OUT / 'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
(OUT / 'install.ps1').write_text('\n'.join(installer), 'utf-8-sig')
report = {'installed': False, 'runtime_verified': False, 'column_id': COLUMN, 'header_translation': 3251,
          'binding': column['m_valueBindings'], 'sort': column['m_sortBinding'], 'sort_plugin': column['m_sortBindingPlugin'],
          'format': 'native direct numeric label; raw fatigue including negative values; no percent or scaling',
          'width': 56, 'position': 'immediately after condition/sharpness combined column', 'views': views,
          'existing_columns_preserved': True, 'world_bundle_and_catalog_unchanged': True,
          'after_sha256': {n: sha(b) for n, b in outputs.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
for p, b in before.items(): assert p.read_bytes() == b
for p, h in protected.items(): assert sha(p.read_bytes()) == h
proc = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'waiting_for_game_exit': True, 'output': str(OUT)})); sys.exit(0)
try:
    for n, b in outputs.items():
        for f in [GAME, SKIN]: (f / n).write_bytes(b); assert (f / n).read_bytes() == b
    for p, h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p, b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True, installed_verified=True)
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': True, 'output': str(OUT), 'views': len(views), 'raw_fatigue_binding': 'binding.Player.fatigue'}))
