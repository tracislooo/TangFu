from pathlib import Path
source = Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig')
exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-', 'tactics-subs-training-effectiveness-'), 'backup-and-helpers', 'exec'))
PID = 1593217430813700770
TARGET = -1711414761868513156
GUID = '2f9f95dd255b5a64b9b894591fcda036'
doc = objs[PID].read_typetree()
rr = refs(doc)
original = copy.deepcopy(rr)
sid = doc['inlineSheet']['m_PathID']
sheet = objs[sid].read_typetree()
target = objs[TARGET].read_typetree()
assert target['m_Name'] == 'TacticalEffectivenessBlock'
scrollnode, scrollsd = copy.deepcopy(rr[1005]), copy.deepcopy(rr[rr[1005]['data']['m_SerializedData']['rid']])
donor = objs[-8273082868742719783].read_typetree()
dr = refs(donor)
mapnode, mapsd = copy.deepcopy(dr[1002]), copy.deepcopy(dr[dr[1002]['data']['m_SerializedData']['rid']])
template = objs[9171409697554336706].read_typetree()
tr = refs(template)
tn, ts = copy.deepcopy(tr[1010]), copy.deepcopy(tr[tr[1010]['data']['m_SerializedData']['rid']])
next_rid = max(rr) + 1
next_id = max(a.get('data', {}).get('m_Id', 0) for a in rr.values()) + 1
# Retain the original root contract and mode-dependent sizing class setter.
keep = {-2, 1000, 1001, 1002, 1003, 1006}
rr = {i: a for i, a in rr.items() if i in keep}
rr[1002]['data']['m_Children'] = []
doc['references']['RefIds'] = [a for a in doc['references']['RefIds'] if a['rid'] in keep]
doc['m_Usings'] = [{'alias': 'EmbeddedTrainingTacticalEffectiveness', 'path': GUID, 'asset': {'m_FileID': 0, 'm_PathID': 0}}]
def add(node, sd, parent, name):
    global next_rid, next_id
    a, s = copy.deepcopy(node), copy.deepcopy(sd)
    a['rid'], s['rid'] = next_rid, next_rid + 1
    next_rid += 2
    a['data'].update(m_Id=next_id, m_Parent={'rid': parent}, m_Children=[], m_RuleIndex=-1, m_SerializedData={'rid': s['rid']}, m_Classes=[], m_Properties=[])
    s['data'].update(uxmlAssetId=next_id, name=name, name_UxmlAttributeFlags=1)
    next_id += 1
    rr[a['rid']], rr[s['rid']] = a, s
    doc['references']['RefIds'] += [a, s]
    rr[parent]['data']['m_Children'].append({'rid': a['rid']})
    return a['rid']
def sd(i): return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
scroll = add(scrollnode, scrollsd, 1002, 'TrainingTacticalEffectivenessScroll')
for key, value in {'mode': 0, 'horizontalScrollerVisibility': 2, 'verticalScrollerVisibility': 0}.items():
    sd(scroll)[key] = value
    sd(scroll)[key + '_UxmlAttributeFlags'] = 1
