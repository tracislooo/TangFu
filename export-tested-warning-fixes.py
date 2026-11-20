from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parent
AA=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa')
OUT=R/'exports/FM27-main-warning-fixes-20261111';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
transactions=['game-retired-image-cleanup-20261111-195101','game-retired-image-cleanup-20261111-195226','small-match-texture-fix-20261111-201626']
rows=[]
for txn in transactions:
 m=json.loads((R/txn/'manifest.json').read_text('utf8'))
 files=m.get('files',[m])
 for row in files:
  p=Path(row['target'])
  if not p.is_relative_to(AA) or p.suffix!='.bundle':continue
  b=p.read_bytes();assert sha(b)==row['after'],str(p)+' changed since validation'
  rel=p.relative_to(AA);q=OUT/'aa'/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
  rows.append({'path':rel.as_posix(),'before_sha256':row['before'],'after_sha256':sha(b),'size':len(b)})
assert len(rows)==5
manifest={'source':'Current installed main skin, 2026-11-11','files':rows,'catalog_included':False,'local_test':{'unknown_pseudo_class':0,'invalid_texture_enum':0,'invalid_image':0,'small_grid_error':0,'texture_format_fallback':0},'unresolved':['SerializeReference Refid -2','PanelSettings theme stylesheet warnings','Exit JobTempAlloc warnings'],'crash_fix_proven':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
readme='''FM27 主皮肤警告修复文件（2026-11-11）

共5个资源文件，基于发送方当前主皮肤制作。仅供使用同一主皮肤及匹配游戏资源版本的人测试；其他版本直接覆盖可能覆盖其界面修改或造成资源不匹配。

使用方法：
1. 完全退出游戏。
2. 备份接收方游戏 fm_Data/StreamingAssets/aa/StandaloneWindows64 下的这5个同名文件。
3. 将本包 aa 目录内文件按相同层级复制到接收方游戏 fm_Data/StreamingAssets/aa 下。
4. 启动游戏，复现原来闪退时的操作。记录操作和时间；退出后保留 Player.log。若仍闪退，同时保留最新 crash dumps。
5. 如出现新问题，退出游戏，将第2步备份的5个文件原位恢复。请使用接收方自己的备份。

修复范围：无效伪类、废弃空背景层、非法背景图片值、Small比赛布局副本及预加载、23张纹理的RGBA32格式兼容。
发送方本次运行上述5类警告均为0；这不能证明已修复接收方的闪退。
尚未修复：Refid -2序列化缺项、主题样式表提示、退出时JobTempAlloc提示。
本包不包含catalog.bin/catalog.hash，不应混入其他版本的目录文件。
manifest.json记录5文件的修复前/后SHA256。接收方原文件若既不匹配before也不匹配after，请先确认资源版本，不要直接覆盖。
'''
(OUT/'使用说明.txt').write_text(readme,'utf-8-sig')
z=OUT.with_suffix('.zip')
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in OUT.rglob('*'):
  if p.is_file():f.write(p,p.relative_to(OUT))
with zipfile.ZipFile(z) as f:
 assert f.testzip() is None
 for row in rows:assert sha(f.read('aa/'+row['path']))==row['after_sha256']
print(json.dumps({'zip':str(z),'size_MB':round(z.stat().st_size/1024**2,1),'bundle_count':len(rows)}))
