"""Expose the native club overview team and tactic contexts to the XI scores."""
import ast,copy,datetime,hashlib,json,struct,sys
from pathlib import Path

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
def defs(file,names):
    for n in ast.parse((R/file).read_text('utf8')).body:
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names:
            exec(compile(ast.Module([n],[]),file,'exec'),globals())
defs('add-card-six-ratings.py',{'write','validate_ui'})
defs('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
defs('build-club-stadium-overlay-local.py',{'stage'})
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
out=R/('club-starting-xi-context-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
def args(raw):
    data=bytes(raw)
    i=1
    for _ in range(data[0]):
        size=struct.unpack_from('<I',data,i)[0]
        yield data[i+4:i+4+size]
        i+=4+size
    assert i==len(data)
def path_arg(text):
    t=b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
    p=text.encode('ascii')
    return bytes([len(t)])+t+bytes([1,len(p)])+p
for tag,folder in [('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
    path=folder/G
    before=path.read_bytes()
    env=UnityPy.load(before)
    af=env.assets[0]
    world=UnityPy.load(str(folder/W))
    objs={G:af.objects,W:world.assets[0].objects}
    top=Doc(G,pid=-991100000000000)
    overview=Doc(W,pid=-991100000000060)
    native=overview.data(1007)['Mappings']
    mappings=[copy.deepcopy(x) for x in native if x['from'] in ('team','tactic')]
    assert [(x['from'],x['to']['m_path']) for x in mappings]==[('team','club.MainTeam'),('tactic','team.Tactic')]
    wrapper=top.add(overview,1007,1006,'ClubOverviewStartingXIContext')
    top.data(wrapper)['Mappings']=mappings
    top.st(wrapper,[(131083,top.enum('row')),(131085,top.num(0)),(131074,top.enum('center'))])
    box=top.named('ClubOverviewStartingXIScores')
    top.move(box,wrapper)
    setters=top.data(box)['BindFunction']
    assert len(setters)==11
    for index,ref in enumerate(setters):
        var=ref['m_inputs']['m_variable']
        parts=list(args(var['m_argumentBytes']))
        assert parts[0]==path_arg('club.MainTeam.Tactic.TacticalPositions')
        assert parts[1]==path_arg(f'xiSlot{index+1}')
        assert struct.unpack('<i',parts[2][-4:])[0]==index
        parts[0]=path_arg('tactic.TacticalPositions')
        var['m_argumentBytes']=list(bytes([len(parts)])+b''.join(struct.pack('<I',len(p))+p for p in parts))
    validate_ui(top.d,top.s)
    changed={top.obj.path_id:top.d,top.sid:top.s}
    hashes={pid:sha(o.get_raw_data()) for pid,o in af.objects.items()}
    for pid,t in changed.items():af.objects[pid].save_typetree(t)
    after=env.file.save(packer='lz4')
    check=UnityPy.load(after).assets[0].objects
    assert set(check)==set(hashes)
    for pid,o in check.items():
        if pid in changed:assert o.read_typetree()==changed[pid]
        else:assert sha(o.get_raw_data())==hashes[pid]
    stage(tag,path,before,after)
for n,d in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},context='club.MainTeam -> team.Tactic -> tactic.TacticalPositions',changed='two private header objects per bundle'))]:
    (out/(n+'.json')).write_text(json.dumps(d,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)
