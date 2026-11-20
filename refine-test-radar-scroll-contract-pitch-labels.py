"""Closer radar captions, contained report scrolling, clear contract, pitch groups."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'add_node','graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PAGE,STYLE=-941100000001020,-941100000001021
BASE,BASESTYLE=-940000000016000,-940000000016001
BASEKEY='de14e90fe14655249deefc697f132781'
OUT=R/('test-radar-scroll-clear-contract-groups-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
positions=[(100,23),(190,68),(190,153),(100,198),(30,153),(30,68)]
tx=[];checks=[]
for tag,root in roots:
    before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
    go={o.path_id:o for o in UnityPy.load(str(root/G)).objects}
    assert BASE in go and BASESTYLE in go
    # Reuse an already registered and preloaded private transparent native frame.
    meta=next(o.read_typetree()for o in go.values()if o.type.name=='AssetBundle')
    entry=next(v for k,v in meta['m_Container']if k==BASEKEY and v['asset']=={'m_FileID':0,'m_PathID':BASE})
    span=meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]
    assert {'m_FileID':0,'m_PathID':BASE}in span and {'m_FileID':0,'m_PathID':BASESTYLE}in span
    catpath=(root.parent if tag=='game'else root)/'catalog.bin';cat=cm.Catalog(catpath.read_bytes())
    assetlocs=[i for i in cat.locations(BASEKEY)if cat.location(i)['type'][1].endswith('VisualTreeAsset')]
    assert assetlocs
    label=next(ls for k,ls in cat.key_records if cat.object(k)=='GlobalVisualTreeAssetPreload')
    preload={v[0]for v in cat.array(label,'I')};assert set(assetlocs)<=preload
    for location in assetlocs:
        deps=cat.location(location)['dependencies'];assert deps
        assert G in str(cat.location(deps[0])),('Frame bundle dependency',cat.location(deps[0]))
    page=obs[PAGE].read_typetree();oldpage=copy.deepcopy(page);rr=refs(page);oldrefs=copy.deepcopy(rr)
    ps=obs[STYLE].read_typetree();oldps=copy.deepcopy(ps);pst=Styles(ps)
    stats=obs[-941100000001050].read_typetree();sr=refs(stats)
    ss=obs[-941100000001051].read_typetree();oldss=copy.deepcopy(ss);sst=Styles(ss)
    page_rules=set();stats_rules=set()
    def rule_edit(sheet,nodes,node,values,changed):
        rule=nodes[node]['data']['m_RuleIndex'];assert rule>=0
        assert [i for i,r in nodes.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
        keys={p['m_Id']for p in values};props=sheet['m_Rules'][rule]['m_Properties']
        sheet['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+values
        changed.add(rule)
    def pe(node,values):rule_edit(ps,rr,node,[pst.p(k,v)for k,v in values],page_rules)
    def se(node,values):rule_edit(ss,sr,node,[sst.p(k,v)for k,v in values],stats_rules)
    # Keep all real-data and chart nodes intact; move only direct caption blocks.
    case=named(stats,'WorkingSeasonRadarGoalkeeperSwitch');moved_labels=[]
    for branch in sr[case]['data']['m_Children']:
        overlay=next(c['rid']for c in sr[branch['rid']]['data']['m_Children']if data(sr,c['rid']).get('name')=='SeasonRadarDirectAxisLabels')
        blocks=sr[overlay]['data']['m_Children'];assert len(blocks)==6
        for axis,(child,(x,y))in enumerate(zip(blocks,positions)):
            se(child['rid'],[(131089,sst.px(x)),(131104,sst.px(y))])
            moved_labels.append(dict(branch=branch['rid'],axis=axis,left=x,top=y))
    data(rr,1043).update(LabelDistanceFromChart=6.,LabelDistanceFromChart_UxmlAttributeFlags=1)
    # Auto cross-axis height allows the existing 12px top margin to be deducted.
    # The old explicit 100% height + margin extended below the outer viewport.
    auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
    pe(6298,[(131087,auto),(131096,pst.px(0)),(131094,none),(131074,pst.en('stretch')),(131085,pst.num(1)),(131098,pst.px(6))])
    for node in [6306,7900,7901]:
        pe(node,[(131087,pst.px(0)),(131096,pst.px(0)),(131094,none),(131082,pst.px(0)),(131084,pst.num(1)),(131085,pst.num(1))])
    for node in [7903,7904]:pe(node,[(131094,none)])
    for node in [7907,7910]:
        pe(node,[(131090,pst.px(4)),(131096,pst.px(0))])
        assert data(rr,node)['DynamicElements']==1 and data(rr,node)['ClampSizeToPage']==0
    aliases=[]
    for using in page['m_Usings']:
        if using['alias']in ['TestContractUnavailable_tile-wide-4x2','TestContractEmpty_tile-wide-4x2']:
            assert using['path']=='f677caec43d6c1342b1bba39c5ae2c5f'
            using['path']=BASEKEY;aliases.append(using['alias'])
    assert len(aliases)==2
    # The existing top pitch band supplies space above the unchanged six columns.
    pe(7942,[(131102,pst.en('relative'))])
    proto_node=rr[8079];proto_sd=rr[proto_node['data']['m_SerializedData']['rid']]
    labels=[]
    for column,title in enumerate(['GK','D','DM','M','AM','ST']):
        node=add_node(page,(proto_node,proto_sd),7942,'TestPitchGroup_'+title);rr=refs(page)
        sd=data(rr,node);sd.update(text=title,text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=1,
            pickingMode=1,pickingMode_UxmlAttributeFlags=1,tooltip='',tooltip_UxmlAttributeFlags=1,
            IgnoreEmbeddedDataStyling=1,IgnoreEmbeddedDataStyling_UxmlAttributeFlags=1)
        sd['TextBinding']['m_kind']=0
        f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
        pst.edit(rr[node],[pst.p(131102,pst.en('absolute')),pst.p(131089,pst.pct(f32(column*100/6))),
            pst.p(131080,pst.px(0)),pst.p(131105,pst.pct(f32(100/6))),pst.p(131087,pst.px(18)),
            pst.p(131096,pst.px(18)),pst.p(131094,pst.px(18)),pst.p(131084,pst.num(0)),pst.p(131085,pst.num(0)),
            pst.p(65537,pst.px(11)),pst.p(65546,pst.en('middle-center')),pst.p(65552,pst.en('nowrap'))],reset=True)
        labels.append(dict(text=title,node=node,left_percent=f32(column*100/6),width_percent=f32(100/6)))
    # Old serialized data stays identical, except the native label distance.
    expected_native=copy.deepcopy(oldrefs[rr[1043]['data']['m_SerializedData']['rid']])
    expected_native['data'].update(LabelDistanceFromChart=6.,LabelDistanceFromChart_UxmlAttributeFlags=1)
    for i,old in oldrefs.items():
        if i==rr[1043]['data']['m_SerializedData']['rid']:assert rr[i]==expected_native
        elif i==7942:
            expected=copy.deepcopy(old);expected['data']['m_Children'] += [{'rid':x['node']}for x in labels];assert rr[i]==expected
        else:assert rr[i]==old,('Existing control or binding changed',i)
    for sheet,old,allowed in [(ps,oldps,page_rules),(ss,oldss,stats_rules)]:
        for i,rule in enumerate(old['m_Rules']):
            if i not in allowed:assert sheet['m_Rules'][i]==rule
        for key,value in old.items():
            if key=='m_Rules':continue
            if key in {'dimensions','floats','strings'}:assert sheet[key][:len(value)]==value
            else:assert sheet[key]==value
    graph(page);validate_ui(page,ps);validate_ui(stats,ss)
    changes={PAGE:page,STYLE:ps,-941100000001051:ss}
    for i,value in changes.items():obs[i].save_typetree(value)
    output=env.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects}
    assert readback.keys()==obs.keys()
    for i,h in hashes.items():
        if i not in changes:assert sha(readback[i].get_raw_data())==h,('Unexpected change',i)
    for i,value in changes.items():assert readback[i].read_typetree()==value
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,moved_radar_labels=moved_labels,native_label_distance=6,
        scroll_fix='auto right-column cross height, bounded flex descendants, bottom clearance',
        native_report_row_templates_and_bindings_unchanged=True,
        transparent_contract_frame=BASEKEY,transparent_frame_catalog_preload_verified=True,contract_aliases=aliases,
        pitch_group_labels=labels,pitch_position_bindings_and_geometry_unchanged=True,
        hidden_stat_modules_retained=True,all_old_controls_and_bindings_preserved=True,
        unrelated_objects_byte_identical=True))
    print('Verified '+tag+': closer labels, contained scroll, transparent contracts and GK/D/DM/M/AM/ST',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,
    previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,
    change='Move radar labels closer; remove pros/cons cross-axis height overflow; reuse registered transparent native contract frame; add GK D DM M AM ST pitch captions')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'test-four-refinements-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
