from pathlib import Path
import runpy
import subprocess

bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(compile(bootstrap.replace('inspect-fitness-backdrop-', 'tactics-three-columns-'), 'current-bundle-helpers', 'exec'))
Catalog = runpy.run_path(str(R/'catalog-binary-v35.py'))['Catalog']
outputs, checks = {}, []

def scope_value(name, value):
    return {'m_name': name, 'm_scopeValue': {'m_serializedData': value}}

def flex(doc, node, direction='column', weight=1):
    doc.st(node, [(131083, doc.enum(direction)), (131082, doc.px(0)),
                  (131084, doc.num(weight)), (131085, doc.num(1)),
                  (131097, doc.px(0)), (131096, doc.px(0)),
                  (131074, doc.enum('stretch'))])

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    env[W] = UnityPy.load(before[folder/W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    changes[W] = {}
    original_hashes = {i: sha(obj.get_raw_data()) for i, obj in objs[W].items()}
    shape = Doc(W, name='TacticalPlannerTeamShape')
    native_double = Doc(W, name='TacticalPlannerCollapsablePitchesDouble')
    native_pitch = Doc(W, name='TacticalPlannerCollapsablePitchesSingle')
    native_subs = Doc(W, name='TacticalPlannerSubsBlock')
    original = copy.deepcopy(shape.d)
    shape.using(native_double, 'TacticalPlannerCollapsablePitches')
    shape.using(native_double, 'TacticalPlannerSubsBlock')

    def add_visibility(parent, name, invert):
        node = shape.add(native_double, 1019, parent, name)
        serialized = shape.data(node)
        serialized['Binding'].update(m_kind=1, m_direct={'Path': {'m_path': 'app.GridBreakpointIsSmall'}, 'Nullable': 0})
        serialized.update(InvertDirectBinding=int(invert), InvertDirectBinding_UxmlAttributeFlags=1)
        return node

    def add_label(parent, name, label):
        node = shape.add(native_pitch, 1071, parent, name)
        shape.a(node)['m_Classes'] = ['heading-md', 'global-text-primary', 'content-ellipsis']
        shape.data(node).update(text=label, text_UxmlAttributeFlags=1, TextBinding_UxmlAttributeFlags=0)
        shape.data(node)['TextBinding']['m_kind'] = 0
        shape.st(node, [(131087, shape.px(22)), (131085, shape.num(0)),
                        (65537, shape.px(13)), (65546, shape.enum('middle-left'))])
        return node

    def add_pitch(parent, key, mode, in_possession):
        scope = shape.add(native_double, 1020, parent, key+'Scope')
        shape.a(scope)['m_Classes'] = ['grid-element-scope']
        shape.data(scope)['ValueVariables'] = [scope_value(name, value) for name, value in [
            ('mode', f'Int|{mode}|'), ('inpossession', f'Bool|{int(in_possession)}|'),
            ('collapsed', 'Bool|0|'), ('hidetabs', 'Bool|1|'), ('hidecollapse', 'Bool|1|'),
            ('hidetag', 'Bool|1|'), ('hideanalysis', 'Bool|1|'),
            ('dragdropkey', 'String|TacticShape-IP|' if in_possession else 'String|TacticShape-OP|'),
        ]]
        flex(shape, scope)
        pitch = shape.add(native_double, 1042, scope, key+'Pitch')
        shape.a(pitch)['m_Classes'] = ['base-template-grow']
        shape.a(pitch)['m_SerializedDataOverride'] = []
        flex(shape, pitch)
        if mode:
            target = native_pitch.a(1052)
            data = copy.deepcopy(native_pitch.r[target['m_SerializedData']['rid']])
            data['rid'] = shape.nr
            shape.nr += 1
            data['data'].update(Orientation=1, Orientation_UxmlAttributeFlags=1)
            shape.r[data['rid']] = data
            shape.d['references']['RefIds'].append(data)
            shape.a(pitch)['m_SerializedDataOverride'] = [{
                'm_ElementId': target['m_Id'], 'm_ElementIdsPath': [target['m_Id']],
                'm_SerializedData': {'rid': data['rid']},
            }]
            assert data['data']['uxmlAssetId'] == target['m_Id']
        return pitch

    # Keep the original pitch template as the compact breakpoint fallback.
    compact = add_visibility(1007, 'OriginalCompactPitchLayout', False)
    shape.move(1013, compact)
    flex(shape, compact)
    desktop = add_visibility(1007, 'ThreeColumnPitchLayout', True)
    flex(shape, desktop, 'row')
    combined = shape.add(native_double, 1002, desktop, 'CombinedPitchColumn')
    phases = shape.add(native_double, 1002, desktop, 'StackedPhasesColumn')
    flex(shape, combined)
    flex(shape, phases)
    shape.st(combined, [(131092, shape.px(8))])
    add_label(combined, 'CombinedPitchTitle', '合并阵型')
    add_pitch(combined, 'Combined', 0, True)
    add_label(phases, 'BothPhasesTitle', '都包括')
    for key, label, mode, in_possession in [('InPossession', '有球阵型', 1, True), ('OutOfPossession', '无球阵型', 2, False)]:
        section = shape.add(native_double, 1002, phases, key+'Section')
        flex(shape, section)
        if mode == 1:
            shape.st(section, [(131090, shape.px(8))])
        add_label(section, key+'Title', label)
        add_pitch(section, key, mode, in_possession)

    # The existing table subtree moves as one unit, retaining all native views.
    right = shape.add(native_double, 1002, 1002, 'TableAndUnderstandingColumn')
    shape.move(1008, right)
    flex(shape, 1007, weight=58)
    flex(shape, right, weight=42)
    flex(shape, 1008)
    lower = add_visibility(right, 'UnderstandingBelowTable', True)
    shape.st(lower, [(131105, shape.pct(100)), (131087, shape.px(196)), (131096, shape.px(196)),
                     (131084, shape.num(0)), (131085, shape.num(0)), (131093, shape.px(8))])
    module = shape.add(native_double, 1010, lower, 'ExistingTacticalUnderstandingModule')
    shape.a(module)['m_Classes'] = ['base-template-grow']
    shape.fill(module)
    assert shape.a(right)['m_Children'] == [{'rid': 1008}, {'rid': lower}]
    assert shape.a(1013)['m_Parent']['rid'] == compact
    for rid, record in refs(original).items():
        current = copy.deepcopy(shape.r[rid])
        old = copy.deepcopy(record)
        if rid in [1007, 1008, 1013, 1002]:
            for key in ['m_Parent', 'm_Children', 'm_RuleIndex']:
                old['data'].pop(key, None)
                current['data'].pop(key, None)
        assert old == current, ('Original table, binding or control changed', rid)
    shape.save()

    # Reuse registered template GUIDs. Include their existing preload spans in
    # the caller's span, while retaining all other container locations.
    meta_object = next(o for o in objs[W].values() if o.type.name == 'AssetBundle')
    meta = meta_object.read_typetree()
    entries = dict(meta['m_Container'])
    owner_key = next(k for k, entry in entries.items() if entry['asset']['m_PathID'] == shape.obj.path_id)
    owner = entries[owner_key]
    original_span = meta['m_PreloadTable'][owner['preloadIndex']:owner['preloadIndex']+owner['preloadSize']]
    span = list(original_span)
    catalog_path = GAME.parent/'catalog.bin' if tag == 'game' else SKIN/'catalog.bin'
    catalog = Catalog(before[catalog_path])
    def vta_dependencies(key):
        locations = [catalog.location(loc) for loc in catalog.locations(key)]
        locations = [loc for loc in locations if loc['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
        assert locations
        for loc in locations:
            dependencies = [catalog.location(i)['internal'].replace('\\', '/').split('/')[-1] for i in loc['dependencies']]
            assert dependencies[0] == W, (tag, key, dependencies)
        return set(dependencies)
    owner_deps = vta_dependencies(owner_key)
    for alias, doc in [('TacticalPlannerCollapsablePitches', native_pitch), ('TacticalPlannerSubsBlock', native_subs)]:
        key = next(u['path'] for u in shape.d['m_Usings'] if u['alias'] == alias)
        entry = entries[key]
        assert entry['asset']['m_PathID'] == doc.obj.path_id
        assert vta_dependencies(key) <= owner_deps
        pointers = meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]
        for pointer in pointers + [entry['asset'], {'m_FileID': 0, 'm_PathID': doc.sid}]:
            if pointer not in span:
                span.append(copy.deepcopy(pointer))
    if span != original_span:
        owner.update(preloadIndex=len(meta['m_PreloadTable']), preloadSize=len(span))
        meta['m_PreloadTable'].extend(span)
        meta_object.save_typetree(meta)
        changes[W][meta_object.path_id] = meta

    result = env[W].file.save(packer='lz4')
    saved = {o.path_id: o for o in UnityPy.load(result).objects}
    assert saved.keys() == objs[W].keys()
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid], (tag, pid)
        else:
            assert sha(obj.get_raw_data()) == original_hashes[pid], (tag, pid)
    outputs[folder/W] = result
    (OUT/('output-'+tag)).mkdir()
    (OUT/('output-'+tag)/W).write_bytes(result)
    checks.append({'target': tag, 'desktop_width_weights': [29, 29, 42], 'phase_height_weights': [1, 1],
                   'table_then_understanding': True, 'native_compact_fallback': True,
                   'typed_catalog_and_preloads_verified': True, 'unrelated_objects_preserved': True})

G = W
tail = Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail = "for p,b in before.items():\n if p.name.startswith('catalog.')" + tail
tail = tail.replace(' restore.append("Copy-Item', ' restore.append("if ((Get-FileHash -LiteralPath \'"+str(p)+"\').Hash.ToLower() -ne \'"+sha(outputs[p])+"\') { throw \'Target changed since installation.\' }")\n restore.append("Copy-Item')
start = tail.index("(OUT/'修改说明.md').write_text(")
end = tail.index('\nprint(', start)
tail = tail[:start] + "(OUT/'修改说明.md').write_text('桌面战术页三栏约29/29/42，左合并、中上有球下无球、右表格下接完整战术理解度。复用原生模板及数据，窄屏保留原球场布局。游戏和皮肤独立修改，未启动游戏。','utf8')" + tail[end:]
exec(compile(tail, 'verify-and-install', 'exec'))
