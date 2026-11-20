"""Restore the chart-specific paint class accidentally discarded during cloning."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
module = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'write'], type_ignores=[]), 'serializer', 'exec'))
TypeTreeHelper.write_value = write
sha = lambda b: hashlib.sha256(b).hexdigest()
index = R / 'current-player-overview-test-variant.json'
previous = json.loads(index.read_text('utf8'))
manifest = json.loads(Path(previous['manifest']).read_text('utf8'))
previous_tx = json.loads(Path(previous['manifest']).with_name('transaction.json').read_text('utf8'))
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT = R / ('season-radar-native-paint-style-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
transactions, checks = [], []
for tag, root in [('game', Path(loc['bundle_root'])), ('skin', Path(loc['skin_packages']))]:
    path = root / W
    before = path.read_bytes()
    prior = next(row for row in previous_tx if Path(row['target']) == path)
    assert sha(before) == prior['after'], ('Changed baseline', tag)
    env = UnityPy.load(before)
    objects = {o.path_id: o for o in env.objects}
    baseline = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
    native = objects[-7642202103200103126].read_typetree()
    prototype = next(r['data'] for r in native['references']['RefIds'] if r.get('data', {}).get('m_FullTypeName') == 'FM.UI.FMSpiderChart')
    assert 'fmspiderchartlarge' in prototype['m_Classes']
    original = objects[manifest['stats']].read_typetree()
    modified = copy.deepcopy(original)
    charts = [r['data'] for r in modified['references']['RefIds'] if r.get('data', {}).get('m_FullTypeName') == 'FM.UI.FMSpiderChart']
    assert len(charts) == 2 and all(c['m_Classes'] == [] for c in charts)
    for chart in charts:
        chart['m_Classes'] = ['fmspiderchartlarge']
    objects[manifest['stats']].save_typetree(modified)
    output = env.file.save(packer='lz4')
    reread = {o.path_id: o for o in UnityPy.load(output).objects}
    assert reread.keys() == objects.keys()
    for pid, digest in baseline.items():
        if pid != manifest['stats']:
            assert sha(reread[pid].get_raw_data()) == digest, (tag, pid)
    actual = reread[manifest['stats']].read_typetree()
    assert actual == modified
    for ref in actual['references']['RefIds']:
        if ref.get('data', {}).get('m_FullTypeName') == 'FM.UI.FMSpiderChart':
            assert ref['data']['m_Classes'] == ['fmspiderchartlarge']
            ref['data']['m_Classes'] = []
    assert actual == original, 'Only the two chart class lists may change'
    src, backup = OUT / tag / W, OUT / ('backup-' + tag) / W
    src.parent.mkdir(); backup.parent.mkdir()
    src.write_bytes(output); backup.write_bytes(before)
    transactions.append(dict(target=str(path), source=str(src), backup=str(backup), before=sha(before), after=sha(output)))
    checks.append(dict(target=tag, chart_classes_restored=2, other_serialized_fields_identical=True, unrelated_objects_byte_identical=True))
    print('Verified ' + tag, flush=True)
manifest.update(installed=False, installed_verified=False, runtime_verified=False,
                previous_fix_manifest=previous['manifest'], change='Restore native fmspiderchartlarge paint class only', checks=checks)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transactions, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'previous-index.json').write_text(json.dumps(previous, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'installer.py').write_text((R / 'install-independent-resource-patch.py').read_text('utf8'), 'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable + "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode + "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
(OUT / 'verification-prepared.json').write_text(json.dumps(dict(passed=True, checks=checks, runtime_verified=False), indent=2), 'utf8')
(R / 'season-radar-style-repair-prepared.json').write_text(json.dumps(dict(output=str(OUT)), indent=2), 'utf8')
print(str(OUT))
