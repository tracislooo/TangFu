from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,re,struct,zlib

R=Path(__file__).resolve().parent
# Load the existing UnityPy codecs and location definitions without running the old patch.
exec((R/'apply-page-background-tf-v1-opaque.py').read_text('utf8').split('out = R /')[0])
exec((R/'update-ledger-bundle-crcs.py').read_text('utf8').split('def crc(data):')[0].split('out=Path')[0].split("sys.path.insert(0,'.codex-deps')")[1])
src=ast.parse((R/'update-ledger-bundle-crcs.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='crc'],type_ignores=[]),'<crc>','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
S='ui-styles_assets_default.bundle'
TF=-910000000000149
ALPHA=struct.unpack('<f',struct.pack('<f',.6))[0]
MARK='tf27-nonmatch-module-alpha30'
TARGETS={'PortalScreen':1021,'SquadScreen':1008,'PlayerContractCard':1001}
before={};updated={};protected={};reports=[]
def patch_bundle(raw, edit):
    env=UnityPy.load(raw);objects={o.path_id:o for o in env.objects};changed=edit(objects)
    for pid,tree in changed.items():objects[pid].save_typetree(tree)
    data=env.file.save(packer='lz4')
    orig={o.path_id:o for o in UnityPy.load(raw).objects};new={o.path_id:o for o in UnityPy.load(data).objects}
    assert set(orig)==set(new)
    for pid,ob in new.items():
        if pid in changed:assert ob.read_typetree()==changed[pid],pid
        else:assert ob.get_raw_data()==orig[pid].get_raw_data(),pid
    return data

for tag,folder in [('game',GAME),('skin',SKIN)]:
    pages={};keys=set();module_count=0
    bg=(folder/BG).read_bytes()
    tex=next(o for o in UnityPy.load(bg).objects if o.path_id==TF)
    assert tex.peek_name()=='TF skin V1' and tex.read().image.convert('RGBA').getextrema()[3]==(255,255)
    world=folder/W;before[world]=world.read_bytes()
    def edit_pages(objects):
        changed={};owned=set()
        for ob in objects.values():
            if ob.type.name!='MonoBehaviour' or ob.peek_name() not in TARGETS:continue
            doc=ob.read_typetree();name=doc['m_Name'];rid=TARGETS[name]
            assert name not in pages
            refs={r['rid']:r for r in doc['references']['RefIds']}
            target=refs[rid]['data'];sid=doc['inlineSheet']['m_PathID'];sheet=objects[sid].read_typetree()
            fid=next(i for i,x in enumerate(ob.assets_file.externals,1) if x.path.lower()==f'archive:/{tex.assets_file.name}/{tex.assets_file.name}'.lower())
            pointer={'m_FileID':fid,'m_PathID':TF}
            st=Styles(sheet)
            st.edit(target,[st.p(458752,st.h(4,dict(r=0.,g=0.,b=0.,a=1.))),
                st.p(458753,st.h(6,pointer)),st.p(262153,st.en('scale-and-crop')),st.p(458767,st.num(1))])
            if name=='PlayerContractCard' and tag=='game':
                instance=next(r['data'] for r in refs.values() if r.get('data',{}).get('m_TemplateAlias')=='FigmaBaseToolMultiGridHeaderTemplate')
                override=next(v for v in instance['m_SerializedDataOverride'] if v['m_ElementIdsPath']==[-1903566030])
                image=refs[override['m_SerializedData']['rid']]['data']
                assert image['uxmlAssetId']==-1903566030
                image['Binding']['m_kind']=0
                image['Binding_UxmlAttributeFlags']=1
                image['tintColor']=dict(r=1.,g=1.,b=1.,a=0.)
                image['tintColor_UxmlAttributeFlags']=1
            changed[ob.path_id]=doc;changed[sid]=sheet;owned.update([ob.path_id,sid])
            pages[name]={'object':ob.path_id,'rid':rid,'element_id':target['m_Id'],'texture':pointer}
        assert set(pages)==set(TARGETS),pages
        metaobj=next(o for o in objects.values() if o.type.name=='AssetBundle')
        meta=metaobj.read_typetree();old=meta['m_PreloadTable'][:]
        for key,entry in meta['m_Container']:
            asset=entry['asset']
            is_page=asset['m_FileID']==0 and asset['m_PathID'] in {v['object'] for v in pages.values()}
            span=old[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]
            if is_page and re.fullmatch('[0-9a-f]{32}',key):keys.add(key)
            if (is_page or any(x['m_FileID']==0 and x['m_PathID'] in owned for x in span)) and pointer not in span:
                entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span)+1)
                meta['m_PreloadTable'].extend(span+[pointer])
        assert len(keys)>=3
        assert tex.assets_file.name.lower() in meta['m_Dependencies']
        changed[metaobj.path_id]=meta
        return changed
    updated[world]=patch_bundle(before[world],edit_pages)
    joint=UnityPy.load(updated[world],bg)
    for page in pages.values():
        ob=next(o for o in joint.objects if o.path_id==page['object'])
        assert PPtr(assetsfile=ob.assets_file,**page['texture']).deref().get_raw_data()==tex.get_raw_data()
    styles=folder/S;before[styles]=styles.read_bytes()
    counts=[]
    def edit_modules(objects):
        ob=next(o for o in objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
        tree=ob.read_typetree()
        for rule in tree['m_Rules']:
            if not any(p['m_Value']==MARK for c in rule.get('m_ComplexSelectors',[]) for s in c['m_Selectors'] for p in s['m_Parts']):continue
            prop=next(p for p in rule['m_Properties'] if p['m_Id']==458752)
            h,=prop['m_Values'];assert h['m_ValueType']==4
            old=tree['colors'][h['valueIndex']]
            assert any(abs(old['a']-previous)<1e-6 for previous in [.3,.5,ALPHA]),old
            tree['colors'].append(dict(old,a=ALPHA));h['valueIndex']=len(tree['colors'])-1
            counts.append(1)
        assert counts
        return {ob.path_id:tree}
    updated[styles]=patch_bundle(before[styles],edit_modules)
    catroot=GAME.parent if tag=='game' else SKIN
    cp=catroot/'catalog.bin';hp=catroot/'catalog.hash'
    before[cp]=cp.read_bytes();before[hp]=hp.read_bytes()
    cat=cm.Catalog(before[cp]);locations={i for _,k in cat.keys() for i, in cat.array(k,'I')}
    locs={cat.location(i)['internal'].replace('\\','/').split('/')[-1]:i for i in locations if cat.location(i)['type'][1].endswith('IAssetBundleResource')}
    for key in keys:
        entries=[cat.location(i) for i in cat.locations(key) if cat.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset']
        assert entries,key
        for v in entries:
            deps=v['dependencies'];assert deps[0]==locs[W],(key,deps)
            if locs[BG] not in deps:
                block=struct.pack('<'+'I'*(len(deps)+1),*(deps+[locs[BG]]))
                struct.pack_into('<II',cat.data,v['offset']+12,cat.append(block,True),zlib.crc32(block))
            assert locs[BG] in cat.location(v['offset'])['dependencies']
    for name,path in [(W,world),(S,styles)]:
        rows=[i for i in locations if cat.location(i)['type'][1].endswith('IAssetBundleResource') and cat.location(i)['internal'].replace('\\','/').endswith('/'+name)]
        assert rows
        data=updated[path];checksum=crc(data)
        for i in rows:
            extra=cat.location(i)['raw'][5]
            if extra==cm.NULL:
                assert tag=='skin'
                continue
            typ,opts=cat.unpack(extra,'2I')
            assert cat.typename(typ)[1].endswith('AssetBundleRequestOptions')
            values=list(cat.unpack(opts,'5I'));values[2:4]=[checksum,len(data)]
            newopts=cat.append(struct.pack('<5I',*values))
            struct.pack_into('<I',cat.data,i+20,cat.append(struct.pack('<2I',typ,newopts)))
            assert cat.unpack(cat.unpack(cat.location(i)['raw'][5],'2I')[1],'5I')[2:4]==(checksum,len(data))
    if bytes(cat.data)!=before[cp]:
        updated[cp]=bytes(cat.data);updated[hp]=hashlib.md5(updated[cp]).hexdigest().encode('ascii')
    else:
        protected[str(cp)]=sha(before[cp]);protected[str(hp)]=sha(before[hp])
    for path in [folder/BG,folder/G]:protected[str(path)]=sha(path.read_bytes())
    reports.append(dict(target=tag,pages=pages,module_rules=len(counts),catalog_keys=sorted(keys)))
    print(tag, list(pages), len(counts), flush=True)

out=R/('page-backgrounds-module60-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
out.mkdir()
statefile=R/'current-ui-surface-theme.json';before[statefile]=statefile.read_bytes()
state=json.loads(before[statefile]);state['nonmatch_module_backgrounds'].update(background_opacity=.6,install_record=str(out/'manifest.json'),runtime_verified=False)
state['page_backgrounds'].update(module_background_alpha=.6,additional_pages=list(TARGETS),additional_pages_record=str(out/'manifest.json'))
state['scope']='Opaque TF skin V1 page backgrounds; non-match module backgrounds at alpha 0.6'
updated[statefile]=json.dumps(state,ensure_ascii=False,indent=2).encode('utf8')
setter=R/'set-nonmatch-module-opacity.py'
before[setter]=setter.read_bytes()
updated[setter]=before[setter].decode('utf8').replace('import argparse, copy, datetime, hashlib, json, sys','import argparse, copy, datetime, hashlib, json, struct, sys').replace('assert 0 <= alpha <= 1','assert 0 <= alpha <= 1\nalpha_f32 = struct.unpack("<f", struct.pack("<f", alpha))[0]').replace('dict(previous, a=alpha)','dict(previous, a=alpha_f32)').replace("bc['a'] == alpha","bc['a'] == alpha_f32").encode('utf8')
tx=dict(game=str(GAME),skin=str(SKIN),workspace=str(R),sources={},before={})
for p,data in updated.items():
    assert p.read_bytes()==before[p]
    tag='game' if p.parent in [GAME,GAME.parent] else 'skin' if p.parent==SKIN else 'workspace'
    source=out/tag/p.name;backup=out/('backup-'+tag)/p.name
    for dest,content in [(source,data),(backup,before[p])]:
        dest.parent.mkdir(exist_ok=True);dest.write_bytes(content)
    tx['sources'][str(p)]=str(source);tx['before'][str(p)]=str(backup)
m=dict(installed=False,runtime_verified=False,reports=reports,protected_sha256=protected,
    before_sha256={str(p):sha(before[p]) for p in updated},after_sha256={str(p):sha(data) for p,data in updated.items()})
for name,data in [('manifest.json',m),('transaction.json',tx),('verification.json',{'passed':True,'runtime_verified':False})]:
    (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install.ps1',''),('restore.ps1','--restore')]:
    (out/name).write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' "+flag+"\n",'utf8')
(R/'pending-page-backgrounds-module60.json').write_text(json.dumps(dict(patch=str(out))),'utf8')
print(out)
