import copy
import datetime
import hashlib
import importlib.util
import json
import random
import struct
import sys
import uuid
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

AA = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
GAME = AA / 'StandaloneWindows64'
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GN = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
FN = 'ui-visualfunctions_assets_all.bundle'
FULL = -930000000001001
SUM = -910000000000303
OLD_SUM_GUID = 'd25e07441190434f86b42ec2ec560039'
SPECS = [
    ('速度', 'Pace', [('Acceleration', 45), ('Pace', 55)]),
    ('射门', 'Shooting', [('Finishing', 65), ('LongShots', 10), ('Movement', 10), ('PenaltyTaking', 5), ('Heading', 10)]),
    ('传球', 'Passing', [('Passing', 55), ('Vision', 15), ('Crossing', 15), ('FreeKicks', 5), ('LongThrows', 5), ('Corners', 5)]),
    ('盘带', 'Dribbling', [('Dribbling', 70), ('FirstTouch', 5), ('Technique', 5), ('Agility', 5), ('Reflexes', 5), ('Composure', 5), ('Balance', 5)]),
    ('防守', 'Defending', [('Tackling', 35), ('Positioning', 30), ('Marking', 20), ('Heading', 10), ('WorkRate', 5)]),
    ('身体', 'Physical', [('Strength', 55), ('Stamina', 10), ('JumpingReach', 20), ('NaturalFitness', 15)]),
]
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT = R / ('第一版卡面六项综合能力-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
before = {}
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    for n in [GN, WN]:
        data = (folder / n).read_bytes()
        before[str(folder / n)] = data
        backup = OUT / ('backup-' + tag) / n
        backup.parent.mkdir(exist_ok=True)
        backup.write_bytes(data)
for n in [GN, WN]:
    assert before[str(GAME / n)] == before[str(SKIN / n)], ('game/skin mismatch', n)
catalog_before = (AA / 'catalog.bin').read_bytes()
(OUT / 'backup-game' / 'catalog.bin').write_bytes(catalog_before)
protected = {n: sha((GAME / n).read_bytes()) for n in [FN, 'ui-backgrounds_assets_common.bundle', 'ui-tileslayouts_assets_all.bundle']}

oldwrite = TypeTreeHelper.write_value
def write(v, n, w, c):
    if n.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, c.assetsfile) is None:
        for ch in n.m_Children:
            if ch.m_Type != 'ReferencedObjectData':
                oldwrite(v[ch.m_Name], ch, w, c)
        if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):
            w.align_stream()
        return
    return oldwrite(v, n, w, c)
TypeTreeHelper.write_value = write

ge = UnityPy.load(before[str(GAME / GN)])
go = {o.path_id: o for o in ge.objects}
we = UnityPy.load(before[str(GAME / WN)])
wo = {o.path_id: o for o in we.objects}
gh = {i: sha(o.get_raw_data()) for i, o in go.items()}
wh = {i: sha(o.get_raw_data()) for i, o in wo.items()}
fe = UnityPy.load(str(GAME / FN))
functions = {o.peek_name(): o for o in fe.objects if o.type.name == 'MonoBehaviour'}
templates = json.loads((R / 'movement-sum-node-templates-v37.json').read_text(encoding='utf-8'))
for obj in functions.values():
    for ref in obj.read_typetree().get('references', {}).get('RefIds', []):
        if ref.get('type', {}).get('class'):
            templates.setdefault(ref['type']['class'], ref)
af = go[SUM].assets_file
native_text = functions['BindIntAddOrSubstractToSIText'].read_typetree()
native_sum = functions['BindMultipleIntArgsAsSumToDestination'].read_typetree()

def guid():
    return {'m_idBytes': list(uuid.uuid4().bytes_le)}

def gid(x):
    return bytes(x['m_idBytes'])

def link(a, port, b, target='m_execInExecInput'):
    a[port]['m_destinationID'] = copy.deepcopy(b[target]['m_id'])

def socket_source(d, port, source):
    d[port]['m_sourceID'] = copy.deepcopy(source)

def constant(d, port, value):
    d[port]['m_sourceID'] = {'m_idBytes': [0] * 16}
    d[port]['m_defaultSocketValue'] = {'m_value': value}

