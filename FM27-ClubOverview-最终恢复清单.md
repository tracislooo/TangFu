## 2026-11-18 荣誉卡片尺寸及两列恢复

按用户要求，仅将私有奖杯行及内联样式逐字节恢复为三列修改前的原样，每行两个，卡片150×192、图片132×130、名称12px。AI页面转入转出左右布局、上下各半及下方荣誉模块继续保留。补丁 club-honours-original-size-20261118-112048 已安装游戏与独立皮肤，仅奖杯两对象变化，其他对象逐字节校验通过。脚本 restore-club-honours-original-size.py。游戏内显示待确认。

## 2026-11-18 荣誉每行三个及 AI 转会荣誉上下两区

私有 TFClubOverviewTrophyRow 宽度改为三分之一，图片最高110px，卡片164px高，名称11px。玩家及AI荣誉均沿用同一私有行。AI ClubSiteBlock 原转会列内新增上下等高容器，上方保留原生转会标题/筛选/数据并将转入转出改左右各半，下方复制当前玩家荣誉模块完整分支，保留原生无数据判断、图片/计数绑定、滚动及点击。游戏和独立主皮肤分别增量制作，原有序列化绑定及其他对象校验通过。补丁 club-trophies-three-columns-20261118-111607，脚本 set-club-trophies-three-columns.py；安装状态见本补丁 manifest.json、automatic-install-status.txt 及 current-club-overview-trophies.json。实际画面待游戏验证。

## 2026-11-17 球场资料压紧并恢复原生联赛历史

球场右侧照片下的六行资料改为每行26px、总高156px，下方接入原生 ClubSiteBlock 的 InactiveClubCheck → LeagueHistory 完整分支及原生 Club.LeagueHistory 图表绑定，图表占余下高度。两套当前资源分别增量制作，原球场/照片/地图绑定和其他对象已校验。补丁 club-stadium-compact-history-20261117-215818，脚本 compact-club-stadium-add-history.py；游戏运行中已安排正常退出后安装，实际状态查看 manifest.json 和 automatic-install-status.txt。运行效果待游戏验证。

## 2026-11-16 招募预算及球队数据统计底板透明

按用户要求去除两模块的底色及外框。招募预算使用专用 ClubOverviewTransparentBudgetTile（-991100000000100，样式 -991100000000101），由原 tile-wide-4x2 复制并清除底板，私有财政面板指向它；数据统计 Content 内联背景/图片/边框颜色设为透明。全部数据、事件及内容不变。脚本 clear-club-module-backplates.py，安装记录 club-module-backplates-clear-20261116-091453/manifest.json。游戏及独立皮肤共 8 文件安装校验通过，游戏内显示待确认。更新迁移须补目录及 GlobalVisualTreeAssetPreload。

## 2026-11-07 AI 球队概况队徽放大

原生 ClubSite 通过 ReportHeaderFactory 的 club-site 项加载 ClubSiteHeader。沿用该页头的 GUID 和资源 ID，复用玩家版 160×166 队徽、两行左侧预留 176、右侧赛季卡自适应，并在 AI 动态页头固定 180 高。游戏与独立主皮肤各改一份 GameWorld 包，补齐预加载。记录 ai-club-overview-crest-20261107-015442/manifest.json，更新脚本 apply-ai-club-overview-crest.py。安装哈希已校验，实际显示待游戏内确认。

## 2026-11-07 首发攻防评分已撤回

按用户要求撤回球衣右侧进攻、防守评分及两次取数试修。游戏与独立主皮肤的六份文件均已核对为加入评分前的版本。此前俱乐部概览布局和球场图片绑定继续沿用。后续游戏更新不恢复首发攻防评分。三个历史补丁的 manifest.json 均已标记 restored，最终回退记录为 club-starting-xi-scores-20261107-010316/manifest.json。

## 2026-11-06 当前采用原生图片函数与球场编码入口试装

已受哈希保护撤回名称匹配版。球场图片改用原生 BindSIImage，BindingPath 为 selectedstadium.UniqueId，7915个球场编码字符串直接映射至现有本地 Texture2D 位置。只更改两套最新 gameworld 面板和各自 catalog/hash 共6文件。名称匹配禁用。脚本 build-club-stadium-native-numeric.py；记录 club-stadium-native-numeric-20261106-100443/manifest.json。文件验证通过，实际显示尚待用户验证，不能据此宣称空白已解决。

## 用户要求按球场编码自动显示（2026-11-06）

