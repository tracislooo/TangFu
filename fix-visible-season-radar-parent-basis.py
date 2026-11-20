"""Fix zero flex basis on the radar host; preserve all visible-source internals."""
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
BASE=R/'test-four-kpis-two-radars-20261115-100951'
OUT=R/('test-radar-parent-basis-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
index=R/'current-player-overview-test-variant.json'
previous=json.loads(index.read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
tx=[];checks=[]
for tag,root in roots:
    before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects}
    donor={o.path_id:o for o in UnityPy.load(str(BASE/tag/W)).objects}
    hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
    # The entire radar UI, numeric bindings and label assets must be exact.
    for i in [-941100000001050,-941100000001052,-941100000001053]:
        assert obs[i].get_raw_data()==donor[i].get_raw_data(),('Visible-source mismatch',i)
    page=obs[-941100000001020].read_typetree();pr=refs(page)
    donor_page=refs(donor[-941100000001020].read_typetree())
    assert pr[6304]==donor_page[6304] and pr[6305]==donor_page[6305]
    sheet=obs[-941100000001021].read_typetree();oldsheet=copy.deepcopy(sheet);st=Styles(sheet)
    rule=pr[2242]['data']['m_RuleIndex']
    assert [i for i,r in pr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[2242]
    def resolved(s,idx):
        return {p['m_Id']:[s[poolmap[h['m_ValueType']]][h['valueIndex']]if h['m_ValueType']in poolmap else h for h in p['m_Values']]for p in s['m_Rules'][idx]['m_Properties']}
    old=resolved(sheet,rule)
    assert old[131082]==[{'unit':1,'value':0.0}] and old[131084]==[0.0]
    changes=[st.p(131082,st.px(249)),st.p(131085,st.num(0)),st.p(131096,st.px(249))]
    keys={p['m_Id']for p in changes}
    props=sheet['m_Rules'][rule]['m_Properties']
    sheet['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+changes
    fixed=resolved(sheet,rule)
    assert fixed[131087]==fixed[131082]==fixed[131096]==[{'unit':1,'value':249.0}]
    assert fixed[131084]==fixed[131085]==[0.0]
    assert len(sheet['m_Rules'])==len(oldsheet['m_Rules'])
    for i,value in enumerate(oldsheet['m_Rules']):
        if i!=rule:assert sheet['m_Rules'][i]==value
    # Radar/card styles remain untouched from the latest layout.
    radar_sheet=obs[-941100000001051].read_typetree()
    radar_refs=refs(obs[-941100000001050].read_typetree())
    column=named(obs[-941100000001050].read_typetree(),'WorkingNativeSeasonDataColumn')
    assert resolved(radar_sheet,radar_refs[column]['data']['m_RuleIndex'])[131081]==['none']
    obs[-941100000001021].save_typetree(sheet)
    output=env.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects}
    assert readback.keys()==obs.keys()
    for i,h in hashes.items():
        if i!=-941100000001021:assert sha(readback[i].get_raw_data())==h,('Unexpected change',i)
    assert readback[-941100000001021].read_typetree()==sheet
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir();source.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(source),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,only_changed_object=-941100000001021,only_changed_rule_node=2242,
        before_host_style=old,after_host_style=fixed,
        exact_visible_source_ui_labels_and_bindings=True,
        latest_radar_style_unchanged=True,four_upper_modules_still_hidden=True,
        native_radar_and_identity_unchanged=True,unrelated_objects_byte_identical=True))
    print('Verified '+tag+': fixed zero-basis host; radar internals unchanged',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,
    previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,
    change='Fix radar host flex-basis from 0px to 249px, min-height to 249px and flex-shrink to 0; no radar or page node changes')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'radar-parent-basis-fix-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
