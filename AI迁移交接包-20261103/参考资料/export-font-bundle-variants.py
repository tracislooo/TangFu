import sys, json, datetime
from pathlib import Path
R=Path.cwd()
base=(R/'replace-game-fonts-rounded.py').read_text(encoding='utf-8-sig')
# Reuse the validated font replacement logic; remove the entire installation section.
base=base.split('\ntry:\n for p,old,new in pending:')[0]
base=base.replace("for tag,folder in [('game',game)]:", "for tag,folder in []:")
base=base.replace("out=R/('font-rounded-replacement-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir(); (out/source.name).write_bytes(data)", "out=export_root/variant;out.mkdir()")
export_root=R/('font-bundle-variants-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));export_root.mkdir()
location=json.loads((R/'current-game-location.json').read_text(encoding='utf-8-sig'))
game_dir=Path(location['bundle_root'])
import hashlib
sha256=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bundle_names=['ui-fonts_assets_production.bundle','ui-fonts_assets_fmuniverse.bundle']
initial={n:sha256(game_dir/n) for n in bundle_names}
for variant in ['UOS黑体M','霞鹭文楷']:
 src='K:/桌面/27skin/fonts/'+variant+'.ttf'
 code=base.replace('K:/桌面/27skin/fonts/FM圆体.ttf',src)
 ns={'export_root':export_root,'variant':variant}
 exec(compile(code,'<export font variant>','exec'),ns)
 out=ns['out'];report=ns['report']
 report['export_only']=True
 report['game_files_unchanged']=all(sha256(game_dir/n)==h for n,h in initial.items())
 assert report['game_files_unchanged']
 (out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'使用说明.txt').write_text('字体：'+variant+'\n\n本文件夹内两个 .bundle 文件为完整的一套，请一起使用。\n退出游戏后，先备份目标目录中的两个同名文件，再复制本文件夹内两个 .bundle 文件覆盖。\n目标目录：'+str(game_dir)+'\n更换另一字体时，复制另一文件夹中的两个 .bundle 文件覆盖即可。\n本次仅导出，未安装到游戏。游戏更新后请重新制作，以免覆盖新版字体资源。\n未启动游戏验证实际显示。\n',encoding='utf-8-sig')
 print(json.dumps({'folder':str(out),'font_family':report['font_family'],'character_count':report['character_count'],'bundles':[(b['name'],b['fonts']) for b in report['bundles']],'game_unchanged':report['game_files_unchanged']},ensure_ascii=True),flush=True)
assert all(sha256(game_dir/n)==h for n,h in initial.items())
print('EXPORT COMPLETE',str(export_root),flush=True)
