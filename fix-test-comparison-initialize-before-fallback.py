"""Initialize native position comparison before evaluating empty-list fallback."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
for fn,names in [('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'graph'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),fn,'exec'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PAGE=-941100000001020
OUT=R/('test-comparison-init-before-fallback-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
tx=[];checks=[]
for tag,root in roots:
    before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
    page=obs[PAGE].read_typetree();oldpage=copy.deepcopy(page);rr=refs(page);oldrefs=copy.deepcopy(rr)
    allowed=named(page,'TestComparisonAllowed');hasrows=named(page,'TestComparisonHasRows')
    initializer=named(page,'comparison-players-list-binding-setter')
    comparison=named(page,'OverviewAlwaysVisibleComparisonContent')
    table=named(page,'comparison-players-list-table')
    parent=rr[allowed]['data']['m_Parent']['rid']
    assert rr[allowed]['data']['m_Children'][1]=={'rid':hasrows}
    assert rr[hasrows]['data']['m_Children'][1]=={'rid':comparison}
    assert rr[comparison]['data']['m_Children']==[{'rid':initializer}]
    assert rr[initializer]['data']['m_Children']==[{'rid':table}]
    assert data(rr,hasrows)['AlwaysInstantiate']==0
    def ancestors(node):
        result=[]
        while node in rr and 'm_Parent'in rr[node].get('data',{}):
            node=rr[node]['data']['m_Parent']['rid'];result.append(node)
        return result
    assert hasrows in ancestors(initializer)
    # This native setter writes positionmask -> report.ReportSelectedPosition.
    # Nesting it under HasRows prevented an empty report from initializing.
    go={o.path_id:o for o in UnityPy.load(str(root/G)).objects}
    native_refs=refs(go[-940000000005000].read_typetree())
    assert data(rr,initializer)['BindFunction']==data(native_refs,1064)['BindFunction']
    assert b'report.ReportSelectedPosition'in bytes(data(rr,initializer)['BindFunction'][0]['m_inputs']['m_variable']['m_argumentBytes'])
    assert data(rr,table)['Binding']['m_direct']['Path']['m_path']=='report.ScoutedSquadComparisonPlayers'
    # Lift the unchanged original setter above both custom gates. Keep the table
    # inside the same visible branch, inheriting the same original setter scope.
    rr[parent]['data']['m_Children']=[{'rid':initializer}if c=={'rid':allowed}else c for c in rr[parent]['data']['m_Children']]
    rr[initializer]['data']['m_Parent']={'rid':parent}
    rr[initializer]['data']['m_Children']=[{'rid':allowed}]
    rr[allowed]['data']['m_Parent']={'rid':initializer}
    rr[comparison]['data']['m_Children']=[{'rid':table}]
    rr[table]['data']['m_Parent']={'rid':comparison}
    assert initializer in ancestors(allowed) and initializer in ancestors(hasrows)
    assert allowed not in ancestors(initializer) and hasrows not in ancestors(initializer)
    assert initializer in ancestors(table)
    changed_refs={parent,initializer,allowed,comparison,table}
    assert len(changed_refs)==5
    for i,old in oldrefs.items():
        if i in changed_refs:
            aa=copy.deepcopy(old);bb=copy.deepcopy(rr[i])
            for value in [aa,bb]:
                value['data'].pop('m_Parent',None);value['data'].pop('m_Children',None)
            assert aa==bb,('Non-hierarchy edit',i)
        else:assert rr[i]==old,('Existing binding or module changed',i)
    assert refs(page).keys()==oldrefs.keys()
    graph(page)
    # Use UnityPy's normal writer: this page already contains no modified types.
    # Match the repository's handling for legacy empty referenced data records.
    from UnityPy.helpers import TypeTreeHelper
    oldwrite=TypeTreeHelper.write_value
    helper=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef)and n.name=='write'],type_ignores=[]),'serializer','exec'))
    TypeTreeHelper.write_value=write
    obs[PAGE].save_typetree(page)
    output=env.file.save(packer='lz4');TypeTreeHelper.write_value=oldwrite
    readback={o.path_id:o for o in UnityPy.load(output).objects}
    assert readback.keys()==obs.keys()
    for i,h in hashes.items():
        if i!=PAGE:assert sha(readback[i].get_raw_data())==h,('Unrelated object changed',i)
    assert readback[PAGE].read_typetree()==page
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,only_changed_object=PAGE,changed_hierarchy_refs=sorted(changed_refs),
        native_position_initializer=initializer,initializer_now_ancestor_of_both_fallback_gates=True,
        native_initializer_function_unchanged=True,native_table_binding_unchanged=True,
        all_existing_serialized_data_and_binding_records_unchanged=True,
        original_contract_fallback_and_transparent_frame_preserved=True,
        styles_radar_pitch_labels_and_hidden_modules_unchanged=True,
        unrelated_objects_byte_identical=True))
    print('Verified '+tag+': original position initializer runs before fallback gates; all bindings/styles unchanged',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,
    previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,
    change='Move unchanged native ReportSelectedPosition initializer above both fallback gates to avoid empty-list initialization deadlock; preserve comparison and contract branches')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'test-comparison-init-fix-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
