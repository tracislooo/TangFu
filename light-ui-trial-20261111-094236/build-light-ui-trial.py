"""Prepare a scoped light palette from independent, currently installed bases.

Run via apply-page-surfaces-theme.py --light-trial. Preparation never installs.
Only visual-tree marker classes, inline paint, and appended style rules may differ.
"""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys, zoneinfo

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
src = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.FunctionDef)
                              and n.name == 'write'], type_ignores=[]), '<bundle-codec>', 'exec'))
TypeTreeHelper.write_value = write
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
assert GAME == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = W.replace('gameworld', 'global')
S = 'ui-styles_assets_default.bundle'
FILES = [W, G, S]
SQUAD, DIALOG = 'tf-light-squad-trial', 'tf-light-dialog-trial'
ROOTS = ['.' + SQUAD, '.' + DIALOG, '.si-dropdown__binding-root',
         '.cascading-menu__folder', '.si-dropdown .virtualised-list__item',
         '.cascading-menu__folder__entry']
POOL = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings',
        6: 'assets', 7: 'strings', 8: 'strings'}
PALETTE = {'page': 'E7E7E7', 'card': 'F7F7F5', 'text': '242424',
           'secondary': '62625D', 'border': 'DEDEDA', 'muted': '979792',
           'odd': 'FAFAF8', 'hover': 'EFEFEB', 'selected': 'E5EBEF',
           'pressed': 'DDE4E8', 'control': 'F4F4F1'}
sha = lambda b: hashlib.sha256(b).hexdigest()
f32 = lambda v: struct.unpack('<f', struct.pack('<f', v))[0]
refs = lambda d: {r['rid']: r for r in d['references']['RefIds']}

