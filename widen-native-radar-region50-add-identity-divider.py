"""Widen the original radar by 50px and add a matching identity divider."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('test-native-radar-width250-dividers-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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
    page=obs[-941100000001020].read_typetree();rr=refs(page)
    sheet=obs[-941100000001021].read_typetree();old=copy.deepcopy(sheet);st=Styles(sheet)
    def props(node):
        return {p['m_Id']:p for p in sheet['m_Rules'][rr[node]['data']['m_RuleIndex']]['m_Properties']}
    def dimension(node,key):
        h=props(node)[key]['m_Values'][0];assert h['m_ValueType']==3
        value=sheet['dimensions'][h['valueIndex']];assert value['unit']==1
        return value['value']
    assert dimension(1173,131105)==dimension(1173,131082)==540
    assert dimension(1026,131105)==200
    assert dimension(2242,131105)==300
    assert dimension(2242,131082)==249 # retain the zero-height fix
    color_handle=props(6288)[458752]['m_Values'][0]
    assert color_handle['m_ValueType']==4
    matching_color=copy.deepcopy(sheet['colors'][color_handle['valueIndex']])
    updates={
        1173:[st.p(131105,st.px(590)),st.p(131082,st.px(590)),
              st.p(131077,st.px(1)),st.p(458761,st.h(4,matching_color))],
        1026:[st.p(131105,st.px(250))],
    }
    modified=set()
    for node,values in updates.items():
        rule=rr[node]['data']['m_RuleIndex']
        assert [i for i,r in rr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
        keys={p['m_Id']for p in values}
        oldprops=sheet['m_Rules'][rule]['m_Properties']
        sheet['m_Rules'][rule]['m_Properties']=[p for p in oldprops if p['m_Id']not in keys]+values
        modified.add(rule)
    assert len(modified)==2 and len(sheet['m_Rules'])==len(old['m_Rules'])
    for i,rule in enumerate(old['m_Rules']):
        if i not in modified:assert sheet['m_Rules'][i]==rule
    for key,value in old.items():
        if key=='m_Rules':continue
        if key in {'dimensions','colors'}:assert sheet[key][:len(value)]==value
        else:assert sheet[key]==value
    assert dimension(1173,131105)==dimension(1173,131082)==590
    assert dimension(1026,131105)==250 and dimension(1026,131089)==308
    assert dimension(6288,131089)==304 # moves 50px left with the wider right-anchored frame
    assert 308+250<=590
    obs[-941100000001021].save_typetree(sheet)
    output=env.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects}
    assert readback.keys()==obs.keys()
    for i,h in hashes.items():
        if i!=-941100000001021:assert sha(readback[i].get_raw_data())==h,('Unexpected change',i)
    assert readback[-941100000001021].read_typetree()==sheet
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,only_changed_object=-941100000001021,changed_rule_nodes=list(updates),
        original_radar_width_before=200,original_radar_width_after=250,
        overall_right_region_before=540,overall_right_region_after=590,
        new_radar_width_unchanged=300,middle_divider_moves_with_frame=True,
        new_identity_divider_width=1,new_identity_divider_color=matching_color,
        vertical_center_and_title_dedup_unchanged=True,
        all_ui_bindings_and_hidden_statistics_modules_unchanged=True,unrelated_objects_byte_identical=True))
    print('Verified '+tag+': original radar 250px; matching identity divider; style-only changes',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,
    previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,
    change='Original radar region 200 to 250px; enclosing right region 540 to 590px with divider moving with it; add 1px left border matching the existing radar divider')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'native-radar-width250-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
