import copy
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

PACKAGES = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT = ROOT / '去光效标志下移头像完整显示-v12'
BANNER_ID = -4194025542157271532
STYLE_ID = 8045407476604796436
PERSON_ID = -910000000000101
PERSON_STYLE_ID = -910000000000102
HEADER_ID = 5775949770471550939
HEADER_STYLE_ID = -1940069326759809061
ICON_DOC_ID = -910000000000201
ICON_STYLE_ID = -910000000000202
ICON_ALIAS = 'ReportIconsBelowPlayerTopBackground'
SCALE_ID = 327681

original_write_value = TypeTreeHelper.write_value
def write_value(value, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(value, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData':
                original_write_value(value[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):
            writer.align_stream()
        return
    return original_write_value(value, node, writer, config)
TypeTreeHelper.write_value = write_value

def load(path):
    env = UnityPy.load(str(path))
    objects = {o.path_id: o for o in env.objects}
    return env, objects
def refs_of(doc):
    return {r['rid']: r for r in doc['references']['RefIds']}
def named(refs, name):
    sd = next(r for r in refs.values() if r.get('data', {}).get('name') == name)
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])['rid']
def pool(sheet, key, value, typ):
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[key].index(value)}
def number(sheet, v):
    return pool(sheet, 'floats', struct.unpack('<f', struct.pack('<f', v))[0], 2)
def px(sheet, v):
    return pool(sheet, 'dimensions', {'unit': 1, 'value': float(v)}, 3)
def pct(sheet, v):
    return pool(sheet, 'dimensions', {'unit': 2, 'value': float(v)}, 3)
def enum(sheet, v):
    return pool(sheet, 'strings', v, 7)
def prop(pid, values):
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1,
            'm_Values': [values] if isinstance(values, dict) else values}
def append_rule(sheet, props):
    i = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': props, 'line': -1})
    return i
def edit_properties(sheet, rule_index, additions=(), remove=()):
    properties = sheet['m_Rules'][rule_index]['m_Properties']
    remove = set(remove) | {p['m_Id'] for p in additions}
    properties[:] = [p for p in properties if p['m_Id'] not in remove]
    properties.extend(additions)
def reachable_nodes(doc):
    refs = refs_of(doc)
    seen = set()
    def visit(rid):
        assert rid not in seen
        seen.add(rid)
        for c in refs[rid].get('data', {}).get('m_Children', []):
            assert refs[c['rid']]['data']['m_Parent']['rid'] == rid
            visit(c['rid'])
    visit(doc['m_VisualTree']['rid'])
    return seen
def prune(doc):
    refs = refs_of(doc)
    alive = reachable_nodes(doc)
    pending = list(alive)
    def referenced(v):
        if isinstance(v, dict):
            if set(v) == {'rid'} and v['rid'] in refs:
                yield v['rid']
            else:
                for x in v.values():
                    yield from referenced(x)
        elif isinstance(v, list):
            for x in v:
                yield from referenced(x)
    while pending:
        rid = pending.pop()
        for dependency in referenced(refs[rid].get('data', {})):
            if dependency not in alive:
                alive.add(dependency)
                pending.append(dependency)
    alive.add(-2)
    doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] in alive]
def hashes(objects):
    return {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}

gsource = PACKAGES / GLOBAL
genv, gobjs = load(gsource)
if PERSON_ID not in gobjs:
    gsource = ROOT / '中间三层缩放调整-v11' / GLOBAL
    genv, gobjs = load(gsource)
