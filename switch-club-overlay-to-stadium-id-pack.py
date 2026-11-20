"""Move the existing stadium overlay to a stadium-ID pack on current assets."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys
import xml.etree.ElementTree as ET
root = Path(__file__).resolve().parent
source = ast.parse((root/'build-club-stadium-overlay-local.py').read_text('utf8'))
# Reuse the established serializer, transaction writer and local texture catalog writer.
prelude = []
for node in source.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='photos' for t in node.targets):
        break
    prelude.append(node)
exec(compile(ast.Module(prelude,[]),'overlay-helpers','exec'),globals())
prefix = 'tf27/stadium/id/'
photos = {}
missing = []
for row in ET.parse(pack/'config.xml').findall('.//record[@to]'):
    match = re.fullmatch(r'graphics/pictures/stadium/(\d+)/background',row.get('to'),re.I)
    if not match:
        continue
    src = (pack/row.attrib['from']).resolve()
    assert src.is_relative_to(pack)
    path = next((f for f in (src,src.with_suffix('.jpg'),src.with_suffix('.png')) if f.suffix.lower() in ('.jpg','.png') and f.is_file()),None)
    if path is None:
        missing.append(row.attrib)
        continue
    key = prefix+match[1]+'/background'
    assert key not in photos or photos[key]==path
    photos[key] = path
assert photos and not missing, missing[:10]
out = root/('club-stadium-id-pack-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
sha = lambda b:hashlib.sha256(b).hexdigest()
tx = []
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('stage','bundle','locations'):
        exec(compile(ast.Module([node],[]),'overlay-helpers','exec'),globals())

def update_path(af):
    pid = -991100000000030
    tree = af.objects[pid].read_typetree()
    photo = next(r['data'] for r in tree['references']['RefIds'] if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto')
    inputs = photo['Binding']['m_visualFunction']['m_inputs']['m_variable']
    old = bytes(inputs['m_argumentBytes'])
    kind = b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
    path = b'club.MainTeam.Stadium.UniqueId'
    arg = bytes([len(kind)])+kind+bytes([1,len(path)])+path
    assert b'club.UniqueId' in old
    inputs['m_argumentBytes'] = list(b'\x01'+struct.pack('<I',len(arg))+arg)
    return {pid:tree}

def update_prefix(af):
    pid = -991100000000070
    tree = af.objects[pid].read_typetree()
    matches = [r['data']['m_dataInText']['m_defaultSocketValue'] for r in tree['references']['RefIds']
               if r['type']['class']=='TextFunctions_Concat' and r['data']['m_dataInText']['m_defaultSocketValue'].get('m_value')=='tf27/stadium/club/']
    assert len(matches)==1
    matches[0]['m_value'] = prefix
    return {pid:tree}

for tag,folder in [('game',game),('skin',Path(cfg['skin_packages']))]:
    bundle(tag,folder/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',update_path)
    bundle(tag,folder/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',update_prefix)
    path = (folder.parent if tag=='game' else folder)/'catalog.bin'
    raw = path.read_bytes()
    result = locations(raw)
    stage(tag,path,raw,result)
    hp = path.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(result).hexdigest().encode('ascii'))

manifest = dict(installed=False,runtime_verified=False,protected_sha256={},provider=provider,
                pack=str(pack),unique_photo_keys=len(photos),binding='club.MainTeam.Stadium.UniqueId',
                prefix=prefix,missing_photo='hide photo only',
                layout='existing stadium photograph under translucent information overlay',
                unrelated_objects_verified=True)
for filename,data in [('transaction',tx),('manifest',manifest)]:
    (out/(filename+'.json')).write_text(json.dumps(data,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(root/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out)
print('Stadium IDs with photos:',len(photos))
