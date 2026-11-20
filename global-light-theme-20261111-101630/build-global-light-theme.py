"""Apply a complete neutral light UI palette to current independent resource bases.

Only paint in stylesheet objects and VTA inline-rule indices may change. Geometry,
serialized data, events, textures, catalogs, and gameplay colour roles are retained.
All new inline paint is literal; inline var() is prohibited.
"""
from pathlib import Path
from collections import Counter
import copy, datetime, importlib.util, json, re, sys, zoneinfo

R = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('trial_palette', R / 'build-light-ui-trial.py')
ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)
UnityPy, GAME, SKIN = ui.UnityPy, ui.GAME, ui.SKIN
PALETTE = {**ui.PALETTE, 'link': '14627B'}
STYLE_FILES = ['ui-styles_assets_default.bundle', 'ui-styles_assets_common.bundle']
PAINT = {65536, 458752, 196610, 262146, 458758, 458761, 458762, 458763}
SEMANTIC = re.compile(r'ability|potential|rating|condition-level|fatigue|sharpness|'
    r'fitness|morale|footed|foot-|injur|heatmap|heat-map|radar|chart|graph|progress|gauge|'
    r'linear-range|linear_range|ranges-|shirt|kit-|kit_|club-primary|club-secondary|team-colou?r|'
    r'pitch|possession-phase|position-colou?r|position-color|status-colou?r|status-color|'
    r'body.?language|status-icon|qualification|communication-feedback|calendar-training|'
    r'priority-|urgency-|severity-|finance-positive|finance-negative|attribute-|attributes-')
OVERLAY = re.compile(r'scrim|dimmer|shadow|sipopup-container|modal-overlay|modal-backdrop|'
                     r'background-dim|greyed-out|darkening|overlay-background')
IMAGE = re.compile(r'portrait|personpicture|person-picture|clubicon|club-icon|nationicon|nation-icon|'
                   r'flag|crest|badge|stadium|background-picture|tfwx|kunshan|patchplayer|skin-v1')
FOUNDATION = re.compile(r'^(white|black|transparent|colours?-[\w-]+|linear-[\w-]+|tifo-text-base-[\w-]+)$')
PRIMARY = re.compile(r'fm27-lake-action|continue-button|continuebutton|buttons-button-primary|'
                     r'buttons-quick-action-primary|button-primary-|buttons-primary|button-danger|button-success')
MARK = 'tf-global-light-theme-v1'

def cname(selector):
    return ' '.join(''.join({3: '.', 4: ':', 6: '#'}.get(p['m_Type'], '') + p['m_Value']
                            for p in s['m_Parts']) for s in selector['m_Selectors'])

def rgba(sh, prop, definitions, seen=()):
    hs = prop['m_Values']
    if len(hs) == 1 and hs[0]['m_ValueType'] == 4:
        return sh['colors'][hs[0]['valueIndex']]
    if len(hs) == 3 and hs[0]['m_ValueType'] == 10 and hs[2]['m_ValueType'] == 8:
        name = sh['strings'][hs[2]['valueIndex']]
        if name in seen or name not in definitions: return None
        source, p = definitions[name]
        return rgba(source, p, definitions, (*seen, name))
    return None

def neutral(c):
    if not c or c['a'] <= .025: return False
    rgb = [c[k] for k in ['r', 'g', 'b']]
    return max(rgb) - min(rgb) <= .105 or (
        max(rgb) <= .32 and max(rgb) - min(rgb) <= .18)

def paint(role, alpha=1.):
    c = ui.color(PALETTE.get(role, role))
    c['a'] = ui.f32(alpha)
    return c

def surface_role(context):
    text = context.lower()
    if any(x in text for x in ['--selected', ':checked', '--active', '-active-true', 'highlighted', 'cell--selected']): return 'selected'
    if ':active' in text or 'pressed' in text: return 'pressed'
    if 'hover' in text or 'visual-highlighted' in text: return 'hover'
    if '--odd' in text or 'background-odd' in text: return 'odd'
    if any(x in text for x in ['sidebar', 'touchbar', 'mainnav', 'primary-navigation', 'primary-nav',
                              'secondary-navigation', 'main-menu-layer-body', 'panel_root', 'card-frame',
                              'base-layer-content', 'gameworldbackground']): return 'page'
    if any(x in text for x in ['button', 'selection-field', 'text-field', 'input', 'table__header', 'checkbox', 'toggle']): return 'control'
    return 'card'