用户明确拒绝城市与球场名称匹配。名称版不作为恢复要求。已安排游戏正常退出后受哈希保护撤回该轮改动，状态见 club-stadium-id-required-20261106/status.txt。恢复 selectedstadium.UniqueId 编码绑定，图片实际加载仍待修复；不得声称编码方案已验证。

## 2026-11-06 城市和球场名称匹配试装

当前球场包 stadium_backgrounds 按球场 ID 命名。用本地 2700 数据库的城市、球场多语言名称建立目录别名。面板订阅 selectedstadium.City.Name 和 selectedstadium.Name，巴塞罗那与诺坎普球场对应 1040.jpg。跳过二者都同名的歧义组合。覆盖 7,883 个球场，登记 59,535 组名称。本机文件已验证，界面效果待确认。更新时在前一版基础上迁移 build-club-stadium-native-name.py，需 Python zstandard 并核对新版数据库格式。记录 club-stadium-native-name-20261106-094251/manifest.json。

## 2026-11-06 球场图片空白继续诊断

用户反馈球场ID版仍为空白。改为从球场原生面板现有 selectedstadium.UniqueId 读取 ID；函数加入实际请求图片键的运行日志。补丁 club-stadium-context-fix-20261106-092602/manifest.json 已安装，4文件校验通过，游戏显示及空白根因待运行日志确认。后续迁移应追加 fix-club-stadium-context.py，不把该试装描述成已验证成功。

## 2026-11-06 最新球场图片来源采用球场 ID

用户指定最新图片包为 G:/Doc/Sports Interactive/Football Manager 27/graphics/Stadiums/stadium_backgrounds。配置为 graphics/pictures/stadium/<球场ID>/background，7915 个不同球场 ID 均有对应图片文件。面板订阅 club.MainTeam.Stadium.UniqueId，专用图片键 tf27/stadium/id/<id>/background 由 SI.Core.LocalAssetProvider 读取对应本地 JPG/PNG。继续采用照片底层、资料上层半透明堆叠。此条取代此前俱乐部 ID 图片来源。图片目录移动或配置增删后需重建索引。游戏与独立皮肤已安装并完成文件校验，游戏显示尚未验证。迁移顺序先恢复既有叠层及加载函数，再应用 switch-club-overlay-to-stadium-id-pack.py；本次记录 club-stadium-id-pack-20261106-091858/manifest.json。

## 2026-11-06 球场照片铺底、资料叠加（取代此前上下分区）

照片为绝对定位底层，覆盖球场模块正文。六行资料位于上层，背景半透明。按当前 club.UniqueId 加载本地照片，仅在找到资源时显示图片层。基于按俱乐部 ID 登记 background 的 config.xml，按实际 JPG/PNG 路径创建专用 Texture2D 目录记录，使用 SI.Core.LocalAssetProvider。移动图片包或增删映射后需重建索引。更新时先迁移上一版通用绑定，再在相应基线上应用 build-club-stadium-overlay-local.py。记录 club-stadium-overlay-local-20261106-014754/manifest.json；游戏内效果待核实。

## 2026-11-06 球场图通用绑定试装

更新后在两套最新资源上迁移 build-club-background-pack-binding.py 的改动。概览图片订阅 club.UniqueId，先清除上一张图片，再请求 graphics/pictures/club/<id>/background。保留资料在上、图片在下。此规则适用于按俱乐部 ID 登记背景的图片包，运行时外部资源加载待确认。补丁记录见 club-stadium-pack-by-club-20261106-012923/manifest.json。

# Club → Overview 最终恢复清单

## 2026-11-05 追加：底部控制条、招募预算与转会左右布局

本节覆盖下方涉及底部控制条、财政样式及上排宽度的规格。

- 恢复用户截图中的原生底部控制条，包含原 ShowTiles／HideTiles 模板、事件、焦点及其控制的 BottomTiles 原生分栏窗口。原生变量与开关绑定保留；旧五张默认底部快捷卡片仍从外部 Club 网格移除。用户通过控制条可展开原生分栏窗口。
- 左下第二列由“财政总余额＋走势图”改为原生 RecruitmentBudgetsTile_4x2 的“招募预算”卡，显示转会可用、工资可用及球探可用三行；沿用原生标题、图标、分隔线、金额格式及点击绑定，外部旧“财政”标题隐藏，避免重复。
- 上排四列grow改为2:2:3:1（扣除分隔线后约25%／25%／37.5%／12.5%）；新闻宽度为上版一半，腾出的宽度全部分给转会历史。下排四列等宽保持。
- 转会历史保持季节与转会类型筛选；转入、转出改左右各半，中间原生竖线，各自列表保留原有绑定与滚动。
- 仅增量修改游戏与独立主皮肤各自gameworld包内ClubOverviewEightPanelBody、ClubOverviewFinancesPanel及其样式和必要preload。队徽、球场图片、其他模块与其他资源包保持。

