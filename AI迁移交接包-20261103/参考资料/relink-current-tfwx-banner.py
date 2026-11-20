"""Resolve the banner's TFWX pointer against the latest installed background bundle."""
from pathlib import Path
R=Path(__file__).resolve().parent
base=(R/'start-banner-video520-tfwx120.py').read_text('utf8')
exec(compile(base.split("assert rr[1002]['data']['m_Children']==[{'rid':1004}]")[0],'current-bundles-and-validators','exec'))
parsed=ast.parse(base)
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ['val','px','en','num','style','styled']],type_ignores=[]),'style-helpers','exec'))
nr=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement' and data(i).get('name')=='StartScreenTFWX')
assert styled(1004,131105)=={'unit':1,'value':390.0}
assert styled(nr,131105)=={'unit':1,'value':240.0}
assert styled(nr,131087)=={'unit':1,'value':112.0}
assert styled(nr,262153)=='scale-to-fit'
expected_path=f'archive:/{ba.name}/{ba.name}'
matches=[i+1 for i,x in enumerate(a.externals) if x.path==expected_path]
assert len(matches)==1
ptr={'m_FileID':matches[0],'m_PathID':PID};previous=copy.deepcopy(styled(nr,458753));changed=previous!=ptr
if changed:style(nr,[(458753,val(6,ptr))])
validate_ui(d,s)
if changed:
 obj.save_typetree(d);a.objects[sid].save_typetree(s);outbytes=e.file.save(packer='lz4')
else:outbytes=before[GAME/INTRO]
sa=UnityPy.load(outbytes).assets[0]
for i,h in hashes.items():
 if changed and i in [obj.path_id,sid]:assert sa.objects[i].read_typetree()=={obj.path_id:d,sid:s}[i]
 else:assert sha(sa.objects[i].get_raw_data())==h
retired_absent(sa)
link_checks=[]
for folder in [GAME,SKIN]:
 bg_bytes=(folder/BG).read_bytes();assert bg_bytes==bgb
 linked=UnityPy.load(outbytes,bg_bytes);la=next(x for x in linked.assets if x.name==a.name)
 resolved=PPtr(m_FileID=ptr['m_FileID'],m_PathID=PID,assetsfile=la).deref();tree=resolved.read_typetree()
 assert resolved.peek_name()=='TFWX' and sha(resolved.get_raw_data())==tf['texture_sha256']
 assert [tree['m_Width'],tree['m_Height']]==tf['size']
 link_checks.append({'folder':str(folder),'texture':'TFWX','size':tf['size'],'texture_sha256':tf['texture_sha256'],'pointer':ptr,'latest_texture_resolved':True})
worlds={name:UnityPy.load(str(GAME/name)).assets[0] for name in [WORLD,GLOBAL]}
exec(compile(base[base.index("outputs={GAME/INTRO:outbytes,SKIN/INTRO:outbytes};audits=[]"):base.index("agents_text=before[agents].decode('utf8')")],'catalog-audit','exec'))
if not changed:
 outputs.pop(GAME/INTRO);outputs.pop(SKIN/INTRO)
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('relink-tfwx-latest-'+stamp);out.mkdir()
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
items=[]
for p,b in outputs.items():
 tag='game' if p.parent in [AA,GAME] else 'skin';source=Path(tag)/p.name;backup=Path('backup-'+tag)/p.name
 for rel,content in [(source,b),(backup,before[p])]:
  (out/rel).parent.mkdir(exist_ok=True);(out/rel).write_bytes(content)
 items.append({'target':str(p),'source':source.as_posix(),'backup':backup.as_posix(),'before_sha256':sha(before[p]),'after_sha256':sha(b)})
report={'installed':not outputs,'runtime_verified':False,'registry_version':registry['version'],'texture_size':tf['size'],'association_already_current':not changed,'pointer':ptr,'link_checks':link_checks,'video_size':[390,112],'tfwx_slot':[240,112],'all_current_texture_hashes_verified':len(registry['textures']),'catalog_audits':audits,'install_files':items,'protected_sha256':{str(p):h for p,h in protected.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
if outputs:install(out)
print(json.dumps({'verified':True,'reference_changed':changed,'updated_files':len(outputs),'registry_version':registry['version'],'texture_size':tf['size'],'video_size':[390,112],'tfwx_slot':[240,112],'output':str(out)},ensure_ascii=False))