def role_vars(definitions, usages):
    result = ui.theme_variables()
    # Base UI palette colours are also used for chart/data-label ink. Change the
    # semantic surface roles and safe paint usages, never those shared swatches.
    result.update({'--colours-ui-text-soft': 'secondary', '--colours-ui-text-strong': 'text',
        '--global-background': 'page', '--layout-tiles-heading-permanent': 'text',
        '--layout-modules-tiles-heading': 'text', '--global-surface-icon-standard': 'secondary',
        '--global-surface-icon-alternate': 'secondary', '--buttons-icons-default': 'secondary',
        '--buttons-global-secondary-text': 'text', '--buttons-global-icon-surface': 'secondary',
        '--layout-dividers-surface': 'border', '--layout-modules-block-color': 'border',
        '--layout-modules-tiles-border-color': 'border', '--layout-modules-tiles-interaction-border-color': 'border',
        '--layout-ui-tiles-interaction-border-default': 'border', '--layout-ui-trs-background': 'card',
        '--layout-ui-trs-border': 'border', '--layout-modules-tiles-surface-default': 'card',
        '--interaction-input-field-content-text-filled-strong': 'text',
        '--interaction-input-field-content-text-filled-soft': 'secondary',
        '--interaction-input-field-content-text-placeholder-strong': 'secondary',
        '--interaction-input-field-content-text-placeholder-soft': 'muted',
        '--interaction-input-switch-active-surface-default': 'secondary',
        '--interaction-input-switch-active-surface-hover': 'text',
        '--interaction-input-switch-inactive-surface-hover': 'hover',
        '--layout-surfaces-breadcrumb-title-active': 'text', '--layout-surfaces-breadcrumb-title-inactive': 'secondary',
        '--layout-surfaces-breadcrumb-divider-active': 'secondary', '--layout-surfaces-breadcrumb-divider-inactive': 'muted'})
    for name, (sheet, p) in definitions.items():
        if name in result: continue
        if re.search(r'warning|positive|negative|success|danger|status|special-|mens-|womens-|primary|overlay', name): continue
        if name.startswith(('--global-lift-surface-', '--global-sink-surface-')):
            result[name] = 'control'
        elif name.startswith(('--theme-core-base-', '--theme-core-secondary-', '--theme-core-tertiary-',
                               '--buttons-toggle-', '--layout-modules-tiles-interaction-',
                               '--layout-ui-core-controls-', '--core-controls-')):
            c = rgba(sheet, p, definitions)
            if not neutral(c): continue
            if 'disabled' in name:
                role = 'muted' if usages[name][65536] + usages[name][196610] else 'control'
            elif 'border' in name: role = 'border'
            elif 'hover' in name: role = 'hover'
            elif 'pressed' in name: role = 'pressed'
            elif usages[name][65536]: role = 'text'
            elif usages[name][196610]: role = 'secondary'
            elif 'active' in name and 'notactive' not in name: role = 'selected'
            else: role = 'control'
            result[name] = role
    return result

def make_definitions(folder):
    sheets, definitions, usages = {}, {}, {}
    for bn in STYLE_FILES:
        for ob in UnityPy.load(str(folder / bn)).objects:
            if ob.type.name != 'MonoBehaviour': continue
            d = ob.read_typetree()
            if 'm_Rules' not in d: continue
            sheets[(bn, ob.path_id)] = d
            for rule in d['m_Rules']:
                for p in rule['m_Properties']:
                    if p['m_Id'] == -1 and any(cname(s) == ':root' for s in rule['m_ComplexSelectors']):
                        definitions[p['m_CustomName']] = (d, p)
                    if p['m_Id'] in PAINT:
                        for h in p['m_Values']:
                            if h['m_ValueType'] == 8:
                                name = d['strings'][h['valueIndex']]
                                usages.setdefault(name, Counter())[p['m_Id']] += 1
    return definitions, {k: usages.get(k, Counter()) for k in definitions}

