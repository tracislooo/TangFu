"""Use native photo resource availability instead of the kit generator in this panel."""
from pathlib import Path
import ast, copy, datetime, hashlib, json, runpy, struct, subprocess, sys, uuid

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
syntax = ast.parse((R / 'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module([n for n in syntax.body if isinstance(n, ast.FunctionDef) and n.name == 'write'], []), 'codec', 'exec'))
TypeTreeHelper.write_value = write
Catalog = runpy.run_path(str(R / 'catalog-binary-v35.py'))['Catalog']
cfg = json.loads((R / 'current-game-location.json').read_text('utf8'))
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
F = 'ui-visualfunctions_assets_all.bundle'
PID = -991100000000030
NEWPID = -991100000000080
GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27/club-stadium/kunshan-fallback-v1').hex
FALLBACK = 'tf27/club-stadium/fallback/kunshan'
O = R / ('club-stadium-kunshan-fallback-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
O.mkdir()
photo = O / 'kunshan.png'
photo.write_bytes((R / 'kunshan-image-20261118/sources/kunshan.png').read_bytes())
sha = lambda b: hashlib.sha256(b).hexdigest()
tx, audits, protected = [], [], {str(photo): sha(photo.read_bytes())}
zero = {'m_idBytes': [0] * 16}

def stage(tag, path, before, after):
    dst, bak = O / tag / path.name, O / ('backup-' + tag) / path.name
    for p, b in [(dst, after), (bak, before)]:
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(b)
    tx.append(dict(target=str(path), source=str(dst), backup=str(bak), before=sha(before), after=sha(after)))

def find(d, cls):
    return next(r for r in d['references']['RefIds'] if r['type']['class'] == cls)

def graph(base, donors):
    d = copy.deepcopy(base)
    d['m_Name'] = d['m_name'] = 'TFClubStadiumPhotoOrKunshan'
    invoke = find(d, 'InvokeNode')
    refs = d['references']['RefIds']
    refs.remove(invoke)
    d['m_nodes'] = [x for x in d['m_nodes'] if x['rid'] != invoke['rid']]
    entry = find(d, 'EntryNode')['data']
    image = next(s['m_id'] for s in entry['m_dataSockets'] if s['m_name'] == 'ImageElement')
    asstring = find(d, 'TypedValueVisualFunctionLibrary_AsString')['data']['m_dataOutString']['m_id']
    def add(row, label):
        row = copy.deepcopy(row)
        # Remap every socket and node identifier, including its internal references.
        ids = {}
        def collect(v):
            if isinstance(v, dict):
                if set(v) == {'m_idBytes'} and any(v['m_idBytes']):
                    key = tuple(v['m_idBytes'])
                    ids.setdefault(key, list(uuid.uuid5(uuid.NAMESPACE_URL, label + str(key)).bytes_le))
                else:
                    for x in v.values(): collect(x)
            elif isinstance(v, list):
                for x in v: collect(x)
        collect(row['data'])
        def remap(v):
            if isinstance(v, dict):
                if set(v) == {'m_idBytes'} and tuple(v['m_idBytes']) in ids: v['m_idBytes'] = ids[tuple(v['m_idBytes'])]
                else:
                    for x in v.values(): remap(x)
            elif isinstance(v, list):
                for x in v: remap(x)
        remap(row['data'])
        row['data']['m_parentID'] = copy.deepcopy(d['m_id'])
        row['rid'] = max(r['rid'] for r in refs) + 1
        refs.append(row); d['m_nodes'].append({'rid': row['rid']})
        return row['data']
    c1 = add(donors['concat'], 'prefix')
    c2 = add(donors['concat'], 'suffix')
    exists = add(donors['exists'], 'exists')
    branch = add(donors['branch'], 'branch')
    normal = add(donors['set'], 'photo')
    fallback = add(donors['set'], 'kunshan')
    def value(node, field, source=None, default=None):
        node[field]['m_sourceID'] = copy.deepcopy(source or zero)
        if default is not None: node[field]['m_defaultSocketValue'] = {'m_value': default}
    value(c1, 'm_dataInText', default='kit2d_')
    value(c1, 'm_dataInText1', source=asstring)
    value(c2, 'm_dataInText', source=c1['m_dataOutString']['m_id'])
    value(c2, 'm_dataInText1', default='_fmetstadium')
    value(exists, 'm_dataInResourceName', source=c2['m_dataOutString']['m_id'])
    value(branch, 'm_dataInCondition', source=exists['m_dataOutBoolean']['m_id'])
    for node in [normal, fallback]:
        value(node, 'm_target', source=image)
        node['m_dataInResourceGenerationData']['m_sourceID'] = copy.deepcopy(zero)
        node['m_dataInResourceGenerationData']['m_defaultSocketValue'] = {}
        node['m_execOutExecOutput']['m_destinationID'] = copy.deepcopy(zero)
    value(normal, 'm_dataInAddressableID', source=c2['m_dataOutString']['m_id'])
    value(fallback, 'm_dataInAddressableID', default=FALLBACK)
    wait = find(d, 'VisualBindings_Wait')['data']
    wait['m_asyncOutComplete']['m_destinationID'] = c1['m_execInExecInput']['m_id']
    for first, second in [(c1,c2),(c2,exists),(exists,branch)]:
        first['m_execOutExecOutput']['m_destinationID'] = second['m_execInExecInput']['m_id']
    branch['m_execOutTrue']['m_destinationID'] = normal['m_execInExecInput']['m_id']
    branch['m_execOutFalse']['m_destinationID'] = fallback['m_execInExecInput']['m_id']
    # All sources and execution destinations resolve within this private graph.
    ids, links = set(), []
    def validate(v):
        if isinstance(v, dict):
            for k,x in v.items():
                if k == 'm_id' and isinstance(x,dict): ids.add(tuple(x['m_idBytes']))
                elif k in ('m_sourceID','m_destinationID'): links.append(tuple(x['m_idBytes']))
                else: validate(x)
        elif isinstance(v,list):
            for x in v: validate(x)
    validate(d)
    assert all(not any(x) or x in ids for x in links)
    assert len(d['m_nodes']) == len(refs)
    def private_ids(v):
        if isinstance(v,dict):
            if set(v) == {'m_idBytes'} and any(v['m_idBytes']):
                v['m_idBytes'] = list(uuid.uuid5(uuid.NAMESPACE_URL, GUID + str(v['m_idBytes'])).bytes_le)
            else:
                for x in v.values(): private_ids(x)
        elif isinstance(v,list):
            for x in v: private_ids(x)
    private_ids(d)
    return d

for tag, key in [('game','bundle_root'),('skin','skin_packages')]:
    folder = Path(cfg[key]); cp = (folder.parent if tag == 'game' else folder) / 'catalog.bin'
    cb = cp.read_bytes(); cat = Catalog(cb)
    target_bundle = F if (folder/F).exists() else 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
    donorenv = UnityPy.load(str((folder if (folder/F).exists() else Path(cfg['bundle_root']))/F))
    donorobs = {o.path_id:o for o in donorenv.objects}
    fb = (folder/target_bundle).read_bytes(); env = UnityPy.load(fb); af = env.assets[0]
    obs = af.objects; hashes = {i:sha(o.get_raw_data()) for i,o in obs.items()}
    source = next(o for o in donorobs.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'BindSIImage')
    base = source.read_typetree()
    alltrees = [o.read_typetree() for o in donorobs.values() if o.type.name == 'MonoBehaviour']
    rows = [r for d in alltrees for r in d.get('references',{}).get('RefIds',[])]
    donor = lambda cls: next(r for r in rows if r['type']['class'] == cls)
    gd = graph(base, dict(concat=donor('TextFunctions_Concat'), exists=donor('GeneralVisualFunction_ResourceExists'), branch=donor('GeneralVisualFunction_Branch'), set=donor('SIImage_SetImage')))
    assert NEWPID not in obs
    if target_bundle != F:
        needed = {(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in gd['references']['RefIds']}
        known = {(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
        for t in source.assets_file.ref_types:
            k = (t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
            if k in needed and k not in known: af.ref_types.append(copy.copy(t)); known.add(k)
        assert needed <= known
        template = next(o for o in obs.values() if o.type.name == 'MonoBehaviour' and 'm_inputs' in o.read_typetree() and 'm_nodes' in o.read_typetree())
        # VisualFunction script comes from this bundle's own existing function.
        gd['m_Script'] = template.read_typetree()['m_Script']
    else:
        template = source
    clone = copy.copy(template); clone.path_id = NEWPID; clone.data = None; clone._read_until = None
    obs[NEWPID] = clone; clone.save_typetree(gd)
    mo = next(o for o in obs.values() if o.type.name == 'AssetBundle'); meta = mo.read_typetree()
    donormeta = next(o.read_typetree() for o in donorobs.values() if o.type.name == 'AssetBundle')
    sourceguid = next(k for k,v in donormeta['m_Container'] if v['asset'] == dict(m_FileID=0,m_PathID=source.path_id))
    span = len(meta['m_PreloadTable'])
    meta['m_PreloadTable'].extend([gd['m_Script'],dict(m_FileID=0,m_PathID=NEWPID)])
    meta['m_Container'].append((GUID,dict(preloadIndex=span,preloadSize=2,asset=dict(m_FileID=0,m_PathID=NEWPID))))
    meta['m_Container'].sort(key=lambda r:r[0]); mo.save_typetree(meta)
    payload = env.file.save(packer='lz4'); check = {o.path_id:o for o in UnityPy.load(payload).objects}
    assert check[NEWPID].read_typetree() == gd
    assert all(sha(check[i].get_raw_data()) == h for i,h in hashes.items() if i != mo.path_id)
    stage(tag,folder/target_bundle,fb,payload)
    sloc = next(l for l in cat.locations(sourceguid) if cat.location(l)['type'][1] == 'SI.VisualScripting.VisualFunction')
    dependency = sloc
    if target_bundle != F:
        dependency = next(l for k,ls in cat.keys() for l, in cat.array(ls,'I')[:1] if cat.location(l)['dependencies'] and cat.location(cat.location(l)['dependencies'][0])['internal'].endswith(target_bundle))
    cat = Catalog(cat.add_key_location(GUID,sloc,dependency))
    # The fallback reads an archived copy of the user's new kunshan image.
    original_keys = dict(cat.keys()); records = list(cat.key_records)
    stringtype = next(cat.unpack(k,'2I')[0] for k,v in records if isinstance(cat.object(k),str))
    texturetype = next(cat.location(l)['raw'][6] for k,ls in cat.keys() for l, in cat.array(ls,'I')[:1] if cat.location(l)['type'][1] == 'UnityEngine.Texture2D')
    keyoff = cat.add_string(FALLBACK); pathoff = cat.add_string(photo.as_posix())
    loc = cat.append(struct.pack('<7I',keyoff,pathoff,cat.add_string('SI.Core.LocalAssetProvider'),0xffffffff,0,0xffffffff,texturetype))
    obj = cat.append(struct.pack('<IHH',keyoff,0,0))
    records.append((cat.append(struct.pack('<II',stringtype,obj)),cat.append(struct.pack('<I',loc),True)))
    struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*r) for r in records),True))
    cat = Catalog(bytes(cat.data))
    assert cat.location(cat.locations(GUID)[0])['type'][1] == 'SI.VisualScripting.VisualFunction'
    assert cat.location(cat.location(cat.locations(GUID)[0])['dependencies'][0])['internal'].endswith(target_bundle)
    assert cat.location(cat.locations(FALLBACK)[0])['internal'] == photo.as_posix()
    previous = Catalog(cb)
    finalkeys = dict(cat.keys())
    assert all(finalkeys[k] == ls for k,ls in previous.keys())
    stage(tag,cp,cb,bytes(cat.data)); hp = cp.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(bytes(cat.data)).hexdigest().encode('ascii'))
    wb = (folder/W).read_bytes(); we = UnityPy.load(wb); wo = {o.path_id:o for o in we.objects}
    wh = {i:sha(o.get_raw_data()) for i,o in wo.items()}; old = wo[PID].read_typetree(); d = copy.deepcopy(old)
    im = next(r['data'] for r in d['references']['RefIds'] if r.get('data',{}).get('name') == 'ClubOverviewStadiumPackPhoto')
    vf = im['Binding']['m_visualFunction']; assert vf['m_target']['m_guid'] == '7a35874b5cb0acb4d846df3f46c3a872'
    vf['m_target']['m_guid'] = GUID
    kind = b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'; path = b'club.MainTeam.UniqueId'
    args = [bytes([31])+b'SI.Bindable.BindingKeyVisualArg'+b'\0',bytes([len(kind)])+kind+bytes([1,len(path)])+path]
    vf['m_inputs']['m_variable']['m_argumentBytes'] = list(bytes([2])+b''.join(struct.pack('<I',len(a))+a for a in args))
    im['PlaceholderImagePath'] = FALLBACK; im['PlaceholderImagePath_UxmlAttributeFlags'] = 1
    d['m_ContentHash'] += 1
    wo[PID].save_typetree(d); payload = we.file.save(packer='lz4'); checked = {o.path_id:o for o in UnityPy.load(payload).objects}
    assert checked[PID].read_typetree() == d
    assert all(sha(checked[i].get_raw_data()) == h for i,h in wh.items() if i != PID)
    stage(tag,folder/W,wb,payload)
    for bn in ['ui-backgrounds_assets_common.bundle','ui-styles_assets_default.bundle','ui-tileslayouts_assets_all.bundle']:
        p = folder/bn
        if p.exists(): protected[str(p)] = sha(p.read_bytes())
    audits.append(dict(target=tag,private_function_guid=GUID,private_function_path_id=NEWPID,photo_key='kit2d_{club.MainTeam.UniqueId}_fmetstadium',missing_photo=FALLBACK,all_existing_function_objects_unchanged=True,other_vta_objects_unchanged=True,existing_catalog_keys_unchanged=True))
    print('Prepared',tag,flush=True)

manifest = dict(installed=False,runtime_verified=False,request='Replace club stadium kit fallback with kunshan',audits=audits,protected_sha256=protected,desktop_control_used=False)
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(O/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (O/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) {throw 'Operation failed'}\n",'utf-8-sig')
(R/'current-club-stadium-fallback.json').write_text(json.dumps(dict(patch=str(O),installed=False,runtime_verified=False,fallback_source=str(photo),function_guid=GUID),indent=2),'utf8')
print('Patch:',O,flush=True)
result = subprocess.run([sys.executable,str(R/'install-independent-resource-patch.py'),str(O)])
if result.returncode == 0:
    index = json.loads((R/'current-club-stadium-fallback.json').read_text()); index['installed'] = True
    (R/'current-club-stadium-fallback.json').write_text(json.dumps(index,indent=2),'utf8')
sys.exit(result.returncode)
