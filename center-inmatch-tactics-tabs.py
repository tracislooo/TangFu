"""Centre the existing in-match tactics tab group on the header row."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib,subprocess
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
    tree=ast.parse((R/fn).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
BN='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
OUT=R/('inmatch-tactics-tabs-centred-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={str(p):sha(p.read_bytes()) for _,root in roots for p in root.glob('*.bundle') if p.name!=BN}
tx=[];checks=[]
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game' else root)/name;protected[str(p)]=sha(p.read_bytes())
    before=(root/BN).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
    obj=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='OverviewHeader')
    d=obj.read_typetree();old=copy.deepcopy(d);rr={x['rid']:x for x in d['references']['RefIds']}
    sid=d['inlineSheet']['m_PathID'];s=oo[sid].read_typetree();st=Styles(s)
    assert rr[1073]['data']['m_Parent']=={'rid':1066}
    assert rr[1081]['data']['m_TemplateAlias']=='TopBarTacticsButtonGroup'
    def edit(i,props):st.edit(rr[i],[st.p(k,v) for k,v in props])
    edit(1033,[(131084,st.num(1)),(131085,st.num(1)),(131097,st.px(0))])
    edit(1035,[(131084,st.num(0)),(131105,st.px(0))])
    edit(1073,[(131073,st.en('center'))])
    edit(1081,[(131074,st.en('center')),(131084,st.num(0)),(131085,st.num(0))])
    for a in old['references']['RefIds']:
        expected=copy.deepcopy(a)
        if a['rid'] in [1033,1035,1073,1081]:expected['data']['m_RuleIndex']=rr[a['rid']]['data']['m_RuleIndex']
        assert expected==rr[a['rid']],('Unexpected non-style change',a['rid'])
    d['m_ContentHash']=zlib.crc32(json.dumps(s,sort_keys=True).encode())&0x7fffffff
    validate_ui(d,s);obj.save_typetree(d);oo[sid].save_typetree(s)
    raw=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
    assert set(saved)==set(oo)
    for i,h in hashes.items():
        if i not in [obj.path_id,sid]:assert sha(saved[i].get_raw_data())==h
    assert saved[obj.path_id].read_typetree()==d and saved[sid].read_typetree()==s
    src=OUT/tag/BN;backup=OUT/('backup-'+tag)/BN;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(raw);backup.write_bytes(before)
    tx.append(dict(target=str(root/BN),source=str(src),backup=str(backup),before=sha(before),after=sha(raw)))
    checks.append(dict(variant=tag,changed_nodes=[1033,1035,1073,1081],bindings_and_events_unchanged=True,all_other_objects_byte_identical=True,serialization_roundtrip=True,existing_vertical_offset_unchanged=True))
    print('Verified '+tag,flush=True)
manifest=dict(installed=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for name,data in [('manifest.json',manifest),('transaction.json',tx)]:
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
(R/'current-inmatch-tactics-tabs.json').write_text(json.dumps(dict(patch=str(OUT),restore=str(OUT/'restore.ps1'),alignment='center',runtime_verified=False),ensure_ascii=False,indent=2),'utf8')
print(OUT,flush=True)
subprocess.run([sys.executable,str(OUT/'installer.py'),str(OUT)],check=True)
