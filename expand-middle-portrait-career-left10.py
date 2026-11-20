"""Expand career content left by another 10px while keeping its right boundary."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,subprocess,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','owned_refs','rid_links'}),('add-card-six-ratings.py',{'validate_ui'})]:
    t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001000
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-portrait-career-left10-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes()) for _,root in roots for p in root.glob('*.bundle') if p.name!=W}
for tag,root in roots:
    for n in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
    before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
    doc=oo[PAGE].read_typetree();old=copy.deepcopy(doc);rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree()
    image,=[i for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and data(rr,i).get('name')=='OverviewTopRightStatusPanel']
    props=sheet['m_Rules'][rr[image]['data']['m_RuleIndex']]['m_Properties']
    prior=[p for p in props if p['m_Id']==131099]
    assert len(prior)==1 and sheet['dimensions'][prior[0]['m_Values'][0]['valueIndex']]=={'unit':1,'value':49.0}
    st=Styles(sheet);st.edit(rr[image],[st.p(131099,st.px(39))])
    for i,value in refs(old).items():
        expected=copy.deepcopy(value)
        if i==image:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
        assert rr[i]==expected
    doc['m_ContentHash']=zlib.crc32(json.dumps(sheet,sort_keys=True).encode())&0x7fffffff
    validate_ui(doc,sheet)
    oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
    for i,h in hashes.items():
        if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
    assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
    src=OUT/tag/W;bak=OUT/('backup-'+tag)/W;src.parent.mkdir();bak.parent.mkdir();src.write_bytes(output);bak.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(src),backup=str(bak),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,career_left_padding_before_px=49,career_left_padding_px=39,expanded_left_px=10,right_boundary_unchanged=True,scroll_configuration_unchanged=True,portrait_and_crest_unchanged=True,other_nodes_and_bindings_identical=True,other_objects_byte_identical=True,serialization_readback=True))
    print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for n,v in [('manifest.json',m),('transaction.json',tx)]:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-portrait-career-left10-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
