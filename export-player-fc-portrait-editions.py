"""Export two current-resource editions; never install or alter live resources."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, zipfile, zlib

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'}),('apply-hover-large-portrait-trial.py',{'reachable'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME=Path(cfg['bundle_root']);SKIN=Path(cfg['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L='ui-tileslayouts_assets_all.bundle'
SET=1332213496068314481
COMP=3901662990989568885
CARD='64033a72b9925c8dad3b08826077c328'
sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/'exports'/('球员页面与悬浮层-两套版本-'+stamp);OUT.mkdir(parents=True)

# Record all installed bundles, catalogs and layout caches as read-only sources.
protected={}
for root in [GAME,SKIN]:
    for p in root.glob('*.bundle'):protected[str(p)]=sha(p.read_bytes())
    for p in [(root.parent if root==GAME else root)/'catalog.bin',(root.parent if root==GAME else root)/'catalog.hash']:
        if p.exists():protected[str(p)]=sha(p.read_bytes())
cache=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions'
if cache.exists():
    for p in cache.glob('*'):
        if p.is_file():protected[str(p)]=sha(p.read_bytes())
before={bn:(GAME/bn).read_bytes() for bn in [W,L]}
catalog_before=(GAME.parent/'catalog.bin').read_bytes()
reserved={int(t['path_id']) for t in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}

def portrait(doc,sheet):
    rr={r['rid']:r for r in doc['references']['RefIds']};st=Styles(sheet)
    def named(name):
        return next(i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and rr.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name)
    stage,frame=named('ReportPortraitLayerStage'),named('PersonPictureFrame')
    original={i:copy.deepcopy(rr[i]) for i in reachable(rr,frame)}
    rr[stage]['data']['m_Children']=[{'rid':frame}]
    st.box(rr[frame],10,10,320,500)
    keep=reachable(rr,doc['m_VisualTree']['rid'])
    doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in keep]
    assert all(rr[i]==v for i,v in original.items() if i!=frame)
    aliases={r.get('data',{}).get('m_TemplateAlias') for r in doc['references']['RefIds']}-{None,''}
    doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias'] in aliases]
    active=sorted({r['data']['m_RuleIndex'] for r in doc['references']['RefIds'] if r.get('data',{}).get('m_RuleIndex',-1)>=0})
    remap={old:new for new,old in enumerate(active)}
    for r in doc['references']['RefIds']:
        d=r.get('data',{})
        if d.get('m_RuleIndex',-1)>=0:d['m_RuleIndex']=remap[d['m_RuleIndex']]
    sheet['m_Rules']=[sheet['m_Rules'][i] for i in active]
    for pool in set(poolmap.values()):
        used=sorted({h['valueIndex'] for rule in sheet['m_Rules'] for p in rule['m_Properties'] for h in p['m_Values'] if poolmap.get(h['m_ValueType'])==pool})
        remap={old:new for new,old in enumerate(used)};sheet[pool]=[sheet[pool][i] for i in used]
        for rule in sheet['m_Rules']:
            for p in rule['m_Properties']:
                for h in p['m_Values']:
                    if poolmap.get(h['m_ValueType'])==pool:h['valueIndex']=remap[h['valueIndex']]
    assert not any(any(k in r.get('data',{}).get('name','') for k in ['OverviewCard','ReportCACard','TooltipCard']) for r in doc['references']['RefIds'])
    validate_ui(doc,sheet)
    doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff

def crc(data):
    rd=EndianBinaryReader(data);bu=object.__new__(BundleFile)
    bu.signature=rd.read_string_to_null();bu.version=rd.read_u_int();bu.version_player=rd.read_string_to_null();bu.version_engine=rd.read_string_to_null()
    _,block=bu.read_fs(rd);return zlib.crc32(block.bytes)

reports=[]
for mode,title in [('fc','FC卡面版'),('portrait','大头像版')]:
    print('Preparing '+mode,flush=True)
    env={bn:UnityPy.load(raw) for bn,raw in before.items()}
    obs={bn:{o.path_id:o for o in en.objects} for bn,en in env.items()}
    hashes={bn:{i:sha(o.get_raw_data()) for i,o in oo.items()} for bn,oo in obs.items()}
    changes={W:{},L:{}}
    tile=obs[L][SET].read_typetree();original=copy.deepcopy(tile)
    descriptions={p['m_PathID']:obs[L][p['m_PathID']].read_typetree() for p in tile['m_gridElementDescriptions'] if p['m_FileID']==0}
    choices={i:d for i,d in descriptions.items() if d.get('<ID>k__BackingField','').startswith('PlayerOverview')}
    assert len(choices)==9
    fc={i for i,d in choices.items() if 'FC' in d['m_directTitlePath']['m_path']}
    assert len(fc)==3
    keep=fc if mode=='fc' else set(choices)-fc
    removed=set(choices)-keep
    tile['m_gridElementDescriptions']=[p for p in tile['m_gridElementDescriptions'] if p['m_FileID'] or p['m_PathID'] not in removed]
    assert [p for p in tile['m_gridElementDescriptions'] if p['m_PathID'] not in keep]==[p for p in original['m_gridElementDescriptions'] if p['m_PathID'] not in choices]
    changes[L][SET]=tile
    comp=obs[L][COMP].read_typetree();oldcomp=copy.deepcopy(comp)
    slot=next(c for c in comp['m_gridComponents'] if c['m_elementID']=='PlayerAttributesBlock')
    default=-950000000000232 if mode=='fc' else -950000000000231
    slot['m_configDescriptions']=[{'m_FileID':0,'m_PathID':default}]
    slot['m_gridElementConfigs']=copy.deepcopy(choices[default]['<Configurations>k__BackingField'])
    slot['m_configDescriptionKeys']=[]
    comp['m_placementBindings']=[p for p in comp['m_placementBindings'] if p['m_elementID'] not in {choices[i]['<ID>k__BackingField'] for i in removed}]
    # Distinct revisions request native saved-layout migration when switching editions.
    comp['m_compositionVersion']=max(oldcomp['m_compositionVersion']+1,2026111701 if mode=='fc' else 2026111702)
    assert comp['m_gridComponents'][1:]==oldcomp['m_gridComponents'][1:]
    changes[L][COMP]=comp
    cat=cm.Catalog(catalog_before)
    meta=next(o.read_typetree() for o in obs[W].values() if o.type.name=='AssetBundle')
    hoverids={v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==CARD and v['asset']['m_FileID']==0}
    assert hoverids=={-960000000003010,-950000000000141}
    if mode=='portrait':
        for pid in hoverids:
            doc=obs[W][pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=obs[W][sid].read_typetree()
            portrait(doc,sheet);changes[W].update({pid:doc,sid:sheet})
    payloads={}
    for bn in [W,L]:
        for pid,d in changes[bn].items():obs[bn][pid].save_typetree(d)
        raw=env[bn].file.save(packer='lz4') if changes[bn] else before[bn]
        checked={o.path_id:o for o in UnityPy.load(raw).objects}
        assert set(checked)==set(obs[bn]) and reserved.isdisjoint(checked)
        for pid,o in checked.items():
            if pid in changes[bn]:assert o.read_typetree()==changes[bn][pid],(mode,bn,pid)
            else:assert sha(o.get_raw_data())==hashes[bn][pid],(mode,bn,pid)
        payloads[bn]=raw
    # Prove every allowed page still resolves to exactly its current template.
    routes=[]
    for pid in keep:
        d=choices[pid]
        for config in d['<Configurations>k__BackingField']:
            guid=config['AssetRef']['m_AssetGUID'];locations=[cat.location(i) for i in cat.locations(guid)]
            assert len(locations)==1 and locations[0]['type'][1].endswith('VisualTreeAsset')
            assert cat.location(locations[0]['dependencies'][0])['internal'].endswith(W)
            assert cat.locations(guid)[0] in cat.locations('GameWorldVisualTreeAssetPreload')
            entries=[v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==guid and v['asset']['m_FileID']==0 and 'm_VisualTree' in obs[W][v['asset']['m_PathID']].read_typetree()]
            assert len(entries)==1,(guid,entries)
            routes.append({'description':pid,'id':d['<ID>k__BackingField'],'guid':guid,'page':entries[0]})
    for i in cat.locations(CARD):
        assert i in cat.locations('GameWorldVisualTreeAssetPreload')
        assert cat.location(cat.location(i)['dependencies'][0])['internal'].endswith(W)
    locations={i:cat.location(i) for _,ls in cat.keys() for i, in cat.array(ls,'I')}
    metadata=[]
    for bn,raw in payloads.items():
        checksum=crc(raw);count=0
        for i,v in locations.items():
            if v['type'][1].endswith('IAssetBundleResource') and v['internal'].replace('\\','/').endswith('/'+bn):
                typ,p=cat.unpack(v['raw'][5],'2I');request=list(cat.unpack(p,'5I'));request[2:4]=[checksum,len(raw)]
                extra=cat.append(struct.pack('<2I',typ,cat.append(struct.pack('<5I',*request))))
                record=list(v['raw']);record[5]=extra;struct.pack_into('<7I',cat.data,i,*record);count+=1
        assert count
        metadata.append({'bundle':bn,'crc':checksum,'size':len(raw)})
    payloads['catalog.bin']=bytes(cat.data)
    payloads['catalog.hash']=hashlib.md5(payloads['catalog.bin']).hexdigest().encode('ascii')
    dest=OUT/title;aa=dest/'aa';(aa/'StandaloneWindows64').mkdir(parents=True)
    files={}
    for name,raw in payloads.items():
        rel=('aa/StandaloneWindows64/' if name.endswith('.bundle') else 'aa/')+name
        (dest/rel).write_bytes(raw);files[rel]=sha(raw)
    report={'edition':mode,'installed':False,'runtime_verified':False,'choices':routes,'changed_objects':{bn:list(d) for bn,d in changes.items()},'all_other_objects_byte_identical':True,'page_templates_and_bindings_unchanged':True,'bundle_metadata':metadata,'sha256':files,'composition_revision':comp['m_compositionVersion']}
    (dest/'文件校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    explanation='仅保留3个FC卡面概览页面，悬浮层为FC卡面。' if mode=='fc' else '仅保留6个大头像概览页面，悬浮层为320×500大头像。'
    (dest/'使用说明.txt').write_text(explanation+'\n\n本包是基于本次当前完整皮肤资源制作的增量替换文件，需配合现有完整皮肤使用。两版各保留原页面布局、数据绑定、隐藏/非隐藏及新旧版区分；底部其他模块保持。\n每套aa含两个资源包和配套catalog.bin/catalog.hash。以后使用时，退出游戏后将所选一套aa合并到游戏fm_Data/StreamingAssets/aa；两套勿混用。资源基线变化后请重新迁移，不建议覆盖更新后的游戏文件。\n本次仅导出，未安装；游戏文件、独立皮肤、用户布局缓存均未写入。已完成离线回读、其他对象一致性、GUID登记/预加载和压缩包校验，游戏内效果未验证。\n已为两版设置独立布局版本号；若旧布局仍被保留，请在游戏内重置该球员概览布局后再选择。\n','utf-8-sig')
    zp=OUT/(title+'.zip')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for p in dest.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(dest))
    with zipfile.ZipFile(zp) as z:
        assert z.testzip() is None
        for name,h in files.items():assert sha(z.read(name))==h
    report['zip']=str(zp);reports.append(report)
    print('Verified '+mode,flush=True)

for p,h in protected.items():assert sha(Path(p).read_bytes())==h,('Source changed during export',p)
manifest={'export_only':True,'installed':False,'runtime_verified':False,'source':str(GAME),'source_sha256':{bn:sha(b) for bn,b in before.items()},'catalog_source_sha256':sha(catalog_before),'protected_sources_sha256':protected,'sources_unchanged_verified':True,'reports':reports}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'output':str(OUT),'zips':[r['zip'] for r in reports],'sources_unchanged':True},ensure_ascii=True),flush=True)
