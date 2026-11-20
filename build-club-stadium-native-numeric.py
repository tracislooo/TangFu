"""Use the native BindSIImage function with numerical stadium keys."""
import ast,copy,datetime,hashlib,json,struct,sys
from pathlib import Path
root=Path(__file__).resolve().parent
script=ast.parse((root/'build-club-stadium-overlay-local.py').read_text('utf8'))
head=[]
for n in script.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pack' for t in n.targets):break
    head.append(n)
exec(compile(ast.Module(head,[]),'helpers','exec'),globals())
for n in script.body:
    if isinstance(n,ast.FunctionDef) and n.name in ('bundle','stage'):
        exec(compile(ast.Module([n],[]),'helpers','exec'),globals())
out=root/('club-stadium-native-numeric-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
tx=[]
def edit(af):
    pid=-991100000000030
    d=af.objects[pid].read_typetree()
    rs=d['references']['RefIds']
    sd=next(r['data'] for r in rs if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto')
    v=sd['Binding']['m_visualFunction']
    v['m_target']['m_guid']='41e6b45ba23e8834c8c178c2ae247e6c'
    kind=b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
    path=b'selectedstadium.UniqueId'
    args=[bytes([31])+b'SI.Bindable.BindingKeyVisualArg'+b'\0',bytes([len(kind)])+kind+bytes([1,len(path)])+path]
    v['m_inputs']['m_variable']['m_argumentBytes']=list(bytes([2])+b''.join(struct.pack('<I',len(a))+a for a in args))
    return {pid:d}
for tag,folder in [('game',game),('skin',Path(cfg['skin_packages']))]:
    bundle(tag,folder/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',edit)
    p=(folder.parent if tag=='game' else folder)/'catalog.bin'
    before=p.read_bytes()
    c=cm.Catalog(before)
    keys=dict(c.keys())
    recs=list(c.key_records)
    st=next(c.unpack(k,'2I')[0] for k,v in recs if isinstance(c.object(k),str))
    count=0
    skipped=[]
    for key,locs in keys.items():
        if not isinstance(key,str) or not key.startswith('tf27/stadium/id/'):continue
        sid=key.split('/')[3]
        if sid in keys:
            skipped.append(sid)
            continue
        s=c.add_string(sid)
        o=c.append(struct.pack('<IHH',s,0,0))
        recs.append((c.append(struct.pack('<II',st,o)),locs))
        count+=1
    assert count==7915 and not skipped,(count,skipped)
    struct.pack_into('<I',c.data,8,c.append(b''.join(struct.pack('<II',*r) for r in recs),True))
    check=cm.Catalog(bytes(c.data))
    ck=dict(check.keys())
    assert check.key_records[:len(c.key_records)]==c.key_records
    for key in [k for k in keys if isinstance(k,str) and k.startswith('tf27/stadium/id/')]:
        assert ck[key.split('/')[3]]==keys[key]
    stage(tag,p,before,bytes(c.data))
    hp=p.with_suffix('.hash')
    stage(tag,hp,hp.read_bytes(),hashlib.md5(bytes(c.data)).hexdigest().encode('ascii'))
manifest=dict(installed=False,runtime_verified=False,protected_sha256={},stadiums=7915,binding='selectedstadium.UniqueId',function='native BindSIImage',numeric_keys=True,name_matching=False)
for n,d in [('transaction',tx),('manifest',manifest)]:
    (out/(n+'.json')).write_text(json.dumps(d,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(root/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out)
