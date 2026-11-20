from pathlib import Path
from collections import Counter
import re
import subprocess

V = 'ui-tableviews_assets_all.bundle'
S = 'ui-styles_assets_default.bundle'
boot = Path('build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot = boot.replace('NAMES=[W,G,M,F]', 'NAMES=[W,F,V,S]')
boot = boot.replace('match-ui-avatars-layout-', 'tactical-selection-compact-morale-').replace('hours=-4', 'hours=-7')
boot = boot.replace("if SKIN/n in before:assert before[SKIN/n]==before[GAME/n],('game/skin diverged',n)", 'pass')
boot = boot.replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']", 'pass')
exec(compile(boot, 'current-assets', 'exec'))
location = json.loads((R / 'current-game-location.json').read_text('utf-8-sig'))
assert GAME.resolve() == Path(location['bundle_root']).resolve()

for file, names in [
    ('combine-tactics-condition-sharpness.py', {'decode', 'encode', 'f32'}),
    ('unify-lake-blue-controls.py', {'append_rule'}),
    ('fix-primary-navigation-grey-lake-blue.py', {'selector'}),
    ('build-fc-player-hover-layout.py', {'Styles'}),
]:
    parsed = ast.parse((R / file).read_text('utf-8-sig'))
    exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names], type_ignores=[]), file, 'exec'))