def filehash(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def color(value):
    code = PALETTE.get(value, value)
    return dict(zip(('r', 'g', 'b', 'a'), [f32(int(code[i:i+2], 16) / 255)
                                         for i in (0, 2, 4)] + [1.]))

def selector(text, index):
    seq, specificity = [], 0
    for token in text.split():
        parts = []
        matches = re.findall(r'([.#:]?)([a-zA-Z_][\w-]*|\*)', token)
        assert ''.join(a + b for a, b in matches) == token, token
        for prefix, value in matches:
            kind = {'.': 3, '#': 6, ':': 4}.get(prefix, 1 if value == '*' else 2)
            parts.append({'m_Value': value, 'm_Type': kind})
            specificity += {1: 0, 2: 1, 3: 10, 4: 10, 6: 100}[kind]
        seq.append({'m_Parts': parts, 'm_PreviousRelationship': 0 if not seq else 2})
    return {'m_Specificity': specificity, 'm_Selectors': seq, 'ruleIndex': index}

def handle(sh, typ, value):
    sh[POOL[typ]].append(copy.deepcopy(value))
    return {'m_ValueType': typ, 'valueIndex': len(sh[POOL[typ]]) - 1}

def prop(sh, key, value):
    return {'m_Id': -1 if isinstance(key, str) else key,
            'm_CustomName': key if isinstance(key, str) else '', 'm_Line': -1,
            'm_Values': [handle(sh, 4, color(value))]}

def append(sh, sels, values):
    idx = len(sh['m_Rules'])
    sh['m_Rules'].append({'m_ComplexSelectors': [selector(s, idx) for s in sels],
                          'm_Properties': [prop(sh, k, v) for k, v in values.items()], 'line': -1})
    return {'index': idx, 'selectors': sels, 'values': values}

def descendants(targets, roots=ROOTS):
    return [root + ' ' + t for root in roots for t in targets]

def theme_variables():
    v = {}
    def put(role, *keys):
        v.update({k: role for k in keys})
    put('text', '--global-text-primary', '--global-text-primary-alt', '--global-text-men-primary',
        '--global-text-women-primary', '--global-text-primary-mens', '--global-text-primary-womens',
        '--buttons-text-default', '--core-controls-text-default', '--core-controls-icon-default',
        '--layout-ui-core-controls-text-default', '--layout-ui-core-controls-icon-default',
        '--modal-text-primary', '--layout-modules-cell-text-base', '--layout-modules-tiles-title-color',
        '--layout-tiles-heading')
    put('secondary', '--global-text-secondary', '--global-text-men-secondary', '--global-text-women-secondary',
        '--global-text-secondary-mens', '--global-text-secondary-womens', '--layout-modules-cell-text-soft',
        '--global-icon-surface', '--global-icon-surface-alt', '--global-icon-surface-transparency')
    put('muted', '--core-controls-text-disabled', '--core-controls-icon-disabled',
        '--layout-ui-core-controls-text-disabled', '--layout-ui-core-controls-icon-disabled')
    put('card', '--layout-ui-global-background', '--layout-ui-cards-light-background',
        '--layout-ui-cards-dark-background', '--layout-ui-tiles-light-background', '--layout-ui-tiles-dark-background',
        '--layout-modules-tiles-background', '--layout-modules-block-surface', '--layout-surfaces-cards-surface',
        '--layout-surfaces-modules-modal', '--layout-surfaces-modal-surface', '--data-tables-background')
    put('page', '--layout-surfaces-report-surface-default', '--layout-surfaces-tools-surface')
    put('odd', '--data-tables-background-odd', '--data-tables-background-accent')
    put('hover', '--data-tables-background-hover', '--theme-core-base-surface-base-hover',
        '--theme-core-base-surface-soft-hover', '--layout-modules-cell-surface-hover')
    put('selected', '--data-tables-background-selected', '--data-tables-background-focus-cell')
    put('pressed', '--theme-core-base-surface-base-pressed', '--theme-core-base-surface-soft-pressed',
        '--layout-modules-cell-surface-pressed')
    put('control', '--theme-core-base-surface-base-default', '--theme-core-base-surface-soft-default',
        '--layout-modules-cell-surface-default', '--interaction-input-switch-inactive-surface-default',
        '--interaction-input-field-active-surface-default', '--interaction-input-field-inactive-surface-default')
    put('hover', '--interaction-input-field-inactive-surface-hover')
    for state, paint in [('default', 'card'), ('hover', 'hover'), ('pressed', 'pressed'), ('highlighted', 'selected')]:
        v['--layout-ui-tiles-interaction-surface-light-' + state] = paint
        v['--layout-ui-tiles-interaction-surface-dark-' + state] = paint
    put('border', '--global-border-color', '--data-tables-border', '--data-tables-border-selected',
        '--layout-ui-global-border', '--layout-ui-cards-light-border', '--layout-ui-cards-dark-border',
        '--layout-ui-tiles-light-border', '--layout-modules-block-border-colour', '--layout-modules-cell-border-color',
        '--layout-surfaces-color', '--theme-core-base-border-base-default', '--theme-core-base-border-soft-default',
        '--buttons-secondary-border-default', '--buttons-secondary-border-hover', '--buttons-secondary-border-disabled',
        '--interaction-input-switch-border-color-default', '--interaction-input-switch-border-color-disabled')
    for prefix in ['--core-controls', '--layout-ui-core-controls']:
        for state, paint in [('default', 'control'), ('hover', 'hover'), ('pressed', 'pressed'), ('disabled', 'control')]:
            v[prefix + '-surface-pc-' + state] = paint
            v[prefix + '-border-pc-' + state] = 'border'
    return v

def add_theme_rules(sh):
    # Revise the latest resources incrementally, including an existing trial.
    records = []
    def rule(sels, values):
        records.append(append(sh, sels, values))
    rule(ROOTS, {**theme_variables(), 65536: 'text'})
    # Neutral labels only: do not override SIText universally or semantic colour roles.
    rule(descendants(['.global-text-primary', '.primary-text-colour', '.modal-text-primary',
                      '.thematic-modal', '.si-dropdown-selection-label']), {65536: 'text'})
    rule(descendants(['.global-text-secondary', '.secondary-text-colour']), {65536: 'secondary'})
    rule(descendants(['#RosterName', '#player-name-button-template #primary-text',
                      '#player-name-button-template .cell-primary-text',
                      '.squad-numbers-dropdown-no-value .sitext'], ROOTS[:1]), {65536: 'text'})
    rule(descendants(['.data-display-data_display-cell-icon-string-transfer-value'], ROOTS[:1]),
         {458752: 'control', 65536: 'text'})
    rule(descendants(['.streamed-table__header']), {458752: 'control', 65536: 'secondary', 262146: 'border'})
    rule(descendants(['.frame-panel-squad', '.layout-tile-interaction-button-background']), {458752: 'card'})
    # Ordinary buttons and fields keep geometry and native click/disabled behaviour.
    buttons = ['.buttons-button-base-default', '.buttons-button-secondary-default',
               '.buttons-hybrid-split-button-right', '.si-dropdown__selection-field']
    rule(descendants(buttons, ROOTS[:2]), {458752: 'control', 262146: 'border', 65536: 'text'})
    rule(descendants([b + ':hover:enabled' for b in buttons], ROOTS[:2]), {458752: 'hover'})
    rule(descendants([b + ':active:enabled' for b in buttons], ROOTS[:2]), {458752: 'pressed'})
    rule(descendants([b + ':disabled' for b in buttons], ROOTS[:2]), {65536: 'muted'})
    rule(descendants(['.bindableeditbox', '.unity-text-field__input'], ROOTS[:2]),
         {458752: 'card', 262146: 'border', 65536: 'text'})
    rule(descendants(['.bindableeditbox:disabled', '.unity-text-field__input:disabled'], ROOTS[:2]),
         {65536: 'muted', 458752: 'control'})
    icons = ['.si-dropdown__selection-arrow', '.indicator-arrow', '.indicator-tick',
             '.indicator-open', '.ui-concepts-chevron-down_small', '.ui-concepts-chevron-right_small',
             '.ui-concepts-chevron-left_small', '.ui-concepts-tick_small', '.ui-concepts-open_small',
             '.ui-concepts-maximise_small', '.ui-concepts-view_small', '.ui-concepts-add-to-list_small',
             '.ui-concepts-close_small', '.ui-concepts-cross_small', '.streamed-table__sort-indicator']
    rule(descendants(icons), {196610: 'secondary'})
    rule(descendants(['.layout-layout-divider-solid-horizontal', '.layout-layout-divider-solid-vertical',
                      '.cascading-menu__folder__separator']), {458752: 'border'})
    rule(descendants(['.streamed-table__checkbox', '.unity-toggle__input'], ROOTS[:2]), {262146: 'secondary'})
    rule(descendants(['.streamed-table__checkbox:checked:enabled .unity-toggle__checkmark',
                      '.unity-toggle:checked:enabled .unity-toggle__checkmark'], ROOTS[:2]), {458752: 'secondary'})
    # Expanded menus are detached from their source page, so style their own roots.
    entries = ['.si-dropdown .virtualised-list__item', '.cascading-menu__folder__entry']
    rule(['.si-dropdown__binding-root', '.cascading-menu__folder',
          '.full-screen-floating-block-anchor-container CascadingMenu',
          '.full-screen-floating-block-anchor-container FolderView',
          '.full-screen-floating-block-anchor-container .si-dropdown__binding-root'],
         {458752: 'card', 262146: 'border', 65536: 'text'})
    rule(entries, {458752: 'card', 262146: 'border'})
    rule([e + '.virtualised-list__item--odd' for e in entries], {458752: 'odd'})
    # Match native selector specificity, including the duplicated hover selector.
    rule([e + ':hover' for e in entries] + [e + '.visual-highlighted' for e in entries]
         + [e + '.virtualised-list__item--odd:hover' for e in entries]
         + ['.cascading-menu__folder__entry:hover.virtualised-list__item:hover'], {458752: 'hover'})
    rule([e + ':active:enabled' for e in entries] + [e + '.virtualised-list__item--odd:active:enabled' for e in entries],
         {458752: 'pressed'})
    rule([e + '.virtualised-list__item--selected' for e in entries]
         + [e + '.virtualised-list__item--selected:hover' for e in entries]
         + ['.cascading-menu__folder__entry__selected'], {458752: 'selected'})
    rule([e + '.unity-disabled .sitext' for e in entries]
         + [e + ':disabled .sitext' for e in entries], {65536: 'muted'})
    # A primary action's established cyan gradient needs its existing white label.
    rule(descendants(['SIButton.fm27-lake-action:enabled SIText',
                      'SIButton.fm27-lake-action:enabled .global-text-primary'], ROOTS[:2]), {65536: 'FFFFFF'})
    return records

def patch_doc(obs, name, marker, backgrounds):
    found = [o for o in obs.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name]
    assert len(found) == 1, (name, len(found))
    ob = found[0]
    original = ob.read_typetree()
    d = copy.deepcopy(original)
    sid = d['inlineSheet']['m_PathID']
    so = obs[sid]
    sh = so.read_typetree()
    old_sh = copy.deepcopy(sh)
    rr = refs(d)
    elements = {i: r for i, r in rr.items() if 'm_Parent' in r.get('data', {})}
    root = next(r for r in elements.values() if r['data']['m_Parent']['rid'] == d['m_VisualTree']['rid'])
    if marker not in root['data']['m_Classes']:
        root['data']['m_Classes'].append(marker)
    changed = []
    for rid, role in backgrounds.items():
        assert rid in elements
        a = rr[rid]['data']
        prev_idx = a['m_RuleIndex']
        old_props = copy.deepcopy(sh['m_Rules'][prev_idx]['m_Properties']) if prev_idx >= 0 else []
        # Paint only. Keep any image, all sizes, and every non-paint property.
        new_prop = prop(sh, 458752, role)
        a['m_RuleIndex'] = len(sh['m_Rules'])
        sh['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties':
                              [p for p in old_props if p['m_Id'] != 458752] + [new_prop], 'line': -1})
        changed.append({'rid': rid, 'background': role, 'previous_rule': prev_idx,
                        'new_rule': a['m_RuleIndex']})
    normalized = copy.deepcopy(d)
    nn = refs(normalized)
    nn[root['rid']]['data']['m_Classes'] = copy.deepcopy(refs(original)[root['rid']]['data']['m_Classes'])
    for item in changed:
        nn[item['rid']]['data']['m_RuleIndex'] = item['previous_rule']
    assert normalized == original, ('Non-style document change', name)
    assert sh['m_Rules'][:len(old_sh['m_Rules'])] == old_sh['m_Rules']
    for pool in POOL.values():
        assert sh[pool][:len(old_sh[pool])] == old_sh[pool]
    ob.save_typetree(d)
    so.save_typetree(sh)
    return {ob.path_id: d, sid: sh}, {'template': name, 'id': ob.path_id, 'style': sid,
                                    'root': root['rid'], 'marker': marker, 'paint': changed,
                                    'bindings_layout_ids_and_children_unchanged': True}

