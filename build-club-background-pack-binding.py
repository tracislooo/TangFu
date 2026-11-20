"""Prepare a reversible Club Overview binding for club-ID background packs."""
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
def load_helpers(filename, names):
    tree = ast.parse((ROOT / filename).read_text('utf8'))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(functions, []), filename, 'exec'), globals())

load_helpers('redesign-card-top-info-foot.py', {'write'})
TypeTreeHelper.write_value = write
load_helpers('build-match-ui-avatars-layout.py', {'import_types'})
spec = importlib.util.spec_from_file_location('catalog', ROOT / 'catalog-binary-v35.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)
cfg = json.loads((ROOT / 'current-game-location.json').read_text('utf8'))
game = Path(cfg['bundle_root'])
world = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
global_ui = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
source = UnityPy.load(str(game / 'ui-visualfunctions_assets_all.bundle')).assets[0]
name = 'ClubOverviewLoadClubBackground'
guid = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/' + name).hex
pid = -991100000000070
assert pid not in {int(x['path_id']) for x in json.loads((ROOT/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
def guid_ref(label):
    return {'m_idBytes': list(uuid.uuid5(uuid.NAMESPACE_URL, guid + '/' + label).bytes_le)}

def function(label):
    return next(o for o in source.objects.values() if o.peek_name() == label).read_typetree()

def nodes(tree):
    return {r['type']['class']: r for r in tree['references']['RefIds']}

def build_graph():
    graph = function('BindToDatabaseObjectImage')
    graph['m_Name'] = graph['m_name'] = name
    graph['m_id'] = guid_ref('function')
    graph['m_inputs'] = [x for x in graph['m_inputs'] if x['m_name'] in ('BindingBag','Image','Binding')]
    for item in graph['m_inputs']:
        item['m_parentID'] = graph['m_id']
    graph['m_variables'] = []
    old = nodes(graph)
    keep = ['EntryNode','BindNode','VisualDataGetterNode','SIImage_ClearImage','SIImage_SetImage']
    records = [old[k] for k in keep]
    entry, bind, getter, clear, show = [r['data'] for r in records]
    entry['m_dataSockets'] = [s for s in entry['m_dataSockets'] if s['m_name'] in ('BindingBag','Image','Binding')]
    def new_node(src, kind, label):
        record = copy.deepcopy(nodes(function(src))[kind])
        record['rid'] = max(r['rid'] for r in records) + 1
        data = record['data']
        data['m_id'] = guid_ref(label)
        for k,socket in data.items():
            if isinstance(socket,dict) and 'm_id' in socket:
                socket['m_id'] = guid_ref(label + '/' + k)
        records.append(record)
        return data
    convert = new_node('FormatAsString','TypedValueVisualFunctionLibrary_AsString','clubIdText')
    prefix = new_node('BindSITextAndSubString','TextFunctions_Concat','prefix')
    suffix = new_node('BindSITextAndSubString','TextFunctions_Concat','suffix')
    zero = {'m_idBytes':[0]*16}
    def link(out, dest):
        out['m_destinationID'] = dest['m_id']
    def wire(inp, out):
        inp['m_sourceID'] = out['m_id']
    def constant(inp, value):
        inp['m_sourceID'] = zero
        inp['m_defaultSocketValue']['m_value'] = value
    ready = bind['m_outputAsyncExecSocket']
    wire(convert['m_dataInValue'], ready['m_dataOutputSockets'][0])
    constant(prefix['m_dataInText'], 'graphics/pictures/club/')
    wire(prefix['m_dataInText1'], convert['m_dataOutString'])
    wire(suffix['m_dataInText'], prefix['m_dataOutString'])
    constant(suffix['m_dataInText1'], '/background')
    wire(show['m_dataInAddressableID'], suffix['m_dataOutString'])
    link(ready, clear['m_execInExecInput'])
    link(clear['m_execOutExecOutput'], prefix['m_execInExecInput'])
    link(prefix['m_execOutExecOutput'], suffix['m_execInExecInput'])
    link(suffix['m_execOutExecOutput'], show['m_execInExecInput'])
    for r in records:
        r['data']['m_parentID'] = graph['m_id']
    graph['m_nodes'] = [{'rid':r['rid']} for r in records]
    graph['references']['RefIds'] = records
    def walk(x):
        if isinstance(x,dict):
            yield x
            for v in x.values(): yield from walk(v)
        if isinstance(x,list):
            for v in x: yield from walk(v)
    ids = {bytes(v['m_id']['m_idBytes']) for v in walk(graph) if isinstance(v.get('m_id'),dict)}
    for v in walk(graph):
        for k in ('m_sourceID','m_destinationID','m_dataID','m_parentID'):
            if k in v: assert bytes(v[k]['m_idBytes']) in ids | {bytes(16)}, (v,k)
    return graph

sha = lambda b: hashlib.sha256(b).hexdigest()
out = ROOT / ('club-stadium-pack-by-club-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx = []
def stage(tag, path, before, after):
    saved = out / tag / path.name
    backup = out / ('backup-' + tag) / path.name
    for dest, data in [(saved,after),(backup,before)]:
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(data)
    tx.append(dict(target=str(path),source=str(saved),backup=str(backup),before=sha(before),after=sha(after)))

for tag, folder in [('game', game), ('skin', Path(cfg['skin_packages']))]:
    catpath = (folder.parent if tag=='game' else folder) / 'catalog.bin'
    catraw = catpath.read_bytes()
    cat = catalog.Catalog(catraw)
    for bundle in (global_ui, world):
        path = folder / bundle
        before = path.read_bytes()
        env = UnityPy.load(before)
        af = env.assets[0]
        obs = af.objects
        hashes = {i:sha(o.get_raw_data()) for i,o in obs.items()}
        metaobj = next(o for o in obs.values() if o.type.name=='AssetBundle')
        meta = metaobj.read_typetree()
        changes = {}
        if bundle == global_ui:
            donor = obs[-940000000000100]
            graph = build_graph()
            import_types(source,af,graph['references']['RefIds'])
            graph['m_Script'] = donor.read_typetree()['m_Script']
            assert pid not in obs
            obj = copy.copy(donor)
            obj.path_id = pid
            obj.data = obj._read_until = None
            obs[pid] = obj
            obj.save_typetree(graph)
            changes[pid] = graph
            key, base = next((k,v) for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':donor.path_id})
            pointer = {'m_FileID':0,'m_PathID':pid}
            span = [graph['m_Script'],pointer]
            meta['m_Container'].append((guid,dict(asset=pointer,preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span))))
            meta['m_Container'].sort(key=lambda kv:kv[0])
            meta['m_PreloadTable'].extend(span)
            metaobj.save_typetree(meta)
            changes[metaobj.path_id] = meta
            loc = next(i for i in cat.locations(key) if cat.location(i)['type'][1]=='SI.VisualScripting.VisualFunction')
            cat = catalog.Catalog(cat.add_key_location(guid,loc,loc))
            owner = cat.location(cat.locations(guid)[0])['dependencies'][0]
            assert cat.location(owner)['internal'].endswith(global_ui)
        else:
            panel = obs[-991100000000030]
            tree = panel.read_typetree()
            image = next(r['data'] for r in tree['references']['RefIds'] if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto')
            binding = image['Binding']['m_visualFunction']
            assert binding['m_target']['m_guid']=='fd76d979673356a4b899f1075077317f'
            path_type = b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
            club = b'club.UniqueId'
            arg = bytes([len(path_type)])+path_type+bytes([1,len(club)])+club
            binding['m_target']['m_guid'] = guid
            binding['m_inputs']['m_variable']['m_argumentBytes'] = list(b'\x01'+struct.pack('<I',len(arg))+arg)
            panel.save_typetree(tree)
            changes[panel.path_id] = tree
            key = next(k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':panel.path_id})
            loc = cat.locations(key)[0]
            deps = cat.location(loc)['dependencies']
            if owner not in deps:
                data = b''.join(struct.pack('<I',d) for d in deps+[owner])
                idx = cat.append(data,True)
                struct.pack_into('<II',cat.data,loc+12,idx,zlib.crc32(data))
            assert owner in cat.location(loc)['dependencies']
        after = env.file.save(packer='lz4')
        check = UnityPy.load(after).assets[0].objects
        assert set(check)==set(obs)
        for i,tr in changes.items(): assert check[i].read_typetree()==tr
        for i,h in hashes.items():
            if i not in changes: assert sha(check[i].get_raw_data())==h
        stage(tag,path,before,after)
    produced = bytes(cat.data)
    stage(tag,catpath,catraw,produced)
    hp = catpath.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(produced).hexdigest().encode('ascii'))
for n,v in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},binding='club.UniqueId',key='graphics/pictures/club/<id>/background',function_guid=guid,unrelated_objects_verified=True))]:
    (out/(n+'.json')).write_text(json.dumps(v,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(ROOT/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out)


