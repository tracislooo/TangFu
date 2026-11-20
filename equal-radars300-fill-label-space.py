"""Equal 300px radar regions; enlarge plots and use their full 249px height."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('test-equal-radars300-full-area-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
rects=[(100,4,100,28),(220,56,80,28),(220,165,80,28),(100,217,100,28),(0,165,80,28),(0,56,80,28)]
for x,y,w,h in rects:assert 0<=x<x+w<=300 and 0<=y<y+h<=249
for i,(x,y,w,h)in enumerate(rects):
    for xx,yy,ww,hh in rects[i+1:]:
        assert x+w<=xx or xx+ww<=x or y+h<=yy or yy+hh<=y
tx=[];checks=[]
for tag,root in roots:
    before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
    page=obs[-941100000001020].read_typetree();old_page=copy.deepcopy(page);pr=refs(page)
    stats=obs[-941100000001050].read_typetree();rr=refs(stats)
    ps=obs[-941100000001021].read_typetree();old_ps=copy.deepcopy(ps);pst=Styles(ps)
    ss=obs[-941100000001051].read_typetree();old_ss=copy.deepcopy(ss);sst=Styles(ss)
    page_rules=set();stats_rules=set()
    def edit(sheet,nodes,node,values,changed):
        rule=nodes[node]['data']['m_RuleIndex'];assert rule>=0
        assert [i for i,r in nodes.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
        keys={p['m_Id']for p in values}
        props=sheet['m_Rules'][rule]['m_Properties']
        sheet['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+values
        changed.add(rule)
    def se(node,values):edit(ss,rr,node,[sst.p(k,v)for k,v in values],stats_rules)
    def pe(node,values):edit(ps,pr,node,[pst.p(k,v)for k,v in values],page_rules)
    # Keep the proven host height/basis; expand only the original radar width.
    pe(1173,[(131105,pst.px(610)),(131082,pst.px(610))])
    pe(1026,[(131105,pst.px(300))])
    pe(1043,[(131087,pst.px(249)),(131096,pst.px(249)),(131094,pst.px(249)),(131082,pst.px(249)),(131085,pst.num(0))])
    native=data(pr,1043)
    native.update(SpiderChartRadiusPercentage=36.,LabelDistanceFromChart=10.,
                  SpiderChartRadiusPercentage_UxmlAttributeFlags=1,LabelDistanceFromChart_UxmlAttributeFlags=1)
    expected_page=copy.deepcopy(old_page)
    data(refs(expected_page),1043).update(SpiderChartRadiusPercentage=36.,LabelDistanceFromChart=10.,
                  SpiderChartRadiusPercentage_UxmlAttributeFlags=1,LabelDistanceFromChart_UxmlAttributeFlags=1)
    assert page==expected_page # only native presentation parameters, no binding changes
    case=named(stats,'WorkingSeasonRadarGoalkeeperSwitch')
    se(case,[(131087,sst.px(249)),(131096,sst.px(249)),(131094,sst.px(249))])
    labels=[]
    for branch in rr[case]['data']['m_Children']:
        outer=branch['rid']
        overlays=[c['rid']for c in rr[outer]['data']['m_Children']if data(rr,c['rid']).get('name')=='SeasonRadarDirectAxisLabels']
        assert len(overlays)==1;overlay=overlays[0]
        se(overlay,[(131087,sst.px(249)),(131096,sst.px(249)),(131094,sst.px(249))])
        blocks=rr[overlay]['data']['m_Children'];assert len(blocks)==6
        for axis,(block,rect)in enumerate(zip(blocks,rects)):
            node=block['rid'];x,y,w,h=rect
            se(node,[(131089,sst.px(x)),(131104,sst.px(y)),(131105,sst.px(w)),(131087,sst.px(h)),(131096,sst.px(h)),(131094,sst.px(h))])
            title,gate=[c['rid']for c in rr[node]['data']['m_Children']]
            missing,number=[c['rid']for c in rr[gate]['data']['m_Children']]
            assert data(rr,title)['name'].startswith('AxisTitle_seasonRadar')
            assert data(rr,number)['name'].startswith('AxisValue_seasonRadar')
            for child in [title,gate,missing,number]:
                se(child,[(131087,sst.px(14)),(131096,sst.px(14)),(131094,sst.px(14))])
            se(title,[(65537,sst.px(11))])
            for child in [missing,number]:se(child,[(65537,sst.px(12))])
            labels.append(dict(branch=outer,axis=axis,bounds=rect,title=title,value=number))
    assert len(labels)==12
    # Every data node, template and hidden module in the season VTA is unchanged.
    assert stats==obs[-941100000001050].read_typetree()
    assert rr[1048]['data']['m_Children']==[{'rid':i}for i in [1058,1060,1063,1065]]
    for sheet,old,allowed in [(ps,old_ps,page_rules),(ss,old_ss,stats_rules)]:
        assert len(sheet['m_Rules'])==len(old['m_Rules'])
        for i,value in enumerate(old['m_Rules']):
            if i not in allowed:assert sheet['m_Rules'][i]==value
        for key,value in old.items():
            if key=='m_Rules':continue
            if key in {'dimensions','floats'}:assert sheet[key][:len(value)]==value
            else:assert sheet[key]==value
    changes={-941100000001020:page,-941100000001021:ps,-941100000001051:ss}
    for i,value in changes.items():obs[i].save_typetree(value)
    output=env.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects}
    assert readback.keys()==obs.keys()
    for i,h in hashes.items():
        if i not in changes:assert sha(readback[i].get_raw_data())==h,('Unexpected change',i)
    for i,value in changes.items():assert readback[i].read_typetree()==value
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,equal_region_widths=[300,300],radar_height=249,
        overall_right_region=610,new_radar_height_before=159,new_radar_height_after=249,
        native_radius_percentage=36,native_label_distance=10,
        direct_label_bounds=labels,label_rectangles_inside_region_and_nonoverlapping=True,
        direct_title_font=11,direct_value_font=12,
        all_season_ui_nodes_bindings_and_hidden_modules_byte_identical=True,
        native_bindings_unchanged=True,duplicate_label_hiding_unchanged=True,
        both_dividers_preserved=True,host_zero_basis_fix_preserved=True,
        unrelated_objects_byte_identical=True))
    print('Verified '+tag+': two 300x249 regions; enlarged charts; label geometry passes',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,
    previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,
    change='Equal 300px radar regions; season radar uses full 249px height with larger perimeter labels; original radar enlarged with full-height chart and radius 36; all statistic bindings preserved')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'equal-radars300-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