def selector_safe(text, key):
    t = text.lower()
    if OVERLAY.search(t): return False
    if SEMANTIC.search(t):
        label = key == 65536 and bool(re.search(r'axis.*label|legend.*label|chart.*title|graph.*title', t))
        frame = key != 65536 and key != 196610 and bool(re.search(r'background|surface|frame|panel|container|card', t))
        data = bool(re.search(r'rating|gauge|progress|pitch|heatmap|heat-map|bar-fill|series|point', t))
        if not label and not (frame and not data): return False
    if PRIMARY.search(t): return False
    if any(FOUNDATION.fullmatch(x) for x in re.findall(r'\.([\w-]+)', t)): return False
    if key == 196610:
        if IMAGE.search(t): return False
        return bool(re.search(r'ui-concepts|\.nd-|icon|indicator|chevron|arrow|checkbox|checkmark|toggle', t))
    if key == 458752 and ('gradient' in t or 'texture' in t): return False
    return True

def replacement(sh, prop, context, definitions, inline=False, protected_text=False):
    key = prop['m_Id']
    if key not in PAINT: return None
    t = context.lower()
    if not selector_safe(context, key): return None
    if key == 65536 and protected_text: return None
    c = rgba(sh, prop, definitions)
    if key == 65536 and any(x in t for x in ['title-link', 'thematic-modal', 'tifo-text-men-primary',
                                           'tifo-text-women-primary', 'fm-news-link']):
        return paint('link' if 'link' in t else 'text')
    if not neutral(c): return None
    if key == 65536:
        if any(x in t for x in ['disabled', 'muted', 'placeholder']): role = 'muted'
        elif any(x in t for x in ['secondary', 'timestamp', 'caption']): role = 'secondary'
        else: role = 'text'
    elif key == 196610: role = 'muted' if 'disabled' in t else 'secondary'
    elif key == 458752: role = surface_role(context)
    else: role = 'border'
    alpha = c['a'] if 'touchbar' in t else 1.
    new = paint(role, alpha)
    return new if any(abs(new[k] - c[k]) > 1e-6 for k in ['r','g','b','a']) else None

def append_paints(sh, selectors, props):
    i = len(sh['m_Rules'])
    ss = copy.deepcopy(selectors)
    for s in ss: s['ruleIndex'] = i
    sh['m_Rules'].append({'m_ComplexSelectors': ss, 'm_Properties': props, 'line': -1})

def cp(sh, old, c):
    p = copy.deepcopy(old)
    p['m_Values'] = [ui.handle(sh, 4, c)]
    return p

def patch_sheet(original, definitions, variables):
    sh = copy.deepcopy(original)
    edits = []
    for i, rule in enumerate(original['m_Rules']):
        if not rule['m_ComplexSelectors']: continue
        varprops = [cp(sh, p, paint(variables[p['m_CustomName']])) for p in rule['m_Properties']
                    if p['m_Id'] == -1 and p.get('m_CustomName') in variables]
        if varprops:
            append_paints(sh, rule['m_ComplexSelectors'], varprops)
            edits.append({'source_rule': i, 'variables': [p['m_CustomName'] for p in varprops]})
        for sel in rule['m_ComplexSelectors']:
            text = cname(sel)
            props = []
            for p in rule['m_Properties']:
                c = replacement(original, p, text, definitions)
                if c is not None: props.append(cp(sh, p, c))
            if props:
                append_paints(sh, [sel], props)
                edits.append({'source_rule': i, 'selector': text, 'paint_ids': [p['m_Id'] for p in props]})
    return sh, edits

def global_rules(sh):
    records = []
    def rule(sels, values): records.append(ui.append(sh, sels, values))
    # Opaque neutral surfaces, including the former trial's concrete fallback.
    rule(['.tf-light-adaptive-card-surface' + s for s in ['', ':hover', ':active', ':disabled']], {458752: 'card'})
    rule(['.dialog-card', '.notifications--notifications-modal-dialog-default-default',
          '.notifications-modal-dialog-background', '.figma-base-card-template-inner-frame',
          '.figma-base-popup-template-inner-frame', '.frame-panel-squad'], {458752: 'card', 262146: 'border'})
    rule(['.global-text-primary', '.modal-text-primary', '.tile-title-color', '.primary-text-colour'], {65536: 'text'})
    rule(['.global-text-secondary', '.secondary-text-colour'], {65536: 'secondary'})
    rule(['#RosterName', '#player-name-button-template #primary-text', '#player-name-button-template .cell-primary-text',
          '.squad-numbers-dropdown-no-value .sitext'], {65536: 'text'})
    rule(['.si-dropdown-selection-label', '.cascading-menu__folder'], {65536: 'text'})
    rule(['.si-dropdown__selection-arrow', '.indicator-arrow', '.indicator-tick', '.indicator-open'], {196610: 'secondary'})
    rule(['.data-display-data_display-cell-icon-string-transfer-value'], {458752: 'control', 65536: 'text'})
    rule(['.streamed-table__header'], {458752: 'control', 65536: 'secondary', 262146: 'border'})
    rule(['.streamed-table__checkbox', '.unity-toggle__input'], {262146: 'secondary'})
    rule(['.streamed-table__checkbox:checked:enabled .unity-toggle__checkmark'], {458752: 'secondary'})
    rule(['.dialog-card-title', '.dialog-body', '.dialog-button', '.si-dropdown .virtualised-list__item .global-text-primary'], {65536: 'text'})
    # Preserve white ink on the existing cyan primary action gradients.
    rule(['SIButton.fm27-lake-action:enabled SIText', 'SIButton.fm27-lake-action:enabled .global-text-primary',
          '.buttons-button-primary-default SIText', '.buttons-button-primary-default .sitext'], {65536: 'FFFFFF'})
    rule(['.buttons-button-primary-default:disabled .sitext'], {65536: 'muted'})
    return records

