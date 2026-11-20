"""Add native stadium-name photo binding behind the current stadium-ID layer."""
from collections import defaultdict
from pathlib import Path
import ast, copy, datetime, hashlib, json, re, struct, sys, tempfile
root=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(tempfile.gettempdir())/'fm_stad_zstd'))
import zstandard
helpers_tree=ast.parse((root/'build-club-stadium-overlay-local.py').read_text('utf8'))
head=[]
for entry in helpers_tree.body:
    if isinstance(entry,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pack' for t in entry.targets):break
    head.append(entry)
exec(compile(ast.Module(head,[]),'helpers','exec'),globals())
for entry in helpers_tree.body:
    if isinstance(entry,ast.FunctionDef) and entry.name in ('bundle','stage'):
        exec(compile(ast.Module([entry],[]),'helpers','exec'),globals())
out=root/('club-stadium-native-name-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
pack=Path(json.loads((root/'current-club-overview.json').read_text('utf8'))['stadium_image_pack'])
photos={}
for r in ET.parse(pack/'config.xml').findall('.//record[@to]'):
    m=re.fullmatch(r'graphics/pictures/stadium/(\d+)/background',r.get('to'))
    if m:
        p=(pack/r.get('from')).with_suffix('.jpg')
        assert p.is_file()
        photos[int(m[1])]=p
db=Path(cfg['game_root'])/'shared/data/database/db/2700/2700_fm/lang_db.dat'
raw=db.read_bytes()
frames=[m.start() for m in re.finditer(re.escape(bytes.fromhex('28b52ffd')),raw)]+[len(raw)]
def frame(blob, offsets, index):
    return zstandard.ZstdDecompressor().decompressobj().decompress(blob[offsets[index]:offsets[index+1]])
client=db.with_name('client_db.dat').read_bytes()
client_frames=[m.start() for m in re.finditer(re.escape(bytes.fromhex('28b52ffd')),client)]+[len(client)]
stadiums=frame(client,client_frames,22)
def number(blob,pos):
    return struct.unpack_from('<I',blob,pos)[0]
city_index={}
for i in range(number(stadiums,8)):
    record=12+i*38
    assert number(stadiums,record+27)==i
    sid=number(stadiums,record+31)
    assert sid==number(stadiums,record+35)
    city_index[sid]=number(stadiums,record+5)
names=defaultdict(set)
qualified=defaultdict(set)
for j in range(7,len(frames)-1,16):
    if j==199:  # This localized table uses a different record layout.
        continue
    data=zstandard.ZstdDecompressor().decompressobj().decompress(raw[frames[j]:frames[j+1]])
    u=lambda pos:struct.unpack_from('<I',data,pos)[0]
    assert data.startswith(bytes.fromhex('03017461642e'))
    city_frame=frame(raw,frames,j-4)
    cities=[]
    cp=12
    for _ in range(number(city_frame,8)):
        size=number(city_frame,cp+4)
        cities.append(city_frame[cp+8:cp+8+size].decode('utf8',errors='replace'))
        cp+=10+size
    assert cp==len(city_frame)
    pos=12
    for _ in range(u(8)):
        sid=u(pos)
        pos+=4
        for field in range(2):
            length=u(pos)
            pos+=4
            value=data[pos:pos+length]
            pos+=length
            if value:
                try:name=value.decode('utf8')
                except UnicodeDecodeError:continue
                names[name].add(sid)
                ci=city_index.get(sid,len(cities))
                if ci<len(cities):
                    qualified['tf27/stadium/by-name/'+cities[ci]+'|'+name].add(sid)
        pos+=3
    assert pos==len(data)
aliases={k:next(iter(ids)) for k,ids in qualified.items() if len(ids)==1 and next(iter(ids)) in photos}
assert aliases['tf27/stadium/by-name/巴塞罗那|诺坎普球场']==1040
assert aliases['tf27/stadium/by-name/Denia|Camp Nou']==814096
import uuid
def panel(af):
    pid=-991100000000030
    tree=af.objects[pid].read_typetree()
    image=next(r['data'] for r in tree['references']['RefIds'] if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto')
    bind=image['Binding']['m_visualFunction']['m_inputs']['m_variable']
    assert b'selectedstadium.UniqueId' in bytes(bind['m_argumentBytes'])
    kind=b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
    args=[bytes([len(kind)])+kind+bytes([1,len(path)])+path for path in (b'selectedstadium.City.Name',b'selectedstadium.Name')]
    bind['m_argumentBytes']=list(bytes([2])+b''.join(struct.pack('<I',len(a))+a for a in args))
    return {pid:tree}
def graph(af):
    pid=-991100000000070
    d=af.objects[pid].read_typetree()
    recs=d['references']['RefIds']
    def find(kind):
        return next(r['data'] for r in recs if r['type']['class']==kind)
    def identity(label):
        return {'m_idBytes':list(uuid.uuid5(uuid.NAMESPACE_URL,'tf27/stadium/fullname/'+label).bytes_le)}
    def clone_socket(sock,label):
        item=copy.deepcopy(sock)
        item['m_id']=identity(label)
        return item
    orig=d['m_inputs'][-1]
    new=clone_socket(orig,'input')
    new['m_name']='StadiumName'
    d['m_inputs'].append(new)
    entry=find('EntryNode')['m_dataSockets']
    es=clone_socket(entry[-1],'entry')
    es.update(m_name='StadiumName',m_dataID=new['m_id'])
    entry.append(es)
    bind=find('BindNode')
    inputs=bind['m_dynamicDataInputSockets']
    bs=clone_socket(inputs[0],'bind')
    bs.update(m_name='StadiumName',m_dataID=new['m_id'],m_sourceID=es['m_id'])
    inputs.append(bs)
    outputs=bind['m_outputAsyncExecSocket']['m_dataOutputSockets']
    os=clone_socket(outputs[0],'ready')
    os.update(m_name='StadiumName',m_dataID=new['m_id'])
    outputs.append(os)
    def duplicate(kind,label):
        r=copy.deepcopy(next(r for r in recs if r['type']['class']==kind))
        r['rid']=max(x['rid'] for x in recs)+1
        data=r['data']
        data['m_id']=identity(label)
        for k,v in data.items():
            if isinstance(v,dict) and 'm_id' in v:v['m_id']=identity(label+k)
        recs.append(r)
        d['m_nodes'].append({'rid':r['rid']})
        return data
    pre,sep=[r['data'] for r in recs if r['type']['class']=='TextFunctions_Concat']
    pre['m_dataInText']['m_defaultSocketValue']['m_value']='tf27/stadium/by-name/'
    sep['m_dataInText1']['m_defaultSocketValue']['m_value']='|'
    convert=duplicate('TypedValueVisualFunctionLibrary_AsString','nameText')
    convert['m_dataInValue']['m_sourceID']=os['m_id']
    last=duplicate('TextFunctions_Concat','appendName')
    for r in recs:
        for v in r['data'].values():
            if isinstance(v,dict) and v.get('m_sourceID')==sep['m_dataOutString']['m_id']:
                v['m_sourceID']=last['m_dataOutString']['m_id']
    last['m_dataInText']['m_sourceID']=sep['m_dataOutString']['m_id']
    last['m_dataInText1']['m_sourceID']=convert['m_dataOutString']['m_id']
    last['m_execOutExecOutput']['m_destinationID']=sep['m_execOutExecOutput']['m_destinationID']
    sep['m_execOutExecOutput']['m_destinationID']=last['m_execInExecInput']['m_id']
    return {pid:d}

for tag,folder in [('game',game),('skin',Path(cfg['skin_packages']))]:
    bundle(tag,folder/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',panel)
    bundle(tag,folder/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',graph)
    catpath=(folder.parent if tag=='game' else folder)/'catalog.bin'
    before=catpath.read_bytes()
    c=cm.Catalog(before)
    keys=dict(c.keys())
    old=list(c.key_records)
    records=list(old)
    kind=next(c.unpack(k,'2I')[0] for k,v in old if isinstance(c.object(k),str))
    assert not aliases.keys() & keys.keys()
    count=0
    for name,sid in sorted(aliases.items()):
        if name in keys:continue
        locs=keys['tf27/stadium/id/'+str(sid)+'/background']
        location=c.location(c.array(locs,'I')[0][0])
        assert Path(location['internal'])==photos[sid] and location['type'][1]=='UnityEngine.Texture2D'
        s=c.add_string(name) if name.isascii() else c.append(name.encode('utf-16le'),True)|0x80000000
        obj=c.append(struct.pack('<IHH',s,0,0))
        records.append((c.append(struct.pack('<II',kind,obj)),locs))
        count+=1
    struct.pack_into('<I',c.data,8,c.append(b''.join(struct.pack('<II',*r) for r in records),True))
    result=bytes(c.data)
    check=cm.Catalog(result)
    mapping=dict(check.keys())
    assert check.key_records[:len(old)]==old
    for name,sid in aliases.items():
        if name not in keys:assert mapping[name]==mapping['tf27/stadium/id/'+str(sid)+'/background']
    stage(tag,catpath,before,result)
    hp=catpath.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(result).hexdigest().encode('ascii'))
manifest=dict(installed=False,runtime_verified=False,protected_sha256={},name_aliases=count,stadiums_with_name_match=len(set(aliases.values())),sample={'诺坎普球场':1040},source=str(db),pack=str(pack),binding='selectedstadium.City.Name + selectedstadium.Name',ambiguity='skip identical city and stadium combinations shared by different records')
for n,d in [('transaction',tx),('manifest',manifest)]:
    (out/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(root/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,count,manifest['stadiums_with_name_match'])



