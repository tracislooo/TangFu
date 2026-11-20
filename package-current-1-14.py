from pathlib import Path
import json,hashlib,zipfile,datetime,sys
R=Path.cwd();AA=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');O=R/'pinned-1-14-update-20261029-122441';m=json.loads((O/'manifest.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
files=[];different=[]
for n,h in m['after_sha256'].items():
 p=AA/'StandaloneWindows64'/n;actual=sha(p.read_bytes())
 if actual!=h:different.append(n)
 files.append((p,'aa/StandaloneWindows64/'+n,actual))
cat=(AA/'catalog.bin').read_bytes();assert (AA/'catalog.hash').read_text().strip()==hashlib.md5(cat).hexdigest()
for n in ['catalog.bin','catalog.hash']:
 p=AA/n;files.append((p,'aa/'+n,sha(p.read_bytes())))
assert not different,('Installed files changed since the completed update',different)
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));assert sha((AA/'StandaloneWindows64/ui-backgrounds_assets_common.bundle').read_bytes())==registry['source_bundle_sha256']
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S');dest=R/('FM27-置顶1-14完整修改包-'+stamp+'.zip');report={'created':stamp,'files':[{'path':arc,'size':p.stat().st_size,'sha256':h} for p,arc,h in files],'catalog_hash_verified':True,'matches_installed_update':True,'active_custom_images':180,'image_registry_version':73,'runtime_tested':False}
readme='''FM27 置顶1–14 完整修改包

包含：14个修改后的bundle及配套catalog.bin、catalog.hash，共16个游戏文件。

安装：
1. 完全退出游戏。
2. 先备份自己游戏目录 fm_Data/StreamingAssets/aa/ 中将要被替换的文件。
3. 将压缩包内的 aa 文件夹复制到游戏的 fm_Data/StreamingAssets/ 下，合并文件夹并覆盖对应文件。
   当前本机示例：F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/
4. catalog.bin、catalog.hash 与全部bundle作为一套安装，请勿混用旧版本。
5. 如需恢复，用安装前自己的备份覆盖回去。

本包对应2026-10-29本机游戏更新后的资源版本，其他游戏版本需要重新适配。资源/引用/目录与落盘校验已通过，尚未进行游戏内画面和交互实测。
保留V73的180张有效图片及原生背景覆盖；永久禁用70张和已删除TF patch未恢复。状态环辅助纹理保留。
独立安装的外部球员头像、队徽和其他graphics图片包不包含在本包中。
比赛轮播重启后的选择记忆及主裁判姓名仍按原记录属于未完成项。

修改清单见 修改说明.md；文件完整性见 文件校验清单.json。
'''
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,arc,h in files:z.write(p,arc)
 z.writestr('安装说明.txt',readme.encode('utf-8-sig'));z.writestr('文件校验清单.json',json.dumps(report,ensure_ascii=False,indent=2).encode('utf8'));z.writestr('修改说明.md',(O/'修改说明.md').read_bytes())
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for p,arc,h in files:assert sha(z.read(arc))==h,arc
assert all(sha(p.read_bytes())==h for p,arc,h in files)
print(json.dumps({'zip':str(dest),'size_bytes':dest.stat().st_size,'size_mib':round(dest.stat().st_size/1024**2,1),'game_files':len(files),'verified':True},ensure_ascii=False))
