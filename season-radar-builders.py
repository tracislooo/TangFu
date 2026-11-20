"""Native visual-function graph and UXML builders for the private season radar."""
import copy
import struct
import uuid

POOL = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}


def guid():
    return {'m_idBytes': list(uuid.uuid4().bytes_le)}


def make_stat_function(native, templates, script):
    tree = copy.deepcopy(native)
    root = guid()
    tree.update(m_Name='LeftTestSeasonRadarValues', m_name='LeftTestSeasonRadarValues', m_id=root,
                m_description='Observe raw season numbers; preserve raw labels; reverse only the plotted value.',
                m_inputs=[], m_outputs=[], m_variables=[], m_nodes=[])
    tree['m_Script'] = copy.deepcopy(script)
    parameters = [
        ('BindingBag', native['m_inputs'][0]), ('Target', native['m_inputs'][1]),
        ('Source', native['m_inputs'][2]), ('Maximum', native['m_inputs'][2]),
        ('Minimum', {'m_type': {'m_typeString': 'System.Single, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'}}),
        ('Reverse', {'m_type': {'m_typeString': 'System.Boolean, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089'}}),
    ] + [(name, native['m_inputs'][2]) for name in ['RawDestination', 'PlotDestination', 'MaximumDestination', 'ValidDestination']]
    for name, template in parameters:
        p = copy.deepcopy(template)
        p.update(m_name=name, m_id=guid(), m_parentID=copy.deepcopy(root))
        tree['m_inputs'].append(p)
    refs = []

    def node(cls, name):
        r = copy.deepcopy(templates[cls])
        r['rid'] = 195000000000000000 + len(refs)
        def reset(v):
            if isinstance(v, dict):
                for k, x in v.items():
                    if k == 'm_id' and isinstance(x, dict) and 'm_idBytes' in x:
                        v[k] = guid()
                    elif k in ['m_sourceID', 'm_destinationID']:
                        v[k] = {'m_idBytes': [0] * 16}
                    else:
                        reset(x)
            elif isinstance(v, list):
                for x in v:
                    reset(x)
        reset(r['data'])
        r['data'].update(m_name=name, m_id=guid(), m_parentID=copy.deepcopy(root))
        refs.append(r)
        return r['data']

    def source(d, port, value):
        d[port]['m_sourceID'] = copy.deepcopy(value)

    def const(d, port, value):
        d[port]['m_sourceID'] = {'m_idBytes': [0] * 16}
        d[port]['m_defaultSocketValue'] = {'m_value': value}

    def link(a, port, b, target='m_execInExecInput'):
        a[port]['m_destinationID'] = copy.deepcopy(b[target]['m_id'])

    entry = node('EntryNode', 'Entry')
    entry['m_dataSockets'] = [dict(m_id=guid(), m_name=p['m_name'], m_dataID=copy.deepcopy(p['m_id'])) for p in tree['m_inputs']]
    ports = {p['m_name']: p['m_id'] for p in entry['m_dataSockets']}
    bind = node('BindNode', 'Observe current season statistic and its range')
    source(bind, 'm_bindingBagDataInputSocket', ports['BindingBag'])
    source(bind, 'm_componentDataInputSocket', ports['Target'])
    din = copy.deepcopy(bind['m_dynamicDataInputSockets'][0])
    dout = copy.deepcopy(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0])
    bind['m_dynamicDataInputSockets'] = []
    bind['m_outputAsyncExecSocket']['m_dataOutputSockets'] = []
    for name in ['Source', 'Maximum']:
        p = next(p for p in tree['m_inputs'] if p['m_name'] == name)
        a, b = copy.deepcopy(din), copy.deepcopy(dout)
        a.update(m_id=guid(), m_name=name, m_sourceID=copy.deepcopy(ports[name]), m_dataID=copy.deepcopy(p['m_id']))
        b.update(m_id=guid(), m_name=name, m_dataID=copy.deepcopy(p['m_id']))
        bind['m_dynamicDataInputSockets'].append(a)
        bind['m_outputAsyncExecSocket']['m_dataOutputSockets'].append(b)
    casts = [node('TypedValueVisualFunctionLibrary_TryCastToFloat', 'Read ' + name) for name in ['Source', 'Maximum']]
    for cast, out in zip(casts, bind['m_outputAsyncExecSocket']['m_dataOutputSockets']):
        source(cast, 'm_dataInValue', out['m_id'])
    valid = node('GeneralVisualFunction_AND', 'Both values available')
    for port, cast in zip(['m_dataInA', 'm_dataInB'], casts):
        source(valid, port, cast['m_dataOutBoolean']['m_id'])
    sum_range = node('GeneralVisualFunction_AddFloat_float_float_float', 'Minimum plus maximum')
    source(sum_range, 'm_dataInA', ports['Minimum'])
    source(sum_range, 'm_dataInB', casts[1]['m_dataOutFloatValue']['m_id'])
    reverse = node('GeneralVisualFunction_SubtractFloat_float_float_float', 'Reverse radius, retain raw statistic')
    source(reverse, 'm_dataInA', sum_range['m_dataOutSingle']['m_id'])
    source(reverse, 'm_dataInB', casts[0]['m_dataOutFloatValue']['m_id'])

    def boxed_float(value):
        n = node('TypedValueVisualFunctionLibrary_FloatToTypedValue', 'Create<float>')
        source(n, 'm_dataInValue', value)
        return n['m_dataOutTypedValue']['m_id']

    raw, maximum = [boxed_float(cast['m_dataOutFloatValue']['m_id']) for cast in casts]
    inverted, missing = boxed_float(reverse['m_dataOutSingle']['m_id']), boxed_float(ports['Minimum'])
    bool_box = node('TypedValueVisualFunctionLibrary_BoolToTypedValue', 'Availability flag')
    source(bool_box, 'm_dataInValue', valid['m_dataOutBoolean']['m_id'])

    def setter(destination, value):
        n = node('VisualFunctionLibrary_SetBinding', 'Set ' + destination)
        source(n, 'm_dataInTarget', ports['Target'])
        source(n, 'm_dataInDest', ports[destination])
        source(n, 'm_dataInValue', value)
        const(n, 'm_dataInForceUpdate', 1)
        return n

    set_raw, set_max, set_valid = setter('RawDestination', raw), setter('MaximumDestination', maximum), setter('ValidDestination', bool_box['m_dataOutTypedValue']['m_id'])
    branch_valid = node('GeneralVisualFunction_Branch', 'Available or missing')
    source(branch_valid, 'm_dataInCondition', valid['m_dataOutBoolean']['m_id'])
    branch_reverse = node('GeneralVisualFunction_Branch', 'Positive or reverse axis')
    source(branch_reverse, 'm_dataInCondition', ports['Reverse'])
    link(entry, 'm_outputExecSocket', bind, 'm_inputExecSocket')
    link(bind, 'm_outputAsyncExecSocket', casts[0])
    chain = casts + [valid, set_raw, set_max, set_valid, branch_valid]
    for a, b in zip(chain, chain[1:]):
        link(a, 'm_execOutExecOutput', b)
    link(branch_valid, 'm_execOutTrue', branch_reverse)
    link(branch_valid, 'm_execOutFalse', setter('PlotDestination', missing))
    link(branch_reverse, 'm_execOutTrue', setter('PlotDestination', inverted))
    link(branch_reverse, 'm_execOutFalse', setter('PlotDestination', raw))
    tree['m_nodes'] = [{'rid': r['rid']} for r in refs]
    tree['references'] = {'version': 2, 'RefIds': refs}
    return tree


