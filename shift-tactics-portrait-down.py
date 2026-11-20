"""Shift only the portrait on the current combined and detailed tactics cards."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / 'current-tactics-card-layout.json'
BUNDLE = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
INSTALLER = ROOT / 'install-independent-resource-patch.py'
TOP = 131104
SHIFT = 3


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf8')


def install(patch):
    manifest = json.loads((patch / 'manifest.json').read_text('utf8'))
    index = json.loads(INDEX.read_text('utf8'))
    assert index['patch'] in (manifest['previous_patch'], str(patch)), 'Tactics layout changed since preparation.'
    subprocess.run([sys.executable, str(INSTALLER), str(patch)], check=True)
    index.update(patch=str(patch), installed=True, runtime_verified=False,
                 portrait_top=manifest['portrait_top'], manifest=str(patch / 'manifest.json'))
    write_json(INDEX, index)


def prepare():
    sys.path.insert(0, str(ROOT / '.codex-deps'))
    import UnityPy

    config = json.loads((ROOT / 'current-game-location.json').read_text('utf-8-sig'))
    index = json.loads(INDEX.read_text('utf8'))
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
    patch = ROOT / f'tactics-portrait-down-3px-{stamp}'
    patch.mkdir()
    checks, transactions = [], []
    for tag, folder in [('game', config['bundle_root']), ('skin', config['skin_packages'])]:
        target = Path(folder) / BUNDLE
        original = target.read_bytes()
        env = UnityPy.load(original)
        objects = {obj.path_id: obj for obj in env.objects}
        hashes = {pid: hashlib.sha256(obj.get_raw_data()).hexdigest() for pid, obj in objects.items()}
        changed = {}
        for template in ('TacticsPositionCombined', 'TacticsPositionDetailed'):
            doc = next(obj for obj in objects.values() if obj.type.name == 'MonoBehaviour' and obj.peek_name() == template).read_typetree()
            refs = {record['rid']: record.get('data', {}) for record in doc['references']['RefIds']}
            portrait, = [record for record in refs.values() if 'm_Parent' in record
                         and refs.get(record.get('m_SerializedData', {}).get('rid'), {}).get('name') == 'TacticsPlayerPortraitBinding']
            rule = portrait['m_RuleIndex']
            assert sum(record.get('m_RuleIndex') == rule for record in refs.values()) == 1
            sheet_obj = objects[doc['inlineSheet']['m_PathID']]
            sheet = sheet_obj.read_typetree()
            prop, = [p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == TOP]
            handle, = prop['m_Values']
            assert handle['m_ValueType'] == 3
            old = sheet['dimensions'][handle['valueIndex']]
            assert old['unit'] == 1
            handle['valueIndex'] = len(sheet['dimensions'])
            sheet['dimensions'].append(dict(old, value=old['value'] + SHIFT))
            sheet_obj.save_typetree(sheet)
            changed[sheet_obj.path_id] = sheet
            checks.append({'target': tag, 'template': template, 'before_px': old['value'], 'after_px': old['value'] + SHIFT})

        data = env.file.save(packer='lz4')
        saved = {obj.path_id: obj for obj in UnityPy.load(data).objects}
        assert saved.keys() == objects.keys()
        for pid, obj in saved.items():
            if pid in changed:
                assert obj.read_typetree() == changed[pid]
            else:
                assert hashlib.sha256(obj.get_raw_data()).hexdigest() == hashes[pid]
        backup, source = patch / f'backup-{tag}' / BUNDLE, patch / f'output-{tag}' / BUNDLE
        for path, content in ((backup, original), (source, data)):
            path.parent.mkdir()
            path.write_bytes(content)
        transactions.append({'target': str(target), 'backup': str(backup), 'source': str(source),
                             'before': hashlib.sha256(original).hexdigest(), 'after': hashlib.sha256(data).hexdigest()})

    portrait_top, = {check['after_px'] for check in checks}
    write_json(patch / 'transaction.json', transactions)
    write_json(patch / 'manifest.json', {'previous_patch': index['patch'], 'installed': False, 'runtime_verified': False,
                                        'protected_sha256': {}, 'portrait_top': portrait_top, 'checks': checks})
    install_command = f"& '{sys.executable}' '{__file__}' --install $PSScriptRoot"
    restore_command = f"& '{sys.executable}' '{INSTALLER}' $PSScriptRoot --restore"
    for name, command in (('install.ps1', install_command), ('restore.ps1', restore_command)):
        (patch / name).write_text(command + '\nexit $LASTEXITCODE\n', 'utf-8-sig')
    watcher = f"""$status = Join-Path $PSScriptRoot 'automatic-install-status.txt'
Set-Content -LiteralPath $status -Value 'Waiting for Football Manager to exit normally.'
while (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ Start-Sleep -Seconds 3 }}
{install_command} *> (Join-Path $PSScriptRoot 'automatic-install.log')
if ($LASTEXITCODE -eq 0) {{ Set-Content -LiteralPath $status -Value 'Installed and verified.' }}
else {{ Set-Content -LiteralPath $status -Value 'Installation stopped. See automatic-install.log.' }}
"""
    (patch / 'install-after-game-exits.ps1').write_text(watcher, 'utf-8-sig')
    print(patch)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--install':
        install(Path(sys.argv[2]).resolve())
    else:
        prepare()