def bind_tile_surfaces(obs):
    """Use the existing context variable for neutral inline card paint.

    Its unscoped native value is still #263445. Only the trial overrides it.
    """
    expected, edits = {}, []
    for ob in list(obs.values()):
        name = ob.peek_name() if ob.type.name == 'MonoBehaviour' else ''
        if not name or not name.startswith('tile-figma-') or 'fixture-background' in name:
            continue
        original = ob.read_typetree()
        if 'inlineSheet' not in original: continue
        d = copy.deepcopy(original)
        sid = d['inlineSheet']['m_PathID']
        so = obs[sid]
        sh = so.read_typetree()
        old_sh = copy.deepcopy(sh)
        changed = []
        for rec in refs(d).values():
            a = rec.get('data', {})
            if 'layout-tile-interaction-button-background' not in a.get('m_Classes', []): continue
            idx = a.get('m_RuleIndex', -1)
            if idx < 0: continue
            props = copy.deepcopy(sh['m_Rules'][idx]['m_Properties'])
            bg = next((p for p in props if p['m_Id'] == 458752), None)
            if not bg: continue
            vals = bg['m_Values']
            if len(vals) != 1 or vals[0]['m_ValueType'] != 4: continue
            c = sh['colors'][vals[0]['valueIndex']]
            if any(abs(c[k] - color('263445')[k]) > 1e-6 for k in ['r','g','b','a']): continue
            bg['m_Values'] = [{'m_ValueType': 10, 'valueIndex': 1}, handle(sh, 2, 1.),
                              handle(sh, 8, '--layout-modules-block-surface')]
            a['m_RuleIndex'] = len(sh['m_Rules'])
            sh['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': props, 'line': -1})
            changed.append({'rid': rec['rid'], 'previous_rule': idx, 'new_rule': a['m_RuleIndex'],
                            'background_variable': '--layout-modules-block-surface'})
        if not changed: continue
        norm = copy.deepcopy(d)
        nr = refs(norm)
        for edit in changed: nr[edit['rid']]['data']['m_RuleIndex'] = edit['previous_rule']
        assert norm == original
        assert sh['m_Rules'][:len(old_sh['m_Rules'])] == old_sh['m_Rules']
        ob.save_typetree(d)
        so.save_typetree(sh)
        expected.update({ob.path_id: d, sid: sh})
        edits.append({'template': name, 'id': ob.path_id, 'style': sid,
                      'paint': changed, 'outside_trial_uses_original_native_variable': True,
                      'bindings_layout_ids_and_children_unchanged': True})
    return expected, edits