override(rr[1001]['data'], [prop(131097, px(0)), prop(131096, px(0)), prop(131105, pct(100))])
override(rr[1002]['data'], [prop(131083, en('column')), prop(131105, pct(100)), prop(131097, px(0)), prop(131096, px(0))])
override(rr[scroll]['data'], [prop(131105, pct(100)), prop(131087, pct(100)), prop(131097, px(0)), prop(131096, px(0)), prop(131084, num(1)), prop(131085, num(1))])
mapper = add(mapnode, mapsd, scroll, 'TrainingTacticalEffectivenessContext')
sd(mapper).update(Mappings=[
    {'m_serialisedType': 0, 'from': 'tactic', 'to': {'m_path': 'Tactic'}, 'type': {'id': 2003981122}},
    {'m_serialisedType': 0, 'from': 'humanteam', 'to': {'m_path': 'team'}, 'type': {'id': 1145176088}},
    {'m_serialisedType': 0, 'from': 'player', 'to': {'m_path': 'const.nullref'}, 'type': {'id': 1145176065}},
], Mappings_UxmlAttributeFlags=1)
override(rr[mapper]['data'], [prop(131105, pct(100)), prop(131097, px(0)), prop(131084, num(0)), prop(131085, num(0))])
instance = add(tn, ts, mapper, 'TrainingTacticalEffectivenessPage')
rr[instance]['data'].update(m_TemplateAlias='EmbeddedTrainingTacticalEffectiveness', m_AttributeOverrides=[], m_SerializedDataOverride=[], m_SlotUsages=[])
sd(instance).update(templateId='EmbeddedTrainingTacticalEffectiveness', templateId_UxmlAttributeFlags=1)
override(rr[instance]['data'], [prop(131105, pct(100)), prop(131097, px(0)), prop(131096, px(480)), prop(131084, num(0)), prop(131085, num(0))])
assert rr[1003] == original[1003], 'Original Tactic/mode/team parameter contract changed'
assert rr[1006] == original[1006], 'Mode-dependent original sizing bindings changed'
assert sd(mapper)['Mappings'][1]['to']['m_path'] == 'team'
assert not any(a.get('data', {}).get('m_FullTypeName', '').endswith(('WrappedObjectList', 'StreamedObjectList')) for a in rr.values())
validate_ui(doc, sheet)
objs[PID].save_typetree(doc)
objs[sid].save_typetree(sheet)
# Include the existing full-page VTA dependency in this module's preload list.
metaobj = next(o for o in objs.values() if o.type.name == 'AssetBundle')
meta = metaobj.read_typetree()
source_entry = next(v for k, v in meta['m_Container'] if k == GUID and v['asset']['m_PathID'] == TARGET)
entry = next(v for k, v in meta['m_Container'] if v['asset']['m_PathID'] == PID)
span = copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
for ptr in meta['m_PreloadTable'][source_entry['preloadIndex']:source_entry['preloadIndex'] + source_entry['preloadSize']] + [source_entry['asset']]:
    if ptr not in span: span.append(copy.deepcopy(ptr))
entry.update(preloadIndex=len(meta['m_PreloadTable']), preloadSize=len(span))
meta['m_PreloadTable'].extend(span)
metaobj.save_typetree(meta)
changed = {PID: doc, sid: sheet, metaobj.path_id: meta}
output = env.file.save(packer='lz4')
check = {o.path_id: o for o in UnityPy.load(output).objects}
assert check.keys() == objs.keys()
for i, h in hashes.items():
    if i not in changed: assert sha(check[i].get_raw_data()) == h, i
for i, d in changed.items(): assert check[i].read_typetree() == d, i
assert sha(check[TARGET].get_raw_data()) == hashes[TARGET], 'Native training page altered'
(OUT / W).write_bytes(output)
(OUT / 'module.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2), 'utf8')
restore = ['$ErrorActionPreference = "Stop"', "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer = list(restore)
for p, b in before.items():
    tag = 'backup-game' if p.parent == GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '" + str(OUT / tag / W) + "' -Destination '" + str(p) + "' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '" + str(p) + "' -Algorithm SHA256).Hash.ToLower() -ne '" + sha(b) + "') { throw 'Package changed; prepare a fresh patch.' }")
for p in before: installer.append("Copy-Item -LiteralPath '" + str(OUT / W) + "' -Destination '" + str(p) + "' -Force")
(OUT / 'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
(OUT / 'install.ps1').write_text('\n'.join(installer), 'utf-8-sig')
report = {'installed': False, 'runtime_verified': False, 'source_module': 'TacticalPlannerSubsBlock',
          'replacement': 'TacticalEffectivenessBlock', 'replacement_guid': GUID, 'current_team_and_tactic': True,
          'team_view_player': 'const.nullref', 'vertical_scroll': True, 'original_module_mode_sizing_retained': True,
          'table_rings_fatigue_and_avatars_unchanged': True, 'changed_objects': list(changed), 'after_sha256': sha(output)}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
for p, b in before.items(): assert p.read_bytes() == b
for p, h in protected.items(): assert sha(p.read_bytes()) == h
proc = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'waiting_for_game_exit': True, 'output': str(OUT)})); sys.exit(0)
try:
    for p in before: p.write_bytes(output); assert p.read_bytes() == output
    for p, h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p, b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True, installed_verified=True)
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': True, 'output': str(OUT), 'replacement': 'TacticalEffectivenessBlock'}))
