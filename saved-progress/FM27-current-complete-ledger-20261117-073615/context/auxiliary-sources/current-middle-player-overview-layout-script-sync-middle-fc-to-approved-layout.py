"""Update only the middle FC overview from current approved portrait regions."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, zlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'}),('verify-two-portrait-hidden-overviews.py',{'canonical'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
# Generalize the existing verified subtree importer, including styles and IDs.
source=(R/'add-approved-left-fc-hidden-overview.py').read_text('utf8')
source=source[source.index('def graft_fc('):source.index(' # Fit the complete original card')]
source=source.replace('def graft_fc(doc,sheet,donor,ds):','def graft(doc,sheet,donor,ds,oldroot,newroot):')
source=source.replace(" rr,dr=refs(doc),refs(donor);oldroot=named(doc,'ReportPortraitStatusColumn');newroot=named(donor,'ReportPortraitStatusColumn')"," rr,dr=refs(doc),refs(donor)")
source+='\n return dict(root=ridmap[newroot],ridmap=ridmap,removed=removed,parent=parent)\n'
exec(compile(source,'verified-subtree-importer','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PAGE=-930000000001001;DONOR=-941100000001020
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/('middle-fc-approved-layout-'+stamp);OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={str(p):sha(p.read_bytes()) for _,root in roots for p in root.glob('*.bundle') if p.name!=W}
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
tx=[];checks=[]
def add_tx(tag,target,output,before):
    src=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name
    src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True)
    src.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
def normalized_subtree(doc,sheet,node):
    temporary=copy.deepcopy(doc);temporary['m_VisualTree']={'rid':node}
    return canonical(temporary,sheet)
for tag,root in roots:
    print('Preparing '+tag,flush=True)
    before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
    doc=obs[PAGE].read_typetree();old=copy.deepcopy(doc)
    sid=doc['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree();oldsheet=copy.deepcopy(sheet)
    donor=obs[DONOR].read_typetree();ds=obs[donor['inlineSheet']['m_PathID']].read_typetree()
    existing={u['alias']:u for u in doc['m_Usings']}
    renames={u['alias']:'MiddleFCApproved_'+u['alias'] for u in donor['m_Usings'] if u['alias'] in existing and u!=existing[u['alias']]}
    def rename_aliases(v):
        if isinstance(v,list):return [rename_aliases(x) for x in v]
        if isinstance(v,dict):return {k:rename_aliases(x) for k,x in v.items()}
        return renames.get(v,v) if isinstance(v,str) else v
    donor=rename_aliases(donor)
    preserved={i:normalized_subtree(old,oldsheet,i) for i in [1007,1009,1293]}
    transferred=[]
    for oldid,newid in [(1291,1291),(1173,1173),(1703,1703)]:
        detail=graft(doc,sheet,donor,ds,oldid,newid)
        assert normalized_subtree(doc,sheet,detail['root'])==normalized_subtree(donor,ds,newid)
        transferred.append(dict(source=newid,target=detail['root']))
    rr=refs(doc)
    # Keep the original card and the first two lower columns exactly as installed.
    for i,value in preserved.items():assert normalized_subtree(doc,sheet,i)==value,('Preserved region changed',i)
    assert [data(rr,c['rid']).get('name') for c in rr[1169]['data']['m_Children']]==['ReportIdentityColumn','ReportPortraitStatusColumn','Frame']
    # Inline the existing icon template so the crest adjustment belongs only here.
    icons=obs[-910000000000201].read_typetree();ics=obs[icons['inlineSheet']['m_PathID']].read_typetree()
    ir=refs(icons);ist=Styles(ics)
    ist.edit(ir[1138],[ist.p(131099,ist.px(0)),ist.p(131100,ist.px(0)),ist.p(131092,ist.px(12))])
    ist.edit(ir[1008],[ist.p(131105,ist.px(646)),ist.p(131082,ist.px(646)),ist.p(131084,ist.num(0)),ist.p(131085,ist.num(1)),ist.p(131099,ist.px(0)),ist.p(131100,ist.px(0))])
    # Relative positioning leaves the flag and the row's centering unchanged.
    ist.edit(ir[1154],[ist.p(131102,ist.en('relative')),ist.p(131089,ist.px(16))])
    detail=graft(doc,sheet,icons,ics,1163,1001)
    rr=refs(doc);data(rr,detail['root'])['name']='MiddleFCPrivateFlagClubContext'
    for i,value in preserved.items():assert normalized_subtree(doc,sheet,i)==value
    # Native season root/remappers remain identical in the untouched attributes.
    for i in owned_refs(refs(old),1041):assert rr[i]==refs(old)[i]
    graph(doc);validate_ui(doc,sheet)
    ab=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
    def entry(pid):return next((k,v) for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid})
    key,e=entry(PAGE);donorkey,de=entry(DONOR)
    assert [v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==key]==[PAGE], 'Resolve duplicate middle FC GUID entries before preparing another layout patch.'
    span=copy.deepcopy(meta['m_PreloadTable'][e['preloadIndex']:e['preloadIndex']+e['preloadSize']])
    for ptr in meta['m_PreloadTable'][de['preloadIndex']:de['preloadIndex']+de['preloadSize']]:
        ptr=copy.deepcopy(ptr)
        if ptr['m_FileID']==0:ptr['m_PathID']={DONOR:PAGE,donor['inlineSheet']['m_PathID']:sid}.get(ptr['m_PathID'],ptr['m_PathID'])
        if ptr not in span:span.append(ptr)
    assert not any(p['m_PathID'] in reserved for p in span)
    e.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
    catpath=(root.parent if tag=='game' else root)/'catalog.bin'
    catbefore=catpath.read_bytes();cat=cm.Catalog(catbefore)
    assetloc=next(i for i in cat.locations(key) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
    donorloc=next(i for i in cat.locations(donorkey) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
    olddeps=cat.location(assetloc)['dependencies'];deps=list(dict.fromkeys(olddeps+cat.location(donorloc)['dependencies']))
    assert cat.location(deps[0])['internal'].endswith(W)
    if deps!=olddeps:
        raw=b''.join(struct.pack('<I',i) for i in deps);offset=cat.append(raw,True)
        struct.pack_into('<2I',cat.data,assetloc+12,offset,zlib.crc32(raw))
    cat=cm.Catalog(bytes(cat.data));assert cat.location(assetloc)['dependencies']==deps
    assert assetloc in cat.locations('GameWorldVisualTreeAssetPreload')
    changes={PAGE:doc,sid:sheet,ab.path_id:meta}
    for i,value in changes.items():obs[i].save_typetree(value)
    output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
    assert check.keys()==obs.keys()
    for i,h in hashes.items():
        if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
    for i,value in changes.items():assert check[i].read_typetree()==value
    newdoc=check[PAGE].read_typetree();newsheet=check[sid].read_typetree()
    for i,value in preserved.items():assert normalized_subtree(newdoc,newsheet,i)==value
    add_tx(tag,root/W,output,before)
    catout=bytes(cat.data);hashpath=catpath.with_name('catalog.hash')
    if catout!=catbefore:
        add_tx(tag,catpath,catout,catbefore);add_tx(tag,hashpath,hashlib.md5(catout).hexdigest().encode('ascii'),hashpath.read_bytes())
    else:
        protected[str(catpath)]=sha(catbefore);protected[str(hashpath)]=sha(hashpath.read_bytes())
    checks.append(dict(target=tag,source_page=DONOR,updated_page=PAGE,regions=transferred,
        identity_left_offset_removed=True,right_header_career_and_ability_radar_match_approved=True,
        hidden_attributes_and_scout_pros_cons_match_approved=True,crest_right_shift_px=16,
        original_fc_card_exact=True,original_pitch_and_attributes_exact=True,
        native_season_context_exact=True,all_other_overview_objects_byte_identical=True,
        catalog_preload_and_dependencies_verified=True,serialization_readback=True))
    print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,change='Middle FC overview only: approved identity, header data and right report layout; private crest +16px',protected_sha256=protected,checks=checks)
for name,value in [('manifest.json',m),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-fc-approved-layout-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