spec = importlib.util.spec_from_file_location('tactical_catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog_module)
morale_pid = -981107000000100
morale_style = morale_pid - 1
morale_guid = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/TacticalSelectionNumericMorale/v1').hex
fatigue_guid = 'fbe52cf67d9f5e02a9fd84c936911101'
health_ids = {'condition', 'sharpness', 'condition-in-match', 'sharpness-in-match', 'condition-icon', 'match-sharpness', 'fatigue-icon', 'tactics-fatigue-value'}
widths = {
    'picked-position': 44, 'picked-role': 46, 'overview-position': 44,
    'ip-position': 48, 'oop-position': 48, 'ip-overview-position': 48, 'oop-overview-position': 48,
    'ip-role': 46, 'oop-role': 46, 'tactic-ability': 60, 'role-ability': 60,
    'morale': 32, 'morale-icon-only': 32,
}
outputs = {}
checks = []


def native_morale_palette(folder):
    collection = next(o.read_typetree() for o in UnityPy.load(str(folder / 'ui-datacollections_assets_all.bundle')).objects
                      if o.type.name == 'MonoBehaviour' and o.peek_name() == 'MoraleDataCollection')
    columns = {r['data']['m_name']: r['data']['m_rows'] for r in collection['references']['RefIds']
               if r.get('data', {}).get('m_name') in {'Key', 'SmallIcon'}}
    images = UnityPy.load(str(folder / 'ui-icons_assets_1x.bundle'), str(folder / 'ui-iconspriteatlases_assets_1x.bundle'))
    sprites = {o.path_id: o for o in images.objects if o.type.name == 'Sprite'}
    palette = {-1: {'r': .5, 'g': .5, 'b': .5, 'a': 1.}}
    for o in UnityPy.load(str(folder / 'ui-styles_assets_1x.bundle')).objects:
        if o.type.name != 'MonoBehaviour':
            continue
        sheet = o.read_typetree()
        for rule in sheet.get('m_Rules', []):
            names = {p['m_Value'] for sel in rule['m_ComplexSelectors'] for s in sel['m_Selectors'] for p in s['m_Parts']}
            levels = [v for v, icon in zip(columns['Key'], columns['SmallIcon']) if icon and icon in names]
            if not levels:
                continue
            handle = next(x for x in rule['m_Properties'] if x['m_Id'] == 458753)['m_Values'][0]
            pointer = sheet['assets'][handle['valueIndex']]
            sprite = sprites[pointer['m_PathID']]
            assert sprite.assets_file.name == o.assets_file.externals[pointer['m_FileID'] - 1].name
            pixels = sprite.read().image.convert('RGBA').getdata()
            rgb = Counter((r,g,b) for r,g,b,a in pixels if a >= 200 and max(r,g,b)-min(r,g,b)>35).most_common(1)[0][0]
            for level in levels:
                palette[level] = dict(zip('rgba', [f32(c / 255) for c in rgb] + [1.]))
    assert set(palette) == set(range(-1, 21))
    return palette


def register_morale(catalog_bytes):
    catalog = catalog_module.Catalog(catalog_bytes)
    source = next(i for i in catalog.locations(fatigue_guid) if catalog.location(i)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset')
    updated = catalog_module.Catalog(catalog.add_key_location(morale_guid, source, source))
    loc = updated.locations(morale_guid)[0]
    index = next(i for i, (key, _) in enumerate(updated.keys()) if key == 'GameWorldVisualTreeAssetPreload')
    key_ptr, loc_ptr = updated.key_records[index]
    location_list = [p for (p,) in updated.array(loc_ptr, 'I')] + [loc]
    records = list(updated.key_records)
    records[index] = (key_ptr, updated.append(b''.join(struct.pack('<I', p) for p in location_list), True))
    struct.pack_into('<I', updated.data, 8, updated.append(b''.join(struct.pack('<2I', *r) for r in records), True))
    return bytes(updated.data)


def copy_asset(source, pid, tree):
    assert pid not in objs[W]
    obj = copy.copy(source)
    obj.path_id, obj.data, obj._read_until = pid, None, None
    obj.assets_file.objects[pid] = obj
    objs[W][pid] = obj
    obj.save_typetree(tree)


def add_numeric_morale(palette):
    meta_obj = next(o for o in objs[W].values() if o.type.name == 'AssetBundle')
    meta = meta_obj.read_typetree()
    donor_entry = dict(meta['m_Container'])[fatigue_guid]
    donor = Doc(W, pid=donor_entry['asset']['m_PathID'])
    tree, style = copy.deepcopy(donor.d), copy.deepcopy(donor.s)
    tree.update(m_Name='TacticalSelectionNumericMorale', inlineSheet={'m_FileID': 0, 'm_PathID': morale_style})
    style['m_Name'] = 'TacticalSelectionNumericMorale_Style'
    root = donor.named('FatigueAbove-2147483648')
    missing = donor.named('FatigueRawColourNone')
    keep = {1000, 1001, root, missing}
    keep |= {donor.a(i).get('m_SerializedData', {}).get('rid', -2) for i in tuple(keep)}
    tree['references']['RefIds'] = [r for r in tree['references']['RefIds'] if r['rid'] in keep]
    refs(tree)[root]['data']['m_Children'] = [{'rid': missing}]
    copy_asset(donor.obj, morale_pid, tree)
    copy_asset(objs[W][donor.sid], morale_style, style)
    doc = Doc(W, pid=morale_pid, tree=tree, style=style)
    root_inputs = doc.data(root)['Binding']['m_visualFunction']['m_inputs']['m_variable']
    root_args = decode(root_inputs['m_argumentBytes'])
    struct.pack_into('<i', root_args[1], len(root_args[1])-4, -1)
    root_inputs['m_argumentBytes'] = encode(root_args)
    doc.st(1001, [(key, doc.px(32)) for key in (131105, 131097, 131095)])
    def leaf(parent, level):
        node = doc.add(donor, donor.named('FatigueRawColour0'), parent, 'MoraleLevel'+str(level))
        label = doc.data(node)
        label.update(text=str(level), text_UxmlAttributeFlags=1, TextBinding_UxmlAttributeFlags=0)
        label['TextBinding']['m_kind'] = 0
        doc.st(node, [(131105, doc.pct(100)), (131087, doc.pct(100)), (65537, doc.px(11)),
                      (65546, doc.enum('middle-center')), (65536, doc.val(4, palette[level]))])
        return node
    def branch(parent, low, high):
        if low == high:
            return leaf(parent, low)
        middle = (low + high) // 2
        node = doc.add(donor, root, parent, 'MoraleAbove'+str(middle))
        args = decode(doc.data(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        struct.pack_into('<i', args[1], len(args[1])-4, middle)
        doc.data(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode(args)
        doc.st(node, [(131105, doc.pct(100)), (131087, doc.pct(100))])
        branch(node, low, middle)
        branch(node, middle+1, high)
        return node
    branch(root, 0, 20)
    for value in [-2147483648, -1, *range(21)]:
        node = root
        while doc.data(node).get('Binding', {}).get('m_kind') == 2:
            args = decode(doc.data(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
            limit = struct.unpack_from('<i', args[1], len(args[1])-4)[0]
            node = doc.a(node)['m_Children'][int(value > limit)]['rid']
        assert doc.data(node)['text'] == ('--' if value < 0 else str(value))
    doc.save()
    span = copy.deepcopy(meta['m_PreloadTable'][donor_entry['preloadIndex']:donor_entry['preloadIndex']+donor_entry['preloadSize']])
    for pointer in span:
        if pointer['m_FileID'] == 0:
            pointer['m_PathID'] = {donor.obj.path_id: morale_pid, donor.sid: morale_style}.get(pointer['m_PathID'], pointer['m_PathID'])
    for pid in [morale_pid, morale_style]:
        if {'m_FileID': 0, 'm_PathID': pid} not in span:
            span.append({'m_FileID': 0, 'm_PathID': pid})
    meta['m_Container'].append((morale_guid, {'preloadIndex': len(meta['m_PreloadTable']), 'preloadSize': len(span), 'asset': {'m_FileID': 0, 'm_PathID': morale_pid}}))
    meta['m_PreloadTable'].extend(span)
    meta_obj.save_typetree(meta)
    changes[W][meta_obj.path_id] = meta


def shrink(colid):
    if colid in widths:
        return widths[colid]
    if re.search(r'(^|-)(goals?|assists?)(-|$)', colid) and 'goalkeeping' not in colid:
        return 36 if 'expected' in colid or 'per90' in colid or 'per-goal' in colid else 28
    return None


palette = native_morale_palette(GAME)
for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    for bundle in NAMES:
        env[bundle] = UnityPy.load(before[folder / bundle])
        objs[bundle] = {o.path_id: o for o in env[bundle].objects}
        hashes[bundle] = {i: sha(o.get_raw_data()) for i,o in objs[bundle].items()}
        changes[bundle] = {}
    add_numeric_morale(palette)
    normal = find(F, 'TacticTeamSelectionTableFactory').read_typetree()
    normal_health = {c['m_id']: c for c in normal['m_rowData'] if c['m_id'] in ['condition', 'tactics-fatigue-value']}
    match_donor = find(F, 'InMatchTacticsFitnessFactory').read_typetree()
    match_health = {c['m_id']: c for c in match_donor['m_rowData'] if c['m_id'] in normal_health}
    assert len(normal_health) == len(match_health) == 2
    factory_count = view_count = frame_count = 0
    for o in objs[F].values():
        if o.type.name != 'MonoBehaviour' or o.peek_name() not in ['TacticTeamSelectionTableFactory', 'TacticTeamSelectionTableFactoryInMatch', 'InMatchTacticsFitnessFactory']:
            continue
        d = o.read_typetree()
        name = d['m_Name']
        rows = d['m_rowData']
        if name == 'TacticTeamSelectionTableFactoryInMatch':
            for key,c in match_health.items():
                index = next((i for i,v in enumerate(rows) if v['m_id'] == key), None)
                if index is None:
                    rows.append(copy.deepcopy(c))
                else:
                    rows[index] = copy.deepcopy(c)
        for c in rows:
            colid = c['m_id']
            wanted = shrink(colid)
            if wanted is not None:
                width = min(c['m_defaultWidth'], float(wanted))
                c.update(m_defaultWidth=width, m_minimumWidth=min(c['m_minimumWidth'], width))
            if colid in ['morale', 'morale-icon-only']:
                original_sort = c['m_sortBinding']['m_path']
                assert original_sort.lower().endswith('.morale')
                c['m_uxmlRef']['m_AssetGUID'] = morale_guid
                c['m_valueBindings'] = [{'m_serialisedType': 0, 'from':'binding', 'to': {'m_path':original_sort}, 'type': {'id':0}}]
            if colid in normal_health:
                width = float(normal_health[colid]['m_defaultWidth'])
                c.update(m_defaultWidth=width, m_minimumWidth=width, m_allowWidthAutoResizing=0)
        o.save_typetree(d);changes[F][o.path_id] = d;factory_count += 1
    for o in objs[V].values():
        if o.type.name != 'MonoBehaviour' or 'TacticTeamSelectionTableView' not in o.peek_name():
            continue
        d = o.read_typetree()
        config = d.get('m_tableView', {}).get('m_tableConfig')
        if not config:
            continue
        old = copy.deepcopy(config)
        condition = next((c for c in config if c['m_columnID'] == 'condition'), None)
        if condition is not None:
            config[:] = [c for c in config if c['m_columnID'] not in health_ids - {'condition'}]
            condition['m_columnMetadata'].update(m_widthOverride=90., m_minWidthOverride=90.)
            fat = copy.deepcopy(condition)
            fat['m_columnID'] = 'tactics-fatigue-value'
            fat['m_columnMetadata'].update(m_widthOverride=40., m_minWidthOverride=40.)
            fat['m_columnMetadata']['m_titleTranslationIdOverride']['GameID'] = 0
            config.insert(config.index(condition)+1, fat)
        for c in config:
            wanted = shrink(c['m_columnID'])
            if wanted is None:
                continue
            md = c['m_columnMetadata']
            width = min(md['m_widthOverride'] or float(wanted), float(wanted))
            md.update(m_widthOverride=width, m_minWidthOverride=min(md['m_minWidthOverride'] or width, width))
        if config != old:
            o.save_typetree(d);changes[V][o.path_id] = d;view_count += 1
    for o in list(objs[W].values()):
        if o.type.name != 'MonoBehaviour':
            continue
        name = o.peek_name()
        if name == 'TacticalPlannerTeamShapeTableTemplate':
            doc = Doc(W, pid=o.path_id)
            node = doc.named('Table')
            doc.a(node)['m_Classes'].append('tf-compact-tactical-table')
            doc.save()
        elif name == 'TacticsDetailedCardDetailsDesktop':
            doc = Doc(W, pid=o.path_id)
            frame = next(i for i,r in doc.r.items() if 'layout-tile-interaction_border_tactics' in r.get('data', {}).get('m_Classes', []))
            # The decorative stationary frame is separate from FMDraggableObject's drag visual.
            doc.st(frame, [(458767, doc.num(0))])
            doc.save();frame_count += 1
    for o in objs[S].values():
        if o.type.name != 'MonoBehaviour' or o.peek_name() not in ['AlwaysAppliedStyleSheet', 'FigmaGeneratedStyles']:
            continue
        sheet = o.read_typetree()
        for cls in ['fm-star-rating-star', 'fm-star-rating-star-no-margin']:
            added = append_rule(sheet, ['.tf-compact-tactical-table.tf-compact-tactical-table .' + cls],
                                [(131105, 11.), (131087, 11.), (131097, 11.)])
            style = Styles(sheet)
            for prop in sheet['m_Rules'][added['index']]['m_Properties']:
                prop['m_Values'] = [style.px(11)]
        o.save_typetree(sheet);changes[S][o.path_id] = sheet
    assert factory_count >= 2 and view_count >= 8 and frame_count
    catalog_path = GAME.parent/'catalog.bin' if tag == 'game' else SKIN/'catalog.bin'
    catalog_bytes = register_morale(before[catalog_path])
    catalog = catalog_module.Catalog(catalog_bytes)
    loc = catalog.locations(morale_guid)[0]
    assert catalog.location(loc)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset'
    assert catalog.location(catalog.location(loc)['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
    preload_ptr = dict(catalog.keys())['GameWorldVisualTreeAssetPreload']
    assert (loc,) in catalog.array(preload_ptr,'I')
    outputs[catalog_path] = catalog_bytes
    outputs[catalog_path.with_suffix('.hash')] = hashlib.md5(catalog_bytes).hexdigest().encode('ascii')
    for bundle in NAMES:
        raw = env[bundle].file.save(packer='lz4')
        saved = {o.path_id:o for o in UnityPy.load(raw).objects}
        assert saved.keys() == objs[bundle].keys()
        for pid, tree in changes[bundle].items():
            assert saved[pid].read_typetree() == tree, (tag,bundle,pid)
        for pid,h in hashes[bundle].items():
            if pid not in changes[bundle]:
                assert sha(saved[pid].get_raw_data()) == h, (tag,bundle,pid)
        outputs[folder/bundle] = raw
    checks.append({'target':tag, 'factories':factory_count, 'table_views':view_count, 'idle_frames_hidden':frame_count,
                   'morale': '0–20, native icon RGB', 'morale_guid':morale_guid, 'condition':90, 'fatigue':40})

transaction = {'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for path, data in outputs.items():
    tag = 'game' if path.parent in [GAME,GAME.parent] else 'skin'
    dest = OUT / ('output-'+tag) / path.name
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(data)
    transaction['sources'][str(path)] = str(dest)
    transaction['before'][str(path)] = str(OUT / ('backup-'+tag) / path.name) if path in before else None
    protected.pop(path,None)
manifest = {'installed':False,'runtime_verified':False,'checks':checks,
            'before_sha256':{str(p):sha(before[p]) if p in before else None for p in outputs},
            'after_sha256':{str(p):sha(b) for p,b in outputs.items()},
            'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),'utf8')
(OUT/'transaction.json').write_text(json.dumps(transaction,indent=2),'utf8')
installer = (R/'install-native-background-overrides.py').read_text('utf8')
installer = installer.replace('assert p.parent.resolve() in allowed,p', "assert p.parent.resolve() in allowed or (p.parent.resolve()==Path(tx['game']).resolve().parent and p.name in {'catalog.bin','catalog.hash'}),p")
(OUT/'installer.py').write_text(installer,'utf8')
for name, flag in [('install.ps1',''),('restore.ps1',' --restore')]:
    (OUT/name).write_text(f"$ErrorActionPreference = 'Stop'\n& '{PYTHON}' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot{flag}\nif ($LASTEXITCODE) {{ exit $LASTEXITCODE }}\n",'utf-8-sig')
print(json.dumps({'prepared':str(OUT),'checks':checks},ensure_ascii=False),flush=True)
process = subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if not process.stdout.strip():
    subprocess.run([str(PYTHON),str(OUT/'installer.py'),str(OUT)],check=True)
