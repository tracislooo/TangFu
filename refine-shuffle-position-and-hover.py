from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

cfg = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(cfg['bundle_root']), Path(cfg['skin_packages'])
FN = 'ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GN = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
BG = 'ui-backgrounds_assets_common.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
poolmap = {2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
oldwrite = TypeTreeHelper.write_value
helpers = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name == 'write' or isinstance(n, ast.ClassDef) and n.name == 'Styles'],type_ignores=[]), '<styles>', 'exec'))
TypeTreeHelper.write_value = write
helpers = ast.parse((R / 'update-shuffle-player-tile.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in ast.walk(helpers) if isinstance(n, ast.FunctionDef) and n.name in ['managed','import_tree']],type_ignores=[]), '<tree-import>', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)

def objects(source):
    env = UnityPy.load(source)
    return env, {o.path_id:o for o in env.objects}

def container(obs):
    return next(o.read_typetree()['m_Container'] for o in obs.values() if o.type.name == 'AssetBundle')

def serialized(i):
    return refs[refs[i]['data']['m_SerializedData']['rid']]['data']

def edit(i, props, reset=False):
    st.edit(refs[i], props, reset=reset)

def children(i):
    return refs[i]['data']['m_Children']

def move(i, parent):
    children(refs[i]['data']['m_Parent']['rid']).remove({'rid':i})
    refs[i]['data']['m_Parent'] = {'rid':parent}
    children(parent).append({'rid':i})

def box(parent, name):
    global next_rid, next_eid
    node, sd = copy.deepcopy(refs[1038]), copy.deepcopy(refs[refs[1038]['data']['m_SerializedData']['rid']])
    node['rid'], sd['rid'] = next_rid, next_rid + 1
    node['data'].update(m_Id=next_eid, m_Parent={'rid':parent}, m_Children=[], m_Classes=[], m_RuleIndex=-1, m_SerializedData={'rid':sd['rid']})
    sd['data'].update(uxmlAssetId=next_eid, name=name, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    refs[node['rid']], refs[sd['rid']] = node, sd
    children(parent).append({'rid':node['rid']})
    next_rid += 2
    next_eid += 1
    return node['rid']

def named(name):
    matches = [i for i,r in refs.items() if r.get('data',{}).get('m_SerializedData',{}).get('rid',-2) != -2 and serialized(i).get('name') == name]
    assert len(matches)==1, name
    return matches[0]

def walk(i):
    yield i
    for child in children(i):
        j = child['rid']
        assert refs[j]['data']['m_Parent']['rid']==i
        yield from walk(j)

def rgba(r,g,b):
    return st.h(4,{'r':r,'g':g,'b':b,'a':1.0})

def apply_tile_layout():
    white = rgba(1.,1.,1.)
    edit(1029,[P(131087,st.px(21)),P(131085,st.num(0))])
    edit(1039,[P(131081,st.en('none'))])
    details = box(1023,'ShufflePositionAndRatings')
    edit(details,[P(131083,st.en('row')),P(131105,st.pct(100)),P(131084,st.num(1)),P(131096,st.px(0)),P(131079,st.px(1)),P(262146,white)])
    left = box(details,'ShufflePositionHalf')
    right = box(details,'ShuffleRatingsHalf')
    for side in [left,right]:
        edit(side,[P(131105,st.pct(50)),P(131087,st.pct(100)),P(131085,st.num(0)),P(131097,st.px(0)),P(131073,st.en('center')),P(131088,st.en('center'))])
    edit(right,[P(131077,st.px(1)),P(262146,white)])
    pitch_ids = import_tree(pitch,pitch_styles,1013,left)
    children(left).append({'rid':pitch_ids[1013]})
    edit(pitch_ids[1013],[P(131102,st.en('relative')),P(131105,st.px(78)),P(131087,st.px(46)),P(131094,st.pct(100)),P(131095,st.pct(100)),P(131085,st.num(0))])
    for layer in [1021,1022]:
        edit(pitch_ids[layer],[P(131102,st.en('absolute')),P(131089,st.px(0)),P(131104,st.px(0)),P(131105,st.pct(100)),P(131087,st.pct(100))])
    assert serialized(pitch_ids[1021])['TacticPositionsBinding']['m_path']=='player.positionaptitudelist'
    assert serialized(pitch_ids[1021])['Orientation']==1
    ratings = named('OverviewCardGoalkeeperSwitch')
    move(ratings,right)
    edit(ratings,[P(131105,st.pct(100)),P(131087,st.pct(100)),P(131085,st.num(0))],True)
    scoring_guids = set()
    for name in ['OverviewCardSixRatings','OverviewCardGoalkeeperRatings']:
        branch = named(name)
        first = children(branch)[0]['rid']
        cells = [x['rid'] for x in children(first)]
        assert len(cells)==6
        second = box(branch,name+'SecondRow')
        for cell in cells[3:]:
            move(cell,second)
        for row in [first,second]:
            edit(row,[P(131083,st.en('row')),P(131105,st.pct(100)),P(131087,st.pct(50)),P(131085,st.num(0))],True)
            assert len(children(row))==3
            for cell in children(row):
                i = cell['rid']
                edit(i,[P(131105,st.pct(33.33333206176758)),P(131087,st.pct(100)),P(131077,st.px(0)),P(131085,st.num(0))])
                title, value = [x['rid'] for x in children(i)]
                edit(title,[P(65537,st.px(8))])
                edit(value,[P(65537,st.px(10))])
                scoring_guids.add(serialized(value)['TextBinding']['m_visualFunction']['m_target']['m_guid'])
    assert len(scoring_guids)==11
    # Some installed copies reverted to the older corner badge.
    if refs[1030]['data']['m_Parent']['rid']==1022:
        move(1030,1020)
        edit(1020,[P(131102,st.en('relative'))])
        edit(1030,[P(131102,st.en('absolute')),P(131089,st.pct(50)),P(131104,st.pct(50)),P(131105,st.px(160)),P(131087,st.px(32)),P(327683,st.px(-80),st.px(-16)),P(458768,st.en('visible'))],True)
        serialized(1030).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1)
        for i in walk(named('ShuffleDraftManagerRedRibbon')):
            node = refs[i]['data']
            if 'data_display-draft-player-selection-label' in node.get('m_Classes',[]):
                edit(i,[P(262148,st.px(1)),P(262146,rgba(1.,0.,0.))])
            if node.get('m_FullTypeName')=='SI.Bindable.SIText':
                edit(i,[P(65537,st.px(16))])
    return scoring_guids

def inline_hover(instance):
    old = refs[instance]['data']
    assert old['m_TemplateAlias']=='PlayerReportPreviewTooltip' and not old['m_Children']
    assert not old['m_SerializedDataOverride'] and not old['m_AttributeOverrides']
    parent = old['m_Parent']['rid']
    result = import_tree(hover,hover_styles,1001,parent)
    children(parent)[children(parent).index({'rid':instance})] = {'rid':result[1001]}
    del refs[old['m_SerializedData']['rid']], refs[instance]
    using = {u['alias']:u for u in doc['m_Usings'] if u['alias']!='PlayerReportPreviewTooltip'}
    for u in hover['m_Usings']:
        assert u['alias'] not in using or using[u['alias']]==u
        using[u['alias']] = copy.deepcopy(u)
    doc['m_Usings'] = list(using.values())
    assert children(result[1005]) == [{'rid':result[1010]}]
    assert len(list(walk(result[1001]))) > 10

historical = R / 'shuffle-draft-current-hover-20261102-104742/game' / WN
_, historical_objects = objects(str(historical))
hover = historical_objects[-3760232355926433866].read_typetree()
hover_styles = historical_objects[hover['inlineSheet']['m_PathID']].read_typetree()
assert not hover_styles['assets']

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
out = R / ('shuffle-position-grid-hover-' + stamp)
out.mkdir()
tx, audits, protected = [], [], {}
for tag, root in [('game',GAME),('skin',SKIN)]:
    path = root / FN
    before = path.read_bytes()
    env, obs = objects(before)
    _, world = objects(str(root / WN))
    pitch = world[7787073379322181298].read_typetree()
    pitch_styles = world[pitch['inlineSheet']['m_PathID']].read_typetree()
    assert not pitch_styles['assets']
    expected = {}
    for pid, instance in [(1519666771143645661,1071),(-1262615097586593695,1052)]:
        obj = obs[pid]
        doc = obj.read_typetree()
        refs = {r['rid']:r for r in doc['references']['RefIds']}
        sheetobj = obs[doc['inlineSheet']['m_PathID']]
        sheet = sheetobj.read_typetree()
        st = Styles(sheet)
        P = st.p
        next_rid, next_eid = max(refs)+100, 1958000000
        if pid==1519666771143645661:
            scoring_guids = apply_tile_layout()
        inline_hover(instance)
        doc['references']['RefIds'] = list(refs.values())
        live = list(walk(doc['m_VisualTree']['rid']))
        assert len(set(live))==len(live)
        assert all(i in live for i,r in refs.items() if 'm_Parent' in r.get('data',{}))
        obj.save_typetree(doc)
        sheetobj.save_typetree(sheet)
        expected[pid],expected[sheetobj.path_id] = doc,sheet
    # Validate real addressable objects, their resource types and owning bundle dependencies.
    catpath = (GAME.parent if tag=='game' else SKIN) / 'catalog.bin'
    cat = catalog.Catalog(catpath.read_bytes())
    keys = dict(cat.keys())
    _, glob = objects(str(root/GN))
    resource_maps = {WN:(world,container(world)),GN:(glob,container(glob))}
    checked = {}
    targets = {u['path']:'UnityEngine.UIElements.VisualTreeAsset' for u in hover['m_Usings']}
    targets['8c1726c6882bcf9419e7bba95d92f280'] = 'UnityEngine.UIElements.VisualTreeAsset'
    targets.update({guid:'SI.VisualScripting.VisualFunction' for guid in scoring_guids})
    for guid, kind in targets.items():
        locations = [cat.location(a[0]) for a in cat.array(keys[guid],'I')]
        loc = next(l for l in locations if l['type'][1]==kind and l['internal']==guid)
        dependencies = [cat.location(x)['internal'].replace('\\','/').split('/')[-1] for x in loc['dependencies']]
        bundle = dependencies[0]
        if bundle not in resource_maps:
            _, resources = objects(str(root/bundle))
            resource_maps[bundle] = resources,container(resources)
        resources, entries = resource_maps[bundle]
        field = 'm_VisualTree' if kind.endswith('VisualTreeAsset') else 'm_nodes'
        candidates = [resources[v['asset']['m_PathID']] for key,v in entries if key==guid and v['asset']['m_FileID']==0 and v['asset']['m_PathID'] in resources]
        resolved = [o.path_id for o in candidates if field in o.read_typetree()]
        assert resolved,(tag,guid,bundle)
        if guid=='64033a72b9925c8dad3b08826077c328':
            assert BG in dependencies
        checked[guid] = {'bundle':bundle,'type':kind,'objects':resolved}
    output = env.file.save(packer='lz4')
    _, saved = objects(output)
    assert set(saved)==set(obs)
    for i,o in saved.items():
        if i in expected:
            assert o.read_typetree()==expected[i],i
        else:
            assert o.get_raw_data()==obs[i].get_raw_data(),i
    backup,source = out/('backup-'+tag)/FN,out/tag/FN
    backup.parent.mkdir()
    source.parent.mkdir()
    backup.write_bytes(before)
    source.write_bytes(output)
    tx.append({'target':str(path),'backup':str(backup),'source':str(source),'before':sha(before),'after':sha(output)})
    for p in [catpath,root/WN,root/GN]:
        protected[str(p)] = sha(p.read_bytes())
    audits.append({'target':tag,'updated_objects':list(expected),'verified_addressables':checked,'rating_grid':[3,3],'hover_entries':['draft cards','live picks']})

manifest = {'installed':False,'runtime_verified':False,'protected_sha256':protected,'audits':audits}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (out/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed.' }\n",'utf-8-sig')
watcher = (R/'shuffle-tile-width-smaller-values-20261103-030512/install-after-game-exits.ps1').read_text('utf-8-sig')
(out/'install-after-game-exits.ps1').write_text(watcher,'utf-8-sig')
print(out)
