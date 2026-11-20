"""Apply approved middle portrait layout to the existing nonhidden page only."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, zlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
source=(R/'sync-middle-portrait-hidden-to-fc.py').read_text('utf8')
exec(source[source.index("source=(R/'add-approved"):source.index('spec=importlib')])
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PAGE,SOURCE,RADAR,STATS=-930000000001003,-941100000001000,-941100000001080,-950000000000164
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-portrait-nonhidden-radar-table-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={str(p):sha(p.read_bytes()) for _,root in roots for p in root.glob('*.bundle') if p.name!=W}
tx=[];checks=[]
def add_tx(tag,target,output,before):
    src=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name
    src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True)
    src.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
def remove(doc,node):
    rr=refs(doc);parent=rr[node]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':node})
    gone=owned_refs(rr,node);doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in gone]
def box(st,rr,node,width,height,direction='column'):
    st.edit(rr[node],[st.p(131102,st.en('relative')),st.p(131105,width),st.p(131087,height),st.p(131097,st.px(0)),st.p(131096,st.px(0)),st.p(131095,{'m_ValueType':1,'valueIndex':3}),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131082,{'m_ValueType':1,'valueIndex':2}),st.p(131084,st.num(0)),st.p(131085,st.num(1)),st.p(131083,st.en(direction)),st.p(131073,st.en('stretch')),st.p(131081,st.en('flex'))])
for tag,root in roots:
    print('Preparing '+tag,flush=True)
    before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
    original=oo[PAGE].read_typetree();sid=original['inlineSheet']['m_PathID']
    doc=copy.deepcopy(oo[SOURCE].read_typetree());sheet=copy.deepcopy(oo[doc['inlineSheet']['m_PathID']].read_typetree())
    doc.update(m_Name=original['m_Name'],inlineSheet=original['inlineSheet']);sheet['m_Name']=oo[sid].read_typetree()['m_Name']
    data(refs(doc),1705)['name']='LargePortraitNoHiddenOverviewFrame'
    # Preserve each native cell's complete value/missing and season bindings.
    table=copy.deepcopy(oo[STATS].read_typetree());ts=oo[table['inlineSheet']['m_PathID']].read_typetree();tr=refs(table);st=Styles(ts)
    for panel,prefix in [(1601,'SeasonStatCell_'),(1603,'GoalkeeperStatCell_')]:
        tr=refs(table);rows=[c['rid']for c in tr[panel]['data']['m_Children']]
        cells=[c['rid']for row in rows for c in tr[row]['data']['m_Children'] if data(tr,c['rid']).get('name','').startswith(prefix)]
        assert len(cells)==12
        preserved={i:copy.deepcopy(tr[i]) for cell in cells for i in owned_refs(tr,cell)}
        proto=(copy.deepcopy(tr[rows[0]]),copy.deepcopy(tr[tr[rows[0]]['data']['m_SerializedData']['rid']]))
        for cell in cells:
            parent=tr[cell]['data']['m_Parent']['rid'];tr[parent]['data']['m_Children'].remove({'rid':cell})
        for row in rows:
            for ch in list(refs(table)[row]['data']['m_Children']):remove(table,ch['rid'])
        for j in range(2):rows.append(add_node(table,proto,panel,'NonHiddenSeasonRow'+str(j+5)))
        tr=refs(table)
        for row in rows:box(st,tr,row,st.pct(100),st.pct(struct.unpack('<f',struct.pack('<f',100/6))[0]),'row')
        for j,cell in enumerate(cells):
            tr[cell]['data']['m_Parent']={'rid':rows[j//2]};tr[rows[j//2]]['data']['m_Children'].append({'rid':cell})
            box(st,tr,cell,st.pct(50),st.pct(100));st.edit(tr[cell],[st.p(131088,st.en('center'))])
            for i in owned_refs(tr,cell):
                if tr[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':
                    title='Title_' in data(tr,i).get('name','');st.edit(tr[i],[st.p(65537,st.px(10 if title else 16))])
        box(st,tr,panel,st.pct(100),st.pct(100))
        for i,v in preserved.items():
            now=copy.deepcopy(tr[i]);old=copy.deepcopy(v)
            for q in [now,old]:q['data'].pop('m_RuleIndex',None)
            if i in cells:
                now['data'].pop('m_Parent');old['data'].pop('m_Parent')
            assert now==old,('Cell binding changed',i)
    box(st,refs(table),1599,st.pct(100),st.pct(100))
    box(st,refs(table),1041,st.pct(100),st.pct(50))
    # Embed the native table below the current radar, retaining both contexts.
    radar=copy.deepcopy(oo[RADAR].read_typetree());rs=oo[radar['inlineSheet']['m_PathID']].read_typetree()
    imported=graft(radar,rs,table,ts,1599,1041);rr=refs(radar);rst=Styles(rs)
    rr[1041]['data']['m_Children'].sort(key=lambda c:c['rid']!=1601)
    box(rst,rr,1041,rst.pct(100),rst.pct(100));box(rst,rr,1601,rst.pct(100),rst.pct(50))
    graph(radar);validate_ui(radar,rs)
    detail=graft(doc,sheet,radar,rs,named(doc,'RightHiddenAttributesPanel'),1041)
    rr=refs(doc);st=Styles(sheet);box(st,rr,detail['root'],st.pct(50),st.pct(100))
    data(rr,detail['root'])['name']='MiddleNonHiddenSeasonRadarAndTwelveStats'
    # Restore the native status fallback in the vacated radar position.
    remove(doc,named(doc,'OverviewTopSeasonTwelveStats'))
    rr=refs(doc)
    for name in ['FirstOverviewNativeTransferStatusFallback','FirstOverviewFavouredPersonnelFallback']:
        i=named(doc,name);st.edit(rr[i],[st.p(131081,st.en('flex')),st.p(131105,st.pct(100)),st.p(131087,{'m_ValueType':1,'valueIndex':2}),st.p(131096,st.px(0)),st.p(131082,{'m_ValueType':1,'valueIndex':2}),st.p(131084,st.num(1)),st.p(131085,st.num(1))])
    assert not any('RightHidden' in data(rr,i).get('name','') for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2)
    graph(doc);validate_ui(doc,sheet)
    doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
    ab=next(o for o in oo.values()if o.type.name=='AssetBundle');meta=ab.read_typetree()
    def entry(pid):return next((k,v)for k,v in meta['m_Container']if v['asset']=={'m_FileID':0,'m_PathID':pid})
    key,e=entry(PAGE)
    meta['m_Container']=[(k,v) for k,v in meta['m_Container'] if k!=key or v['asset']=={'m_FileID':0,'m_PathID':PAGE}]
    assert [v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==key]==[PAGE]
    span=copy.deepcopy(meta['m_PreloadTable'][e['preloadIndex']:e['preloadIndex']+e['preloadSize']])
    keys=[]
    for pid in [SOURCE,RADAR,STATS]:
        k,en=entry(pid);keys.append(k)
        for ptr in meta['m_PreloadTable'][en['preloadIndex']:en['preloadIndex']+en['preloadSize']]:
            if ptr not in span:span.append(copy.deepcopy(ptr))
    e.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
    catpath=(root.parent if tag=='game'else root)/'catalog.bin';catbefore=catpath.read_bytes();cat=cm.Catalog(catbefore)
    cl=next(i for i in cat.locations(key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'));deps=list(cat.location(cl)['dependencies'])
    for k in keys:
        dl=next(i for i in cat.locations(k)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
        deps=list(dict.fromkeys(deps+cat.location(dl)['dependencies']))
    assert cat.location(deps[0])['internal'].endswith(W) and cl in cat.locations('GameWorldVisualTreeAssetPreload')
    if deps!=cat.location(cl)['dependencies']:
        raw=b''.join(struct.pack('<I',i)for i in deps);offset=cat.append(raw,True);struct.pack_into('<2I',cat.data,cl+12,offset,zlib.crc32(raw))
    changes={PAGE:doc,sid:sheet,ab.path_id:meta}
    for i,v in changes.items():oo[i].save_typetree(v)
    output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==oo.keys()
    for i,h in hashes.items():
        if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
    for i,v in changes.items():assert check[i].read_typetree()==v,('Serialization mismatch',i)
    add_tx(tag,root/W,output,before)
    catout=bytes(cat.data);hp=catpath.with_name('catalog.hash')
    if catout!=catbefore:add_tx(tag,catpath,catout,catbefore);add_tx(tag,hp,hashlib.md5(catout).hexdigest().encode(),hp.read_bytes())
    else:protected[str(catpath)]=sha(catbefore);protected[str(hp)]=sha(hp.read_bytes())
    checks.append(dict(target=tag,page=PAGE,hidden_source_page=SOURCE,existing_nonhidden_entry=True,radar_above_table=True,table_columns=2,table_rows=6,native_both_position_branches_and_cell_bindings_preserved=True,other_objects_byte_identical=True,serialization_readback=True,catalog_dependencies_and_preload_verified=True))
    print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for name,v in [('manifest.json',m),('transaction.json',tx)]: (OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-portrait-nonhidden-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