wsource = PACKAGES / WORLD
wenv, wobjs = load(wsource)
source_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [gsource, wsource, PACKAGES / GLOBAL]}
ghashes, whashes = hashes(gobjs), hashes(wobjs)
gfile, wfile = gobjs[BANNER_ID].assets_file, wobjs[HEADER_ID].assets_file
banner, gs = gobjs[BANNER_ID].read_typetree(), gobjs[STYLE_ID].read_typetree()
header, ws = wobjs[HEADER_ID].read_typetree(), wobjs[HEADER_STYLE_ID].read_typetree()
old_banner, old_gs = copy.deepcopy(banner), copy.deepcopy(gs)
old_header, old_ws = copy.deepcopy(header), copy.deepcopy(ws)
gr, wr = refs_of(banner), refs_of(header)
stage = named(gr, 'ReportPortraitLayerStage')
icons = named(gr, 'ReportFlagClubBackgroundLayer')
blue = named(gr, 'ReportMiddleBlueLightLayer')
card = named(gr, 'ReportMiddleCA000Layer')
frame = named(gr, 'PersonPictureFrame')
middle = named(gr, 'ReportPortraitStatusColumn')
root = named(gr, 'report-player-banner-max')
assert gr[stage]['data']['m_Children'] == [{'rid': r} for r in [icons, blue, card, frame]]

# A private copy keeps the same binding context and three-column geometry for the icons.
icon_doc = copy.deepcopy(banner)
ir = refs_of(icon_doc)
for child in ir[root]['data']['m_Children']:
    rid = child['rid']
    if rid != middle:
        ir[rid]['data']['m_Children'] = []
ir[middle]['data']['m_Children'] = [{'rid': stage}]
ir[stage]['data']['m_Children'] = [{'rid': icons}]
prune(icon_doc)
icon_doc['m_Name'] = ICON_ALIAS
icon_doc['m_Usings'] = []
icon_doc['m_AssetEntries'] = []
icon_doc['inlineSheet'] = {'m_FileID': 0, 'm_PathID': ICON_STYLE_ID}
icon_style = copy.deepcopy(ws)
icon_style['m_Name'] = ICON_ALIAS + 'InlineStyle'
for k in ['m_Rules', 'floats', 'dimensions', 'colors', 'strings', 'assets', 'imports',
          'm_FlattenedImportedStyleSheets', 'scalableImages']:
    icon_style[k] = []
rule_map = {}
for ref in icon_doc['references']['RefIds']:
    d = ref.get('data', {})
    index = d.get('m_RuleIndex', -1)
    if index < 0:
        continue
    if index not in rule_map:
        copied = copy.deepcopy(gs['m_Rules'][index])
        for p in copied['m_Properties']:
            for v in p['m_Values']:
                key = {2: 'floats', 3: 'dimensions', 4: 'colors', 6: 'assets', 7: 'strings'}.get(v['m_ValueType'])
                if key:
                    assert key != 'assets', 'Icon underlay must not depend on local global textures'
                    val = copy.deepcopy(gs[key][v['valueIndex']])
                    v['valueIndex'] = pool(icon_style, key, val, v['m_ValueType'])['valueIndex']
        rule_map[index] = len(icon_style['m_Rules'])
        icon_style['m_Rules'].append(copied)
    d['m_RuleIndex'] = rule_map[index]

# Ensure the destination supports the copied native binding serialized types.
type_key = lambda t: (t.m_ClassName, t.m_NameSpace, t.m_AssemblyName)
existing_keys = {type_key(t) for t in wfile.ref_types}
needed_keys = {(r['type']['class'], r['type']['ns'], r['type']['asm']) for r in icon_doc['references']['RefIds'] if r['rid'] >= 0}
for t in gfile.ref_types:
    if type_key(t) in needed_keys and type_key(t) not in existing_keys:
        wfile.ref_types.append(copy.copy(t))
        existing_keys.add(type_key(t))
assert needed_keys <= existing_keys
for pid, original, tree in [(ICON_DOC_ID, wobjs[HEADER_ID], icon_doc),
                            (ICON_STYLE_ID, wobjs[HEADER_STYLE_ID], icon_style)]:
    assert pid not in wfile.objects
    new = copy.copy(original)
    new.path_id, new.data, new._read_until = pid, None, None
    new.save_typetree(tree)
    wfile.objects[pid] = new

# Remove the visible icon and BlueLight layers from the foreground banner.
gr[stage]['data']['m_Children'] = [{'rid': card}, {'rid': frame}]
prune(banner)
edit_properties(gs, gr[frame]['data']['m_RuleIndex'], remove=[SCALE_ID])