def short(s):
    b = s.encode('utf8')
    assert len(b) < 128
    return bytes([len(b)]) + b


def path_arg(path):
    return short('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]') + b'\x01' + short(path)


def float_arg(value):
    return short('SI.VisualScripting.SingleVisualArg') + struct.pack('<f', value)


def bool_arg(value):
    return short('SI.VisualScripting.BooleanVisualArg') + bytes([int(value)])


def pack_args(*args):
    return list(bytes([len(args)]) + b''.join(struct.pack('<I', len(x)) + x for x in args))


def path_list_arg(paths):
    assert len(paths) <= 10, 'Native SI.Core.StructList<T> has only m_value0 through m_value9'
    # Same StructList<BindingPath> encoding as the shipped BindCreateListToDestination.
    return short('SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]') + bytes([len(paths)]) + b''.join(b'\x01' + short(p) for p in paths)


def make_merge_function(native, templates, script):
    """Reuse the native list observer; flatten two short lists into a growable List."""
    tree = copy.deepcopy(native)
    old_root, root = tree['m_id'], guid()
    tree.update(m_Name='LeftTestSeasonRadarMergeLists', m_name='LeftTestSeasonRadarMergeLists',
                m_id=root, m_Script=copy.deepcopy(script),
                m_description='Observe two list bindings and flatten them without the ten-item StructList limit.')
    def parents(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k == 'm_parentID' and x == old_root:
                    v[k] = copy.deepcopy(root)
                else:
                    parents(x)
        elif isinstance(v, list):
            for x in v:
                parents(x)
    parents(tree)
    rr = tree['references']['RefIds']
    creation = next(r for r in rr if r.get('type', {}).get('class') ==
                    'ListFunctions_CreateListFromItems_SI_Core_TypedValue_in_SI_Core_StructList_SI_Core_TypedValue_')
    old = creation['data']
    combined_class = 'ListFunctions_CombinedLists_System_Collections_Generic_List_SI_Core_TypedValue__in_SI_Core_StructList_SI_Core_TypedValue__bool'
    combined = copy.deepcopy(templates[combined_class])
    combined['rid'] = creation['rid']
    d = combined['data']
    for key in ['m_id', 'm_parentID', 'm_position', 'm_execInExecInput', 'm_execOutExecOutput', 'm_dataInValues']:
        d[key] = copy.deepcopy(old[key])
    d['m_name'] = 'Flatten the two radar halves'
    d['m_dataOutList'] = copy.deepcopy(old['m_dataOutTypedValue'])
    d['m_dataOutList']['m_name'] = 'List'
    d['m_dataInAllowDuplicates'].update(m_id=guid(), m_sourceID={'m_idBytes': [0] * 16},
                                      m_defaultSocketValue={'m_value': 1})
    creation.clear()
    creation.update(combined)
    setter = next(r for r in rr if r.get('type', {}).get('class') == 'VisualFunctionLibrary_SetBinding')
    setter['type'] = copy.deepcopy(templates['VisualFunctionLibrary_SetListBinding']['type'])
    setter['data']['m_name'] = 'Set merged radar list'
    setter['data']['m_dataInValue']['m_sourceID'] = copy.deepcopy(d['m_dataOutList']['m_id'])
    return tree


def function(guid, *args):
    return dict(m_target={'m_guid': guid}, m_inputs={'m_variable': {'m_argumentBytes': pack_args(*args)}},
                m_outputs={'m_variable': {'m_argumentBytes': []}})


def rewrite_argument_text(binding, replacements):
    result = copy.deepcopy(binding)
    data = bytes(result['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    # Rebuild the outer argument byte lengths after replacing length-prefixed strings.
    count, pos, args = data[0], 1, []
    for _ in range(count):
        length = struct.unpack_from('<I', data, pos)[0]
        arg = data[pos + 4:pos + 4 + length]
        pos += 4 + length
        for before, after in replacements.items():
            arg = arg.replace(short(before), short(after))
        args.append(arg)
    assert pos == len(data)
    result['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = pack_args(*args)
    return result
