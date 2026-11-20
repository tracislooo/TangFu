"""Read-only export of current main-skin bundles and paired catalog."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, sys, zipfile

R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
cfg=read(R/'current-game-location.json');AA=Path(cfg['aa_root']);GAME=Path(cfg['bundle_root'])
baseline=Path(read(R/'current-game-update-comparison.json')['archive'])
native={x['name']:x['sha256'] for x in read(baseline/'updated-all-bundle-hashes.json')}
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/'exports'/('FM27-当前主皮肤-顶部导航-'+stamp);OUT.mkdir(parents=True)
selected=set(read(R/'pinned-1-14-update-20261029-122441/manifest.json')['after_sha256'])
selected.update(read(R/'main-1-14-rebuild-20261102-101644/manifest.json')['after_sha256'])
guards={};changed=[]
for p in sorted(GAME.glob('*.bundle')):
    h=sha(p.read_bytes());guards[p.name]=h
    if h!=native.get(p.name):selected.add(p.name);changed.append(p.name)
print('Inventory verified; exporting',len(selected),'bundles',flush=True)
files=[]
for name in sorted(selected):
    source=GAME/name;raw=source.read_bytes();assert sha(raw)==guards[name]
    relative='aa/StandaloneWindows64/'+name;p=OUT/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    files.append(dict(path=relative,size=len(raw),sha256=sha(raw)))
cat=(AA/'catalog.bin').read_bytes();cat_hash=(AA/'catalog.hash').read_bytes()
assert cat_hash.decode().strip()==hashlib.md5(cat).hexdigest()
for name,raw in [('catalog.bin',cat),('catalog.hash',cat_hash)]:
    (OUT/'aa'/name).write_bytes(raw);files.append(dict(path='aa/'+name,size=len(raw),sha256=sha(raw)))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
c=cm.Catalog(cat);external={}
for key,ls in c.keys():
    for loc, in c.array(ls,'I'):
        v=c.location(loc)
        if v['provider']=='SI.Core.LocalAssetProvider':external.setdefault(v['internal'],set()).add(str(key))
external_rows=[dict(path=p,keys=sorted(keys),exists=Path(p).is_file()) for p,keys in external.items()]
(OUT/'外置图片依赖清单.json').write_text(json.dumps(external_rows,ensure_ascii=False,indent=2),'utf8')
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
e=UnityPy.load(str(OUT/'aa/StandaloneWindows64'/W))
assert not any('TFReferenceBookmarkSidebar' in (o.peek_name() or '') for o in e.objects if o.type.name=='MonoBehaviour')
report=dict(export_only=True,installed=False,runtime_verified=False,source=str(AA),navigation='top',exact_live_snapshot=True,native_baseline=str(baseline),files=files,modified_vs_native=changed,all_modified_bundles_included=True,external_image_count=len(external_rows),external_images_embedded=False)
(OUT/'文件校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'使用说明.txt').write_text('当前游戏实际安装的顶部导航主皮肤，保留现有球员页面选择器及悬浮层，未应用FC/大头像分组或侧边栏替换包。\n全部文件从当前游戏逐字节提取，包含主皮肤资源包及配套catalog.bin、catalog.hash；原版未改资源由游戏自身提供。\n以后安装时，完全退出游戏，备份同名文件，将本包aa文件夹合并覆盖至游戏fm_Data/StreamingAssets/。所有文件配套使用；游戏更新后须重新迁移。\n本次只导出，未安装或修改游戏、独立皮肤和用户设置。压缩包和源文件哈希已校验，未进行游戏内验证。\n球场图库、地图等外置图片由catalog中的原路径读取，本包附依赖清单，未包含这些外置图片；迁移到其他电脑时需另行迁移图片并适配路径。\n','utf-8-sig')
zp=OUT.with_suffix('.zip')
with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in OUT.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(zp) as z:
    assert z.testzip() is None
    for row in files:assert sha(z.read(row['path']))==row['sha256']
for name,h in guards.items():assert sha((GAME/name).read_bytes())==h,('Live source changed',name)
assert (AA/'catalog.bin').read_bytes()==cat and (AA/'catalog.hash').read_bytes()==cat_hash
(OUT/'导出验证.json').write_text(json.dumps(dict(passed=True,zip=str(zp),zip_sha256=sha(zp.read_bytes()),all_live_bundles_unchanged=True,catalog_unchanged=True,zip_entries_verified=True),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(zip=str(zp),files=len(files),size_mib=round(zp.stat().st_size/2**20,1),external_images=len(external_rows),external_missing=sum(not r['exists'] for r in external_rows),passed=True),ensure_ascii=True),flush=True)