脚本 `refine-club-footer-budgets-transfers.py`；安装／回退目录 `club-footer-budgets-horizontal-transfers-20261105-011936`，`restore.ps1`校验当前哈希后仅回退本次。两版各18条模板覆盖路径及12个视觉函数登记检查通过，原预算控件绑定与覆盖完整保留，原底栏事件／数据绑定比对通过；成品序列化与其他对象逐字节检查通过。游戏内排版与交互尚未验证，未启动游戏或操作桌面。

## 2026-11-05 最新：四列上下八模块与跨两行队徽

本节覆盖下方 2026-10-29 的旧布局规格。当前游戏目标为 `F:/Steam/steamapps/common/Football Manager 27`，资源目录从 `current-game-location.json` 读取。游戏与独立主皮肤各自在最新基线上增量应用，不能用历史整包相互覆盖。

- 顶部操作快捷卡片保持原始高度、图文和事件。
- 删除页面下方 Club Site、Club Profile、Club Info、Facilities、Transfer History 原五张卡片及中间原生底部卡片展开/收起入口，中间 Overview 延伸至旧底部边缘。仅修改普通版 ClubComposition-Large／Standard／Small，FMC 独立布局保留。
- Large 仍为20列，总高10行；顶部操作 y=0、高1，中间 y=1、高9。Standard为16列、Small为12列，总高8行；顶部操作 y=0、高1，中间 y=1、高7。横向最大宽100，避免重复锁死宽度造成右侧留白。
- 中间上方队徽改160×166 UI单位，跨球队信息与赛季信息两行；队名、球衣及原有资料向右让位。两行左侧均预留176 UI单位；第一行66高、第二行100高，两者间4单位。赛季信息卡按剩余宽度伸缩，保留原分支、数据及点击。
- 头部下方为四列等宽、上下等高八模块。上排依次：一线队阵容、关于俱乐部、转会历史、新闻；下排依次：球场资料与图片上下堆叠、财政总余额与原生走势图、俱乐部荣誉、球队统计。上排关于俱乐部的荣誉子树移至下排第三列，保留绑定及无数据分支。
- 四列宽度为flex等分，最小宽0；上下区域基值0、各grow=1，均限制在可用高度中。新闻增加内部滚动；荣誉、阵容、转会与统计沿用原生列表/滚动与作用域。
- 球场图不使用固定kunshan图片或新增纹理。SIImage调用原生 `BindToDatabaseObjectImage`，绑定 `club.MainTeam.Stadium.UniqueId`，数据库类型为当前原生 `DatabaseTableType.Stadium=21`。该值已由当前metadata核对，更新后须重新确认。图片从游戏原生数据库对象图片入口加载，以对接玩家球场包；缺图沿用原生缺图处理。当前未找到已安装球场照片包，实际加载尚未实测。
- 原 ClubSiteHeader／ClubSiteBlock、共用Global头部及原生球场/财政/统计模板保持；改用7个私有VTA副本与各自内联样式，保留源控件ID及嵌套覆盖路径。宿主 ClubScreenOverviewBlock 保留原GUID、Path ID、club/team输入。
- 私有模板：ClubOverviewWideHeaderDetails、ClubOverviewInsetSeasonCards、ClubOverviewLargeCrestHeader、ClubOverviewStadiumStack、ClubOverviewFinancesPanel、ClubOverviewTeamStatsPanel、ClubOverviewEightPanelBody。新ID从 `-991100000000000` 起按每模板10递减，样式为模板ID-1；GUID及完整对象清单见本次manifest。
- 补齐新模板的catalog类型、所属bundle首项依赖、Global／GameWorld实际预加载标签locations、容器和preload。背景纹理、图片清单、字体、比赛布局及无关对象保持；保留并行球员页修改。

实施：`build-club-overview-eight-panels.py`；验证：`verify-club-eight-panels.py`。

当前安装与回退记录：`club-overview-eight-panels-20261105-003750`。游戏与独立皮肤共10文件已安装校验；每版36条完整模板覆盖路径及27个视觉函数登记核验通过，序列化回读和未修改对象逐字节检查通过。`restore.ps1` 受当前哈希保护，仅回退本次；后续有修改须重新合并，禁止用旧整包覆盖。当前索引：`current-club-overview.json`。

未启动游戏或控制桌面。后续需游戏内检查：不同球队/长队名、队徽与球衣不重叠、四列上下边界、各列表滚动/筛选、数据刷新、无球场图/已安装球场包时的显示，以及不同分辨率。静态校验不代表实际显示通过。

