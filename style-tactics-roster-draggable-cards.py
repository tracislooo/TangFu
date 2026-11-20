from pathlib import Path
import subprocess

source = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
source = source.replace('inspect-fitness-backdrop-', 'tactics-draggable-roster-cards-')
exec(compile(source, 'load-current-game-and-skin', 'exec'))

location = json.loads((R / 'current-game-location.json').read_text('utf-8-sig'))
assert GAME.resolve() == Path(location['bundle_root']).resolve()
catalog_spec = importlib.util.spec_from_file_location('roster_catalog', R / 'catalog-binary-v35.py')
catalog_module = importlib.util.module_from_spec(catalog_spec)
catalog_spec.loader.exec_module(catalog_module)
outputs = {}
checks = []

def rgba(hexcode):
    channels = [int(hexcode[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return dict(zip('rgba', struct.unpack('<4f', struct.pack('<4f', *channels, 1.0))))

def frame(doc, node, color, radius):
    widths = [(key, doc.px(1)) for key in (131076, 131077, 131078, 131079)]
    edges = [(key, doc.val(4, rgba(color))) for key in (458758, 458761, 458762, 458763)]
    doc.st(node, widths + edges + [(262147, doc.px(radius))])

for folder, tag in ((GAME, 'game'), (SKIN, 'skin')):
    env[W] = UnityPy.load(before[folder / W])
    objs[W] = {obj.path_id: obj for obj in env[W].objects}
    hashes[W] = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    changes[W] = {}
    portraits = [Doc(W, pid=obj.path_id) for obj in objs[W].values()
                 if obj.type.name == 'MonoBehaviour' and obj.peek_name() == 'TacticsPlayerPortraitNameCell']
    assert portraits
    for name in ('TacticsTeamSelectionDraggableRowElement', 'TacticsTeamSelectionDraggableRowElementInMatch'):
        doc = Doc(W, name=name)
        drag = doc.named('DragObject')
        original_drag = copy.deepcopy(doc.r[drag])
        original_drag_data = copy.deepcopy(doc.data(drag))
        parent = doc.a(drag)['m_Parent']['rid']
        backdrop = doc.add(portraits[0], 1003, parent, 'TacticsRosterCardSurface')
        doc.move(backdrop, parent, 0)
        doc.st(backdrop, [(131102, doc.enum('absolute')), (131089, doc.px(0)),
                          (131103, doc.px(0)), (131104, doc.px(2)), (131080, doc.px(2)),
                          (458752, doc.val(4, rgba('263445')))])
        frame(doc, backdrop, '52677E', 6)
        assert doc.data(backdrop)['pickingMode'] == 1
        assert doc.r[drag] == original_drag and doc.data(drag) == original_drag_data
        assert original_drag_data['Droppable'] and original_drag_data['DragDropKeyBinding']['m_path']
        doc.save()

    table = Doc(W, name='TacticalPlannerTeamShapeTableTemplate')
    table_data = table.data(table.named('Table'))
    assert table_data['FixedElementSize_UxmlAttributeFlags']
    table_data['FixedElementSize'] = 44.0
    table.save()
    for doc in portraits:
        portrait = doc.named('TacticsTablePlayerPortrait')
        mapper = doc.a(portrait)['m_Parent']['rid']
        holder = doc.a(mapper)['m_Parent']['rid']
        for node in (holder, mapper, portrait):
            doc.size(node, 34, 34)
        frame(doc, holder, '52677E', 4)
        doc.st(holder, [(458768, doc.enum('hidden'))])
        doc.save()

    catalog_path = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    catalog = catalog_module.Catalog(before[catalog_path])
    meta = next(obj.read_typetree() for obj in objs[W].values() if obj.type.name == 'AssetBundle')
    templates = {pid for pid, doc in changes[W].items() if 'inlineSheet' in doc}
    registered = set()
    for key, entry in meta['m_Container']:
        pid = entry['asset']['m_PathID']
        if pid not in templates:
            continue
        for index in catalog.locations(key):
            detail = catalog.location(index)
            if detail['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset' and detail['dependencies']:
                bundle = catalog.location(detail['dependencies'][0])['internal'].replace('\\', '/')
                if bundle.endswith('/' + W):
                    registered.add(pid)
    assert templates == registered, ('missing typed catalog registration', tag, templates - registered)
    data = env[W].file.save(packer='lz4')
    saved = {obj.path_id: obj for obj in UnityPy.load(data).objects}
    assert saved.keys() == objs[W].keys()
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid]
        else:
            assert sha(obj.get_raw_data()) == hashes[W][pid]
    outputs[folder / W] = data
    (OUT / ('output-' + tag)).mkdir()
    (OUT / ('output-' + tag) / W).write_bytes(data)
    checks.append({'target': tag, 'row_height': 44, 'portrait_size': 34, 'native_drag_payload_and_drop_key_preserved': True,
                   'registered_templates': sorted(registered), 'unrelated_assets_unchanged': True})

G = W
marker = "for p,b in before.items():\n if p.name.startswith('catalog.')"
tail = marker + Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split(marker, 1)[1]
start = tail.index("(OUT/'修改说明.md').write_text(")
end = tail.index('\nprint(', start)
tail = tail[:start] + "(OUT/'修改说明.md').write_text('战术右侧名单横向卡片，44px行高、34px头像、深灰蓝圆角卡面。使用现有拖拽行模板，保留原数据、拖拽键、落点及名单列。装饰层忽略鼠标。资源回读与目录检查通过，实际显示及拖拽待游戏内验证。','utf8')" + tail[end:]
exec(compile(tail, 'verify-backup-install', 'exec'))
