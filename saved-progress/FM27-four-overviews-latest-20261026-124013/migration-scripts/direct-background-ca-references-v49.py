import copy,hashlib,importlib.util,json,struct,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BN='ui-backgrounds_assets_common.bundle'
CAT=GAME.parent/'catalog.bin'
OUT=R/'CA卡面直接引用backgrounds修正-V49'
IDS=set(range(-910000000000007,-910000000000002))
sha=lambda b:hashlib.sha256(b).hexdigest()
world=(GAME/WN).read_bytes();background=(GAME/BN).read_bytes();catalog=CAT.read_bytes()
assert sha(world)=='c6b3dcacd3a66a4d1de4f4ee553efe0f55ccdd679e6aaddcffe96bf6d630bcab'
assert sha(background)=='b2bbb97be8da1f7e88a1c29df00cf131e3b545f70f64e4c3374dc05343662c63'
before={GAME/WN:world,SKIN/WN:(SKIN/WN).read_bytes(),CAT:catalog}
assert before[SKIN/WN]==world
protected={p:sha(p.read_bytes()) for p in [GAME/BN,GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',SKIN/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',GAME/'ui-visualfunctions_assets_all.bundle',GAME/'ui-tileslayouts_assets_all.bundle']}
be=UnityPy.load(background);bgaf=be.assets[0];bo=bgaf.objects
e=UnityPy.load(world);af=e.assets[0];obs=af.objects
hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
assert all(i in obs and obs[i].type.name=='Texture2D' for i in IDS)
bgpath=f'archive:/{bgaf.name}/{bgaf.name}'
assert all(ex.path!=bgpath for ex in af.externals)
external=copy.copy(af.externals[1]);external.path=bgpath;external.guid=bytes(16);external.type=0
af.externals.append(external);fileid=len(af.externals)
assert fileid==7

changed={};needles=[struct.pack('<q',i) for i in IDS];reference_count=0
def redirect(v):
    count=0
    if isinstance(v,dict):
        if v.get('m_FileID')==0 and v.get('m_PathID') in IDS:
            v['m_FileID']=fileid;count+=1
        for x in v.values():count+=redirect(x)
    elif isinstance(v,(list,tuple)):
        for x in v:count+=redirect(x)
    return count
for pid,o in list(obs.items()):
    if pid in IDS or not any(n in o.get_raw_data() for n in needles):continue
    old=o.read_typetree();new=copy.deepcopy(old);count=redirect(new)
    if count:
        assert o.type.name=='MonoBehaviour' and 'assets' in old
        assert len(old['assets'])==len(new['assets'])
        changed[pid]={'before':old,'after':new,'count':count}
        reference_count+=count;o.save_typetree(new)
assert len(changed)==8 and reference_count==40
styles=set(changed)

