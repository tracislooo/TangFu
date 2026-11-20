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
out=R/('navigation-controls70-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
before={};payloads={};protected={};reports=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
    path=folder/W;raw=path.read_bytes();before[path]=raw
    env=UnityPy.load(raw);objects={o.path_id:o for o in env.objects};expected={};edits=[]

    stylepath=folder/'ui-styles_assets_default.bundle'
    before[stylepath]=stylepath.read_bytes()
    styleenv=UnityPy.load(before[stylepath]);styleobjects={o.path_id:o for o in styleenv.objects}
    sheetobj=next(o for o in styleobjects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
    global_sheet=sheetobj.read_typetree();oldglobal=copy.deepcopy(global_sheet)
    defs={}
    for rule in global_sheet['m_Rules']:
        for prop in rule['m_Properties']:
            if prop.get('m_CustomName'):defs[prop['m_CustomName']]=prop
    def resolve(prop,seen=None):
        seen=set() if seen is None else seen
        hs=prop['m_Values']
        if len(hs)==1 and hs[0]['m_ValueType']==4:return global_sheet['colors'][hs[0]['valueIndex']]
        for h in hs:
            if h['m_ValueType']==8:
                name=global_sheet['strings'][h['valueIndex']]
                if name in defs and name not in seen:return resolve(defs[name],seen|{name})
        return None
    # Follow actual nested templates to select only paint used by the top bar.
    docs={};guidmap={}
    for bn in [G,W]:
        en=env if bn==W else UnityPy.load(str(folder/bn))
        for ob in en.objects:
            if ob.type.name=='AssetBundle':
                for key,entry in ob.read_typetree()['m_Container']:
                    if entry['asset']['m_FileID']==0:guidmap[key]=(bn,entry['asset']['m_PathID'])
            elif ob.type.name=='MonoBehaviour':
                d=ob.read_typetree()
                if 'inlineSheet' in d:docs[bn,ob.path_id]=d
    navkey=next(k for k,d in docs.items() if d['m_Name']=='PrimaryNavigationBar')
    pending=[navkey];closure=set();classes=set();names=set();inline_edits=0
    while pending:
        key=pending.pop()
        if key in closure:continue
        closure.add(key);doc=docs[key]
        refs={r['rid']:r for r in doc['references']['RefIds']}
        for r in refs.values():
            a=r.get('data',{})
            classes.update(a.get('m_Classes',[]))
            sd=refs.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
            if sd.get('name'):names.add(sd['name'])
        for u in doc['m_Usings']:
            child=guidmap.get(u['path'])
            if child in docs and not any(x in u['alias'].lower() for x in ['tooltip','preview']):pending.append(child)
    paint={458752,262146,458758,458761,458762,458763}
    additions=[]
    for rule in oldglobal['m_Rules']:
        props=[]
        for prop in rule['m_Properties']:
            if prop['m_Id'] not in paint and prop.get('m_CustomName') not in ['--start-colour','--end-colour']:continue
            color=resolve(prop)
            if color is None or color['a']==0:continue
            value=dict(color,a=alpha)
            h=Styles(global_sheet).h(4,value)
            props.append(dict(prop,m_Values=[h]))
        if not props:continue
        selectors=[]
        for sel in rule['m_ComplexSelectors']:
            parts=sel['m_Selectors'][-1]['m_Parts']
            if not any((p['m_Type']==3 and p['m_Value'] in classes) or (p['m_Type']==6 and p['m_Value'] in names) for p in parts):continue
            if any(p['m_Value']=='MainNav' for t in sel['m_Selectors'] for p in t['m_Parts']):
                new=copy.deepcopy(sel)
            else:
                new=copy.deepcopy(sel);new['m_Selectors'][0]['m_PreviousRelationship']=2
                new['m_Selectors'].insert(0,{'m_Parts':[{'m_Value':'MainNav','m_Type':6}],'m_PreviousRelationship':0})
            new['m_Specificity']=sel['m_Specificity']+10000
            new['ruleIndex']=len(global_sheet['m_Rules'])
            selectors.append(new)
        if selectors:
            global_sheet['m_Rules'].append({'m_ComplexSelectors':selectors,'m_Properties':props,'line':-1})
            additions.append(len(global_sheet['m_Rules'])-1)
    # Image widgets contain the crest and native toolbar icons.
    src=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selectors>','exec'))
    for typ in ['SIImage','Image']:
        i=len(global_sheet['m_Rules']);sel=selector('#MainNav '+typ,i);sel['m_Specificity']=20000
        global_sheet['m_Rules'].append({'m_ComplexSelectors':[sel],'m_Properties':[Styles(global_sheet).p(458767,Styles(global_sheet).num(alpha))],'line':-1})
    for ob in objects.values():
        if ob.type.name!='MonoBehaviour' or ob.peek_name()!='PrimaryNavigationBar':continue
        doc=ob.read_typetree();sid=doc['inlineSheet']['m_PathID']
        sheet=objects[sid].read_typetree();original=copy.deepcopy(sheet)
        for rule in sheet['m_Rules']:
            for prop in rule['m_Properties']:
                if prop['m_Id'] not in paint:continue
                hs=prop['m_Values']
                if len(hs)!=1 or hs[0]['m_ValueType']!=4:continue
                c=sheet['colors'][hs[0]['valueIndex']]
                if c['a']==0:continue
                sheet['colors'].append(dict(c,a=alpha));hs[0]['valueIndex']=len(sheet['colors'])-1;inline_edits+=1
        expected[sid]=sheet
    assert additions and inline_edits
    assert global_sheet['m_Rules'][:len(oldglobal['m_Rules'])]==oldglobal['m_Rules']
    sheetobj.save_typetree(global_sheet)
    stylebytes=styleenv.file.save(packer='lz4')
    checkstyle={o.path_id:o for o in UnityPy.load(stylebytes).objects}
    for ob in UnityPy.load(before[stylepath]).objects:
        if ob.path_id==sheetobj.path_id:assert checkstyle[ob.path_id].read_typetree()==global_sheet
        else:assert checkstyle[ob.path_id].get_raw_data()==ob.get_raw_data()
    payloads[stylepath]=stylebytes
    edits.append(dict(scoped_rules=len(additions),inline_paints=inline_edits,template_closure=len(closure),background_border_icon_alpha=.7,text_properties_changed=0))
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
state=json.loads(before[statepath]);state['navigation_backgrounds'].update(controls_paint_opacity=.7,icon_opacity=.7,text_opacity=1,controls_install_record=str(out/'manifest.json'),runtime_verified=False)
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
(R/'pending-navigation-controls70.json').write_text(json.dumps(dict(patch=str(out))),'utf8')
print(out)