def main():
    stamp = datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S')
    out = R / ('light-ui-trial-' + stamp)
    out.mkdir()
    targets = {folder / name for folder in [GAME, SKIN] for name in FILES}
    before = {p: p.read_bytes() for p in targets}
    print('Reading current resources and preserving unrelated bundles...', flush=True)
    protected = {str(p): filehash(p) for folder in [GAME, SKIN]
                 for p in folder.glob('*.bundle') if p not in targets}
    for folder in [GAME.parent, SKIN]:
        for name in ['catalog.bin', 'catalog.hash']:
            p = folder / name
            if p.exists(): protected[str(p)] = filehash(p)
    for name in ['reserved-texture-ids.json', 'current-custom-textures.json']:
        p = R / name
        protected[str(p)] = filehash(p)
    previous_trial = json.loads((R / 'current-ui-surface-theme.json').read_text('utf8')).get('light_trial')
    manifest = {'installed': False, 'runtime_verified': False, 'scope': 'SquadScreen and SquadOverviewTableBlock, including neutral tile surfaces; shared expanded dropdowns and GenericModalDialog',
                'palette': PALETTE, 'before_sha256': {str(p): sha(v) for p, v in before.items()},
                'after_sha256': {}, 'protected_sha256': protected, 'changes': [], 'objects': {},
                'original_ui_surface_index': json.loads((R / 'current-ui-surface-theme.json').read_text('utf8')),
                'previous_trial_state': previous_trial,
                'sidebar_index_sha256': filehash(R / 'current-sidebar-version.json')}
    tx = {'game': str(GAME), 'skin': str(SKIN), 'workspace': str(R), 'sources': {}, 'before': {}}
    for tag, folder in [('game', GAME), ('skin', SKIN)]:
        for bn in FILES:
            p = folder / bn
            en = UnityPy.load(before[p])
            obs = {o.path_id: o for o in en.objects}
            expected = {}
            if bn == W:
                for name, bgs in [('SquadScreen', {1001: 'page', 1008: 'page'}),
                                  ('SquadOverviewTableBlock', {1001: 'page', 1007: 'card', 1174: 'card'})]:
                    # The independent skin may legitimately lack the added portrait strip.
                    if name == 'SquadOverviewTableBlock':
                        host = next(o.read_typetree() for o in obs.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name)
                        if 1174 not in refs(host): bgs = {k: v for k, v in bgs.items() if k != 1174}
                        else:
                            rr = refs(host)
                            assert rr[rr[1174]['data']['m_SerializedData']['rid']]['data']['name'] == 'TFClubSquadRosterStrip'
                    exp, change = patch_doc(obs, name, SQUAD, bgs)
                    expected.update(exp)
                    manifest['changes'].append({'target': str(p), **change})
            elif bn == G:
                exp, change = patch_doc(obs, 'GenericModalDialog', DIALOG, {1008: 'card'})
                expected.update(exp)
                manifest['changes'].append({'target': str(p), **change})
                exp, tile_changes = bind_tile_surfaces(obs)
                expected.update(exp)
                manifest['changes'].extend({'target': str(p), **c} for c in tile_changes)
            else:
                ob = next(o for o in obs.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'AlwaysAppliedStyleSheet')
                original = ob.read_typetree()
                sh = copy.deepcopy(original)
                rules = add_theme_rules(sh)
                assert sh['m_Rules'][:len(original['m_Rules'])] == original['m_Rules']
                normalized = copy.deepcopy(sh)
                normalized['m_Rules'] = normalized['m_Rules'][:len(original['m_Rules'])]
                for pool in set(POOL.values()): normalized[pool] = normalized[pool][:len(original[pool])]
                assert normalized == original
                ob.save_typetree(sh)
                expected[ob.path_id] = sh
                manifest['changes'].append({'target': str(p), 'sheet': ob.peek_name(), 'id': ob.path_id, 'rules': rules})
                if tag == 'game':
                    # Human-readable equivalent of the appended compiled rules.
                    lines = []
                    ids = {65536: 'color', 458752: 'background-color', 196610: '-unity-background-image-tint-color', 262146: 'border-color'}
                    for rule in rules:
                        lines.append(',\n'.join(rule['selectors']) + ' {')
                        lines.extend('    ' + (key if isinstance(key, str) else ids[key]) + ': #' + PALETTE.get(value, value) + ';'
                                     for key, value in rule['values'].items())
                        lines.append('}\n')
                    (out / 'light-trial.uss').write_text('\n'.join(lines), 'utf8')
            raw = en.file.save(packer='lz4')
            saved = {o.path_id: o for o in UnityPy.load(raw).objects}
            baseline = {o.path_id: o for o in UnityPy.load(before[p]).objects}
            assert set(saved) == set(baseline), 'Object inventory changed'
            changed_ids = []
            for pid, ob in saved.items():
                if pid in expected:
                    assert ob.read_typetree() == expected[pid], ('Roundtrip failed', p, pid)
                    changed_ids.append(str(pid))
                else:
                    assert ob.get_raw_data() == baseline[pid].get_raw_data(), ('Unrelated object changed', p, pid)
            dest, backup = out / tag / bn, out / ('backup-' + tag) / bn
            for path, data in [(dest, raw), (backup, before[p])]:
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(data)
            manifest['after_sha256'][str(p)] = sha(raw)
            manifest['objects'][str(p)] = {'changed_ids': changed_ids, 'total_objects': len(saved), 'all_other_objects_byte_identical': True}
            tx['sources'][str(p)] = str(dest)
            tx['before'][str(p)] = str(backup)
            print(tag, bn, 'verified changed objects:', len(expected), flush=True)
    for p, raw in before.items(): assert p.read_bytes() == raw, ('Baseline changed while preparing', p)
    for path, digest in protected.items(): assert filehash(Path(path)) == digest, ('Concurrent change', path)
    manifest['prepared_verified'] = True
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
    (out / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
    (out / 'installer.py').write_bytes((R / 'install-light-ui-trial.py').read_bytes())
    for name, flag in [('install', ''), ('restore', ' --restore'), ('verify', ' --verify')]:
        (out / (name + '.ps1')).write_text("$ErrorActionPreference='Stop'\n& '" + sys.executable + "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + flag + "\nif($LASTEXITCODE -ne 0){throw 'Operation failed; see error above.'}\n", 'utf-8-sig')
    (out / '说明.md').write_text('浅色试版修订：一线队页面/列表、共用展开下拉菜单、标准确认弹窗。底色E7E7E7、卡片/弹窗F7F7F5、深灰字242424。修复试版范围内卡片写死深色底与球员姓名可读性；其他页面的普通卡片沿用原生变量默认深色。\n\n游戏与独立主皮肤分别从最新资源增量制作。保留布局、侧栏状态、绑定、数据配色、纹理与目录。菜单与标准弹窗属于共用控件，其他页面调用时同样为浅色。实际显示待用户检查。\n\ninstall.ps1安装，verify.ps1校验，restore.ps1仅回退本轮修订到安装前版本。安装和回退均要求退出游戏并校验哈希；后续资源有改动时须重迁移，不可旧包覆盖。light-trial.uss为新增规则的可读副本。\n', 'utf8')
    (out / 'build-light-ui-trial.py').write_bytes(Path(__file__).read_bytes())
    state = {'status': 'prepared', 'installed': False, 'runtime_verified': False,
             'record': str(out), 'manifest': str(out / 'manifest.json'), 'palette': PALETTE,
             'scope': manifest['scope'], 'restore': str(out / 'restore.ps1')}
    (R / 'current-light-ui-trial.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps({'prepared': True, 'output': str(out), 'files': len(tx['sources'])}, ensure_ascii=False), flush=True)

if __name__ == '__main__': main()
