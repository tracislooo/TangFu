"""Hide legacy label text via styles; center the existing radar without pruning."""
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
OUT=R/('test-radar-deduplicated-centered-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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
    stats=obs[-941100000001050].read_typetree();rr=refs(stats)
    label=obs[-941100000001052].read_typetree();lr=refs(label)
    stats_sheet=obs[-941100000001051].read_typetree();label_sheet=obs[-941100000001053].read_typetree()
    old_stats_sheet=copy.deepcopy(stats_sheet);old_label_sheet=copy.deepcopy(label_sheet)
    def edit_unique_rule(sheet,nodes,node,values):
        st=Styles(sheet);rule=nodes[node]['data']['m_RuleIndex']
        assert rule>=0
        assert [i for i,r in nodes.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
        props=sheet['m_Rules'][rule]['m_Properties']
        keys={p['m_Id']for p in values}
        sheet['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+values
        return rule
    # The native chart overrides its label root visibility. Hide only its text
    # leaves; keep the BindingRoot, switch tree, GUID and numeric bindings intact.
    legacy_text=[1003,1007,1011,1013]
    hidden_rules=set()
    for i in legacy_text:
        assert lr[i]['data']['m_FullTypeName']=='SI.Bindable.SIText'
        st=Styles(label_sheet)
        hidden_rules.add(edit_unique_rule(label_sheet,lr,i,[st.p(131081,st.en('none'))]))
    assert len(hidden_rules)==4
    # The hidden statistics wrapper consumes no height. Center the unchanged
    # 159px radar within its 249px root (45px free space above and below).
    st=Styles(stats_sheet)
    centered_rule=edit_unique_rule(stats_sheet,rr,1041,[st.p(131088,st.en('center'))])
    for sheet,old,allowed in [(label_sheet,old_label_sheet,hidden_rules),(stats_sheet,old_stats_sheet,{centered_rule})]:
        assert len(sheet['m_Rules'])==len(old['m_Rules'])
        for i,rule in enumerate(old['m_Rules']):
            if i not in allowed:assert sheet['m_Rules'][i]==rule
        for key,value in old.items():
            if key=='m_Rules':continue
            if key=='strings':assert sheet[key][:len(value)]==value
            else:assert sheet[key]==value
    column=named(stats,'WorkingNativeSeasonDataColumn')
    colprops=stats_sheet['m_Rules'][rr[column]['data']['m_RuleIndex']]['m_Properties']
    display=next(p for p in colprops if p['m_Id']==131081)['m_Values'][0]
    assert stats_sheet['strings'][display['valueIndex']]=='none'
    assert rr[1048]['data']['m_Children']==[{'rid':i}for i in [1058,1060,1063,1065]]
    names=[r.get('data',{}).get('name','')for r in rr.values()]
    assert sum(n.startswith('AxisTitle_seasonRadar')for n in names)==12
    assert sum(n.startswith('AxisValue_seasonRadar')for n in names)==12
    changes={-941100000001051:stats_sheet,-941100000001053:label_sheet}
    for i,sheet in changes.items():obs[i].save_typetree(sheet)
    output=env.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects}
    assert readback.keys()==obs.keys()
    for i,h in hashes.items():
        if i not in changes:assert sha(readback[i].get_raw_data())==h,('Unexpected change',i)
    for i,sheet in changes.items():assert readback[i].read_typetree()==sheet
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,changed_objects=list(changes),legacy_text_hidden=legacy_text,
        label_root_and_all_children_retained=True,all_ui_objects_and_bindings_byte_identical=True,
        direct_title_and_raw_value_labels_preserved=12,
        four_statistics_modules_preserved_and_hidden=True,
        vertical_center=dict(parent_height=249,radar_height=159,top_and_bottom_space=45),
        fixed_parent_basis_unchanged=True,original_ability_radar_unchanged=True,
        unrelated_objects_byte_identical=True))
    print('Verified '+tag+': styles only; all controls/bindings/cards preserved',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,
    previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,
    change='Hide four legacy template text leaves with display:none; vertically center the unchanged season radar; preserve hidden statistics modules without deletion')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'radar-deduplicated-centered-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
