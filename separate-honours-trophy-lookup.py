"""Isolate the installed legacy honour-row image requests from competition logos."""
from pathlib import Path
import sys,json,hashlib,datetime,struct,importlib.util,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cm',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
pack=Path('G:/Doc/Sports Interactive/Football Manager 27/graphics/sortitoutsi Trophies Megapack 2026.11')
out=R/('honours-trophy-logo-separated-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
tx=[];audit=[];protected={};mapping={}
for row in ET.parse(pack/'config.xml').findall('.//record[@to][@from]'):
    match=re.fullmatch(r'graphics/pictures/comp/(\d+)/trophy',row.get('to'))
    assert match,row.attrib
    uid=int(match[1])
    # The existing honour-row switch uses its trophy branch for IDs above 7.
    # Reserve all real continent IDs (1..8); do not occupy their image names.
    if uid<=8:continue
    image=(pack/row.get('from')).with_suffix('.png').resolve()
    assert image.is_relative_to(pack.resolve()) and image.is_file()
    key=f'continent_default_{uid}'
    assert key not in mapping or mapping[key]==image
    mapping[key]=image
assert len(mapping)>2000
def stage(tag,path,before,after):
    src=out/tag/path.name;bak=out/('backup-'+tag)/path.name
    src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True)
    src.write_bytes(after);bak.write_bytes(before)
    tx.append(dict(target=str(path),source=str(src),backup=str(bak),before=sha(before),after=sha(after)))
for tag,root in [('game',Path(cfg['aa_root'])),('skin',Path(cfg['skin_packages']))]:
    p=root/'catalog.bin';before=p.read_bytes();cat=cm.Catalog(before);keys=dict(cat.keys())
    assert not mapping.keys() & keys.keys(),'An alias already exists; inspect rather than overwrite.'
    records=list(cat.key_records)
    kind=next(cat.unpack(k,'2I')[0] for k,v in records if isinstance(cat.object(k),str))
    texture_type=next(cat.location(q)['raw'][6] for _,ls in keys.items() for q, in cat.array(ls,'I')[:1] if cat.location(q)['type'][1]=='UnityEngine.Texture2D')
    provider=cat.add_string('SI.Core.LocalAssetProvider')
    for key,image in sorted(mapping.items()):
        ko=cat.add_string(key);po=cat.add_string(image.as_posix())
        loc=cat.append(struct.pack('<7I',ko,po,provider,cm.NULL,0,cm.NULL,texture_type))
        obj=cat.append(struct.pack('<IHH',ko,0,0))
        records.append((cat.append(struct.pack('<II',kind,obj)),cat.append(struct.pack('<I',loc),True)))
    struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<II',*x) for x in records),True))
    after=bytes(cat.data);check=cm.Catalog(after);ck=dict(check.keys())
    assert check.key_records[:len(cat.key_records)]==cat.key_records
    assert set(ck)-set(keys)==set(mapping)
    for key,image in mapping.items():
        loc=check.location(check.array(ck[key],'I')[0][0])
        assert (loc['internal'],loc['provider'],loc['type'][1])==(image.as_posix(),'SI.Core.LocalAssetProvider','UnityEngine.Texture2D')
    stage(tag,p,before,after);hp=p.with_suffix('.hash');stage(tag,hp,hp.read_bytes(),hashlib.md5(after).hexdigest().encode('ascii'))
    folder=Path(cfg['bundle_root']) if tag=='game' else root
    for name in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualfunctions_assets_all.bundle']:
        file=folder/name
        if file.exists():protected[str(file)]=sha(file.read_bytes())
    audit.append(dict(target=tag,added_image_keys=len(mapping),all_existing_keys_and_locations_preserved=True))
# Stop the graphics importer from registering these trophy files as competition images.
# Direct catalogue aliases above keep using the same PNG files without copying them.
configs=[pack/'config.xml',pack/'default/config.xml',pack/'friendcup/config.xml']
for i,p in enumerate(configs):
    before=p.read_bytes();tree=ET.fromstring(before)
    maps=tree.find("list[@id='maps']");assert maps is not None
    assert all('/trophy' in row.get('to','') for row in maps)
    count=len(maps)
    for row in list(maps):maps.remove(row)
    amap=tree.find("boolean[@id='amap']")
    if amap is None:amap=ET.SubElement(tree,'boolean',id='amap')
    amap.set('value','false');ET.indent(tree,space='  ')
    after=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
    assert not ET.fromstring(after).findall('.//record[@to]')
    stage('graphics-'+str(i),p,before,after)
    audit.append(dict(config=str(p),generic_trophy_mappings_removed=count,images_preserved=True))
manifest=dict(installed=False,runtime_verified=False,protected_sha256=protected,audits=audit,
              note='Uses the existing honour-row legacy continent_default_<competition ID> requests, excludes continent IDs 1..8. No UI or bundle changes. Original comp/logo requests remain native. Restart required to rebuild imported graphics state.')
for name,value in [('manifest',manifest),('transaction',tx),('image-mapping',{k:str(v) for k,v in mapping.items()})]:
    (out/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
installer=installer.replace("assert p.resolve().parent in allowed or", "assert p.resolve() in "+repr({str(p.resolve()) for p in configs})+" or p.resolve().parent in allowed or")
# Compare strings for the three exact additional configuration targets.
installer=installer.replace('assert p.resolve() in ', 'assert str(p.resolve()) in ')
(out/'installer.py').write_text(installer,'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
    (out/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'README.md').write_text('荣誉奖杯与联赛Logo分离。保留全部原PNG及界面模板，只新增独立加载登记，并清空奖杯包原来的通用导入映射。英超11、英联杯1301426均有独立奖杯PNG；Logo包不改。原控件错误地使用ResourceType=11（Continent），本次仅适配其实际请求键，不把它描述成原生奖杯类型。保留洲际ID1–8不占用。正常退出游戏后运行install.ps1，重新进入后检查荣誉和联赛Logo；尚未游戏实测。restore.ps1校验哈希后回退。本地奖杯目录不能移动，更新catalog后须重新迁移登记。','utf8')
(R/'current-honours-trophy-logo-separation.json').write_text(json.dumps(dict(patch=str(out),installed=False,runtime_verified=False),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(patch=str(out),files=len(tx),trophy_keys=len(mapping),audits=audit),ensure_ascii=False),flush=True)