---

以下为已被上节覆盖的2026-10-29历史规格，仅供追溯。

更新日期：2026-10-29。本文为当前最终规格；此前的缩放和纵向网格加倍方案已取消，不应重做。

## 1. 顶部操作卡片（原截图红框 1）

- 恢复并保持游戏原始高度。
- 图片、文字、按钮均保持原始大小，不做 50% 缩放。
- 使用原生 HumanActionsControlPanelBlock，保留原有数据、点击、菜单和分支绑定。

## 2. 中间 Overview（原截图红框 2）

- 将玩家球队原来的 Board Vision／Finances／Club Staff 大区域替换为其他球队 Overview 的原生样式，内容仍读取当前玩家球队。
- 上部使用 ClubSiteHeader：队徽、球队名称与资料、球衣、战绩、关键人物等原生内容。
- 下部使用 ClubSiteBlock 四列：一线队阵容；俱乐部介绍、联赛历史与荣誉；转会历史；俱乐部新闻。
- 整个中间区域保持修改前的原始高度，不能被内部内容撑高。上部信息栏当前实例高度 180 个 UI 单位，四列主体占剩余高度。
- 容器高度和最大高度为父区域 100%，最小高度 0；四列主体高度基值 0、可伸缩、最大高度 100%，限制溢出。保留原生列表内部的滚动及数据绑定。
- 宽度允许随页面横向伸展，不能因为限制高度而同时锁死最大宽度。

## 3. 底部卡片与布局

- 底部保留原有 Club Site、Club Profile、Club Info、Facilities、Transfer History 卡片；不同分辨率按原生布局显示相应卡片。
- 保持底部卡片原始位置、高度和原生横向布局。
- 使用原始纵向网格单位，不做纵向单位加倍。

| 布局 | 顶部位置/高度 | 中间位置/高度 | 底部位置/高度 | 中间最大尺寸 |
|---|---|---|---|---|
| Large | y=0 / h=1 | y=1 / h=7 | y=8 / h=2 | x=100 / y=7 |
| Standard | y=0 / h=1 | y=1 / h=5 | y=6 / h=2 | x=100 / y=5 |
| Small | y=0 / h=1 | y=1 / h=5 | y=6 / h=2 | x=100 / y=5 |

以上为逻辑网格值，不是屏幕像素。恢复原生描述和 GridElementSet；中间 m_expandToContent=0。FMC 独立布局没有修改。

## 4. 更新后的迁移与校验

- 以更新后的原生 bundle、类型树及 catalog 为基础迁移，不直接覆盖历史整包或旧 catalog。
- 当前宿主 ClubScreenOverviewBlock：Path ID `1984155051551838433`，GUID `6b0f1bffd62c7c74baf0c0a7df280b9e`，inlineStyle ID `-5246020300881899295`。更新后重新核对这些标识是否仍有效。
- 宿主内部引用 ClubSiteHeader（当前 GUID `441736359c3f87447bdebb8316ee98e9`）及 ClubSiteBlock（当前 GUID `155d0cc7fdb38d14589e0035cc82327b`）。优先复用新版原生模板与数据绑定，不复制旧数据或写死球队。
- 同时检查模板、VisualFunction 的 catalog GUID、资源类型、实际包内对象、所属 bundle 为依赖首项及跨包依赖；同步游戏安装目录与皮肤 packages。
- 不必重建已停用的 ClubOverviewCompactActions 或首版私有网格描述。不要重跑首版 build-club-overview-native-site.py，其包含已取消的缩放方案。
- 不修改图片；严格遵循 AGENTS.md、reserved-texture-ids.json、current-custom-textures.json 的永久禁用与最新背景覆盖规则。
- 校验三个分辨率布局，确认顶部原始大小、中间高度固定、四列内容正常、底部位置正确、右侧无异常留白，并检查列表滚动和点击。静态回读通过不等于游戏实测通过。

## 5. 当前文件与回退记录

- 首版内容接入参考：`build-club-overview-native-site.py`，仅参考模板接入与依赖检查部分。
- 恢复原始高度：`restore-club-overview-original-heights.py`；记录目录 `club-overview-original-heights-20261029-112700`。
- 最终宽度修正：`fix-club-overview-width-only.py`；记录目录 `club-overview-width-fix-20261029-114852`。
- 上述是历史实施参考，更新后必须适配新版资源，不能顺序盲跑。最终规格以本文为准。
- 当前已安装并完成资源回读及未修改对象哈希校验；尚未收到最终游戏内效果确认。