# The 200x200 outer frame stays at full size. Scale only the bound image elements.
person = gobjs[PERSON_ID].read_typetree()
ps = gobjs[PERSON_STYLE_ID].read_typetree()
old_person, old_ps = copy.deepcopy(person), copy.deepcopy(ps)
pr = refs_of(person)
portrait_image_rids = []
for r in person['references']['RefIds']:
    d = r.get('data', {})
    if d.get('m_FullTypeName') != 'SI.Bindable.SIImage':
        continue
    portrait_image_rids.append(r['rid'])
    sd = pr[d['m_SerializedData']['rid']]['data']
    sd.update(ScaleMode=2, ScaleMode_UxmlAttributeFlags=1,
              scaleMode=2, scaleMode_UxmlAttributeFlags=1)
    edit_properties(ps, d['m_RuleIndex'], additions=[
        prop(262153, enum(ps, 'scale-to-fit')),
        prop(SCALE_ID, [number(ps, 0.75), number(ps, 0.75)]),
    ])
assert len(portrait_image_rids) == 4

# Clone the existing header positioning and responsive chain as an absolute underlay.
# The original foreground chain is preserved exactly, so its height and layout do not change.
clone_doc = copy.deepcopy(header)
cr = refs_of(clone_doc)
cloned_nodes = set()
def collect(rid):
    cloned_nodes.add(rid)
    d = cr[rid]['data']
    children = []
    for c in d.get('m_Children', []):
        child = cr[c['rid']]
        if child['type']['class'] == 'TemplateAsset' and c['rid'] != 1027:
            continue
        # The original hidden portrait has no purpose in a background-only copy.
        if c['rid'] == 1010:
            continue
        children.append(c)
        collect(c['rid'])
    d['m_Children'] = children
collect(1006)
clone_rids = set(cloned_nodes)
for rid in cloned_nodes:
    serialized = cr[rid]['data'].get('m_SerializedData', {}).get('rid', -2)
    if serialized >= 0:
        clone_rids.add(serialized)
next_rid = max(wr) + 1
rid_map = {rid: next_rid + i for i, rid in enumerate(sorted(clone_rids))}
id_map = {cr[rid]['data']['m_Id']: 1900600000 + i for i, rid in enumerate(sorted(cloned_nodes))}
def remap(value):
    if isinstance(value, dict):
        for key, v in list(value.items()):
            if key == 'rid' and v in rid_map:
                value[key] = rid_map[v]
            elif key in ['m_Id', 'uxmlAssetId', 'm_ParentId'] and isinstance(v, int) and v in id_map:
                value[key] = id_map[v]
            else:
                remap(v)
    elif isinstance(value, list):
        for v in value:
            remap(v)
for rid in sorted(clone_rids):
    ref = copy.deepcopy(cr[rid])
    remap(ref)
    ref['rid'] = rid_map[rid]
    wr[ref['rid']] = ref
    header['references']['RefIds'].append(ref)
underlay = rid_map[1006]
underlay_template = wr[rid_map[1027]]
underlay_template['data']['m_TemplateAlias'] = ICON_ALIAS
underlay_sd = wr[underlay_template['data']['m_SerializedData']['rid']]['data']
underlay_sd.update(templateId=ICON_ALIAS, templateId_UxmlAttributeFlags=1,
                    template={'m_FileID': 0, 'm_PathID': ICON_DOC_ID}, template_UxmlAttributeFlags=1,
                    name='ReportIconsBackgroundTemplate', name_UxmlAttributeFlags=1)
