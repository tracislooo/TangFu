"""Adjust only the possession SelectionInfo column widths in FM27."""
from datetime import datetime
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy

parser = argparse.ArgumentParser()
parser.add_argument('--effect-width', type=float, default=95.)
parser.add_argument('--role-width', type=float)
parser.add_argument('--position-width', type=float)
parser.add_argument('--prepare-only', action='store_true')
parser.add_argument('--view-scope', choices=['possession', 'selection-info'], default='possession')
args = parser.parse_args()
assert args.effect_width > 0 and all(width is None or width > 0 for width in (args.role_width, args.position_width))

paths = json.loads((ROOT / 'current-game-location.json').read_text('utf-8-sig'))
game = Path(paths['bundle_root']).resolve()
skin = Path(paths['skin_packages']).resolve()
assert game == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64').resolve()
bundle = 'ui-tableviews_assets_all.bundle'
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
output = ROOT / f'tactical-{args.view_scope}-column-widths-{stamp}'
output.mkdir()
sha = lambda data: hashlib.sha256(data).hexdigest()
transaction = {'game': str(game), 'skin': str(skin), 'workspace': str(ROOT), 'sources': {}, 'before': {}}
manifest = {'installed': False, 'runtime_verified': False, 'before_sha256': {}, 'after_sha256': {}, 'protected_sha256': {}, 'views': {}}

for tag, folder in [('game', game), ('skin', skin)]:
    target = folder / bundle
    original = target.read_bytes()
    env = UnityPy.load(original)
    objects = {o.path_id: o for o in env.objects}
    hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
    changed = {}
    views = []
    for pid, obj in objects.items():
        if obj.type.name != 'MonoBehaviour':
            continue
        view_name = obj.peek_name() or ''
        matches = ('TacticTeamSelectionTableView' in view_name and 'SelectionInfo' in view_name
                   if args.view_scope == 'selection-info'
                   else 'TacticTeamSelectionTableViewPossessionSelectionInfo' in view_name)
        if not matches:
            continue
        tree = obj.read_typetree()
        columns = {c['m_columnID']: c['m_columnMetadata'] for c in tree['m_tableView']['m_tableConfig']}
        if 'tactical-effectiveness-gauge' not in columns:
            continue
        widths = {'tactical-effectiveness-gauge': args.effect_width}
        if args.role_width is not None:
            widths['role-ability'] = args.role_width
        if args.position_width is not None:
            widths['positions'] = args.position_width
        for name, width in widths.items():
            columns[name].update(m_widthOverride=width, m_minWidthOverride=width)
        obj.save_typetree(tree)
        changed[pid] = tree
        views.append(tree['m_Name'])
    assert any(name == 'TacticTeamSelectionTableViewPossessionSelectionInfo' for name in views)
    packed = env.file.save(packer='lz4')
    readback = {o.path_id: o for o in UnityPy.load(packed).objects}
    assert readback.keys() == objects.keys()
    for pid, obj in readback.items():
        if pid in changed:
            assert obj.read_typetree() == changed[pid]
        else:
            assert sha(obj.get_raw_data()) == hashes[pid]
    manifest['views'][tag] = views
    manifest['before_sha256'][str(target)] = sha(original)
    manifest['after_sha256'][str(target)] = sha(packed)
    for mode, data, field in [('backup', original, 'before'), ('output', packed, 'sources')]:
        file = output / f'{mode}-{tag}' / bundle
        file.parent.mkdir()
        file.write_bytes(data)
        transaction[field][str(target)] = str(file)

manifest['widths'] = {'effect': args.effect_width, 'role': args.role_width, 'positions': args.position_width}
manifest['view_scope'] = args.view_scope
(output/'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), 'utf8')
(output/'transaction.json').write_text(json.dumps(transaction, indent=2), 'utf8')
installer = ROOT / 'install-native-background-overrides.py'
for name, flag in [('install.ps1', ''), ('restore.ps1', ' --restore')]:
    (output/name).write_text(f"$ErrorActionPreference = 'Stop'\n& '{sys.executable}' '{installer}' $PSScriptRoot{flag}\nif ($LASTEXITCODE) {{ exit $LASTEXITCODE }}\n", 'utf-8-sig')
print(output, flush=True)
if not args.prepare_only:
    subprocess.run([sys.executable, str(installer), str(output)], check=True)
