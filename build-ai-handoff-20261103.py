"""Build a text/source handoff; never execute project patch scripts or write game files."""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import subprocess
import zipfile

R = Path(__file__).resolve().parent
O = R / 'AI迁移交接包-20261103'
assert O.is_dir()
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
selected = set()
for pattern in ('*.md', '*.py', 'current-*.json', 'reserved-texture-ids.json'):
    selected.update(p for p in R.glob(pattern) if p.is_file() and p.name != Path(__file__).name)
for p in sorted(selected):
    dest = O / '参考资料' / p.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)

# rg is used for the source inventory, avoiding dependency caches and browser state.
proc = subprocess.run(['rg', '--files', '--hidden', '-g', '!AI迁移交接包-20261103/**',
                       '-g', '!.git/**', '-g', '!.codex-deps/**', '-g', '!**/node_modules/**',
                       '-g', '!**/browser-profile/**', '-g', '!**/__pycache__/**'],
                      cwd=R, capture_output=True, text=True, encoding='utf-8', check=True)
allpaths = [R / line for line in proc.stdout.splitlines() if line.strip()]
record_names = {'manifest.json', 'transaction.json', 'README.md', 'README.txt',
                'automatic-install-status.txt', '安装说明.txt', '修改说明.md', '文件校验清单.json'}
copied_records = []
omitted_records = []
for p in allpaths:
    if p.parent == R or p.name not in record_names or not p.is_file():
        continue
    rel = p.relative_to(R)
    if p.stat().st_size > 2 * 1024 * 1024:
        omitted_records.append({'path': rel.as_posix(), 'reason': 'record exceeds 2 MiB; consult original workspace'})
        continue
    dest = O / '记录' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    copied_records.append(rel.as_posix())

with (O / '工作区文件索引.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['workspace_relative_path', 'size_bytes', 'included_as'])
    writer.writeheader()
    for p in sorted(allpaths):
        if not p.is_file() or p.suffix.lower() == '.zip' and p.stem == O.name:
            continue
        rel = p.relative_to(R).as_posix()
        included = ('参考资料/' + p.name) if p in selected else ('记录/' + rel) if rel in copied_records else ''
        writer.writerow({'workspace_relative_path': rel, 'size_bytes': p.stat().st_size, 'included_as': included})

loc = read(R / 'current-game-location.json')
game = Path(loc['aa_root'])
skin = Path(loc['skin_packages'])
state = read(R / 'current-sidebar-version.json')
names = set()
for rel in ('pinned-1-14-update-20261029-122441/manifest.json', 'main-1-14-rebuild-20261102-101644/manifest.json'):
    names.update(read(R / rel).get('after_sha256', {}))
assets = []
for kind, base in (('installed_game', game), ('independent_main_skin', skin)):
    for n in sorted(names | {'catalog.bin', 'catalog.hash'}):
        path = base / n if kind == 'independent_main_skin' or not n.endswith('.bundle') else base / 'StandaloneWindows64' / n
        row = {'scope': kind, 'path': str(path), 'exists': path.is_file(), 'included_in_handoff': False}
        if path.is_file():
            data = path.read_bytes()
            row.update(size_bytes=len(data), sha256=sha(data))
        assets.append(row)

archives = [R / 'FM27-当前游戏主版本-无侧栏-20261103-060314.zip', Path(state['sidebar_aa_export'])]
for p in archives:
    row = {'scope': 'existing_installation_archive', 'path': str(p), 'exists': p.is_file(), 'included_in_handoff': False}
    if p.is_file():
        row.update(size_bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
        with zipfile.ZipFile(p) as z:
            row['entries'] = z.namelist()
    assets.append(row)

deps = []
for p in (R / '.codex-deps').glob('*.dist-info/METADATA'):
    fields = {}
    for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
        if line.startswith(('Name: ', 'Version: ')):
            k, v = line.split(': ', 1)
            fields[k.lower()] = v
        if 'name' in fields and 'version' in fields:
            break
    deps.append(fields)

write(O / '资产与环境清单.json', {
    'date': '2026-11-03', 'timezone': 'America/Denver', 'workspace': str(R),
    'scope': 'Read-only file identity snapshot; not a new semantic or runtime test. Binary files listed here are not bundled.',
    'current_game_mode_index': state['current_game_mode'], 'independent_skin_mode': 'non-sidebar',
    'paths': loc, 'assets': assets, 'local_dependency_metadata': deps,
    'python_for_this_export': __import__('sys').version,
    'record_files_copied': len(copied_records), 'omitted_large_records': omitted_records,
    'inventory_excludes': ['.git', '.codex-deps', 'node_modules', 'browser-profile', '__pycache__', 'this handoff'],
    'not_included': ['game/skin bundles and catalog binaries', 'source PNG/TTF/OTF assets',
                     'historical binary backups', 'large JSON data unless explicitly copied as a current index',
                     'external graphics/savegames', 'full chat history and screenshot pixels', 'installed Python dependencies'],
    'notes': ['Historical records retain original paths and potentially stale statuses.',
              'Scripts are source references and may have top-level mutations. Do not import or run in bulk.',
              'A copied manifest does not imply its referenced payload/backup was copied.']})

# Produce a portable per-chat textual snapshot without commands or reasoning.
snapshot = read(O / '证据/置顶聊天最近记录.json')
lines = ['# 19个置顶聊天最近文字记录', '', snapshot['scope'], '']
for t in snapshot['threads']:
    lines += ['## ' + t['title'], '', '聊天ID：' + t['id'], '',
              '仍有更早历史：' + str(t['page']['hasMore']), '']
    for turn in t['turns']:
        lines += ['### 轮次 ' + turn['id'] + ' / ' + turn['status'], '']
        for item in turn['items']:
            lines += [('用户' if item['role'] == 'user' else '最终答复') + '：', '', item.get('text') or '', '']
(O / '证据/置顶聊天最近文字记录.md').write_text('\n'.join(lines), encoding='utf-8')

# Manifest is deliberately not self-hashed.
rows = []
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name != '文件校验清单.json':
        data = p.read_bytes()
        rows.append({'path': p.relative_to(O).as_posix(), 'size_bytes': len(data), 'sha256': sha(data)})
write(O / '文件校验清单.json', {'date': '2026-11-03', 'files': rows, 'manifest_self_hash_excluded': True})
dest = O.with_suffix('.zip')
assert not dest.exists(), 'Do not overwrite an existing export'
with zipfile.ZipFile(dest, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(O.rglob('*')):
        if p.is_file():
            z.write(p, (Path(O.name) / p.relative_to(O)).as_posix())
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for row in rows:
        assert sha(z.read(O.name + '/' + row['path'])) == row['sha256']
subprocess.run([__import__('sys').executable, str(O / '校验交接包.py')], check=True)
print(json.dumps({'folder': str(O), 'zip': str(dest), 'files': len(rows) + 1,
                  'pinned_threads': len(snapshot['threads']), 'size_mib': round(dest.stat().st_size / 1024**2, 2),
                  'copied_source_files': len(selected), 'copied_records': len(copied_records),
                  'zip_sha256': sha(dest.read_bytes()), 'verified': True}, ensure_ascii=False))
