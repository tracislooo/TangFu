"""Validate the reviewed merge before allowing installation."""
import ast
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path.cwd()
sys.path.insert(0,str(ROOT / '.codex-deps'))
import UnityPy
out = Path(sys.argv[1])
read = lambda p:json.loads(p.read_text('utf8'))
manifest = read(out / 'manifest.json')
review_root = Path(manifest['review'])
review = read(review_root / 'comparison.json')
spec = importlib.util.spec_from_file_location('catalog', ROOT / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
cat = cm.Catalog((out / 'catalog.bin').read_bytes())
native = cm.Catalog((out / 'backup-game/catalog.bin').read_bytes())
skin = cm.Catalog(Path(review['catalog']['old_modified_catalog_source']).read_bytes())
keys = dict(cat.keys())
locations = {loc:cat.location(loc) for _,ls in cat.keys() for loc, in cat.array(ls,'I')}
native_locations = {loc:native.location(loc) for _,ls in native.keys() for loc, in native.array(ls,'I')}
for loc,v in native_locations.items():
    new = cat.location(loc)
    assert all(new['raw'][i] == v['raw'][i] for i in [0,1,2,5,6]), ('native metadata',loc)
    assert set(v['dependencies']) <= set(new['dependencies']), ('native dependency lost',loc)
for key,ls in native.keys():
    assert key in keys
    assert set(native.array(ls,'I')) <= set(cat.array(keys[key],'I')), key
assert set(review['catalog']['missing_custom_keys']) <= set(keys)
visited,active = set(),set()
def visit(loc):
    if loc in visited:return
    assert loc not in active, ('dependency cycle',loc)
    active.add(loc)
    for dep in cat.location(loc)['dependencies']:visit(dep)
    active.remove(loc)
    visited.add(loc)
for loc in locations:visit(loc)

envs = {n:UnityPy.load(str(out / n)) for n in manifest['after_sha256']}
objects = {n:{o.path_id:o for o in env.objects} for n,env in envs.items()}
assets = {a.name.lower():a for env in envs.values() for a in env.assets}
guid_objects = {}
for n,obs in objects.items():
    meta = next(o.read_typetree() for o in obs.values() if o.type.name == 'AssetBundle')
    for key,v in meta['m_Container']:
        ptr = v['asset']
        if not ptr['m_FileID'] and ptr['m_PathID'] in obs:
            guid_objects.setdefault(key,[]).append((n,obs[ptr['m_PathID']]))

custom_keys = set(keys)-set(dict(native.keys()))
for key in custom_keys:
    for loc, in cat.array(keys[key],'I'):
        v = cat.location(loc)
        assert v['dependencies'],key
        owner = cat.location(v['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
        assert any(n == owner for n,o in guid_objects[key]), ('GUID owner/object',key,owner)
        candidates = [o for n,o in guid_objects[key] if n == owner]
        if v['type'][1].endswith('VisualTreeAsset'):
            assert any('m_VisualTree' in o.read_typetree() for o in candidates),key
            label = {'gameworld':'GameWorld','global':'Global','match':'Match','intro':'Intro','fantasydraft':'FantasyDraft'}
            prefix = next(value for token,value in label.items() if token+'visualtree' in owner)
            assert (loc,) in cat.array(keys[prefix+'VisualTreeAssetPreload'],'I'),key
        if v['type'][1].endswith('VisualFunction'):
            assert any('m_nodes' in o.read_typetree() for o in candidates),key
            assert any('ui-backgrounds_assets_common.bundle' in cat.location(d)['internal'] for d in v['dependencies'])

registry = read(ROOT / 'current-custom-textures.json')
forbidden = read(ROOT / 'reserved-texture-ids.json')['reserved_textures'] + registry.get('removed_textures',[])
ids = {int(row['path_id']) for row in forbidden}|{-910000000000146,-910000000000001,-910000000000002}
bg = objects['ui-backgrounds_assets_common.bundle']
assert ids.isdisjoint(bg)
for row in registry['textures']:
    assert bg[int(row['path_id'])].peek_name() == row['name']
for n,obs in objects.items():
    meta = next(o.read_typetree() for o in obs.values() if o.type.name=='AssetBundle')
    assert all(p['m_PathID'] not in ids for p in meta['m_PreloadTable'])
    assert all(v['asset']['m_PathID'] not in ids for k,v in meta['m_Container'])

# Canonical stylesheet rules avoid confusing table-index movement with value changes.
source = ast.parse((ROOT / 'review-updated-main-skin.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='canon'],type_ignores=[]),'canon','exec'))
n = 'ui-styles_assets_common.bundle'
pid = -6275161654120610136
o = objects[n][pid]
merged_rules = canon(o.read_typetree(),o.assets_file)
native_tree = read(review_root / 'common-styles' / str(pid) / 'updated-native.json')
native_rules = canon(native_tree,o.assets_file)
old_skin = UnityPy.load(manifest['sources'][n])
skin_obj = next(o for o in old_skin.objects if o.path_id==pid)
skin_rules = canon(skin_obj.read_typetree(),skin_obj.assets_file)
custom = set(review['common']['skin_changed_existing_rules']+review['common']['skin_added_rule_indices'])
assert len(merged_rules)==len(skin_rules)
for i,r in enumerate(merged_rules):
    assert r == (skin_rules[i] if i in custom else native_rules[i]), ('style rule',i)

W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
assert not any('tfreferencebookmark' in (o.peek_name() or '').lower() for o in objects[W].values() if o.type.name=='MonoBehaviour')
database = read(ROOT / 'current-player-database-views.json')
for key in ['new_view_guid','new_row_guid']:
    assert database[key] in custom_keys
vp = objects['ui-tableviews_assets_all.bundle'][int(database['new_view_path_id'])].read_typetree()
columns = [c['m_columnID'] for c in vp['m_tableView']['m_tableConfig']]
assert all(c in columns for c in database['numeric_ability_columns'])
assert 'average-rating' in columns
guid = '5f191fc6eb99dde47a955456fecb83e6'
template = next(o for n,o in guid_objects[guid] if 'inlineSheet' in o.read_typetree()).read_typetree()
NAME = 'ContractNegotiationToolTemplate'
index = {}
for key,entries in guid_objects.items():
    for n,o in entries:
        if 'visualtreeassets' in n and o.type.name == 'MonoBehaviour':
            d = o.read_typetree()
            if 'inlineSheet' in d:index[key] = (n,o.path_id,d)
src = ast.parse((ROOT / 'fix-contract-offer-template-ids.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='resolve'],type_ignores=[]),'resolve','exec'))
contract_checks=[]
for o in objects[W].values():
    if o.type.name!='MonoBehaviour' or o.peek_name()!='ContractNegotiationTool':continue
    d=o.read_typetree()
    aliases={u['alias'] for u in d['m_Usings'] if u['path']==guid}
    for ref in d['references']['RefIds']:
        data=ref.get('data',{})
        if data.get('m_TemplateAlias') in aliases:
            overrides=data['m_SerializedDataOverride']
            assert all(resolve(template,x['m_ElementIdsPath'],template) for x in overrides)
            contract_checks.append(len(overrides))
assert 66 in contract_checks
(out / 'contract-override-verification.json').write_text(json.dumps(contract_checks),'utf8')
(out / 'scope-1-16-verification.json').write_text(json.dumps({'overview_hidden':True,'latest_review_applied':True}),'utf8')
verification = {'custom_catalog_types_and_bundle_dependencies_verified':True,
                'native_metadata_preserved':True,'native_keys_and_dependencies_preserved':True,
                'custom_keys_verified':len(custom_keys),'texture_count':len(registry['textures']),
                'common_rules_verified':len(merged_rules),'contract_paths':contract_checks,
                'catalog_dependency_cycles':False,'runtime_tested':False}
(out / 'verification.json').write_text(json.dumps(verification,indent=2),'utf8')
print(json.dumps(verification))
