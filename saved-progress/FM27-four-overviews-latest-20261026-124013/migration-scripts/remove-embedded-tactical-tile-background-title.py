from pathlib import Path
import struct, uuid, importlib.util
source = Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig')
exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-', 'tactics-overview-content-no-background-title-'), 'backup-and-helpers', 'exec'))
PID, SID = -970000000005000, -970000000005001
GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/EmbeddedTrainingEffectivenessContent/v1').hex
MODULE = 1593217430813700770
TILE = 4958372856258444847
for p in [GAME.parent/'catalog.bin', GAME.parent/'catalog.hash', SKIN/'catalog.bin']:
    before[p] = p.read_bytes()
    protected.pop(p, None)
    (OUT/('backup-skin' if p.parent == SKIN else 'backup-game')/p.name).write_bytes(before[p])
assert before[GAME.parent/'catalog.bin'] == before[SKIN/'catalog.bin']
doc = objs[TILE].read_typetree()
rr = refs(doc)
old = copy.deepcopy(rr)
old_sid = doc['inlineSheet']['m_PathID']
sheet = objs[old_sid].read_typetree()
doc['m_Name'] = 'EmbeddedTrainingEffectivenessContent'
doc['inlineSheet']['m_PathID'] = SID
sheet['m_Name'] = 'EmbeddedTrainingEffectivenessContent_Style'
assert rr[1004]['data']['m_TemplateAlias'] == 'tile-figma-base-template'
assert rr[1004]['data']['m_Children'] == [{'rid':1006}]
assert rr[1009]['data']['DebugDisplay'] == 'Tactical Effectiveness'
# Remove the shared tile shell, title, and header action. Keep all data content.
discard = {1004, rr[1004]['data']['m_SerializedData']['rid'], 1008, 1009}
assert len(discard) == 4
rr[1001]['data']['m_Children'] = [{'rid':1002}, {'rid':1003}, {'rid':1006}]
rr[1006]['data']['m_Parent'] = {'rid':1001}
doc['references']['RefIds'] = [a for a in doc['references']['RefIds'] if a['rid'] not in discard]
rr = refs(doc)
doc['m_Usings'] = [u for u in doc['m_Usings'] if u['alias'] != 'tile-figma-base-template']
for i in [1001,1006]:
    override(rr[i]['data'], [prop(458752, val(4, {'r':0.,'g':0.,'b':0.,'a':0.})), prop(458753, {'m_ValueType':1,'valueIndex':3}), prop(262150,px(0)), prop(262151,px(0))])
for i, a in old.items():
    if i not in discard and i not in [1001,1006]: assert rr[i] == a, ('content or binding altered', i)
validate_ui(doc,sheet)
def clone(source,pid,data):
    assert pid not in objs
    o = copy.copy(source)
    o.path_id, o.data, o._read_until = pid, None, None
    o.assets_file.objects[pid] = o
    objs[pid] = o
    o.save_typetree(data)
clone(objs[TILE],PID,doc)
clone(objs[old_sid],SID,sheet)
module = objs[MODULE].read_typetree()
oldmodule = copy.deepcopy(module)
using = next(u for u in module['m_Usings'] if u['alias'] == 'EmbeddedTrainingTacticalEffectiveness')
assert using['path'] == '414d4dc7ae21fca47a2684eb783dd244'
using['path'] = GUID
assert module['references'] == oldmodule['references']
objs[MODULE].save_typetree(module)
metaobj = next(o for o in objs.values() if o.type.name == 'AssetBundle')
meta = metaobj.read_typetree()
native = next(v for k,v in meta['m_Container'] if v['asset']['m_PathID'] == TILE)
span = copy.deepcopy(meta['m_PreloadTable'][native['preloadIndex']:native['preloadIndex']+native['preloadSize']])
span = [p for p in span if not (p['m_FileID']==0 and p['m_PathID'] in [TILE,old_sid])]
span += [{'m_FileID':0,'m_PathID':PID},{'m_FileID':0,'m_PathID':SID}]
meta['m_Container'].append((GUID, {'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}))
meta['m_PreloadTable'].extend(span)
entry = next(v for k,v in meta['m_Container'] if v['asset']['m_PathID'] == MODULE)
module_span = copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for p in span:
    if p not in module_span: module_span.append(p)
entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(module_span))
meta['m_PreloadTable'].extend(module_span)
meta['m_Container'].sort(key=lambda x:x[0])
metaobj.save_typetree(meta)
spec=importlib.util.spec_from_file_location('catalog', R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin'])
loc=oldcat.locations('414d4dc7ae21fca47a2684eb783dd244')[0]
cat=cm.Catalog(oldcat.add_key_location(GUID,loc,loc))
idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GameWorldVisualTreeAssetPreload')
keyobj,locset=cat.key_records[idx]
locs=[a[0] for a in cat.array(locset,'I')]+cat.locations(GUID)
records=list(cat.key_records)
records[idx]=(keyobj,cat.append(b''.join(struct.pack('<I',i) for i in locs),True))
struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*a) for a in records),True))
catout=bytes(cat.data)
newcat=cm.Catalog(catout);newkeys=dict(newcat.keys())
assert set(newkeys)==set(dict(oldcat.keys()))|{GUID}
for key,locset in oldcat.keys():
    assert [a[0] for a in newcat.array(newkeys[key],'I')]==[a[0] for a in oldcat.array(locset,'I')]+(newcat.locations(GUID) if key=='GameWorldVisualTreeAssetPreload' else [])
changed={PID:doc,SID:sheet,MODULE:module,metaobj.path_id:meta}
output=env.file.save(packer='lz4')
check={o.path_id:o for o in UnityPy.load(output).objects}
assert check.keys()==objs.keys()
for i,h in hashes.items():
    if i not in changed:assert sha(check[i].get_raw_data())==h,i
for i,d in changed.items():assert check[i].read_typetree()==d,i
(OUT/W).write_bytes(output)
(OUT/'catalog.bin').write_bytes(catout)
hashout=hashlib.md5(catout).hexdigest().encode('ascii')
(OUT/'catalog.hash').write_bytes(hashout)
(OUT/'content.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
install={GAME/W:output,SKIN/W:output,GAME.parent/'catalog.bin':catout,GAME.parent/'catalog.hash':hashout,SKIN/'catalog.bin':catout}
report={'installed':False,'runtime_verified':False,'card_shell_background_removed':True,'title_and_header_space_removed':True,'native_training_overview_unchanged':True,'all_content_and_bindings_preserved':True,'embedded_content_guid':GUID,'changed_objects':list(changed),'after_sha256':{str(p):sha(b) for p,b in install.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer=list(restore)
for p,b in before.items():
    tag='backup-skin' if p.parent==SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Package changed since preparation.' }")
for p in install:installer.append("Copy-Item -LiteralPath '"+str(OUT/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,b in install.items():p.write_bytes(b)
    for p,b in install.items():assert p.read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'background_removed':True,'title_removed':True}))
