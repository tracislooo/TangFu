"""Prepare a private 12-axis season radar on the restored seventh overview."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import uuid
import zlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
for filename, names in [
    ('build-fc-player-hover-layout.py', {'write', 'Styles'}),
    ('add-card-six-ratings.py', {'validate_ui', 'check_graph', 'gid'}),
    ('add-two-portrait-hidden-overviews.py', {'refs', 'data', 'named', 'rid_links', 'owned_refs'}),
    ('add-left-test-overview.py', {'prune'}),
]:
    mod = ast.parse((R / filename).read_text('utf-8-sig'))
    exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names],
                            type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, R / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

rb, cm = module('radar_builders', 'season-radar-builders.py'), module('catalog', 'catalog-binary-v35.py')
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
F = 'ui-visualfunctions_assets_all.bundle'
PAGE, SOURCE_STATS, STATS, STYLE = -941100000001020, -950000000000168, -941100000001050, -941100000001051
LABEL_SOURCE, LABEL, LABEL_STYLE, FUNC = -4069184508898986273, -941100000001052, -941100000001053, -941100000001054
KEY = lambda name: uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-left-test-season-radar-' + name + '-v1').hex
STATS_KEY, LABEL_KEY, FUNC_KEY, MERGE_KEY = [KEY(n) for n in ['stats', 'label', 'values', 'merge']]
MERGE = -941100000001055
OUT = R / ('left-test-season-radar-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
reserved = {int(t['path_id']) for t in json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
protected = {str(p): sha(p.read_bytes()) for folder in [GAME, SKIN] for p in folder.glob('*.bundle') if p.name not in [W, G]}
previous = json.loads((R / 'current-player-overview-test-variant.json').read_text('utf8'))
assert previous.get('numbered_layout_reverted'), 'Restore the numbered layout before preparing the radar.'

# Positive and reverse axes use separate, documented drawing ranges. Values on
# labels remain unmodified. Dynamic maxima preserve won/played and penalty ratios.
OUTFIELD = [
    ('获胜/场次', 'GamesWon', 0, 'GamesPlayed', False),
    ('当场最佳', 'PlayerOfTheMatchAwards', 0, 10, False),
    ('进球', 'Goals', 0, 40, False),
    ('预期进球/90', 'ExpectedGoalsPer90', 0, 1.2, False),
    ('射正/90', 'ShotsOnTargetPer90', 0, 3, False),
    ('创造机会', 'ChancesCreated', 0, 100, False),
    ('预期助攻/90', 'ExpectedAssistsPer90', 0, 0.6, False),
    ('关键传球', 'KeyPasses', 0, 150, False),
    ('传球成功/90', 'PassCompletedPer90', 0, 100, False),
    ('关键抢断', 'KeyTackles', 0, 50, False),
    ('抢断成功/90', 'TacklesCompletedPer90', 0, 6, False),
    ('关键头球/90', 'KeyHeadersPer90', 0, 6, False),
]
GOALKEEPER = [
    ('获胜/场次', 'GamesWon', 0, 'GamesPlayed', False),
    ('当场最佳', 'PlayerOfTheMatchAwards', 0, 10, False),
    ('解围', 'Clearances', 0, 100, False),
    ('预期阻止进球/90', 'ExpectedGoalsPreventedPer90', -1, 1, False),
    ('扑救/90', 'TotalSavesPer90', 0, 8, False),
    ('失球/90', 'ConcededPer90', 0, 3, True),
    ('赢得球权/90', 'PossessionWonPer90', 0, 10, False),
    ('丢失球权/90', 'PossessionLostPer90', 0, 15, True),
    ('传球成功/90', 'PassCompletedPer90', 0, 60, False),
    ('点球失球/面对', 'Penalties', 0, 'PenaltiesFaced', True),
    ('失球间隔(分)', 'MinutesPerGoalConceded', 0, 180, False),
    ('致命失误', 'GoalMistakes', 0, 10, True),
]
tx, audits = [], []


def add_tx(tag, path, output, original):
    source, backup = OUT / tag / path.name, OUT / ('backup-' + tag) / path.name
    source.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    source.write_bytes(output)
    backup.write_bytes(original)
    tx.append(dict(target=str(path), source=str(source), backup=str(backup), before=sha(original), after=sha(output)))


def direct(path):
    return dict(m_kind=1, m_direct={'Path': {'m_path': path}, 'Nullable': 0},
                m_visualFunction=rb.function(''))


for tag, folder in [('game', GAME), ('skin', SKIN)]:
    print('Preparing ' + tag, flush=True)
    initial = {n: (folder / n).read_bytes() for n in [W, G]}
    env = {n: UnityPy.load(b) for n, b in initial.items()}
    obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
    hashes = {n: {i: sha(o.get_raw_data()) for i, o in oo.items()} for n, oo in obs.items()}
    modified = {W: {}, G: {}}
    fenv = UnityPy.load(str(GAME / F))
    functions = {o.peek_name(): o for o in fenv.objects if o.type.name == 'MonoBehaviour'}
    fmeta = next(o.read_typetree() for o in fenv.objects if o.type.name == 'AssetBundle')
    fnkey = lambda name: next(k for k, e in fmeta['m_Container'] if e['asset']['m_PathID'] == functions[name].path_id)
    templates = {}
    for o in functions.values():
        for ref in o.read_typetree().get('references', {}).get('RefIds', []):
            if ref.get('type', {}).get('class'):
                templates.setdefault(ref['type']['class'], ref)
    float_class = 'TypedValueVisualFunctionLibrary_FloatToTypedValue'
    templates[float_class] = copy.deepcopy(templates['TypedValueVisualFunctionLibrary_IntToTypedValue'])
    templates[float_class]['type']['class'] = float_class
    templates[float_class]['data']['m_dataInValue']['m_defaultSocketValue']['m_value'] = 0.0
    gaf = obs[G][-940000000000101].assets_file
    # Native FloatToTypedValue has the same fields as IntToTypedValue; its input
    # default is Single. Include its exact primitive schema in this serialized file.
    for typ in next(iter(functions.values())).assets_file.ref_types:
        if not any((x.m_ClassName, x.m_NameSpace, x.m_AssemblyName) ==
                   (typ.m_ClassName, typ.m_NameSpace, typ.m_AssemblyName) for x in gaf.ref_types):
            gaf.ref_types.append(copy.copy(typ))
    ft = copy.copy(next(t for t in gaf.ref_types if t.m_ClassName == 'TypedValueVisualFunctionLibrary_IntToTypedValue'))
    ft.node = type(ft.node).from_list([{k: v for k, v in n.items() if k != 'm_Children'}
                                      for n in ft.node.to_dict_list()])
    ft.m_ClassName, ft.node.m_Type = float_class, float_class
    input_node = next(n for n in ft.node.m_Children if n.m_Name == 'm_dataInValue')
    def float_default(node):
        if node.m_Name == 'm_value':
            assert node.m_Type == 'int'
            node.m_Type = 'float'
        for child in node.m_Children:
            float_default(child)
    float_default(input_node)
    gaf.ref_types.append(ft)

    def save(n, pid, d):
        obs[n][pid].save_typetree(d)
        modified[n][pid] = copy.deepcopy(d)

    def add(n, source, pid, d):
        assert pid not in obs[n] and pid not in reserved
        o = copy.copy(obs[n][source])
        o.path_id, o.data, o._read_until = pid, None, None
        o.assets_file.objects[pid] = o
        obs[n][pid] = o
        save(n, pid, d)

    func = rb.make_stat_function(functions['BindAndSetToDestination'].read_typetree(), templates,
                                 obs[G][-940000000000101].read_typetree()['m_Script'])
    check_graph(func)
    add(G, -940000000000101, FUNC, func)
    merge_func = rb.make_merge_function(functions['BindCreateListToDestination'].read_typetree(), templates,
                                       obs[G][-940000000000101].read_typetree()['m_Script'])
    check_graph(merge_func)
    add(G, -940000000000101, MERGE, merge_func)
    main = obs[W][PAGE].read_typetree()
    stats = obs[W][SOURCE_STATS].read_typetree()
    original_stats = copy.deepcopy(stats)
    ss = obs[W][stats['inlineSheet']['m_PathID']].read_typetree()
    label = obs[W][LABEL_SOURCE].read_typetree()
    ls = obs[W][label['inlineSheet']['m_PathID']].read_typetree()
    mainr, statr, lr = refs(main), refs(stats), refs(label)
    plain = (copy.deepcopy(mainr[1291]), copy.deepcopy(mainr[mainr[1291]['data']['m_SerializedData']['rid']]))
    setter_proto = (copy.deepcopy(mainr[1167]), copy.deepcopy(mainr[mainr[1167]['data']['m_SerializedData']['rid']]))
    switch_node = named(stats, 'SeasonStatsIsGoalkeeperSwitch')
    switch_proto = (copy.deepcopy(statr[switch_node]), copy.deepcopy(statr[statr[switch_node]['data']['m_SerializedData']['rid']]))
    text_id = next(i for i, r in lr.items() if r.get('data', {}).get('m_FullTypeName') == 'SI.Bindable.SIText')
    text_proto = (copy.deepcopy(lr[text_id]), copy.deepcopy(lr[lr[text_id]['data']['m_SerializedData']['rid']]))
    chart_page = obs[W][-7642202103200103126].read_typetree()
    cr = refs(chart_page)
    chart_id = next(i for i, r in cr.items() if r.get('data', {}).get('m_FullTypeName') == 'FM.UI.FMSpiderChart')
    chart_proto = (copy.deepcopy(cr[chart_id]), copy.deepcopy(cr[cr[chart_id]['data']['m_SerializedData']['rid']]))

    def new_node(doc, proto, parent, name):
        rr = refs(doc)
        node, sd = copy.deepcopy(proto)
        rid = max(rr) + 1
        ident = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
        assert ident < 2147483647
        node['rid'], sd['rid'] = rid, rid + 1
        node['data'].update(m_Id=ident, m_Parent={'rid': parent}, m_Children=[], m_RuleIndex=-1,
                            m_Classes=[], m_Stylesheets=[], m_SerializedData={'rid': rid + 1})
        sd['data'].update(uxmlAssetId=ident, name=name, name_UxmlAttributeFlags=1)
        doc['references']['RefIds'].extend([node, sd])
        rr[parent]['data']['m_Children'].append({'rid': rid})
        return rid

    def fill(st, height=None):
        p = [st.p(131105, st.pct(100)), st.p(131097, st.px(0)), st.p(131096, st.px(0)),
             st.p(131084, st.num(1)), st.p(131085, st.num(1)), st.p(131082, st.px(0)),
             st.p(131073, st.en('stretch'))]
        if height is not None:
            p.append(st.p(131087, height))
        return p

    # A compact native label with the real value, ratio formatting and a genuine
    # missing-data branch. Our private DynamicReferences use registered UniqueId
    # and Regenerated properties only as local availability/ratio flags, never IDs.
    for child in list(refs(label)[label['m_VisualTree']['rid']]['data']['m_Children']):
        prune(label, child['rid'])
    root = new_node(label, plain, label['m_VisualTree']['rid'], 'SeasonRadarAxisLabel')
    lst = Styles(ls)
    def label_text(parent, name, text='', binding=None):
        i = new_node(label, text_proto, parent, name)
        rr = refs(label)
        sd = data(rr, i)
        sd.update(text=text, text_UxmlAttributeFlags=1, TextBinding=binding or direct(''),
                  TextBinding_UxmlAttributeFlags=1 if binding else 0)
        lst.edit(rr[i], [lst.p(131105, lst.pct(100)), lst.p(131087, lst.px(11)), lst.p(65537, lst.px(8)),
                         lst.p(65536, lst.h(4, dict(r=1., g=1., b=1., a=1.))),
                         lst.p(65546, lst.en('middle-center')), lst.p(131085, lst.num(0))], reset=True)
        return i
    lr = refs(label)
    lst.edit(lr[root], [lst.p(131105, lst.px(66)), lst.p(131087, lst.px(24)),
                       lst.p(131083, lst.en('column')), lst.p(131073, lst.en('stretch'))], reset=True)
    label_text(root, 'AxisTitle', binding=direct('binding.StatNameLabel'))
    available = new_node(label, switch_proto, root, 'SeasonRadarValueAvailable')
    data(refs(label), available)['Binding'] = direct('binding.UniqueId')
    label_text(available, 'MissingValue', '--')
    ratio = new_node(label, switch_proto, available, 'SeasonRadarRatioValue')
    data(refs(label), ratio)['Binding'] = direct('binding.Regenerated')
    def original_binding(name):
        return data(refs(original_stats), named(original_stats, name))['TextBinding']
    numeric = rb.rewrite_argument_text(original_binding('SeasonStatValue_ExpectedGoalsPer90'),
                                      {'SeasonStats.ExpectedGoalsPer90': 'binding.MeanStatValue'})
    composite = rb.rewrite_argument_text(original_binding('SeasonStatValue_GamesWonAndPlayed'),
          {'SeasonStats.GamesWon': 'binding.MeanStatValue', 'SeasonStats.GamesPlayed': 'binding.MaxStatValue',
           '[%number#1] / [%number#2]': '[%fraction#1-1.0] / [%fraction#2-1.0]'})
    label_text(ratio, 'RawValue', binding=numeric)
    label_text(ratio, 'RawRatio', binding=composite)
    label['m_Usings'] = []
    old_label_style = label['inlineSheet']['m_PathID']
    label.update(m_Name='LeftTestSeasonRadarAxisLabel', inlineSheet={'m_FileID': 0, 'm_PathID': LABEL_STYLE},
                 m_ContentContainerId=0)
    ls['m_Name'] = label['m_Name'] + 'Style'
    validate_ui(label, ls)
    add(W, LABEL_SOURCE, LABEL, label)
    add(W, old_label_style, LABEL_STYLE, ls)

    # Preserve the entire league/season lookup and original IsGoalkeeper switch.
    for panel_name, specs in [('SeasonStatsOutfielderPanel', OUTFIELD), ('SeasonStatsGoalkeeperPanel', GOALKEEPER)]:
        panel = named(stats, panel_name)
        for child in list(refs(stats)[panel]['data']['m_Children']):
            prune(stats, child['rid'])
        setter = new_node(stats, setter_proto, panel, 'SeasonRadarValues_' + panel_name)
        rr = refs(stats)
        sd = data(rr, setter)
        sd.update(ValueVariables=[], ReferenceVariables=[], BindFunction=[])
        for f in ['ValueVariables', 'ReferenceVariables', 'BindFunction']:
            sd[f + '_UxmlAttributeFlags'] = 1
        for list_name in ['radarPoints', 'radarPointsFirstHalf', 'radarPointsSecondHalf']:
            sd['ReferenceVariables'].append(dict(m_type={'id': 0}, m_initToNull=1, m_name=list_name))
        def literal(name, value):
            sd['ValueVariables'].append(dict(m_name=name, m_scopeValue={'m_serializedData': value}))
        literal('radarZero', 'Int|0|')
        point_names = []
        for i, (title, field, minimum, maximum, reverse) in enumerate(specs):
            prefix = 'seasonRadar' + str(i)
            for suffix in ['Raw', 'Plot', 'Max', 'Valid']:
                sd['ReferenceVariables'].append(dict(m_type={'id': 0}, m_initToNull=1, m_name=prefix + suffix))
            literal(prefix + 'Title', 'String|' + title + '|')
            literal(prefix + 'Ratio', 'Bool|' + str(int(isinstance(maximum, str))) + '|')
            literal(prefix + 'False', 'Bool|0|')
            literal(prefix + 'Min', 'Float|' + str(minimum) + '|')
            if isinstance(maximum, str):
                maxpath = 'SeasonStats.' + maximum
            else:
                literal(prefix + 'RangeMax', 'Float|' + str(maximum) + '|')
                maxpath = prefix + 'RangeMax'
            fields = {
                0x37675A32: prefix + 'Title', 0x3870434D: prefix + 'Title',
                0x74594C76: prefix + 'Max', 0x4E657758: prefix + 'Min',
                0x3167704D: prefix + 'Raw', 0x5A74416A: prefix + 'Plot',
                0x4F627175: prefix + 'False', 1970170212: prefix + 'Valid',
                1349674343: prefix + 'Ratio',
            }
            dynamic = {'$type': 'SI.Bindable.DynamicReferenceScopeValue, SI.Bindable',
                       'm_data': [dict(PropertyID={'id': k, 'ID': k}, BindingPath=v) for k, v in fields.items()]}
            point_name = prefix + 'Point'
            literal(point_name, json.dumps(dynamic, separators=(',', ':')))
            point_names.append(point_name)
            sd['BindFunction'].append(rb.function(FUNC_KEY, rb.path_arg('SeasonStats.' + field), rb.path_arg(maxpath),
                rb.float_arg(minimum), rb.bool_arg(reverse), rb.path_arg(prefix + 'Raw'), rb.path_arg(prefix + 'Plot'),
                rb.path_arg(prefix + 'Max'), rb.path_arg(prefix + 'Valid')))
        for paths, destination in [(point_names[:6], 'radarPointsFirstHalf'), (point_names[6:], 'radarPointsSecondHalf')]:
            sd['BindFunction'].append(rb.function(fnkey('BindCreateListToDestination'), rb.path_list_arg(paths), rb.path_arg(destination)))
        sd['BindFunction'].append(rb.function(MERGE_KEY, rb.path_list_arg(['radarPointsFirstHalf', 'radarPointsSecondHalf']),
                                             rb.path_arg('radarPoints')))
        chart = new_node(stats, chart_proto, setter, 'SeasonRadarTwelveAxes')
        cd = data(refs(stats), chart)
        cd.update(LabelsTemplate={'m_AssetGUID': LABEL_KEY, 'm_SubObjectName': '', 'm_SubObjectType': ''},
                  SpiderChartVertices=12, NumberOfInnerRings=4,
                  SizeOfInnerRings=struct.unpack('<f', struct.pack('<f', 0.2))[0],
                  SpiderChartRadiusPercentage=27.0, LabelDistanceFromChart=12.0,
                  BindDataFunction=rb.function(fnkey('SetDataAnalysisSpiderChart'), rb.path_arg('radarPoints'),
                                              rb.bool_arg(False), rb.bool_arg(False), rb.path_arg('radarZero')))
        for name in ['LabelsTemplate', 'SpiderChartVertices', 'NumberOfInnerRings', 'SizeOfInnerRings',
                     'SpiderChartRadiusPercentage', 'LabelDistanceFromChart', 'BindDataFunction']:
            cd[name + '_UxmlAttributeFlags'] = 1
        st = Styles(ss)
        for i in [panel, setter, chart]:
            st.edit(refs(stats)[i], fill(st, st.pct(100)), reset=True)
    old_stats_style = stats['inlineSheet']['m_PathID']
    stats.update(m_Name='LeftTestSeasonTwelveAxisRadar', inlineSheet={'m_FileID': 0, 'm_PathID': STYLE},
                 m_ContentHash=struct.unpack('<i', struct.pack('<I', zlib.crc32(STATS_KEY.encode())))[0])
    ss['m_Name'] = stats['m_Name'] + 'Style'
    assert data(refs(stats), switch_node) == data(refs(original_stats), switch_node)
    validate_ui(stats, ss)
    add(W, SOURCE_STATS, STATS, stats)
    add(W, old_stats_style, STYLE, ss)
    # Only this test page receives the private season module.
    using = next(u for u in main['m_Usings'] if u['alias'] == 'OverviewNativeSeasonFourGauges')
    using.update(path=STATS_KEY, asset={'m_FileID': 0, 'm_PathID': STATS})
    data(refs(main), 6304).update(template={'m_FileID': 0, 'm_PathID': STATS}, template_UxmlAttributeFlags=1)
    main['m_ContentHash'] = struct.unpack('<i', struct.pack('<I', zlib.crc32(b'left-test-season-radar-v1')))[0]
    save(W, PAGE, main)

    catpath = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    catbefore, hashbefore = catpath.read_bytes(), catpath.with_name('catalog.hash').read_bytes()
    cat = cm.Catalog(catbefore)
    metas = {n: next(o for o in obs[n].values() if o.type.name == 'AssetBundle') for n in [W, G]}
    metadata = {n: o.read_typetree() for n, o in metas.items()}
    registrations = [(G, -940000000000101, FUNC, None, FUNC_KEY, 'SI.VisualScripting.VisualFunction'),
                     (G, -940000000000101, MERGE, None, MERGE_KEY, 'SI.VisualScripting.VisualFunction'),
                     (W, LABEL_SOURCE, LABEL, LABEL_STYLE, LABEL_KEY, 'UnityEngine.UIElements.VisualTreeAsset'),
                     (W, SOURCE_STATS, STATS, STYLE, STATS_KEY, 'UnityEngine.UIElements.VisualTreeAsset')]
    for n, source_id, pid, sid, key, expected_type in registrations:
        meta = metadata[n]
        source_key, entry = next((k, e) for k, e in meta['m_Container'] if e['asset']['m_PathID'] == source_id)
        span = copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        source_sid = obs[n][source_id].read_typetree().get('inlineSheet', {}).get('m_PathID')
        for ptr in span:
            if ptr['m_FileID'] == 0:
                ptr['m_PathID'] = {source_id: pid, source_sid: sid}.get(ptr['m_PathID'], ptr['m_PathID'])
        for p in [{'m_FileID': 0, 'm_PathID': pid}] + ([{'m_FileID': 0, 'm_PathID': sid}] if sid else []):
            if p not in span:
                span.append(p)
        assert not any(p['m_PathID'] in reserved for p in span)
        meta['m_Container'].append((key, dict(preloadIndex=len(meta['m_PreloadTable']), preloadSize=len(span),
                                           asset={'m_FileID': 0, 'm_PathID': pid})))
        meta['m_PreloadTable'].extend(span)
        source_loc = next(i for i in cat.locations(source_key) if cat.location(i)['type'][1] == expected_type)
        cat = cm.Catalog(cat.add_key_location(key, source_loc, source_loc))
        newloc = cat.locations(key)[0]
        assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(n)
        # Append the new resource to every actual preload label used by its source.
        labels = []
        for label_key, locset in cat.keys():
            if isinstance(label_key, str) and 'Preload' in label_key and source_loc in [x[0] for x in cat.array(locset, 'I')]:
                labels.append(label_key)
        if n == W:
            labels = list(dict.fromkeys(labels + ['GameWorldVisualTreeAssetPreload']))
        for label_key in labels:
            idx = next(i for i, (k, _) in enumerate(cat.key_records) if cat.object(k) == label_key)
            k, ls0 = cat.key_records[idx]
            locations = [x[0] for x in cat.array(ls0, 'I')] + [newloc]
            ls0 = cat.append(b''.join(struct.pack('<I', x) for x in locations), True)
            records = list(cat.key_records)
            records[idx] = k, ls0
            struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *r) for r in records), True))
            cat = cm.Catalog(bytes(cat.data))
        assert n != W or newloc in cat.locations('GameWorldVisualTreeAssetPreload')

    # Cross-bundle dependency and object preload closure for the two private VTAs
    # and the sole changed page. Existing registrations retain their identity.
    waf, gaf = obs[W][PAGE].assets_file, obs[G][FUNC].assets_file
    global_id = next(i + 1 for i, e in enumerate(waf.externals) if e.path.endswith('/' + gaf.name))
    extra = [{'m_FileID': 0, 'm_PathID': p} for p in [STATS, STYLE, LABEL, LABEL_STYLE]] + [
        {'m_FileID': global_id, 'm_PathID': p} for p in [FUNC, MERGE]]
    wm = metadata[W]
    page_key = next(k for k, e in wm['m_Container'] if e['asset']['m_PathID'] == PAGE)
    function_deps = cat.location(cat.locations(FUNC_KEY)[0])['dependencies']
    label_deps = cat.location(cat.locations(LABEL_KEY)[0])['dependencies']
    for key in [STATS_KEY, LABEL_KEY, page_key]:
        locn = cat.locations(key)[0]
        dependencies = list(dict.fromkeys(cat.location(locn)['dependencies'] + function_deps + label_deps))
        raw = list(cat.unpack(locn, '7I'))
        encoded = b''.join(struct.pack('<I', x) for x in dependencies)
        raw[3], raw[4] = cat.append(encoded, True), zlib.crc32(encoded)
        struct.pack_into('<7I', cat.data, locn, *raw)
        entry = next(e for k, e in wm['m_Container'] if k == key)
        span = copy.deepcopy(wm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        for p in extra:
            if p not in span:
                span.append(p)
        entry['preloadIndex'], entry['preloadSize'] = len(wm['m_PreloadTable']), len(span)
        wm['m_PreloadTable'].extend(span)
    cat = cm.Catalog(bytes(cat.data))
    for n, meta in metadata.items():
        meta['m_Container'].sort(key=lambda x: x[0])
        save(n, metas[n].path_id, meta)
    for n, e in env.items():
        output = e.file.save(packer='lz4')
        check = {o.path_id: o for o in UnityPy.load(output).objects}
        assert set(check) == set(obs[n])
        for pid, h in hashes[n].items():
            if pid not in modified[n]:
                assert sha(check[pid].get_raw_data()) == h, ('unrelated object changed', tag, n, pid)
        for pid, expected in modified[n].items():
            assert check[pid].read_typetree() == expected, ('roundtrip mismatch', tag, n, pid)
        add_tx(tag, folder / n, output, initial[n])
    add_tx(tag, catpath, bytes(cat.data), catbefore)
    add_tx(tag, catpath.with_name('catalog.hash'), hashlib.md5(bytes(cat.data)).hexdigest().encode('ascii'), hashbefore)
    audits.append(dict(target=tag, original_six_and_shared_season_modules_unchanged=True,
                       goalkeeper_switch_and_season_context_preserved=True, data_function_graph_valid=True,
                       original_layout_preserved=True))
    print('Verified ' + tag + ': separate goalkeeper/outfield twelve-axis radars.', flush=True)

for row in tx:
    assert sha(Path(row['target']).read_bytes()) == row['before']
for p, h in protected.items():
    assert sha(Path(p).read_bytes()) == h
manifest = dict(installed=False, runtime_verified=False, previous_index=previous,
                page=PAGE, stats=STATS, style=STYLE, label=LABEL, label_style=LABEL_STYLE, function=FUNC,
                stats_guid=STATS_KEY, label_guid=LABEL_KEY, function_guid=FUNC_KEY,
                merge=MERGE, merge_guid=MERGE_KEY, outfield=OUTFIELD, goalkeeper=GOALKEEPER, outer_means_better=True,
                normalized_range_is_fixed_reference_not_percentile=True, raw_values_preserved=True,
                audits=audits, protected_sha256=protected)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'installer.py').write_text((R / 'install-independent-resource-patch.py').read_text('utf8').replace('.codex-fitness-', '.codex-radar-'), 'utf8')
for mode, filename in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / filename).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable +
        "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode +
        "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
index = dict(manifest=str(OUT / 'manifest.json'), script=str(Path(__file__).resolve()), title='左边版-测试版',
             count=7, installed=False, runtime_verified=False, numbered_layout_reverted=True,
             previous_manifest=previous['manifest'], layout='original seventh layout; private 12-axis season radar')
(R / 'current-player-overview-test-variant.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(prepared=True, installed=False, output=str(OUT), files=len(tx)), ensure_ascii=False))