bundle=next(o for o in obs.values() if o.type.name=='AssetBundle')
meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta)
dep=bgaf.name.lower()
assert dep not in meta['m_Dependencies'];meta['m_Dependencies'].append(dep)
preload=oldmeta['m_PreloadTable'];updated_entries=[]
for index,(key,entry) in enumerate(meta['m_Container']):
    span=copy.deepcopy(preload[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
    if entry['asset']['m_FileID']==0 and entry['asset']['m_PathID'] in styles or any(p['m_FileID']==0 and p['m_PathID'] in styles for p in span):
        for pid in sorted(IDS):
            ptr={'m_FileID':fileid,'m_PathID':pid}
            if ptr not in span:span.append(ptr)
        entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span)
        meta['m_PreloadTable'].extend(span);updated_entries.append(index)
assert len(updated_entries)==13
bundle.save_typetree(meta)
for pid in IDS:del af.objects[pid]
newworld=e.file.save(packer='lz4')

# The catalog stores flattened bundle dependencies on each asset location.
spec=importlib.util.spec_from_file_location('catalog_editor',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
c=cm.Catalog(catalog)
locations={loc for _,p in c.keys() for (loc,) in c.array(p,'I')}
def bundle_location(suffix):
    found=[loc for loc in locations if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+suffix)]
    assert len(found)==1,(suffix,len(found))
    return found[0]
worldloc=bundle_location(WN);bgloc=bundle_location(BN)
dep_arrays={};modified_locations={}
for loc in sorted(locations):
    raw=c.unpack(loc,'7I');deps=[x[0] for x in c.array(raw[3],'I')]
    if worldloc not in deps or bgloc in deps:continue
    assert raw[4]==0
    if raw[3] not in dep_arrays:
        dep_arrays[raw[3]]=c.append(struct.pack('<'+'I'*(len(deps)+1),*(deps+[bgloc])),True)
    struct.pack_into('<I',c.data,loc+12,dep_arrays[raw[3]])
    modified_locations[loc]=deps
newcatalog=bytes(c.data);assert len(dep_arrays)==15 and len(modified_locations)==19764
cc=cm.Catalog(newcatalog);assert cc.keys()==cm.Catalog(catalog).keys()
oldc=cm.Catalog(catalog)
allowed_offsets=set()
for loc in locations:
    oldraw=oldc.unpack(loc,'7I');newraw=cc.unpack(loc,'7I')
    if loc in modified_locations:
        assert [x[0] for x in cc.array(newraw[3],'I')]==modified_locations[loc]+[bgloc]
        assert oldraw[:3]+oldraw[4:]==newraw[:3]+newraw[4:]
        allowed_offsets.update(range(loc+12,loc+16))
    else:assert oldraw==newraw
for i,(a,b) in enumerate(zip(catalog,newcatalog)):
    if i not in allowed_offsets:assert a==b,i

# Resolve the actual saved cross-bundle pointers, with no local texture fallback.
check=UnityPy.load(newworld,background)
wf=next(f for f in check.assets if f.name==af.name);saved=wf.objects
assert set(saved)==set(hashes)-IDS
assert wf.externals[fileid-1].path==bgpath
for pid,h in hashes.items():
    if pid in IDS:continue
    if pid in changed:assert saved[pid].read_typetree()==changed[pid]['after']
    elif pid==bundle.path_id:assert saved[pid].read_typetree()==meta
    else:assert sha(saved[pid].get_raw_data())==h,pid
resolved=[]
for pid in sorted(IDS):
    obj=PPtr(m_FileID=fileid,m_PathID=pid,assetsfile=wf).deref()
    assert obj.assets_file.name==bgaf.name and obj.get_raw_data()==bo[pid].get_raw_data()
    resolved.append({'name':obj.peek_name(),'file_id':fileid,'path_id':pid,'resolved_cab':obj.assets_file.name,'resolved_texture_sha256':sha(obj.get_raw_data())})
for o in saved.values():
    if not any(n in o.get_raw_data() for n in needles):continue
    t=o.read_typetree()
    def reject_local(v):
        if isinstance(v,dict):
            assert not(v.get('m_FileID')==0 and v.get('m_PathID') in IDS)
            for x in v.values():reject_local(x)
        elif isinstance(v,(list,tuple)):
            for x in v:reject_local(x)
    reject_local(t)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h

OUT.mkdir(exist_ok=True)
outputs={WN:newworld,'catalog.bin':newcatalog,BN:background}
for n,b in outputs.items():(OUT/n).write_bytes(b)
install=[]
for p,b in before.items():
    tag='skin' if p.parent==SKIN else 'game';backup=Path('回退')/tag/p.name
    (OUT/backup).parent.mkdir(parents=True,exist_ok=True);(OUT/backup).write_bytes(b)
    install.append({'target':str(p),'source':p.name,'backup':backup.as_posix(),'before_sha256':sha(b),'after_sha256':sha(outputs[p.name])})
m={'version':49,'installed':False,'game_runtime_verified':False,'image_source_bundle':BN,
   'background_sha256_unchanged':sha(background),'deleted_gameworld_texture_copies':sorted(IDS),
   'cross_bundle_reference_file_id':fileid,'background_external_path':bgpath,'resolved_references':resolved,
   'changed_style_count':len(changed),'redirected_style_references':reference_count,
   'updated_public_preload_entries':len(updated_entries),'catalog_locations_with_background_dependency':len(modified_locations),
   'unchanged_gameworld_assets_verified':len(hashes)-len(IDS)-len(changed)-1,
   'layout_and_binding_assets_unchanged':True,'install_files':install,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'直接引用校验记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for back in [False,True]:
    rows=[]
    for item in install:
        src=item['backup'] if back else item['source'];backup=item['source'] if back else item['backup']
        old=item['after_sha256'] if back else item['before_sha256'];new=item['before_sha256'] if back else item['after_sha256']
        rows.append("    @{ Target = '"+item['target']+"'; Source = '"+src+"'; Backup = '"+backup+"'; Before = '"+old+"'; After = '"+new+"' }")
    script="""$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$files = @(
"""+',\n'.join(rows)+"""
)
foreach ($item in $files) {
    if ((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before) { throw ('Bundle version mismatch: ' + $item.Target) }
    if ((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After) { throw 'Source bundle hash mismatch.' }
}
try {
    foreach ($item in $files) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force
        if ((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After) { throw 'Installed bundle hash mismatch.' }
    }
} catch {
    foreach ($item in $files) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Backup) -Destination $item.Target -Force }
    throw
}
Write-Host 'Complete.'
"""
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V49：纠正CA图片引用来源。\n五张CA图片仅保留在ui-backgrounds_assets_common.bundle中；该背景包的图片内容和文件字节保持V48。\n已移除gameworld中五张CA图片副本，将8处样式的40个纹理引用直接指向backgrounds的CAB（FileID 7）。\ngameworld仅保留界面结构、样式及跨包引用；图像数据从backgrounds加载。\n补全跨包外部引用、AssetBundle依赖、13个资源预加载范围与catalog中gameworld资源的backgrounds依赖。\n原卡面节点、能力切换、数值绑定及布局资源原始字节均保持不变。\n已在同时加载两个bundle且gameworld不含CA副本的条件下验证：全部跨包图片指针解析到backgrounds的同名纹理。\n安装更新游戏和皮肤工程的gameworld，以及游戏catalog；无需再次替换backgrounds。\n退出游戏后运行安装.ps1；回退.ps1恢复V48。游戏内实际显示待验证。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'version':49,'world_sha256':sha(newworld),'catalog_sha256':sha(newcatalog),'background_unchanged':True,'style_references_redirected':reference_count,'deleted_texture_copies':5,'all_external_pointers_resolve_to_backgrounds':True},ensure_ascii=False))