def patch_documents(obs, definitions):
    expected, docs, sheets = {}, [], {}
    for ob in list(obs.values()):
        if ob.type.name != 'MonoBehaviour': continue
        original = ob.read_typetree()
        if 'inlineSheet' not in original or original['inlineSheet']['m_FileID'] != 0: continue
        sid = original['inlineSheet']['m_PathID']
        if not sid or sid not in obs: continue
        if sid not in sheets:
            sheet = obs[sid].read_typetree()
            sheets[sid] = (sheet, copy.deepcopy(sheet))
        sh, old_sh = sheets[sid]
        d = copy.deepcopy(original)
        rr = ui.refs(d)
        elements = {rid: r for rid, r in rr.items() if 'm_RuleIndex' in r.get('data', {}) and 'm_Parent' in r.get('data', {})}
        def data(rid):
            a = rr[rid]['data']
            return rr.get(a.get('m_SerializedData', {}).get('rid'), {}).get('data', {})
        def descr(rid):
            a = rr[rid]['data']; sd = data(rid)
            return ' '.join([sd.get('name', '') or '', sd.get('templateId', '') or '', *a.get('m_Classes', [])])
        def ancestry(rid):
            seen = set()
            while rid in elements and rid not in seen:
                seen.add(rid); yield rid
                rid = rr[rid]['data']['m_Parent']['rid']
        def protected_text(rid):
            if re.search(r'TacticsPosition|TooltipFC|FCPlayerCard|Shuffle.*Player|SquadOverviewPlayerBlock', d['m_Name']): return True
            for ancestor in ancestry(rid):
                text = descr(ancestor).lower()
                if PRIMARY.search(text) or re.search(r'shirt|kit-|rating-|badge|fc-card|shield', text): return True
                if re.search(r'portraitlayerstage|overviewcardsixratings|overviewcardgoalkeeperratings|reportmiddleca\d+layer', text): return True
                idx = rr[ancestor]['data'].get('m_RuleIndex', -1)
                if idx >= 0:
                    for p in sh['m_Rules'][idx]['m_Properties']:
                        if p['m_Id'] == 458752:
                            c = rgba(sh, p, definitions)
                            if c and c['a'] > .3 and not neutral(c): return True
                        if p['m_Id'] == 458753 and any(h['m_ValueType'] in [6, 13] for h in p['m_Values']): return True
            return False
        changes = []
        for rid, rec in elements.items():
            a = rec['data']; idx = a['m_RuleIndex']
            own = descr(rid)
            parent_context = ' '.join(descr(j) for j in list(ancestry(rid))[1:3])
            context = ' '.join([d['m_Name'], own, parent_context])
            updates = {}
            original_props = copy.deepcopy(sh['m_Rules'][idx]['m_Properties']) if idx >= 0 else []
            safe_text = protected_text(rid) if a.get('m_FullTypeName', '').endswith(('SIText', 'SIButton')) else False
            for p in original_props:
                c = replacement(sh, p, context, definitions, inline=True, protected_text=safe_text)
                if c is not None: updates[p['m_Id']] = cp(sh, p, c)
            name = data(rid).get('name', '') or ''
            # The global page canvas replaces its decorative blue paint, not its assets.
            if d['m_Name'] == 'GameWorldBackground' and name in ['panel_root', 'background_image', 'TFBlueDynamicBackground']:
                updates[458752] = ui.prop(sh, 458752, 'page')
                if name != 'panel_root':
                    updates[458753] = {'m_Id': 458753, 'm_CustomName': '', 'm_Line': -1,
                                       'm_Values': [ui.handle(sh, 7, 'none')]}
                    clear = paint('FFFFFF', 0.)
                    updates[196610] = cp(sh, {'m_Id':196610,'m_CustomName':'','m_Line':-1,'m_Values':[]}, clear)
            # Sidebar's medical icon uses a white injury-icon asset as a navigation glyph.
            if d['m_Name'] == 'TFReferenceBookmarkSidebar' and name.startswith('FixedIcon_'):
                updates[196610] = cp(sh, {'m_Id':196610,'m_CustomName':'','m_Line':-1,'m_Values':[]}, paint('text'))
            if not updates: continue
            a['m_RuleIndex'] = len(sh['m_Rules'])
            props = [p for p in original_props if p['m_Id'] not in updates] + list(updates.values())
            for p in updates.values():
                assert all(h['m_ValueType'] != 10 for h in p['m_Values']), 'Inline var() prohibited'
            sh['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': props, 'line': -1})
            changes.append({'rid': rid, 'name': name, 'old_rule': idx, 'new_rule': a['m_RuleIndex'],
                            'paint_ids': sorted(updates)})
        if changes:
            normalized = copy.deepcopy(d)
            nr = ui.refs(normalized)
            for c in changes: nr[c['rid']]['data']['m_RuleIndex'] = c['old_rule']
            assert normalized == original, ('Non-paint VTA change', d['m_Name'])
            ob.save_typetree(d); expected[ob.path_id] = d
            docs.append({'name': d['m_Name'], 'id': ob.path_id, 'style': sid, 'nodes': changes})
    for sid, (sh, old) in sheets.items():
        if sh == old: continue
        assert sh['m_Rules'][:len(old['m_Rules'])] == old['m_Rules']
        obs[sid].save_typetree(sh); expected[sid] = sh
    return expected, docs

