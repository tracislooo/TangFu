"""Resolve the middle FC GUID to exactly one current page in each bundle."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
tree=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'serializer','exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
KEY='1f6ebbeeaeba50cbbb57ef2d123b47dc';PAGE=-930000000001001
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/('middle-fc-unique-guid-'+stamp);OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
tx=[];checks=[]
protected={str(p):sha(p.read_bytes()) for _,root in roots for p in root.glob('*.bundle') if p.name!=W}
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game' else root)/name;protected[str(p)]=sha(p.read_bytes())
    before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
    ab=next(o for o in oo.values() if o.type.name=='AssetBundle');meta=ab.read_typetree();oldmeta=copy.deepcopy(meta)
    entries=[(k,e) for k,e in meta['m_Container'] if k==KEY]
    assert len(entries)==2 and {e['asset']['m_PathID'] for _,e in entries}=={PAGE,-950000000000187}
    kept=next((k,e) for k,e in entries if e['asset']=={'m_FileID':0,'m_PathID':PAGE})
    meta['m_Container']=[(k,e) for k,e in meta['m_Container'] if k!=KEY or e['asset']=={'m_FileID':0,'m_PathID':PAGE}]
    assert [(k,e) for k,e in meta['m_Container'] if k==KEY]==[kept]
    assert [x for x in oldmeta['m_Container'] if x[0]!=KEY]==[x for x in meta['m_Container'] if x[0]!=KEY]
    assert meta['m_PreloadTable']==oldmeta['m_PreloadTable']
    doc=oo[PAGE].read_typetree();old=copy.deepcopy(doc)
    marker=zlib.crc32(json.dumps(doc,ensure_ascii=False,sort_keys=True).encode('utf8')) & 0x7fffffff
    assert marker!=old['m_ContentHash'];doc['m_ContentHash']=marker
    assert {k:v for k,v in doc.items() if k!='m_ContentHash'}=={k:v for k,v in old.items() if k!='m_ContentHash'}
    oo[PAGE].save_typetree(doc);ab.save_typetree(meta)
    output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
    assert new.keys()==oo.keys()
    for i,h in hashes.items():
        if i not in [PAGE,ab.path_id]:assert sha(new[i].get_raw_data())==h,('Unrelated object changed',i)
    assert new[PAGE].read_typetree()==doc and new[ab.path_id].read_typetree()==meta
    src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,guid=KEY,previous_candidates=[e['asset']['m_PathID'] for _,e in entries],unique_resolved_page=PAGE,old_content_hash=old['m_ContentHash'],new_content_hash=marker,all_other_objects_byte_identical=True,catalog_and_preload_unchanged=True))
    print('Verified '+tag+': GUID uniquely resolves to updated page',flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,change='Remove duplicate legacy middle FC container entry; refresh modified page content hash',protected_sha256=protected,checks=checks)
for name,value in [('manifest.json',m),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-fc-unique-guid-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