def make_function(code, attrs):
    tree = copy.deepcopy(go[SUM].read_typetree())
    root = guid()
    tree.update(m_Name='OverviewCard' + code + 'Rating', m_name='OverviewCard' + code + 'Rating',
                m_id=root, m_description='Weighted rating; integer arithmetic, final half-up rounding; -- when unavailable.',
                m_inputs=[], m_outputs=[], m_variables=[], m_nodes=[])
    for name, source in [('BindingBag', native_text['m_inputs'][0]), ('SITextElement', native_text['m_inputs'][1])] + [
            ('Attribute' + str(i), native_sum['m_inputs'][3]) for i in range(len(attrs))]:
        p = copy.deepcopy(source)
        p.update(m_name=name, m_id=guid(), m_parentID=copy.deepcopy(root))
        tree['m_inputs'].append(p)
    refs = []
    def clone(cls, name):
        r = copy.deepcopy(templates[cls]); r['rid'] = 194000000000000000 + len(refs)
        d = r['data']; d.update(m_name=name, m_id=guid(), m_parentID=copy.deepcopy(root))
        def reset(v):
            if isinstance(v, dict):
                for k, x in list(v.items()):
                    if k == 'm_id' and isinstance(x, dict) and 'm_idBytes' in x:
                        v[k] = guid()
                    elif k in ['m_sourceID', 'm_destinationID']:
                        v[k] = {'m_idBytes': [0] * 16}
                    else:
                        reset(x)
            elif isinstance(v, list):
                for x in v: reset(x)
        for k, v in d.items():
            if k not in ['m_id', 'm_parentID']: reset(v)
        refs.append(r)
        return d
    entry = clone('EntryNode', 'Entry')
    entry['m_dataSockets'] = [{'m_id': guid(), 'm_name': p['m_name'], 'm_dataID': copy.deepcopy(p['m_id'])} for p in tree['m_inputs']]
    ports = {p['m_name']: p['m_id'] for p in entry['m_dataSockets']}
    bind = clone('BindNode', 'Observe Current Player Attributes')
    socket_source(bind, 'm_bindingBagDataInputSocket', ports['BindingBag'])
    socket_source(bind, 'm_componentDataInputSocket', ports['SITextElement'])
    din = copy.deepcopy(bind['m_dynamicDataInputSockets'][0])
    dout = copy.deepcopy(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0])
    bind['m_dynamicDataInputSockets'] = []; bind['m_outputAsyncExecSocket']['m_dataOutputSockets'] = []
    for p in tree['m_inputs'][2:]:
        di, do = copy.deepcopy(din), copy.deepcopy(dout)
        di.update(m_id=guid(), m_name=p['m_name'], m_sourceID=copy.deepcopy(ports[p['m_name']]), m_dataID=copy.deepcopy(p['m_id']))
        do.update(m_id=guid(), m_name=p['m_name'], m_dataID=copy.deepcopy(p['m_id']))
        bind['m_dynamicDataInputSockets'].append(di); bind['m_outputAsyncExecSocket']['m_dataOutputSockets'].append(do)
    casts = [clone('TypedValueVisualFunctionLibrary_TryCastToInt', 'Read ' + a) for a, weight in attrs]
    for cast, out in zip(casts, bind['m_outputAsyncExecSocket']['m_dataOutputSockets']):
        socket_source(cast, 'm_dataInValue', out['m_id'])
    def add(a, b, name):
        d = clone('GeneralVisualFunction_Add_int_int_int', name)
        socket_source(d, 'm_dataInA', a); socket_source(d, 'm_dataInB', b)
        return d['m_dataOutInt32']['m_id']
    def times(value, coefficient, name):
        powers = {1: value}; p = 1
        while p * 2 <= coefficient:
            powers[p * 2] = add(powers[p], powers[p], name + ' x' + str(p * 2)); p *= 2
        parts = [port for bit, port in powers.items() if coefficient & bit]
        total = parts[0]
        for part in parts[1:]: total = add(total, part, name + ' Weighted Sum')
        return total
    weighted = []
    for (attribute, percent), cast in zip(attrs, casts):
        value = cast['m_dataOutIntValue']['m_id']
        if attribute == 'InjuryProneness':
            sub = clone('GeneralVisualFunction_Subtract_int_int_int', '20 Minus Injury Proneness')
            constant(sub, 'm_dataInA', 20); socket_source(sub, 'm_dataInB', value)
            value = sub['m_dataOutInt32']['m_id']
        weighted.append(times(value, percent // 5, attribute))
    numerator = weighted[0]
    for part in weighted[1:]: numerator = add(numerator, part, 'Total Numerator')
    # All percentages are multiples of five: score = numerator / 4.
    # A balanced threshold tree implements half-up rounding without float or new node classes.
    def leaf(value):
        n = clone('ITextElement_SetText', 'Display ' + str(value))
        socket_source(n, 'm_target', ports['SITextElement']); constant(n, 'm_dataInText', str(value))
        return n
    def choose(lo, hi):
        if lo == hi: return leaf(lo)
        mid = (lo + hi) // 2
        cmp = clone('GeneralVisualFunction_CompareIntInt', 'Numerator Above ' + str(4 * mid + 1))
        constant(cmp, 'm_dataInOp', 4)  # Native GreaterThan enum.
        socket_source(cmp, 'm_dataInA', numerator); constant(cmp, 'm_dataInB', 4 * mid + 1)
        branch = clone('GeneralVisualFunction_Branch', 'Rounded Rating Above ' + str(mid))
        socket_source(branch, 'm_dataInCondition', cmp['m_dataOutBoolean']['m_id'])
        link(cmp, 'm_execOutExecOutput', branch)
        link(branch, 'm_execOutTrue', choose(mid + 1, hi)); link(branch, 'm_execOutFalse', choose(lo, mid))
        return cmp
    rounding_root = choose(0, 100)
    checks = [c['m_dataOutBoolean']['m_id'] for c in casts]
    # A successfully cast sentinel such as 0/-1 must not fabricate a rating.
    validation_nodes = []
    for (attribute, weight), cast in zip(attrs, casts):
        for limit, reversed_args in [(0, False), (21, True)]:
            cmp = clone('GeneralVisualFunction_CompareIntInt', 'Valid ' + attribute + (' Upper Bound' if reversed_args else ' Lower Bound'))
            constant(cmp, 'm_dataInOp', 4)
            if reversed_args:
                constant(cmp, 'm_dataInA', limit); socket_source(cmp, 'm_dataInB', cast['m_dataOutIntValue']['m_id'])
            else:
                socket_source(cmp, 'm_dataInA', cast['m_dataOutIntValue']['m_id']); constant(cmp, 'm_dataInB', limit)
            validation_nodes.append(cmp); checks.append(cmp['m_dataOutBoolean']['m_id'])
    ands = []
    valid = checks[0]
    for check in checks[1:]:
        n = clone('GeneralVisualFunction_AND', 'All Inputs Available And In Range')
        socket_source(n, 'm_dataInA', valid); socket_source(n, 'm_dataInB', check)
        valid = n['m_dataOutBoolean']['m_id']; ands.append(n)
    valid_branch = clone('GeneralVisualFunction_Branch', 'Display Rating Or Missing')
    socket_source(valid_branch, 'm_dataInCondition', valid)
    failed = clone('ITextElement_SetText', 'Display Missing')
    socket_source(failed, 'm_target', ports['SITextElement']); constant(failed, 'm_dataInText', '--')
    link(entry, 'm_outputExecSocket', bind, 'm_inputExecSocket')
    link(bind, 'm_outputAsyncExecSocket', casts[0])
    chain = casts + validation_nodes + ands + [valid_branch]
    for a, b in zip(chain, chain[1:]): link(a, 'm_execOutExecOutput', b)
    link(valid_branch, 'm_execOutTrue', rounding_root); link(valid_branch, 'm_execOutFalse', failed)
    tree['m_nodes'] = [{'rid': r['rid']} for r in refs]
    tree['references'] = {'version': 2, 'RefIds': refs}
    return tree

def check_graph(tree):
    ids = set(); sources = []; destinations = []
    def visit(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k == 'm_id' and isinstance(x, dict) and 'm_idBytes' in x:
                    i = gid(x); assert i not in ids; ids.add(i)
                elif k == 'm_sourceID' and any(x['m_idBytes']): sources.append(gid(x))
                elif k == 'm_destinationID' and any(x['m_idBytes']): destinations.append(gid(x))
                else: visit(x)
        elif isinstance(v, list):
            for x in v: visit(x)
    visit(tree)
    assert set(sources + destinations) <= ids
    assert len(tree['m_nodes']) == len(tree['references']['RefIds'])

def graph_runner(tree):
    refs = tree['references']['RefIds']; by_input = {}; outputs = {}
    for r in refs:
        d = r['data']
        for k, v in d.items():
            if isinstance(v, dict) and 'm_id' in v:
                if k in ['m_execInExecInput', 'm_inputExecSocket']: by_input[gid(v['m_id'])] = r
                elif k.startswith('m_dataOut'): outputs[gid(v['m_id'])] = (r, k)
    entry = next(r['data'] for r in refs if r['type']['class'] == 'EntryNode')
    bind = next(r['data'] for r in refs if r['type']['class'] == 'BindNode')
    def run(values, numerator_override=None):
        memo = {}
        for p, value in zip(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'], values): memo[gid(p['m_id'])] = value
        def value(d, port):
            p = d[port]; source = gid(p['m_sourceID'])
            if not any(source): return p.get('m_defaultSocketValue', {}).get('m_value')
            return resolve(source)
        def resolve(source):
            if source in memo: return memo[source]
            r, port = outputs[source]; d = r['data']; cls = r['type']['class']
            if cls == 'GeneralVisualFunction_Add_int_int_int': result = value(d, 'm_dataInA') + value(d, 'm_dataInB')
            elif cls == 'GeneralVisualFunction_Subtract_int_int_int': result = value(d, 'm_dataInA') - value(d, 'm_dataInB')
            elif cls == 'GeneralVisualFunction_AND': result = bool(value(d, 'm_dataInA')) and bool(value(d, 'm_dataInB'))
            elif cls == 'GeneralVisualFunction_CompareIntInt':
                assert value(d, 'm_dataInOp') == 4
                result = (numerator_override if numerator_override is not None and d['m_name'].startswith('Numerator Above') else value(d, 'm_dataInA')) > value(d, 'm_dataInB')
            else: raise AssertionError(cls)
            memo[source] = result
            return result
        target = gid(bind['m_outputAsyncExecSocket']['m_destinationID'])
        for _ in range(300):
            r = by_input[target]; d = r['data']; cls = r['type']['class']
            if cls == 'TypedValueVisualFunctionLibrary_TryCastToInt':
                v = value(d, 'm_dataInValue'); valid = type(v) is int
                memo[gid(d['m_dataOutBoolean']['m_id'])] = valid
                memo[gid(d['m_dataOutIntValue']['m_id'])] = v if valid else 0
                port = 'm_execOutExecOutput'
            elif cls == 'GeneralVisualFunction_Branch': port = 'm_execOutTrue' if value(d, 'm_dataInCondition') else 'm_execOutFalse'
            elif cls == 'ITextElement_SetText': return value(d, 'm_dataInText')
            elif cls in ['GeneralVisualFunction_CompareIntInt', 'GeneralVisualFunction_AND']:
                resolve(gid(d['m_dataOutBoolean']['m_id'])); port = 'm_execOutExecOutput'
            else: raise AssertionError(cls)
            target = gid(d[port]['m_destinationID'])
        raise AssertionError('execution did not terminate')
    return run

trees = []; calculations = []; test_count = 0
rng = random.Random(20261017)
for index, (title, code, attrs) in enumerate(SPECS):
    tree = make_function(code, attrs); check_graph(tree); run = graph_runner(tree)
    for numerator in range(401):
        assert run([10] * len(attrs), numerator) == str(int((Decimal(numerator) / 4).quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
        test_count += 1
    samples = [[10] * len(attrs), [1] * len(attrs), [20] * len(attrs)] + [[rng.randint(1, 20) for _ in attrs] for _ in range(300)]
    for axis in range(len(attrs)):
        for n in range(1, 21):
            sample = [10] * len(attrs); sample[axis] = n; samples.append(sample)
    for values in samples:
        expected = sum(Decimal(weight) / 100 * (20 - v if a == 'InjuryProneness' else v) for (a, weight), v in zip(attrs, values)) * 5
        assert run(values) == str(int(expected.quantize(Decimal('1'), rounding=ROUND_HALF_UP))), (code, values)
        test_count += 1
    for axis in range(len(attrs)):
        for missing in [None, 0, -1, 21]:
            v = [10] * len(attrs); v[axis] = missing
            assert run(v) == '--'; test_count += 1
    pid = -940000000000100 - index
    key = uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-overview-card-six-rating-' + code).hex
    assert pid not in go
    trees.append((pid, key, tree))
    paths = ['person.InjuryProneness.PropertyValue' if a == 'InjuryProneness' else 'person.attribute' + a.lower() + '.AttributeMinValue' for a, w in attrs]
    calculations.append({'title': title, 'code': code, 'inputs': list(zip(paths, [w for a, w in attrs])), 'function_guid': key, 'path_id': pid, 'nodes': len(tree['m_nodes'])})

known = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in af.ref_types}
needed = {(r['type']['class'], r['type']['ns'], r['type']['asm']) for _, _, t in trees for r in t['references']['RefIds']}
for t in next(iter(functions.values())).assets_file.ref_types:
    k = (t.m_ClassName, t.m_NameSpace, t.m_AssemblyName)
    if k in needed and k not in known: af.ref_types.append(copy.copy(t)); known.add(k)
assert needed <= known
metaobj = next(o for o in go.values() if o.type.name == 'AssetBundle')
meta = metaobj.read_typetree()
for pid, key, tree in trees:
    new = copy.copy(go[SUM]); new.path_id = pid; af.objects[pid] = new; new.save_typetree(tree)
    start = len(meta['m_PreloadTable'])
    meta['m_PreloadTable'].extend([copy.deepcopy(tree['m_Script']), {'m_FileID': 0, 'm_PathID': pid}])
    meta['m_Container'].append((key, {'preloadIndex': start, 'preloadSize': 2, 'asset': {'m_FileID': 0, 'm_PathID': pid}}))
meta['m_Container'].sort(key=lambda x: x[0]); metaobj.save_typetree(meta)

doc = wo[FULL].read_typetree(); rr = {r['rid']: r for r in doc['references']['RefIds']}
sid = doc['inlineSheet']['m_PathID']; sheet = wo[sid].read_typetree()
def named(name):
    return next(r for r in rr.values() if rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name)
def handle(typ, value):
    pool = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}[typ]
    sheet[pool].append(value)
    return {'m_ValueType': typ, 'valueIndex': len(sheet[pool]) - 1}
def px(v): return handle(3, {'unit': 1, 'value': float(v)})
def pct(v): return handle(3, {'unit': 2, 'value': float(v)})
def num(v): return handle(2, float(v))
def en(v): return handle(7, v)
def prop(pid, *values): return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': list(values)}
def rule(properties):
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': properties, 'line': -1})
    return len(sheet['m_Rules']) - 1
def override(node, properties):
    old = copy.deepcopy(sheet['m_Rules'][node['m_RuleIndex']]['m_Properties']) if node.get('m_RuleIndex', -1) >= 0 else []
    replaced = {p['m_Id'] for p in properties}
    node['m_RuleIndex'] = rule([p for p in old if p['m_Id'] not in replaced] + properties)
def zero(): return [prop(262150, px(0)), prop(262151, px(0))]

rid = max(rr) + 1
eid = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
def pair(nt, st, parent, name, style):
    global rid, eid
    n, s = copy.deepcopy(nt), copy.deepcopy(st)
    n['rid'], s['rid'] = rid, rid + 1; rid += 2
    n['data'].update(m_Id=eid, m_Parent={'rid': parent}, m_Children=[], m_SerializedData={'rid': s['rid']},
                     m_RuleIndex=style, m_Classes=[], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[], m_SkipClone=0)
    s['data'].update(uxmlAssetId=eid, name=name, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    eid += 1; rr[n['rid']] = n; rr[s['rid']] = s
    doc['references']['RefIds'].extend([n, s]); rr[parent]['data']['m_Children'].append({'rid': n['rid']})
    return n, s

stage = named('ReportPortraitLayerStage')
frame = next(r for r in rr.values() if r.get('data', {}).get('m_Parent', {}).get('rid') == stage['rid'] and rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == 'PersonPictureFrame')
override(frame['data'], [prop(131105, px(160)), prop(131087, px(160)), prop(131089, px(145)), prop(131104, px(12)), prop(327681, num(1), num(1))])

# Inline the avatar only into the first version, so its internal image scale can be changed privately.
avatar = wo[-910000000000101].read_typetree(); avs = wo[avatar['inlineSheet']['m_PathID']].read_typetree()
old_avatar_node = next(r for r in rr.values() if r.get('data', {}).get('m_TemplateAlias') == 'MovedBanner_ReportMiddleSquarePersonPicture')
old_sd = old_avatar_node['data']['m_SerializedData']['rid']; av_parent = old_avatar_node['data']['m_Parent']['rid']
av_refs = [copy.deepcopy(r) for r in avatar['references']['RefIds'] if r['rid'] not in [-2, avatar['m_VisualTree']['rid']]]
mapping = {r['rid']: rid + i for i, r in enumerate(av_refs)}; rid += len(av_refs)
mapping[avatar['m_VisualTree']['rid']] = av_parent
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
offsets = {}
for pool in set(poolmap.values()):
    offsets[pool] = len(sheet[pool]); sheet[pool].extend(copy.deepcopy(avs[pool]))
rule_offset = len(sheet['m_Rules'])
for ar in avs['m_Rules']:
    ar = copy.deepcopy(ar)
    for p in ar['m_Properties']:
        for h in p['m_Values']:
            if h['m_ValueType'] in poolmap: h['valueIndex'] += offsets[poolmap[h['m_ValueType']]]
    sheet['m_Rules'].append(ar)
def remap(v):
    if isinstance(v, dict):
        if set(v) == {'rid'}:
            if v['rid'] != -2: v['rid'] = mapping[v['rid']]
        else:
            for x in v.values(): remap(x)
    elif isinstance(v, list):
        for x in v: remap(x)
for r in av_refs:
    oldid = r['rid']; remap(r.get('data', {})); r['rid'] = mapping[oldid]
    d = r.get('data', {})
    if 'm_Parent' in d:
        old_eid = d['m_Id']; d['m_Id'] = eid; eid += 1
        if d.get('m_RuleIndex', -1) >= 0: d['m_RuleIndex'] += rule_offset
        sd = next((a for a in av_refs if a['rid'] == d.get('m_SerializedData', {}).get('rid')), None)
        # Serialized-data rid renaming can happen later in this loop.
    rr[r['rid']] = r
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in [old_avatar_node['rid'], old_sd]] + av_refs
for r in av_refs:
    d = r.get('data', {})
    if 'm_Parent' in d and d.get('m_SerializedData', {}).get('rid', -2) != -2:
        rr[d['m_SerializedData']['rid']]['data']['uxmlAssetId'] = d['m_Id']
    if d.get('m_FullTypeName') == 'SI.Bindable.SIImage':
        override(d, [prop(327681, num(1), num(1))])
av_root = mapping[1001]
rr[av_parent]['data']['m_Children'] = [{'rid': av_root} if x['rid'] == old_avatar_node['rid'] else x for x in rr[av_parent]['data']['m_Children']]
del rr[old_avatar_node['rid']]; del rr[old_sd]

# Keep status tags at the bottom of the portrait, above the six statistics.
status = rr[1172]
old_parent = status['data']['m_Parent']['rid']
rr[old_parent]['data']['m_Children'] = [c for c in rr[old_parent]['data']['m_Children'] if c['rid'] != status['rid']]
status['data']['m_Parent'] = {'rid': stage['rid']}; stage['data']['m_Children'].append({'rid': status['rid']})
override(status['data'], [prop(131102, en('absolute')), prop(131089, px(135)), prop(131104, px(156)), prop(131105, px(180)),
                          prop(131087, px(24)), prop(131097, px(0)), prop(131093, px(0)), prop(131084, num(0)), prop(131085, num(0))])

ve = named('ReportPortraitLayerStage'); ves = rr[ve['data']['m_SerializedData']['rid']]
integer = json.loads((R / 'native-integer-text-template-v36.json').read_text(encoding='utf-8'))
integer['sd']['data'].pop('BindTextFunction', None)
integer['sd']['data'].pop('BindTextFunction_UxmlAttributeFlags', None)
container_style = rule([prop(131102, en('absolute')), prop(131089, px(135)), prop(131104, px(182)), prop(131105, px(180)),
                        prop(131087, px(44)), prop(131083, en('column')), prop(131084, num(0)), prop(131085, num(0))] + zero())
grid, _ = pair(ve, ves, stage['rid'], 'OverviewCardSixRatings', container_style)
row_style = rule([prop(131105, pct(100)), prop(131087, px(22)), prop(131083, en('row')), prop(131085, num(0))] + zero())
cell_style = rule([prop(131105, px(60)), prop(131087, px(22)), prop(131083, en('row')), prop(131073, en('center')),
                   prop(131088, en('center')), prop(131085, num(0))] + zero())
def text_style(size, width, bold):
    return rule([prop(131105, px(width)), prop(131087, px(22)), prop(131097, px(0)), prop(131085, num(0)), prop(65537, px(size)),
                 prop(65546, en('middle-center')), prop(65552, en('nowrap')), prop(65543, en('bold' if bold else 'normal')),
                 prop(65536, handle(4, {'r': 1.0, 'g': 1.0, 'b': 1.0, 'a': 1.0}))] + zero())
title_style = text_style(13, 28, False); value_style = text_style(14, 28, True)
def string(s):
    b = s.encode('utf-8'); assert len(b) < 128
    return bytes([len(b)]) + b
BC = 'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
def vf(key, paths):
    b = bytearray([len(paths)])
    for path in paths:
        p = string(BC) + b'\x01' + string(path); b.extend(struct.pack('<i', len(p))); b.extend(p)
    return {'m_target': {'m_guid': key}, 'm_inputs': {'m_variable': {'m_argumentBytes': list(b)}}, 'm_outputs': {'m_variable': {'m_argumentBytes': []}}}
def clear_text_binding(d):
    d['TextBinding']['m_kind'] = 0; d['TextBinding']['m_visualFunction'] = vf('', [])
    d['TextBinding_UxmlAttributeFlags'] = 1
    d['bindingPath'] = ''; d['bindingPath_UxmlAttributeFlags'] = 0
for row_index in range(2):
    row, _ = pair(ve, ves, grid['rid'], 'OverviewCardRatingRow' + str(row_index + 1), row_style)
    for col in range(3):
        index = row_index * 3 + col; spec = calculations[index]
        cell, _ = pair(ve, ves, row['rid'], 'OverviewCard' + spec['code'] + 'Cell', cell_style)
        title, ts = pair(integer['node'], integer['sd'], cell['rid'], 'OverviewCard' + spec['code'] + 'Title', title_style)
        clear_text_binding(ts['data']); ts['data'].update(text=spec['title'], text_UxmlAttributeFlags=1, DebugDisplay=spec['title'])
        value, vs = pair(integer['node'], integer['sd'], cell['rid'], 'OverviewCard' + spec['code'] + 'Value', value_style)
        clear_text_binding(vs['data']); vs['data'].update(text='--', text_UxmlAttributeFlags=1, DebugDisplay='--')
        vs['data']['TextBinding']['m_kind'] = 2
        vs['data']['TextBinding']['m_visualFunction'] = vf(spec['function_guid'], [p for p, w in spec['inputs']])

def validate_ui(d, s):
    refs = {r['rid']: r for r in d['references']['RefIds']}; assert len(refs) == len(d['references']['RefIds'])
    seen = set(); element_ids = set()
    def visit(i):
        assert i not in seen; seen.add(i); a = refs[i]['data']
        assert a['m_Id'] not in element_ids; element_ids.add(a['m_Id'])
        if a.get('m_RuleIndex', -1) >= 0: assert a['m_RuleIndex'] < len(s['m_Rules'])
        sd = a.get('m_SerializedData', {}).get('rid', -2)
        if sd != -2: assert refs[sd]['data']['uxmlAssetId'] == a['m_Id']
        for ch in a.get('m_Children', []):
            assert refs[ch['rid']]['data']['m_Parent']['rid'] == i; visit(ch['rid'])
    visit(d['m_VisualTree']['rid'])
    assert all(r['rid'] in seen for r in refs.values() if 'm_Parent' in r.get('data', {}))
    for rule_ in s['m_Rules']:
        for p in rule_['m_Properties']:
            for h in p['m_Values']:
                if h['m_ValueType'] in poolmap: assert 0 <= h['valueIndex'] < len(s[poolmap[h['m_ValueType']]])
    for r in refs.values():
        if r.get('data', {}).get('m_TemplateAlias'):
            alias = r['data']['m_TemplateAlias']; u = next(u for u in d['m_Usings'] if u['alias'] == alias)
            assert refs[r['data']['m_SerializedData']['rid']]['data']['templateId'] == alias
    return len(seen)
element_count = validate_ui(doc, sheet)
wo[FULL].save_typetree(doc); wo[sid].save_typetree(sheet)

cs = importlib.util.spec_from_file_location('card_catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(cs); cs.loader.exec_module(cm)
cat_bytes = catalog_before
for pid, key, tree in trees:
    cat = cm.Catalog(cat_bytes)
    loc = cat.locations(OLD_SUM_GUID)[0]
    cat_bytes = cat.add_key_location(key, loc, loc)
cat = cm.Catalog(cat_bytes)
for pid, key, tree in trees:
    assert len(cat.locations(key)) == 1
    assert cat.location(cat.locations(key)[0])['type'] == cat.location(cat.locations(OLD_SUM_GUID)[0])['type']

result = {GN: ge.file.save(packer='lz4'), WN: we.file.save(packer='lz4')}
for name, data in result.items(): (OUT / name).write_bytes(data)
(OUT / 'catalog.bin').write_bytes(cat_bytes)
savedg = {o.path_id: o for o in UnityPy.load(result[GN]).objects}
savedw = {o.path_id: o for o in UnityPy.load(result[WN]).objects}
assert set(savedg) == set(go) | {p for p, k, t in trees}
assert set(savedw) == set(wo)
for i, h in gh.items():
    if i == metaobj.path_id: assert savedg[i].read_typetree() == meta
    else: assert sha(savedg[i].get_raw_data()) == h, ('global unrelated changed', i)
for i, h in wh.items():
    if i in [FULL, sid]: assert savedw[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(savedw[i].get_raw_data()) == h, ('world unrelated changed', i)
for pid, key, tree in trees:
    reread = savedg[pid].read_typetree(); assert reread == tree; check_graph(reread)
    assert graph_runner(reread)([10] * (len(reread['m_inputs']) - 2)) == '50'
validate_ui(savedw[FULL].read_typetree(), savedw[sid].read_typetree())
assert all(sha((GAME / n).read_bytes()) == h for n, h in protected.items())
manifest = {'installed': False, 'runtime_verified': False, 'formula_tests_passed': test_count, 'card_size': [260, 260], 'bar_height': 250,
            'portrait_size': [160, 160], 'statistics_layout': '2 rows x 3 columns', 'rounding': 'final half-up only',
            'second_version_unchanged': True, 'background_unchanged': True, 'navigation_and_actions_unchanged': True,
            'stats': calculations, 'full_version_elements': element_count,
            'unchanged_global_objects': len(gh) - 1, 'unchanged_world_objects': len(wh) - 2,
            'before_sha256': {p: sha(b) for p, b in before.items()}, 'before_catalog_sha256': sha(catalog_before),
            'after_sha256': {n: sha(b) for n, b in result.items()}, 'after_catalog_sha256': sha(cat_bytes),
            'protected_game_sha256': protected, 'modified_world_objects': [FULL, sid]}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

if '--install' in sys.argv:
    for p, b in before.items(): assert Path(p).read_bytes() == b, ('target changed during build', p)
    assert (AA / 'catalog.bin').read_bytes() == catalog_before
    try:
        for folder in [GAME, SKIN]:
            for n, data in result.items():
                (folder / n).write_bytes(data); assert (folder / n).read_bytes() == data
        (AA / 'catalog.bin').write_bytes(cat_bytes); assert (AA / 'catalog.bin').read_bytes() == cat_bytes
    except Exception:
        for p, b in before.items(): Path(p).write_bytes(b)
        (AA / 'catalog.bin').write_bytes(catalog_before)
        raise
    manifest['installed'] = True
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), 'installed': manifest['installed'], 'tests_passed': test_count, 'new_function_nodes': [len(t['m_nodes']) for p, k, t in trees], 'sha256': manifest['after_sha256']}, ensure_ascii=False, indent=2))