def main():
    stamp = datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S')
    out = R / ('global-light-theme-' + stamp)
    out.mkdir()
    names = sorted({p.name for folder in [GAME, SKIN] for p in folder.glob('*visualtree*.bundle')} | set(STYLE_FILES))
    snapshots = {folder / bn: (folder / bn).read_bytes() for folder in [GAME, SKIN] for bn in names if (folder / bn).exists()}
    print('Snapshot current UI bundles; hash protected resources...', flush=True)
    protected = {str(p): ui.filehash(p) for folder in [GAME, SKIN] for p in folder.glob('*.bundle') if p not in snapshots}
    for folder in [GAME.parent, SKIN]:
        for name in ['catalog.bin','catalog.hash']:
            p = folder / name
            if p.exists(): protected[str(p)] = ui.filehash(p)
    for name in ['current-custom-textures.json','reserved-texture-ids.json','current-sidebar-version.json']:
        protected[str(R / name)] = ui.filehash(R / name)
    m = {'installed': False, 'runtime_verified': False, 'palette': PALETTE, 'scope': 'All UI visual-tree bundles and shared default/common styles; neutral chrome only',
         'before_sha256': {}, 'after_sha256': {}, 'protected_sha256': protected, 'changes': [], 'objects': {},
         'original_ui_surface_index': json.loads((R / 'current-ui-surface-theme.json').read_text('utf8')),
         'previous_global_state': json.loads((R / 'current-ui-surface-theme.json').read_text('utf8')).get('global_light_theme'),
         'scanned_bundles': [], 'new_inline_color_variables': 0, 'semantic_colour_rule': SEMANTIC.pattern}
    tx = {'game': str(GAME), 'skin': str(SKIN), 'workspace': str(R), 'sources': {}, 'before': {}}
    for tag, folder in [('game',GAME),('skin',SKIN)]:
        definitions, usages = make_definitions(folder)
        variables = role_vars(definitions, usages)
        for bn in names:
            p = folder / bn
            if p not in snapshots: continue
            en = UnityPy.load(snapshots[p]); obs = {o.path_id:o for o in en.objects}
            expected, docs, sheet_changes, extra_rules = {}, [], [], []
            if bn in STYLE_FILES:
                for ob in obs.values():
                    if ob.type.name != 'MonoBehaviour': continue
                    original = ob.read_typetree()
                    if 'm_Rules' not in original: continue
                    sh, edits = patch_sheet(original, definitions, variables)
                    if bn == STYLE_FILES[0] and original['m_Name'] == 'AlwaysAppliedStyleSheet':
                        extra_rules = global_rules(sh)
                    if sh != original:
                        ob.save_typetree(sh); expected[ob.path_id] = sh
                        sheet_changes.append({'name': original['m_Name'], 'id': ob.path_id, 'edits': edits,
                                              'added_rules': len(sh['m_Rules']) - len(original['m_Rules'])})
            else:
                expected, docs = patch_documents(obs, definitions)
            m['scanned_bundles'].append({'target':str(p), 'changed':bool(expected), 'documents_changed':len(docs), 'sheets_changed':len(sheet_changes)})
            if not expected:
                protected[str(p)] = ui.sha(snapshots[p]); print(tag,bn,'unchanged',flush=True); continue
            raw = en.file.save(packer='lz4')
            saved = {o.path_id:o for o in UnityPy.load(raw).objects}
            old = {o.path_id:o for o in UnityPy.load(snapshots[p]).objects}
            assert set(saved) == set(old)
            actual_changed = []
            for pid, o in saved.items():
                if pid in expected:
                    assert o.read_typetree() == expected[pid], ('Roundtrip failed',p,pid)
                    if o.get_raw_data() != old[pid].get_raw_data(): actual_changed.append(str(pid))
                else: assert o.get_raw_data() == old[pid].get_raw_data(), ('Unrelated object changed',p,pid)
            assert len(actual_changed) == len(expected)
            dest, backup = out/tag/bn, out/('backup-'+tag)/bn
            for path,data in [(dest,raw),(backup,snapshots[p])]: path.parent.mkdir(exist_ok=True); path.write_bytes(data)
            m['before_sha256'][str(p)] = ui.sha(snapshots[p]); m['after_sha256'][str(p)] = ui.sha(raw)
            m['objects'][str(p)] = {'changed_ids':actual_changed,'total_objects':len(saved),'all_other_objects_byte_identical':True}
            m['changes'].append({'target':str(p),'documents':docs,'sheets':sheet_changes,'extra_rules':extra_rules})
            tx['sources'][str(p)], tx['before'][str(p)] = str(dest),str(backup)
            print(tag,bn,'documents',len(docs),'sheets',len(sheet_changes),'verified objects',len(expected),flush=True)
    for p,raw in snapshots.items(): assert p.read_bytes() == raw, ('Baseline changed',p)
    for path,digest in protected.items(): assert ui.filehash(Path(path)) == digest, ('Protected resource changed',path)
    m['prepared_verified'] = True
    for name,data in [('manifest.json',m),('transaction.json',tx)]: (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
    for src,dst in [('build-global-light-theme.py','build-global-light-theme.py'),('install-global-light-theme.py','installer.py')]:
        (out/dst).write_bytes((R/src).read_bytes())
    for name,flag in [('install',''),('verify',' --verify'),('restore',' --restore')]:
        (out/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed; see error above.'}\n",'utf-8-sig')
    (out/'说明.md').write_text('全局浅色主题：页面E7E7E7、卡片/弹窗F7F7F5、主字242424、次字62625D。覆盖主界面、导航/侧栏、设置、比赛、选秀、开始页的中性UI配色；保留球队/球衣/图标身份、评分/体能/伤病等数据颜色，以及头像和图片资源。\n\n基于游戏与独立主皮肤各自最新资源，只改绘制颜色；绑定、事件、布局、目录与资源ID保持。新增内联颜色全部为具体值，禁止var()。游戏背景的装饰性蓝色图片通过绘制属性隐藏，源纹理保留，专用卡面和图片面板保持。\n\ninstall.ps1安装、verify.ps1校验、restore.ps1回到本次修改前的浅色试版。安装/回退均要求退出游戏且匹配哈希；有后续修改时须重新迁移。文件校验不代表全页面已实测。\n','utf8')
    state = {'status':'prepared','installed':False,'record':str(out),'manifest':str(out/'manifest.json'),
             'palette':PALETTE,'scope':m['scope'],'restore':str(out/'restore.ps1'),'runtime_verified':False}
    (R/'current-global-light-theme.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps({'prepared':True,'record':str(out),'files':len(tx['sources']),
          'documents':sum(len(c['documents']) for c in m['changes']),
          'style_objects':sum(len(c['sheets']) for c in m['changes'])},ensure_ascii=False),flush=True)

if __name__ == '__main__': main()