wr[underlay]['data']['m_Parent'] = {'rid': 1004}
underlay_root_sd = wr[wr[underlay]['data']['m_SerializedData']['rid']]['data']
underlay_root_sd.update(name='ReportIconsUnderBackgroundLayer', name_UxmlAttributeFlags=1)
base_rule = copy.deepcopy(ws['m_Rules'][wr[underlay]['data']['m_RuleIndex']]['m_Properties'])
underlay_rule = append_rule(ws, base_rule)
wr[underlay]['data']['m_RuleIndex'] = underlay_rule
edit_properties(ws, underlay_rule, additions=[
    prop(131102, enum(ws, 'absolute')), prop(131089, px(ws, 0)), prop(131104, px(ws, 0)),
    prop(131105, pct(ws, 100)), prop(131087, pct(ws, 100)),
])
background_image = named(wr, 'PlayerTopBackgroundTextureLayer')
assert wr[1004]['data']['m_Children'] == [{'rid': background_image}, {'rid': 1006}]
wr[1004]['data']['m_Children'].insert(0, {'rid': underlay})
alias_hash = hashlib.md5(ICON_ALIAS.encode()).hexdigest()
header['m_Usings'].append({'alias': ICON_ALIAS, 'path': alias_hash,
                          'asset': {'m_FileID': 0, 'm_PathID': ICON_DOC_ID}})

# Existing styles, bindings and layouts are unchanged except the requested middle edits.
new_gr = refs_of(banner)
old_gr = refs_of(old_banner)
removed_refs = set(old_gr) - set(new_gr)
for rid in set(new_gr) & set(old_gr):
    if rid != stage:
        assert new_gr[rid] == old_gr[rid], rid
for r in old_header['references']['RefIds']:
    expected = copy.deepcopy(r)
    if r['rid'] == 1004:
        expected['data']['m_Children'].insert(0, {'rid': underlay})
    assert wr[r['rid']] == expected, r['rid']
assert ws['m_Rules'][:len(old_ws['m_Rules'])] == old_ws['m_Rules']
for i, old_rule in enumerate(old_gs['m_Rules']):
    if i != gr[frame]['data']['m_RuleIndex']:
        assert gs['m_Rules'][i] == old_rule
for doc in [banner, header, icon_doc, person]:
    live = reachable_nodes(doc)
    rr = refs_of(doc)
    assert live == {rid for rid, r in rr.items() if 'm_Id' in r.get('data', {})}
    assert len(live) == len({rr[rid]['data']['m_Id'] for rid in live})
assert 'ReportMiddleBlueLightLayer' not in {r.get('data', {}).get('name') for r in new_gr.values()}
assert 'ReportFlagClubBackgroundLayer' not in {r.get('data', {}).get('name') for r in new_gr.values()}
assert new_gr[stage]['data']['m_Children'] == [{'rid': card}, {'rid': frame}]
assert all(p['m_Id'] != SCALE_ID for p in gs['m_Rules'][gr[frame]['data']['m_RuleIndex']]['m_Properties'])

for pid, tree in [(BANNER_ID, banner), (STYLE_ID, gs), (PERSON_ID, person), (PERSON_STYLE_ID, ps)]:
    gobjs[pid].save_typetree(tree)
for pid, tree in [(HEADER_ID, header), (HEADER_STYLE_ID, ws)]:
    wobjs[pid].save_typetree(tree)

world_bundle_obj = next(o for o in wenv.objects if o.type.name == 'AssetBundle')
world_bundle = world_bundle_obj.read_typetree()
extra = [{'m_FileID': 0, 'm_PathID': pid} for pid in [ICON_DOC_ID, ICON_STYLE_ID]]
for key, info in world_bundle['m_Container']:
    items = copy.deepcopy(world_bundle['m_PreloadTable'][info['preloadIndex']:info['preloadIndex'] + info['preloadSize']])
    if any(p['m_FileID'] == 0 and p['m_PathID'] in [HEADER_ID, HEADER_STYLE_ID] for p in items):
        info['preloadIndex'] = len(world_bundle['m_PreloadTable'])
        info['preloadSize'] = len(items) + len(extra)
        world_bundle['m_PreloadTable'].extend(items + copy.deepcopy(extra))
