from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,zlib
R=Path(__file__).resolve().parent
exec((R/'apply-page-background-tf-v1-opaque.py').read_text('utf8').split('out = R /')[0])
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
source=ast.parse((R/'update-ledger-bundle-crcs.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='crc'],type_ignores=[]),'<crc>','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
alpha=struct.unpack('<f',struct.pack('<f',.7))[0]
out=R/('navigation-background70-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
before={};payloads={};protected={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
    path=folder/W;raw=path.read_bytes();before[path]=raw
    env=UnityPy.load(raw);objects={o.path_id:o for o in env.objects};expected={};edits=[]
    for ob in objects.values():
        if ob.type.name!='MonoBehaviour':continue
        name=ob.peek_name()
        if name not in ['PrimaryNavigationBar','SecondaryNavigationBar']:continue
        doc=ob.read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']}
        rid=1002 if name=='PrimaryNavigationBar' else 1001
        sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree();old=copy.deepcopy(sheet)
        node=rr[rid]['data'];rule=sheet['m_Rules'][node['m_RuleIndex']]
        prop=next(p for p in rule['m_Properties'] if p['m_Id']==458752)
        handle,=prop['m_Values'];assert handle['m_ValueType']==4
        prev=sheet['colors'][handle['valueIndex']]
        newcolor=dict(prev,a=alpha);sheet['colors'].append(newcolor);handle['valueIndex']=len(sheet['colors'])-1
        verification=copy.deepcopy(sheet);verification['colors']=old['colors']
        verification['m_Rules'][node['m_RuleIndex']]=old['m_Rules'][node['m_RuleIndex']]
        assert verification==old
        expected[sid]=sheet
        edits.append(dict(template=name,node=rid,before=prev,after=newcolor))
    assert len(edits)==2
    for pid,tree in expected.items():objects[pid].save_typetree(tree)
    packed=env.file.save(packer='lz4')
    check={o.path_id:o for o in UnityPy.load(packed).objects}
    original={o.path_id:o for o in UnityPy.load(raw).objects}
    assert set(check)==set(original)
    for pid,ob in check.items():
        if pid in expected:assert ob.read_typetree()==expected[pid]
        else:assert ob.get_raw_data()==original[pid].get_raw_data(),pid
    payloads[path]=packed
    catroot=GAME.parent if tag=='game' else SKIN;cp=catroot/'catalog.bin';hp=catroot/'catalog.hash'
    before[cp]=cp.read_bytes();before[hp]=hp.read_bytes();cat=cm.Catalog(before[cp])
    locations={q for _,ls in cat.keys() for q, in cat.array(ls,'I')}
    records=[]
    for q in locations:
        v=cat.location(q)
        if not v['type'][1].endswith('IAssetBundleResource') or not v['internal'].replace('\\','/').endswith('/'+W):continue
        extra=v['raw'][5]
        if extra==cm.NULL:
            assert tag=='skin'
            continue
        typ,p=cat.unpack(extra,'2I');assert cat.typename(typ)[1].endswith('AssetBundleRequestOptions')
        options=list(cat.unpack(p,'5I'));options[2:4]=[crc(packed),len(packed)]
        opts=cat.append(struct.pack('<5I',*options));newextra=cat.append(struct.pack('<2I',typ,opts))
        struct.pack_into('<I',cat.data,q+20,newextra)
        assert cat.unpack(cat.unpack(cat.location(q)['raw'][5],'2I')[1],'5I')[2:4]==(crc(packed),len(packed))
        records.append(q)
    if tag=='game':assert records
    if bytes(cat.data)!=before[cp]:
        payloads[cp]=bytes(cat.data);payloads[hp]=hashlib.md5(payloads[cp]).hexdigest().encode('ascii')
    for p in list(folder.glob('*.bundle'))+[cp,hp]:
        if p not in payloads and p.exists():protected[str(p)]=sha(p.read_bytes())
    reports.append(dict(target=tag,edits=edits,catalog_bundle_options_updated=len(records)))
    print(tag,'2 navigation backgrounds verified',flush=True)
statepath=R/'current-ui-surface-theme.json';before[statepath]=statepath.read_bytes()
state=json.loads(before[statepath]);state['navigation_backgrounds']={'primary_opacity':.7,'secondary_tab_opacity':.7,'install_record':str(out/'manifest.json'),'runtime_verified':False}
payloads[statepath]=json.dumps(state,ensure_ascii=False,indent=2).encode('utf8')
out.mkdir();tx=dict(game=str(GAME),skin=str(SKIN),workspace=str(R),sources={},before={})
for path,data in payloads.items():
    assert path.read_bytes()==before[path],('Concurrent change',path)
    tag='game' if path.parent in [GAME,GAME.parent] else 'skin' if path.parent==SKIN else 'workspace'
    dst=out/tag/path.name;bak=out/('backup-'+tag)/path.name
    for p,b in [(dst,data),(bak,before[path])]:
        p.parent.mkdir(exist_ok=True);p.write_bytes(b)
    tx['sources'][str(path)]=str(dst);tx['before'][str(path)]=str(bak)
manifest=dict(installed=False,runtime_verified=False,reports=reports,protected_sha256=protected,
    before_sha256={str(p):sha(before[p]) for p in payloads},after_sha256={str(p):sha(b) for p,b in payloads.items()})
for name,d in [('manifest.json',manifest),('transaction.json',tx),('verification.json',{'passed':True,'runtime_verified':False})]:
    (out/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install.ps1',''),('restore.ps1','--restore')]:
    (out/name).write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' "+flag+"\n",'utf8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
(R/'pending-navigation-background70.json').write_text(json.dumps(dict(patch=str(out))),'utf8')
print(out)
