from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,sys,zlib
R=Path(__file__).resolve().parent
exec((R/'apply-page-background-tf-v1-opaque.py').read_text('utf8').split('out = R /')[0])
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
source=ast.parse((R/'update-ledger-bundle-crcs.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='crc'],type_ignores=[]),'<crc>','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
alpha=struct.unpack('<f',struct.pack('<f',.7))[0]
out=R/('navigation-native-foreground-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
before={};payloads={};protected={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
    path=folder/W;raw=path.read_bytes();before[path]=raw
    env=UnityPy.load(raw);objects={o.path_id:o for o in env.objects};expected={};edits=[]


    baseline=Path(json.loads((R/'current-game-update-comparison.json').read_text('utf8'))['archive'])
    nativeworld=UnityPy.load(str(next(baseline.rglob(W))))
    native_doc=next(o.read_typetree() for o in nativeworld.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PrimaryNavigationBar')
    nr={r['rid']:r for r in native_doc['references']['RefIds']}
    for ob in objects.values():
        if ob.type.name!='MonoBehaviour' or ob.peek_name()!='PrimaryNavigationBar':continue
        doc=ob.read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']}
        for rid in [1004,1011]:
            sd=rr[rr[rid]['data']['m_SerializedData']['rid']]['data']
            native_sd=nr[nr[rid]['data']['m_SerializedData']['rid']]['data']
            for key in ['BindFunction','BindFunction_UxmlAttributeFlags','PrimaryColorDataLink','SecondaryColorDataLink','PrimaryColorDataLink_UxmlAttributeFlags','SecondaryColorDataLink_UxmlAttributeFlags']:
                sd[key]=copy.deepcopy(native_sd[key])
        rr[1002]['data']['m_Classes']=[c for c in rr[1002]['data']['m_Classes'] if c not in ['nav-on-light','nav-on-dark']]
        for r in rr.values():
            a=r.get('data',{})
            if 'm_Classes' not in a:continue
            a['m_Classes']=list(a['m_Classes'])
            sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
            if sd.get('name') in ['HeaderHolidayDate','HeaderHolidayCustomDate']:
                if 'global-text-primary' not in a['m_Classes']:a['m_Classes'].append('global-text-primary')
        expected[ob.path_id]=doc
    stylepath=folder/'ui-styles_assets_default.bundle'
    before[stylepath]=stylepath.read_bytes()
    se=UnityPy.load(before[stylepath]);so={o.path_id:o for o in se.objects}
    ob=next(o for o in so.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
    sheet=ob.read_typetree();old=copy.deepcopy(sheet);removed=0
    for rule in sheet['m_Rules']:
        text=json.dumps(rule['m_ComplexSelectors'])
        if any(c in text for c in ['MainNav','fm27-fixed-nav-ink','fm27-holiday-']):
            ps=rule['m_Properties'];rule['m_Properties']=[p for p in ps if p['m_Id'] not in [65536,196610]]
            removed+=len(ps)-len(rule['m_Properties'])
    native_sheet=next(o.read_typetree() for o in UnityPy.load(str(next(baseline.rglob('ui-styles_assets_default.bundle')))).objects if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
    added=0
    for rule in native_sheet['m_Rules']:
        props=[copy.deepcopy(p) for p in rule['m_Properties'] if p['m_Id'] in [65536,196610]]
        if not props:continue
        selectors=[copy.deepcopy(c) for c in rule['m_ComplexSelectors'] if any(any(k in p['m_Value'].lower() for k in ['nav','portal','nd-','calendar','button','global-text','dropdown','white']) for t in c['m_Selectors'] for p in t['m_Parts'])]
        if not selectors:continue
        for prop in props:
            for h in prop['m_Values']:
                if h['m_ValueType'] in poolmap:
                    pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(native_sheet[pool][h['valueIndex']]))
                    h['valueIndex']=len(sheet[pool])-1
        idx=len(sheet['m_Rules'])
        for c in selectors:
            c['m_Selectors'][0]['m_PreviousRelationship']=2
            c['m_Selectors'].insert(0,{'m_Parts':[{'m_Value':'MainNav','m_Type':6}],'m_PreviousRelationship':0})
            c['ruleIndex']=idx;c['m_Specificity']+=30000
        sheet['m_Rules'].append({'m_ComplexSelectors':selectors,'m_Properties':props,'line':-1});added+=1
    # New holiday controls follow the same native primary text variable as navigation.
    src=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selectors>','exec'))
    nativeprop=next(p for r in native_sheet['m_Rules'] for p in r['m_Properties'] if p['m_Id']==65536 and any(h['m_ValueType']==8 and native_sheet['strings'][h['valueIndex']]=='--global-text-primary' for h in p['m_Values']))
    prop=copy.deepcopy(nativeprop)
    for h in prop['m_Values']:
        if h['m_ValueType'] in poolmap:
            pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(native_sheet[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    idx=len(sheet['m_Rules'])
    sels=[selector(t,idx) for t in ['#MainNav .fm27-holiday-date SIText','#MainNav .fm27-holiday-custom-date SIText']]
    for c in sels:c['m_Specificity']+=31000
    sheet['m_Rules'].append({'m_ComplexSelectors':sels,'m_Properties':[prop],'line':-1})
    ob.save_typetree(sheet);stylebytes=se.file.save(packer='lz4')
    saved={o.path_id:o for o in UnityPy.load(stylebytes).objects}
    for original in UnityPy.load(before[stylepath]).objects:
        if original.path_id==ob.path_id:assert saved[original.path_id].read_typetree()==sheet
        else:assert saved[original.path_id].get_raw_data()==original.get_raw_data()
    payloads[stylepath]=stylebytes
    edits.append(dict(native_foreground_rules=added,removed_fixed_color_properties=removed,native_foreground_bindings_restored=True))
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
        if not v['type'][1].endswith('IAssetBundleResource') or v['internal'].replace('\\','/').split('/')[-1] not in [W,'ui-styles_assets_default.bundle']:continue
        extra=v['raw'][5]
        if extra==cm.NULL:
            assert tag=='skin'
            continue
        requestdata=packed if v['internal'].replace('\\','/').endswith('/'+W) else stylebytes
        typ,p=cat.unpack(extra,'2I');assert cat.typename(typ)[1].endswith('AssetBundleRequestOptions')
        options=list(cat.unpack(p,'5I'));options[2:4]=[crc(requestdata),len(requestdata)]
        opts=cat.append(struct.pack('<5I',*options));newextra=cat.append(struct.pack('<2I',typ,opts))
        struct.pack_into('<I',cat.data,q+20,newextra)
        assert cat.unpack(cat.unpack(cat.location(q)['raw'][5],'2I')[1],'5I')[2:4]==(crc(requestdata),len(requestdata))
        records.append(q)
    if tag=='game':assert records
    if bytes(cat.data)!=before[cp]:
        payloads[cp]=bytes(cat.data);payloads[hp]=hashlib.md5(payloads[cp]).hexdigest().encode('ascii')
    for p in list(folder.glob('*.bundle'))+[cp,hp]:
        if p not in payloads and p.exists():protected[str(p)]=sha(p.read_bytes())
    reports.append(dict(target=tag,edits=edits,catalog_bundle_options_updated=len(records)))
    print(tag,'2 navigation backgrounds verified',flush=True)
statepath=R/'current-ui-surface-theme.json';before[statepath]=statepath.read_bytes()
state=json.loads(before[statepath]);state['navigation_backgrounds'].update(foreground_colors='native theme and club bindings',added_text_colors='native navigation primary',foreground_install_record=str(out/'manifest.json'),runtime_verified=False)
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
(R/'pending-navigation-native-foreground.json').write_text(json.dumps(dict(patch=str(out))),'utf8')
print(out)