for pid in [ICON_DOC_ID, ICON_STYLE_ID]:
    start = len(world_bundle['m_PreloadTable'])
    world_bundle['m_PreloadTable'].extend(copy.deepcopy(extra))
    world_bundle['m_Container'].append((alias_hash, {'preloadIndex': start, 'preloadSize': len(extra),
                                                   'asset': {'m_FileID': 0, 'm_PathID': pid}}))
world_bundle['m_Container'].sort(key=lambda pair: pair[0])
world_bundle_obj.save_typetree(world_bundle)

OUT.mkdir(exist_ok=True)
outputs = {GLOBAL: (genv, gobjs, ghashes, {BANNER_ID, STYLE_ID, PERSON_ID, PERSON_STYLE_ID}),
           WORLD: (wenv, wobjs, whashes, {HEADER_ID, HEADER_STYLE_ID, world_bundle_obj.path_id})}
for filename, (env, objs, old_hashes, changed) in outputs.items():
    target = OUT / filename
    target.write_bytes(env.file.save(packer='lz4'))
    check_env, check = load(target)
    extra_ids = {ICON_DOC_ID, ICON_STYLE_ID} if filename == WORLD else set()
    assert set(check) == set(objs) | extra_ids
    for pid, digest in old_hashes.items():
        if pid not in changed:
            assert hashlib.sha256(check[pid].get_raw_data()).digest() == digest, (filename, pid)
    trees = [(BANNER_ID, banner), (STYLE_ID, gs), (PERSON_ID, person), (PERSON_STYLE_ID, ps)] if filename == GLOBAL else [
        (HEADER_ID, header), (HEADER_STYLE_ID, ws), (ICON_DOC_ID, icon_doc), (ICON_STYLE_ID, icon_style),
        (world_bundle_obj.path_id, world_bundle)]
    for pid, tree in trees:
        assert check[pid].read_typetree() == tree, (filename, pid)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p, digest in source_hashes.items())

readme = '''去光效、标志下移、头像完整显示 v12

安装：备份后，用本包两个同名bundle替换皮肤packages内的global和gameworld bundle，然后重启游戏。
本版必须同时替换两个文件，backgrounds bundle不需要替换。

从下到上的层级：
俱乐部渐变 → 国旗/俱乐部队徽 → PlayerTopBackground → CA000（115%）→ 球员头像。
BlueLight的显示节点已移除。

国旗、队徽保留原图片绑定及位置、尺寸、间隔和现有旋转设置。
为使其确实位于PlayerTopBackground下方，建立同几何布局的独立背景节点，并放在gameworld的球场背景图片之前绘制。
背景节点绝对定位，原来的前景内容、左右栏布局及头部高度不变。

头像外框恢复200×200、保持100%尺寸，不再缩放整套头像模板。
内部四种球员图片分支均改为scale-to-fit完整显示，只对实际SIImage图片元素缩放75%，居中显示。
图片不再按scale-and-crop裁剪。原有球员图片绑定和共享模板保持不变。

成品已重读，验证图层顺序、父子关系、绑定、图片显示方式、75%内部缩放和未修改资源字节。
源packages文件未覆盖。尚未在游戏中确认实际显示效果。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({
    'source_sha256': source_hashes,
    'layer_order': ['club gradient', 'flag and club logo', 'PlayerTopBackground', 'CA000', 'portrait'],
    'blue_light_removed': True, 'portrait_outer_frame_scale': 1.0,
    'portrait_image_scale': 0.75, 'portrait_scale_mode': 'scale-to-fit',
    'portrait_image_branches': portrait_image_rids, 'CA000_scale': 1.15,
    'removed_global_ref_ids': sorted(removed_refs), 'new_underlay_visualtree': ICON_DOC_ID,
    'untouched_global_objects': len(ghashes) - 4, 'untouched_gameworld_objects': len(whashes) - 3,
}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'global_untouched': len(ghashes)-4,
                  'gameworld_untouched': len(whashes)-3, 'image_scale': 0.75,
                  'image_scale_mode': 'scale-to-fit', 'outer_frame_scale': 1,
                  'layer_order_verified': True}, ensure_ascii=True))
