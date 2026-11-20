"""Reapply only the staff hover portrait subtree to the current game bundle."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, os, subprocess, sys, uuid

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

loc = json.loads((R/'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PID = -1465827634544911600
sha = lambda b: hashlib.sha256(b).hexdigest()
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT = R/('staff-hover-current-direct-portrait-'+stamp)
OUT.mkdir()
oldwrite = TypeTreeHelper.write_value
helpers = ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name=='write' or isinstance(n, ast.ClassDef) and n.name=='Styles'], type_ignores=[]), 'portrait-codec', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
sp = importlib.util.spec_from_file_location('catalog', R/'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(sp); sp.loader.exec_module(cm)
before = {p/W:(p/W).read_bytes() for p in [GAME, SKIN]}
protected = {p:sha(p.read_bytes()) for f in [GAME, SKIN] for p in f.glob('*.bundle') if p != GAME/W}
for f in [GAME.parent, SKIN]:
    for name in ['catalog.bin','catalog.hash']:
        protected[f/name] = sha((f/name).read_bytes())
source_env = UnityPy.load(before[SKIN/W])
source_objects = {o.path_id:o for o in source_env.objects}
source_doc = source_objects[PID].read_typetree()
sr = {r['rid']:r for r in source_doc['references']['RefIds']}
source_style = source_objects[source_doc['inlineSheet']['m_PathID']].read_typetree()
def data(rr, i):
    return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
source_root = next(i for i in sr if data(sr,i).get('name')=='StaffPortraitResourceBinding')
source_ids = []
def descend(i):
    source_ids.append(i)
    sd = sr[i]['data']['m_SerializedData']['rid']
    source_ids.append(sd)
    for c in sr[i]['data']['m_Children']: descend(c['rid'])
descend(source_root)
assert len(source_ids)==6
source_image = next(sr[i]['data'] for i in source_ids if sr[i]['type']['class']=='SIImage/UxmlSerializedData')
assert source_image['Binding']['m_visualFunction']['m_target']['m_guid']=='6579775e848422d42a8a5ab277ded932'
source_vars = data(sr,source_root)['ValueVariables']
assert 'person.UniqueId' in source_vars[0]['m_scopeValue']['m_serializedData']

env = UnityPy.load(before[GAME/W]); obs = {o.path_id:o for o in env.objects}
hashes = {i:sha(o.get_raw_data()) for i,o in obs.items()}
ob = obs[PID]; d = ob.read_typetree(); original = copy.deepcopy(d)
rr = {r['rid']:r for r in d['references']['RefIds']}
assert rr[1024]['data']['m_TemplateAlias']=='PersonPicture', 'Current target changed; inspect before patching'
style_obj = obs[d['inlineSheet']['m_PathID']]; style = style_obj.read_typetree()
old_style = copy.deepcopy(style)
old_root = rr[1024]; parent = old_root['data']['m_Parent']['rid']
old_sd = old_root['data']['m_SerializedData']['rid']
next_rid = max(rr)+1
ridmap = {i:next_rid+j for j,i in enumerate(source_ids)}
next_element = max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
elementmap = {sr[i]['data']['m_Id']:next_element+j for j,i in enumerate(source_ids) if 'm_Id' in sr[i].get('data',{})}
def remap(v):
    if isinstance(v,dict):
        if set(v)=={'rid'}: return {'rid':ridmap.get(v['rid'],v['rid'])}
        return {k:remap(x) for k,x in v.items()}
    if isinstance(v,list): return [remap(x) for x in v]
    return v
rules = {}
for i in source_ids:
    row = remap(copy.deepcopy(sr[i])); row['rid'] = ridmap[i]
    a = row.get('data',{})
    for key in ['m_Id','uxmlAssetId']:
        if key in a: a[key] = elementmap[a[key]]
    ix = a.get('m_RuleIndex',-1)
    if ix>=0:
        if ix not in rules:
            rule = copy.deepcopy(source_style['m_Rules'][ix]); rule['m_ComplexSelectors'] = []
            for prop in rule['m_Properties']:
                for handle in prop['m_Values']:
                    if handle['m_ValueType'] in poolmap:
                        pool = poolmap[handle['m_ValueType']]
                        value = copy.deepcopy(source_style[pool][handle['valueIndex']])
                        if pool=='assets': assert value['m_PathID']==0, 'Unexpected external image pointer'
                        handle['valueIndex'] = len(style[pool]); style[pool].append(value)
            rules[ix] = len(style['m_Rules']); style['m_Rules'].append(rule)
        a['m_RuleIndex'] = rules[ix]
    rr[row['rid']] = row
root = ridmap[source_root]
rr[root]['data']['m_Parent'] = {'rid':parent}
rr[parent]['data']['m_Children'] = [{'rid':root} if c['rid']==1024 else c for c in rr[parent]['data']['m_Children']]
del rr[1024]; del rr[old_sd]
d['references']['RefIds'] = list(rr.values())
d['m_ContentHash'] += 1
assert data(rr,root)['ValueVariables']==source_vars
assert next(data(rr,i) for i in ridmap.values() if rr[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIImage')['Binding']==source_image['Binding']
for i,row in {r['rid']:r for r in original['references']['RefIds']}.items():
    if i in [1024,old_sd]: continue
    actual = copy.deepcopy(rr[i])
    if i==parent: actual['data']['m_Children'] = row['data']['m_Children']
    assert actual==row, ('Unrelated staff data changed',i)
visited, element_ids = set(), set()
def walk(i):
    assert i not in visited; visited.add(i); a=rr[i]['data']
    assert a['m_Id'] not in element_ids; element_ids.add(a['m_Id'])
    sd=a.get('m_SerializedData',{}).get('rid',-2)
    if sd!=-2: assert rr[sd]['data']['uxmlAssetId']==a['m_Id']
    for child in a['m_Children']:
        assert rr[child['rid']]['data']['m_Parent']=={'rid':i}; walk(child['rid'])
walk(d['m_VisualTree']['rid'])
assert all(i in visited for i,r in rr.items() if 'm_Parent' in r.get('data',{}))

# Resolve the actual hover and image function registrations without altering catalogs.
catalog_audits=[]
for tag,folder,objects in [('game',GAME,obs),('skin',SKIN,source_objects)]:
    meta=next(o.read_typetree() for o in objects.values() if o.type.name=='AssetBundle')
    guid=next(k for k,v in meta['m_Container'] if v['asset']['m_FileID']==0 and v['asset']['m_PathID']==PID)
    cat=cm.Catalog(((folder.parent if tag=='game' else folder)/'catalog.bin').read_bytes())
    keys=dict(cat.keys())
    def locations(key): return [i for (i,) in cat.array(keys[key],'I')]
    vtas=[i for i in locations(guid) if cat.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset']
    assert len(vtas)==1
    assert cat.location(cat.location(vtas[0])['dependencies'][0])['internal'].endswith(W)
    assert vtas[0] in locations('GameWorldVisualTreeAssetPreload')
    vf=[i for i in locations('6579775e848422d42a8a5ab277ded932') if cat.location(i)['type'][1]=='SI.VisualScripting.VisualFunction']
    assert vf
    catalog_audits.append({'variant':tag,'hover_guid':guid,'vta_type_and_owner_valid':True,'hover_preload_valid':True,'native_image_function_registered':True})
ob.save_typetree(d); style_obj.save_typetree(style)
payload=env.file.save(packer='lz4')
check={o.path_id:o for o in UnityPy.load(payload).objects}
assert set(check)==set(obs)
changed={PID:d,style_obj.path_id:style}
for i,o in check.items():
    if i in changed: assert o.read_typetree()==changed[i]
    else: assert sha(o.get_raw_data())==hashes[i],i
backup=OUT/'backup-game'/W; backup.parent.mkdir(); backup.write_bytes(before[GAME/W])
(OUT/W).write_bytes(payload)
(OUT/'before-hover.json').write_text(json.dumps(original,ensure_ascii=False,indent=2),'utf8')
(OUT/'after-hover.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
report={'installed':False,'runtime_verified':False,'desktop_control_used':False,'cause_evidence':'Game hover reverted to original shared PersonPicture and thumbnail class; independent skin retains direct native resource portrait fix.', 'changed_objects':[PID,style_obj.path_id], 'size':[180,180],'skin_already_has_direct_portrait':True,'native_person_resource_variables_and_function_preserved':True,'unrelated_game_objects_byte_identical':True,'catalog_checks':catalog_audits,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
tx=[{'target':str(GAME/W),'source':str(OUT/W),'backup':str(backup),'before':sha(before[GAME/W]),'after':sha(payload)}]
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
proc=subprocess.run([sys.executable,str(OUT/'installer.py'),str(OUT)],capture_output=True,text=True)
print(proc.stdout); print(proc.stderr)
assert proc.returncode==0,'Patch prepared but installation did not complete'
(R/'current-staff-hover-portrait.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'installed':True,'runtime_verified':False,'portrait':'direct native resource binding','size':[180,180]},ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'modified_game_objects':2,'skin_unchanged':True,'runtime_verified':False},ensure_ascii=True))
