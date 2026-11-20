from pathlib import Path
import sys,json,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
out=R/'player-popups-scale75-20261028-010812';assert json.loads((out/'manifest.json').read_text('utf8'))['installed']
docs=['球员弹窗最终版本说明.md','球员位置模块统一恢复顺序.md','球员弹窗最终版本资源快照.json']
for name in docs:
 if not (out/name).exists():(out/name).write_bytes((R/name).read_bytes())
p=R/docs[0];s=p.read_text('utf8')
s=s.replace('更新日期：2026-10-27。以最终状态重建','更新日期：2026-10-28。以最终状态重建',1)
s=s.replace('最终球场黑底、方块40%、尺寸200×327px。','最终球场黑底、方块40%；内部设计尺寸200×327px，75%缩放后显示150×245.25px。',1)
s=s.replace('## 外框及右侧最终坐标','## 内部100%设计坐标（外层统一缩放75%）',1)
s=s.replace('悬浮内容外框 **1342×620 px**；','悬浮内容内部设计画布 **1342×620 px**，实际占用及显示尺寸为 **1006.5×465 px**；',1)
s=s.replace('当前壳层尺寸为1342×676，不能把包含标题栏的外层误当成悬浮内容尺寸。','壳层设计尺寸为1342×676，整体75%缩放后外框为1006.5×507；标题栏、关闭与导航控件一起缩放。不能把含标题栏外框与内容尺寸混淆。',1)
marker='## 最终效果与范围'
new='''## 当前显示尺寸与恢复顺序

- Squad overview悬停、比赛姓名悬停：**1006.5×465px**；比赛点击报告含标题栏：**1006.5×507px**。保留0.5px宽度，不强制取整。
- 内部沿用1342×620设计画布；点击报告含标题栏设计画布1342×676。外层视口使用缩小后的实际尺寸，内部画布以左上角为原点统一scale(0.75,0.75)，卡面、属性、文字、球场、间距及关闭／导航控件一起缩放。下文旧坐标表均为100%设计坐标，不再逐项乘0.75修改。
- 悬停两个入口在原BindingRemapper内加入 `PlayerPopupCanvas75`；点击报告在卡片壳层外加入 `PlayerPopupViewport75`。同一入口只能有一层缩放，禁止嵌套第二层75%。原有绑定和点击事件保留，点击区域随UI变换同步缩放。
- 位置恢复清单P06统一完成此步骤：先按设计尺寸完成内容，再给三条入口各安装一次75%视口／画布，之后执行P07目录检查与P08验收。主页面球场不参与这次缩放。
- 当前显示值：卡面区域300×447；球场模块150×447，实际球场150×245.25；右侧520.5×447，Small属性高285，底部三模块高96，间隔9px。
- 实现脚本 `scale-all-player-popups-75.py`；记录 `player-popups-scale75-20261028-010812/manifest.json`。脚本基于未缩放设计画布，只执行一次，已安装时会停止，不能作为更新后无检查重放的脚本链。
- 已同步游戏／皮肤并完成回读、布局树、绑定、目录与图片清单校验；本轮尚未进行游戏内显示及点击实测。

'''
if '## 当前显示尺寸与恢复顺序' not in s:s=s.replace(marker,new+marker,1)
p.write_text(s,'utf8')
p=R/docs[1];s=p.read_text('utf8')
s=s.replace('更新日期：2026-10-27','更新日期：2026-10-28',1)
s=s.replace('弹窗球场为 **200×327px**，在200×596px区域内垂直居中，Y=134.5。','弹窗球场内部设计尺寸为 **200×327px**，在200×596px区域内垂直居中，Y=134.5；P06统一外层75%后实际球场为 **150×245.25px**。主页面不缩放。',1)
s=s.replace('检查永久禁用70张和有效173张图片清单','检查永久禁用70张及 `current-custom-textures.json` 当前有效图片清单',1)
s=s.replace('| P06 三条弹窗入口 | 将同一个弹窗球场接入共用悬停、比赛姓名悬停和比赛点击报告 | 三条入口各核对一次；保留点击报告关闭与导航，不为每条入口复制球场资源 |','| P06 三条弹窗入口与75%缩放 | 将同一个弹窗球场接入共用悬停、比赛姓名悬停和比赛点击报告；内部设计完成后各增加一层75%画布与实际尺寸视口 | 悬停1006.5×465，点击报告含标题栏1006.5×507；三条入口各处理一次；已有75%层则跳过，不重复缩放；保留关闭与导航，不复制球场资源 |')
s=s.replace('- 最新安装记录：`black-pitch-40pct-zones-20261027-121230/manifest.json`；文件与目录校验通过，游戏内显示未标记为实测通过。','- 球场配色记录：`black-pitch-40pct-zones-20261027-121230/manifest.json`；最新弹窗75%缩放记录：`player-popups-scale75-20261028-010812/manifest.json`。文件与目录校验通过，游戏内显示未标记为实测通过。',1)
p.write_text(s,'utf8')
p=R/docs[2];snap=json.loads(p.read_text('utf8'));envs={};objects={}
for bn in {a['bundle'] for a in snap['assets']}:
 envs[bn]=UnityPy.load(str(GAME/bn));objects[bn]={o.path_id:o for o in envs[bn].objects}
for a in snap['assets']:
 oo=objects[a['bundle']];tree=oo[a['path_id_reference_only']].read_typetree();a['tree']=tree
 style=tree['inlineSheet'];a['inline_style']=oo[style['m_PathID']].read_typetree() if style['m_FileID']==0 and style['m_PathID'] else None
for bn in snap['bundles']:snap['bundles'][bn]=hashlib.sha256((GAME/bn).read_bytes()).hexdigest()
snap.update(recorded_date='2026-10-28',revision='All three player popup routes scaled once to 75%; hover 1006.5x465, match click 1006.5x507 including controls; main pages unchanged',runtime_verified=False)
snap['popup_scale']={'factor':.75,'hover_design_size':[1342,620],'hover_display_size':[1006.5,465],'click_shell_design_size':[1342,676],'click_shell_display_size':[1006.5,507],'pitch_design_size':[200,327],'pitch_display_size':[150,245.25],'transform_origin':[0,0],'restore_step':'P06','one_transform_per_route':True,'main_player_pages_scaled':False}
snap['restore_order_reference']['popup_scale_task']='P06'
p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8')
for name in docs:assert (out/name).exists()
assert snap['pitch_colors']['zone_fill_opacity']==.4
assert '有效173张' not in (R/docs[1]).read_text('utf8')
print(json.dumps({'documentation_updated':docs,'scale_step':'P06','snapshot_refreshed_from_current_V61_bundles':True,'scale_applied_once':True},ensure_ascii=True))
