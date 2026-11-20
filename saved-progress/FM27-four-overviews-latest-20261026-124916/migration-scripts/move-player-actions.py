import copy, datetime, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

PACKAGES = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
OUT = ROOT / ('Action移入属性区-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
(OUT / 'backup').mkdir()
(OUT / 'modified').mkdir()
NAMES = ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
         'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']
sha = lambda b: hashlib.sha256(b).hexdigest()
original = {n: (PACKAGES / n).read_bytes() for n in NAMES}
for n, b in original.items():
    (OUT / 'backup' / n).write_bytes(b)
envs = {n: UnityPy.load(b) for n, b in original.items()}
objects = {n: {o.path_id: o for o in e.objects} for n, e in envs.items()}
hashes = {n: {i: sha(o.get_raw_data()) for i, o in obs.items()} for n, obs in objects.items()}
changed = {n: {} for n in NAMES}

# Unity 6 null managed references have no ReferencedObjectData payload.
old_write = TypeTreeHelper.write_value
def write(v, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData':
                old_write(v[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):
            writer.align_stream()
        return
    return old_write(v, node, writer, config)
TypeTreeHelper.write_value = write

def refs(d):
    return {r['rid']: r for r in d['references']['RefIds']}

g, w = NAMES
banner_obj = objects[g][-4194025542157271532]
banner = banner_obj.read_typetree()
br = refs(banner)
source_sheet = objects[g][banner['inlineSheet']['m_PathID']].read_typetree()
tree_ids = []
def collect(i):
    tree_ids.append(i)
    for child in br[i]['data']['m_Children']:
        collect(child['rid'])
collect(1013)
copy_ids = tree_ids + [br[i]['data']['m_SerializedData']['rid'] for i in tree_ids]
assert len(copy_ids) == len(set(copy_ids)) == 12
template = [copy.deepcopy(br[i]) for i in copy_ids]

targets = ['PlayerAttributesTooltipBlock', 'PlayerAttributesSmallBlock',
           'PlayerAttributesStandardBlock', 'PlayerAttributesLargeBlock', 'PlayerAttributesCompactBlock']
details = []
for name in targets:
    obj = next(o for o in objects[w].values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name)
    doc = obj.read_typetree()
    rr = refs(doc)
    sheet_obj = objects[w][doc['inlineSheet']['m_PathID']]
    sheet = sheet_obj.read_typetree()
    additions = copy.deepcopy(template)
    start = max(rr) + 1
    mapping = {r['rid']: start + k for k, r in enumerate(additions)}
    def remap(v):
        if isinstance(v, dict):
            if set(v) == {'rid'}:
                if v['rid'] in mapping:
                    v['rid'] = mapping[v['rid']]
            else:
                for value in v.values(): remap(value)
        elif isinstance(v, list):
            for value in v: remap(value)
    style_map = {}
    for r in additions:
        old_id = r['rid']
        remap(r.get('data', {}))
        r['rid'] = mapping[old_id]
        a = r.get('data', {})
        rule_id = a.get('m_RuleIndex', -1)
        if rule_id >= 0:
            if rule_id not in style_map:
                rule = copy.deepcopy(source_sheet['m_Rules'][rule_id])
                for prop in rule['m_Properties']:
                    for h in prop['m_Values']:
                        array = {1: 'dimensions', 2: 'floats', 3: 'colors', 4: 'strings', 5: 'strings'}.get(h['m_ValueType'])
                        if array is None:
                            raise ValueError(h)
                        value = copy.deepcopy(source_sheet[array][h['valueIndex']])
                        h['valueIndex'] = len(sheet[array])
                        sheet[array].append(value)
                style_map[rule_id] = len(sheet['m_Rules'])
                sheet['m_Rules'].append(rule)
            a['m_RuleIndex'] = style_map[rule_id]
    new_refs = {r['rid']: r for r in additions}
    row = new_refs[mapping[1013]]['data']
    row['m_Parent'] = {'rid': 1001}
    row['m_Classes'] = ['row-direction-normal', 'align-self-stretch', 'align-items-center',
                        'flex-no-shrink-class', 'margin-bottom-global-gap-small']
    # Each block explicitly declares the current person in this local scope.
    new_refs[mapping[1053]]['data']['BindingPaths'] = [{'m_path': 'person'}]
    root = rr[1001]['data']
    root['m_Classes'] = [c for c in root['m_Classes'] if c != 'row-direction-normal']
    root['m_Classes'].append('column-direction-normal')
    first_visual = next(k for k, c in enumerate(root['m_Children'])
                        if rr[c['rid']]['type']['class'] != 'UxmlObjectAsset')
    root['m_Children'].insert(first_visual, {'rid': mapping[1013]})
    doc['references']['RefIds'].extend(additions)
    changed[w][obj.path_id] = doc
    changed[w][sheet_obj.path_id] = sheet
    details.append({'asset': name, 'path_id': obj.path_id, 'row_rid': mapping[1013],
                    'menu_rid': mapping[1053], 'style_rules': style_map})

# Remove the old button subtree, retaining the adjacent status flags.
br[1007]['data']['m_Children'].remove({'rid': 1013})
banner['references']['RefIds'] = [r for r in banner['references']['RefIds'] if r['rid'] not in copy_ids]
changed[g][banner_obj.path_id] = banner

def verify_tree(doc):
    rr = refs(doc)
    assert len(rr) == len(doc['references']['RefIds'])
    seen = set()
    def visit(i):
        assert i not in seen
        seen.add(i)
        a = rr[i]['data']
        for c in a.get('m_Children', []):
            assert rr[c['rid']]['data']['m_Parent']['rid'] == i
            visit(c['rid'])
    visit(doc['m_VisualTree']['rid'])
    def check(v):
        if isinstance(v, dict):
            if set(v) == {'rid'}: assert v['rid'] in rr, v
            else:
                for value in v.values(): check(value)
        elif isinstance(v, list):
            for value in v: check(value)
    check(doc)

for n in NAMES:
    for i, doc in changed[n].items():
        if 'm_VisualTree' in doc: verify_tree(doc)
        objects[n][i].save_typetree(doc)
    (OUT / 'modified' / n).write_bytes(envs[n].file.save(packer='lz4'))
    saved = {o.path_id: o for o in UnityPy.load(str(OUT / 'modified' / n)).objects}
    assert set(saved) == set(objects[n])
    for i, obj in saved.items():
        if i in changed[n]: assert obj.read_typetree() == changed[n][i], (n, i)
        else: assert sha(obj.get_raw_data()) == hashes[n][i], (n, i)

manifest = {'installed': False, 'game_runtime_verified': False, 'targets': details, 'files': {}}
for n in NAMES:
    manifest['files'][n] = {'before_sha256': sha(original[n]),
                            'after_sha256': sha((OUT / 'modified' / n).read_bytes()),
                            'changed_objects': list(changed[n]),
                            'unchanged_objects_verified': len(objects[n]) - len(changed[n])}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
for n in NAMES: assert (PACKAGES / n).read_bytes() == original[n], 'Source changed during processing'
try:
    for n in NAMES:
        (PACKAGES / n).write_bytes((OUT / 'modified' / n).read_bytes())
        assert sha((PACKAGES / n).read_bytes()) == manifest['files'][n]['after_sha256']
except Exception:
    for n in NAMES: (PACKAGES / n).write_bytes(original[n])
    raise
manifest['installed'] = True
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), **manifest}, ensure_ascii=False, indent=2))
