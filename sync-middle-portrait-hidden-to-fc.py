"""Clone the current middle FC layout, replacing only its foreground card."""
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
source=(R/'add-approved-left-fc-hidden-overview.py').read_text('utf8')
source=source[source.index('def graft_fc('):source.index(' # Fit the complete original card')]
source=source.replace('def graft_fc(doc,sheet,donor,ds):','def graft(doc,sheet,donor,ds,oldroot,newroot):')
source=source.replace(" rr,dr=refs(doc),refs(donor);oldroot=named(doc,'ReportPortraitStatusColumn');newroot=named(donor,'ReportPortraitStatusColumn')"," rr,dr=refs(doc),refs(donor)")
source+='\n return dict(root=ridmap[newroot],ridmap=ridmap,removed=removed,parent=parent)\n'
exec(compile(source,'subtree-importer','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
FC,PAGE=-930000000001001,-941100000001000
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-portrait-hidden-match-fc-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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
    before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
    fc=oo[FC].read_typetree();fs=oo[fc['inlineSheet']['m_PathID']].read_typetree()
    donor=oo[PAGE].read_typetree();ds=oo[donor['inlineSheet']['m_PathID']].read_typetree()
    sid=donor['inlineSheet']['m_PathID'];doc=copy.deepcopy(fc);sheet=copy.deepcopy(fs)
    # Retain the existing portrait variant's identity and registered style ID.
    doc.update(m_Name=donor['m_Name'],inlineSheet=copy.deepcopy(donor['inlineSheet']))
    sheet['m_Name']=ds['m_Name']
    existing={u['alias']:u for u in doc['m_Usings']}
    renames={u['alias']:'MiddlePortrait_'+u['alias'] for u in donor['m_Usings'] if u['alias'] in existing and u!=existing[u['alias']]}
    def rename(v):
        if isinstance(v,list):return [rename(x) for x in v]
        if isinstance(v,dict):return {k:rename(x) for k,x in v.items()}
        return renames.get(v,v) if isinstance(v,str) else v
    donor=rename(donor)
    oldroot=1293;newroot=named(donor,'ReportPortraitStatusColumn')
    assert data(refs(doc),oldroot)['name']=='ReportPortraitStatusColumn'
    outerrule=copy.deepcopy(sheet['m_Rules'][refs(doc)[oldroot]['data']['m_RuleIndex']]['m_Properties'])
    detail=graft(doc,sheet,donor,ds,oldroot,newroot)
    rr=refs(doc)
    # The 310px centre column is part of the FC layout; only its contents change.
    Styles(sheet).edit(rr[detail['root']],outerrule,reset=True)
    for i,value in refs(fc).items():
        if i not in detail['removed'] and i!=detail['parent']:assert rr[i]==value,('Outside card changed',i)
    assert canonical(doc,sheet,skip_portrait=True)==canonical(fc,fs,skip_portrait=True)
    stage=named(doc,'ReportPortraitLayerStage') if sum(data(rr,i).get('name')=='ReportPortraitLayerStage' for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2)==1 else detail['ridmap'][named(donor,'ReportPortraitLayerStage')]
    donorstage=named(donor,'ReportPortraitLayerStage')
    assert normalized_subtree(doc,sheet,stage)==normalized_subtree(donor,ds,donorstage)
    names=[data(rr,i).get('name','') for i in owned_refs(rr,detail['root']) if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2]
    assert {'PersonPictureFrame','CardNativeFootFooter','PlayerStatusFlagsForTeamVisible'}<=set(names)
    assert not any(n.startswith(('ReportCAAbove','OverviewCard','ReportMiddleCA')) for n in names)
    doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
    graph(doc);validate_ui(doc,sheet)
    ab=next(o for o in oo.values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
    def entry(pid):return next((k,v) for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid})
    key,e=entry(PAGE);fkey,fe=entry(FC)
    assert [v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==key]==[PAGE]
    span=copy.deepcopy(meta['m_PreloadTable'][e['preloadIndex']:e['preloadIndex']+e['preloadSize']])
    for ptr in meta['m_PreloadTable'][fe['preloadIndex']:fe['preloadIndex']+fe['preloadSize']]:
        ptr=copy.deepcopy(ptr)
        if ptr['m_FileID']==0:ptr['m_PathID']={FC:PAGE,fc['inlineSheet']['m_PathID']:sid}.get(ptr['m_PathID'],ptr['m_PathID'])
        if ptr not in span:span.append(ptr)
    assert not any(p['m_PathID'] in reserved for p in span)
    e.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
    catpath=(root.parent if tag=='game' else root)/'catalog.bin';catbefore=catpath.read_bytes();cat=cm.Catalog(catbefore)
    targets=[i for i in cat.locations(key) if cat.location(i)['type'][1].endswith('VisualTreeAsset')];assert len(targets)==1
    assetloc=targets[0];floc=next(i for i in cat.locations(fkey) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
    olddeps=cat.location(assetloc)['dependencies'];deps=list(dict.fromkeys(olddeps+cat.location(floc)['dependencies']))
    assert cat.location(deps[0])['internal'].endswith(W)
    if deps!=olddeps:
        raw=b''.join(struct.pack('<I',i) for i in deps);offset=cat.append(raw,True);struct.pack_into('<2I',cat.data,assetloc+12,offset,zlib.crc32(raw))
    assert assetloc in cat.locations('GameWorldVisualTreeAssetPreload')
    changes={PAGE:doc,sid:sheet,ab.path_id:meta}
    for i,v in changes.items():oo[i].save_typetree(v)
    output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
    assert check.keys()==oo.keys()
    for i,h in hashes.items():
        if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
    for i,v in changes.items():assert check[i].read_typetree()==v
    add_tx(tag,root/W,output,before)
    catout=bytes(cat.data);hashpath=catpath.with_name('catalog.hash')
    if catout!=catbefore:
        add_tx(tag,catpath,catout,catbefore);add_tx(tag,hashpath,hashlib.md5(catout).hexdigest().encode('ascii'),hashpath.read_bytes())
    else:
        protected[str(catpath)]=sha(catbefore);protected[str(hashpath)]=sha(hashpath.read_bytes())
    checks.append(dict(target=tag,source_page=FC,page=PAGE,all_layout_outside_portrait_matches_current_fc=True,portrait_stage_matches_previous_large_portrait=True,centre_column_width_px=310,other_objects_byte_identical=True,unique_guid_and_actual_preload_verified=True,serialization_readback=True))
    print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for name,v in [('manifest.json',m),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-portrait-hidden-match-fc-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
