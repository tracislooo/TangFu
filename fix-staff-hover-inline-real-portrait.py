"""Inline the native normal-person photo branch in every active staff hover copy."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, subprocess, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
helpers = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if
    isinstance(n, ast.FunctionDef) and n.name == 'write' or
    isinstance(n, ast.ClassDef) and n.name == 'Styles'], type_ignores=[]), 'helpers', 'exec'))
TypeTreeHelper.write_value = write

loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PRIVATE = 'a86c2c3a1a935f6494217908265a8ce7'
NATIVE = '435b45f976d924542ba614581a0191d1'
PHOTO_FUNC = '6579775e848422d42a8a5ab277ded932'
sha = lambda b: hashlib.sha256(b).hexdigest()
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('staff-hover-inline-real-portrait-' + stamp)
OUT.mkdir()
before = {f / W: (f / W).read_bytes() for f in [GAME, SKIN]}
protected = {p: sha(p.read_bytes()) for f in [GAME, SKIN] for p in f.glob('*.bundle') if p.name != W}
for f in [GAME.parent, SKIN]:
    for n in ['catalog.bin', 'catalog.hash']:
        protected[f / n] = sha((f / n).read_bytes())
for n in ['reserved-texture-ids.json', 'current-custom-textures.json']:
    protected[R / n] = sha((R / n).read_bytes())
sp = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(sp)
sp.loader.exec_module(cm)

def refs(d):
    return {r['rid']: r for r in d['references']['RefIds']}

def sd(rr, i):
    return rr[rr[i]['data']['m_SerializedData']['rid']]['data']

def pointers(value):
    if isinstance(value, dict):
        if set(value) == {'m_FileID', 'm_PathID'}:
            if value['m_PathID']:
                yield value
        else:
            for x in value.values():
                yield from pointers(x)
    elif isinstance(value, (list, tuple)):
        for x in value:
            yield from pointers(x)

audits, tx = [], []
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    env = UnityPy.load(before[folder / W])
    obs = {o.path_id: o for o in env.objects}
    hashes = {i: sha(o.get_raw_data()) for i, o in obs.items()}
    metaob = next(o for o in env.objects if o.type.name == 'AssetBundle')
    meta = metaob.read_typetree()
    oldmeta = copy.deepcopy(meta)
    targets = {v['asset']['m_PathID'] for k, v in meta['m_Container']
               if k in [PRIVATE, NATIVE] and v['asset']['m_FileID'] == 0
               and 'inlineSheet' in obs[v['asset']['m_PathID']].read_typetree()}
    assert targets == {-990000000060050, -950000000000069, -1465827634544911600}, targets

    source = obs[-950000000000195].read_typetree()
    sr = refs(source)
    source_nodes = [1027, 1039, 1046]
    assert [sr[i]['data']['m_FullTypeName'] for i in source_nodes] == [
        'SI.Bindable.BindingVariables', 'UnityEngine.UIElements.VisualElement', 'SI.Bindable.SIImage']
    assert sr[1027]['data']['m_Children'] == [{'rid': 1039}]
    assert sr[1039]['data']['m_Children'] == [{'rid': 1046}]
    native_binding = copy.deepcopy(sd(sr, 1046)['Binding'])
    assert native_binding['m_visualFunction']['m_target']['m_guid'] == PHOTO_FUNC
    assert native_binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'][0] == 3
    native_variables = copy.deepcopy(sd(sr, 1027)['ValueVariables'])
    assert 'person.UniqueId' in native_variables[0]['m_scopeValue']['m_serializedData']
    source_ids = source_nodes + [sr[i]['data']['m_SerializedData']['rid'] for i in source_nodes]
    changed, items = {}, []

    for pid in sorted(targets):
        ob = obs[pid]
        d = ob.read_typetree()
        old = copy.deepcopy(d)
        rr = refs(d)
        instance = next(r for r in rr.values() if r.get('data', {}).get('m_TemplateAlias') == 'PersonPicture')
        oldrid = instance['rid']
        assert not instance['data']['m_Children']
        assert not instance['data']['m_SerializedDataOverride']
        removed = {oldrid, instance['data']['m_SerializedData']['rid']}
        parent = instance['data']['m_Parent']['rid']
        styleob = obs[d['inlineSheet']['m_PathID']]
        sheet = styleob.read_typetree()
        st = Styles(sheet)
        mapping = {i: max(rr) + 1 + j for j, i in enumerate(source_ids)}
        next_id = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
        asset_ids = {sr[i]['data']['m_Id']: next_id + j for j, i in enumerate(source_nodes)}
        assert max(asset_ids.values()) < 2 ** 31

        def remap(v):
            if isinstance(v, dict):
                if set(v) == {'rid'}:
                    return {'rid': mapping.get(v['rid'], v['rid'])}
                return {k: remap(x) for k, x in v.items()}
            if isinstance(v, list):
                return [remap(x) for x in v]
            return v

        for i in source_ids:
            row = remap(copy.deepcopy(sr[i]))
            row['rid'] = mapping[i]
            a = row.get('data', {})
            for k in ['m_Id', 'uxmlAssetId']:
                if k in a:
                    a[k] = asset_ids[a[k]]
            if 'm_RuleIndex' in a:
                a['m_RuleIndex'] = -1
                a['m_Classes'] = []
            rr[row['rid']] = row
        root = mapping[1027]
        rr[root]['data']['m_Parent'] = {'rid': parent}
        rr[parent]['data']['m_Children'] = [
            {'rid': root} if c['rid'] == oldrid else c for c in rr[parent]['data']['m_Children']]
        for i in removed:
            del rr[i]
        for i, name in zip(source_nodes, ['StaffHoverNativePhotoBinding', 'StaffHoverNativePhotoFrame', 'StaffHoverNativePhoto']):
            node = rr[mapping[i]]
            data = sd(rr, mapping[i])
            data.update(name=name, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
            st.edit(node, [st.p(k, st.px(180)) for k in [131105, 131087, 131097, 131096, 131095, 131094]] + [
                st.p(131084, st.num(0)), st.p(131085, st.num(0)),
                st.p(131102, st.en('relative')), st.p(131081, st.en('flex')),
                st.p(458767, st.num(1)), st.p(327681, st.num(1), st.num(1)),
                st.p(262150, st.px(0)), st.p(262151, st.px(0)), st.p(458768, st.en('visible'))], reset=True)
        image = sd(rr, mapping[1046])
        image.update(tintColor={'r': 1., 'g': 1., 'b': 1., 'a': 1.}, tintColor_UxmlAttributeFlags=1)
        assert image['scaleMode'] == image['ScaleMode'] == 2
        st.edit(rr[mapping[1046]], [st.p(262153, st.en('scale-to-fit'))])
        assert image['Binding'] == native_binding
        assert sd(rr, root)['ValueVariables'] == native_variables
        d['m_Usings'] = [u for u in d['m_Usings'] if u['alias'] != 'PersonPicture']
        d['references']['RefIds'] = list(rr.values())
        d['m_ContentHash'] += 1
        sheet['m_ContentHash'] += 1

        # All staff content, events, bindings and ancestors remain exactly as before.
        for i, row in refs(old).items():
            if i in removed:
                continue
            actual = copy.deepcopy(rr[i])
            if i == parent:
                actual['data']['m_Children'] = row['data']['m_Children']
            assert actual == row, ('Unrelated staff content changed', pid, i)
        for i, row in rr.items():
            a = row.get('data', {})
            for child in a.get('m_Children', []):
                assert rr[child['rid']]['data']['m_Parent']['rid'] == i
            if a.get('m_SerializedData', {}).get('rid', -2) != -2:
                assert a['m_Id'] == sd(rr, i)['uxmlAssetId']
        for o, data in [(ob, d), (styleob, sheet)]:
            o.save_typetree(data)
            changed[o.path_id] = data
        old_using = next(u for u in old['m_Usings'] if u['alias'] == 'PersonPicture')
        entries = [v for k, v in oldmeta['m_Container'] if v['asset'] == {'m_FileID': 0, 'm_PathID': pid}]
        old_dependency_missing = any(old_using['asset'] not in oldmeta['m_PreloadTable'][
            v['preloadIndex']:v['preloadIndex'] + v['preloadSize']] for v in entries)
        items.append({'pid': str(pid), 'name': d['m_Name'], 'old_nested_photo_missing_from_preload': old_dependency_missing,
                      'normal_native_photo_binding_byte_identical': True, 'dynamic_person_data_identical': True,
                      'node_rids': [mapping[i] for i in source_nodes], 'source_native_node_rids': source_nodes,
                      'size': [180, 180], 'photo_gates_and_nested_template_dependency_removed': True})

    # Rebuild only these asset preload spans from their actual local pointer closure.
    for key, entry in meta['m_Container']:
        if entry['asset'] != {'m_FileID': 0, 'm_PathID': entry['asset']['m_PathID']} or entry['asset']['m_PathID'] not in targets:
            continue
        span = copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        queue, seen = [entry['asset']], set()
        while queue:
            ptr = queue.pop()
            ident = (ptr['m_FileID'], ptr['m_PathID'])
            if ident in seen:
                continue
            seen.add(ident)
            if ptr not in span:
                span.append(copy.deepcopy(ptr))
            if ptr['m_FileID'] == 0:
                assert ptr['m_PathID'] in obs
                tree = changed.get(ptr['m_PathID'])
                if tree is None:
                    tree = obs[ptr['m_PathID']].read_typetree()
                queue.extend(pointers(tree))
        entry['preloadIndex'] = len(meta['m_PreloadTable'])
        entry['preloadSize'] = len(span)
        meta['m_PreloadTable'].extend(span)
    for (k, e), (ok, oe) in zip(meta['m_Container'], oldmeta['m_Container']):
        assert k == ok and e['asset'] == oe['asset']
        if e['asset']['m_PathID'] not in targets:
            assert e == oe
    assert meta['m_PreloadTable'][:len(oldmeta['m_PreloadTable'])] == oldmeta['m_PreloadTable']
    metaob.save_typetree(meta)
    changed[metaob.path_id] = meta

    cat = cm.Catalog(((folder.parent if tag == 'game' else folder) / 'catalog.bin').read_bytes())
    keys = dict(cat.keys())
    def locations(k):
        return [i for (i,) in cat.array(keys[k], 'I')]
    for guid in [PRIVATE, NATIVE]:
        li = next(i for i in locations(guid) if cat.location(i)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset')
        assert cat.location(li)['internal'] == guid
        assert cat.location(cat.location(li)['dependencies'][0])['internal'].endswith(W)
        assert li in locations('GameWorldVisualTreeAssetPreload')
    fl = next(cat.location(i) for i in locations(PHOTO_FUNC) if cat.location(i)['type'][1] == 'SI.VisualScripting.VisualFunction')
    assert fl['internal'] == PHOTO_FUNC
    fnb = cat.location(fl['dependencies'][0])['internal'].replace('\\', '/').split('/')[-1]
    function_path = folder / fnb if (folder / fnb).exists() else GAME / fnb
    assert function_path.is_file(), function_path
    fe = UnityPy.load(str(function_path))
    fm = next(o.read_typetree() for o in fe.objects if o.type.name == 'AssetBundle')
    fo = {o.path_id: o for o in fe.objects}
    assert any(k == PHOTO_FUNC and fo[v['asset']['m_PathID']].peek_name() == 'DynamicReferenceToAddressableID'
               for k, v in fm['m_Container'] if v['asset']['m_FileID'] == 0)

    data = env.file.save(packer='lz4')
    reread = {o.path_id: o for o in UnityPy.load(data).objects}
    assert set(reread) == set(obs)
    for i, o in reread.items():
        if i in changed:
            assert o.read_typetree() == changed[i]
        else:
            assert sha(o.get_raw_data()) == hashes[i], i
    dest, backup = OUT / tag / W, OUT / ('backup-' + tag) / W
    dest.parent.mkdir()
    backup.parent.mkdir()
    dest.write_bytes(data)
    backup.write_bytes(before[folder / W])
    tx.append({'target': str(folder / W), 'source': str(dest), 'backup': str(backup),
               'before': sha(before[folder / W]), 'after': sha(data)})
    audits.append({'variant': tag, 'targets': items, 'changed_objects': list(changed),
                   'unrelated_objects_byte_identical': True, 'preload_pointer_closure_verified': True,
                   'catalog_types_internal_ids_owners_and_preload_verified': True})

report = {'installed': False, 'runtime_verified': False, 'desktop_control_used': False,
          'confirmed_findings': ['Earlier direct-photo patches targeted native hover only; active private hover copies still used nested portrait templates.',
                                 'Latest nested portrait references were absent from all three hover asset preload spans.'],
          'causal_limit': 'No live UI inspection: which runtime loading/visibility step produced the blank photo is not proven.',
          'approach': 'Inline untouched normal-person dynamic photo binding on actual routes; no shared-template visibility gates or nested portrait dependency.',
          'audits': audits, 'protected_sha256': {str(p): h for p, h in protected.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(tx, indent=2), 'utf8')
(OUT / 'installer.py').write_bytes((R / 'install-independent-resource-patch.py').read_bytes())
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference='Stop'\n& '" + sys.executable + "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode + "\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n", 'utf-8-sig')
for p, b in before.items():
    assert p.read_bytes() == b, ('Target changed during preparation', p)
proc = subprocess.run([sys.executable, str(OUT / 'installer.py'), str(OUT)], capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr)
assert proc.returncode == 0, 'Patch prepared; installation did not complete'
(R / 'current-staff-hover-portrait.json').write_text(json.dumps({
    'manifest': str(OUT / 'manifest.json'), 'installed': True, 'runtime_verified': False,
    'active_hover_guid': PRIVATE, 'portrait': 'Inline native normal-person photo branch in both private hover copies and native hover',
    'size': [180, 180], 'preload_pointer_closure_verified': True}, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'output': str(OUT), 'installed': True, 'runtime_verified': False}, ensure_ascii=True))
