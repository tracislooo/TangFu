from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path.cwd();G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');O=R/'main-1-14-rebuild-20261102-101644';m=json.loads((O/'manifest.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();state=json.loads((R/'current-sidebar-version.json').read_text('utf8'))
names=list(m['after_sha256'])
for n in ['ui-fonts_assets_production.bundle','ui-fonts_assets_fmuniverse.bundle']:
 if n not in names:names.append(n)
files=[]
for n in names:
 p=G/'StandaloneWindows64'/n;b=p.read_bytes();h=sha(b)
 if n in m['after_sha256'] and h!=m['after_sha256'][n]:
  p=O/n;assert p.exists(),('Missing main version file',n);b=p.read_bytes();h=sha(b);assert h==m['after_sha256'][n]
 files.append((p,'aa/StandaloneWindows64/'+n,h))
for n in ['catalog.bin','catalog.hash']:
 p=O/n;files.append((p,'aa/'+n,sha(p.read_bytes())))
assert (O/'catalog.hash').read_text().strip()==hashlib.md5((O/'catalog.bin').read_bytes()).hexdigest()
r=json.loads((R/'current-custom-textures.json').read_text('utf8'));assert sha((G/'StandaloneWindows64/ui-backgrounds_assets_common.bundle').read_bytes())==r['source_bundle_sha256']
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');dest=R/('FM27-当前主版本-无侧栏-'+stamp+'.zip');report={'created':stamp,'mode':'non-sidebar','files':[{'path':arc,'size':p.stat().st_size,'sha256':h} for p,arc,h in files],'catalog_hash_verified':True,'active_custom_images':len(r['textures']),'runtime_tested':False}
readme='''FM27 当前已安装主版本（不含侧边栏）

文件采用本次已完成的1–14主版本资源；当前目录出现并行侧栏变更的文件取已校验主版本成品，含14个bundle及配套catalog.bin、catalog.hash，共16个游戏文件。
包含最新1–14主版本修改和合同页面修复。未加入侧栏归档、试装包或书签预设；未包含整个游戏程序及外部头像/队徽图片包。

安装：退出游戏，先备份自己的对应原文件，再将本包aa文件夹复制到游戏的fm_Data/StreamingAssets/下，合并并覆盖。
本机路径：F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/
catalog与bundle必须配套安装，不要混用旧文件。恢复时使用自己安装前的备份。
本包适用于当前本机资源版本；不同游戏版本需重新适配。
已核对文件哈希、catalog配套及压缩包完整性，未启动游戏进行画面与交互验收。
'''
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,arc,h in files:z.write(p,arc)
 z.writestr('安装说明.txt',readme.encode('utf-8-sig'));z.writestr('文件校验清单.json',json.dumps(report,ensure_ascii=False,indent=2).encode('utf8'));z.writestr('修改说明.md',(O/'修改说明.md').read_bytes())
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for p,arc,h in files:assert sha(z.read(arc))==h
assert all(sha(p.read_bytes())==h for p,arc,h in files),'Game changed during packaging'
print(json.dumps({'zip':str(dest),'size_mib':round(dest.stat().st_size/1024**2,1),'files':len(files),'verified':True},ensure_ascii=False))
