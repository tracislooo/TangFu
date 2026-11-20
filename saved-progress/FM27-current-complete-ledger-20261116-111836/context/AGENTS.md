# 当前游戏安装路径（置顶1–14统一）

- 用户于2026-10-30确认，置顶1–14及其后续修改的游戏根目录统一为 `F:/Steam/steamapps/common/Football Manager 27`。
- Addressables目录：`F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa`；资源包目录为其下的 `StandaloneWindows64`。
- `F:/Steam/steamapps/common/Project Taco` 已停用为修改/安装目标；历史脚本中的该路径须在执行前适配，禁止继续向旧目录写入。
- 历史manifest、备份及回退脚本保留真实历史路径，不批量改写；当前游戏路径以本节和 `current-game-location.json` 为准。

# FM27 自定义图片维护规则

- 用户于 2026-10-27 永久停用 ATT、DEF、FED、KIK、SPD、SPT、TCN 各 10 张图片，共 70 张。其名称及 Path ID 见 `reserved-texture-ids.json`。
- 这些名称及 ID 必须保持未占用：不得恢复旧图片，不得创建占位纹理，不得复用或分配给其他资源。新建及迁移资源前必须检查禁用清单。
- 最新有效图片来源见 `current-custom-textures.json`。V59 已安装，当前有效自定义图片为 181 张（含已打包的 CA150、CA170），不能再从 V53/V54/V55 无筛选恢复全部 243 张。
- 重新打包须以游戏更新后的原生背景包为基础，保留新版原生资源；仅迁移有效自定义图片，并校验禁用 ID 不在成品对象、容器和预加载表中。
- CA000、CA120、CA140、CA160、CA180 保持原名称及 Path ID。游戏卡面引用必须解析到最新背景包中的对应纹理，不能保留旧副本。
- V59 卡面 CA150 为 `-910000000000143`、CA170 为 `-910000000000144`，必须复用，不重复导入或另分配 ID。最新七档切图：1–109 CA120，110–129 CA000，130–139 CA160，140–149 CA140，150–159 CA150，160–169 CA170，170–200 CA180；0 或缺失使用 CA120。
- 历史包与回退文件仅供故障回退，不作为新的默认恢复来源。未经用户明确改变要求，不得取消永久禁用规则。
- 2026-10-27 的 Player.log 报告自定义悬浮卡片 GUID `64033a72b9925c8dad3b08826077c328` 加载失败。V58 发现游戏 catalog 丢失 67 条当前存在的自定义 VisualTreeAsset 登记及 backgrounds 依赖。以后更新/安装须核对实际模板 GUID 在游戏 catalog 中登记、对应 bundle 包含该对象，且跨包背景依赖完整；仅校验 PPtr 可解析不代表 Addressables 能加载。
- 2026-10-27 另发现游戏 catalog 缺少 Global 包内 15 个自定义 VisualFunction 登记（包括非门将/门将共 11 个卡面评分函数），导致六项评分全部 `--`。恢复时必须同时验证 VisualTreeAsset 和 VisualFunction 的 GUID、资源类型、实际包内对象以及所属 bundle 为首项的目录依赖。修复脚本 `repair-fc-rating-functions-catalog.py` 仅补目录，不改公式/图片；安装记录见 `repair-fc-rating-functions-catalog-20261027-051559/manifest.json`。

- V61 新增球场纹理 `kunshan stadium`，Path ID `-910000000000145`，须沿用；保留在 backgrounds；Start screen 的 MainMenu 已引用该纹理，新增全屏图片层覆盖人物模型，菜单保留在图片上层。

- V65 已删除原图 `TF patch`（原 Path ID `-910000000000146`），后续恢复不得重新导入；独立衍生图 `TF patch aligned` 保留。

- V63 新增纹理 `patchplayerbg`，Path ID `-910000000000147`，须沿用；本次仅加入 backgrounds，未设置界面关联。

- V66 新增纹理 `TF skin V1`，Path ID `-910000000000149`，须沿用；现已用于替换原生 `fm-skin-v2` 的图像数据，源纹理本身保持原样。

- fm-skin-v2 默认背景已改用 `TF skin V1` 的现有图像数据；原生名称 `fm-skin-v2` 及 Path ID `-8106300765064621370` 保持不变，源纹理 `TF skin V1`（`-910000000000149`）原样保留。更新后在新版原生背景包上重做该替换，不能仅迁移自定义纹理而遗漏此原生背景覆盖。

- 用户清单内当前存在的 25 张原生默认/赛事背景已统一使用 `TF skin V1` 的图像数据，名称、Path ID、容器与预加载记录均保留；涉及 ui-backgrounds_assets_common.bundle, ui-backgrounds_assets_.bundle。完整目标、实际名称映射与缺失名单见 `current-custom-textures.json` 的 `native_background_overrides`。游戏更新后需在新版各原生包重做这些内容覆盖，不恢复缺失旧资源。

- ui-backgrounds_assets 内名称包含 `fm27_skin` 的全部 29 张原生默认/赛事背景已统一使用 `TF skin V1` 的图像数据，名称、Path ID、容器与预加载记录均保留；涉及 ui-backgrounds_assets_.bundle。完整累计目标、实际名称映射与缺失名单见 `current-custom-textures.json` 的 `native_background_overrides`。游戏更新后需在新版各原生包重做这些内容覆盖，不恢复缺失旧资源。

- V70 新增纹理 `TFWX`，Path ID `-910000000000150`，须沿用；开始页 `MarketingBannerTile_8x2` 已关联：原生视频显示宽度由640减至390px，高112px；右侧240×112px区域等比完整显示TFWX；保留原生循环视频、链接和分支绑定。

- V71 更新纹理 `TFWX`，Path ID `-910000000000150`，须沿用；既有开始页关联保持不变。

- V72 更新 TFWX，原ID不变；同名原生纹理 `fm27-background-texture`（`274891149646581386`，`ui-backgrounds_assets_.bundle`）改用对应PNG。后续更新按 current-custom-textures.json 的 native_individual_replacements 在新版原包上恢复该覆盖。

- V73 更新纹理 `TFWX`，Path ID `-910000000000150`，须沿用；既有开始页关联保持不变。

- 2026-10-29 修复“提供合同”页面空白：新版 `ContractNegotiationTool` 的 66 处 `m_SerializedDataOverride` 使用新版控件 ID，但迁移后的 `ContractNegotiationToolTemplate`（GUID `5f191fc6eb99dde47a955456fecb83e6`）保留旧版 `m_Id`/`uxmlAssetId`，导致 0/66 匹配。已对齐新版原生模板控件 ID，保留现有样式及自定义子模板，修复后包含嵌套路径在内 66/66 可解析。后续迁移不能只校验 GUID/PPtr；须核对模板覆盖的完整 `m_ElementIdsPath`。脚本 `fix-contract-offer-template-ids.py`；安装与回退记录 `contract-offer-template-ids-fix-20261029-190743/manifest.json`。本次按用户要求未启动游戏或操作桌面验证。

- V74（2026-10-30）删除 PlayerTopBackground（-910000000000001）和 PlayerTopBlueLight（-910000000000002），清理纹理、目录/预加载及现有图片引用；后续恢复不得重新导入，其他卡面和布局保留。


# FM27 已认可侧栏版本（2026-11-01）

- 侧栏底色（2026-11-02）：`sidebar-dark-grey-blue-20261102-100742`已安装，侧栏专用外层底色改为深灰蓝`#263445`，内部原40%黑色叠层改透明。仅改侧栏内联样式及专用USS规则，按钮、图标、分隔线及其位置不变，主版本工程未改。`restore-color.ps1`回退本次颜色；当前完整回退需先迁移后续改动，不能使用旧整包覆盖。文件校验通过，实际颜色待用户确认。

- 编辑按钮位置（2026-11-02）：`sidebar-bookmark-editor-top-20261102-095604`已安装，仅调整TFReferenceBookmarkSidebar的Bookmarks子节点顺序，将原1073编辑三角放在书签列表上方。保留20px按钮、16px图标、原生编辑事件及400px列表。回退本次位置用该目录`restore-position.ps1`。其他资源（含后续主导航85%字体/分隔线样式）未改；完整非侧栏回退须先合并这次位置及后续主导航样式，禁止用旧整包覆盖。文件校验通过，实际显示待用户确认。

- 最新侧栏细节（2026-11-02）：`sidebar-icons-groups-20261102-094432`已安装，首行新增“经理中心”，随后14固定入口前复用原生同类书签图标。经理中心/消息/动态/数据中心/医疗中心/比赛/球探/财政之后各加横线，青年与书签之间再加横线，共9条；侧栏右侧加1px竖线。原生书签列表高度400px，行高30px、字体12px、图标16px、左对齐及无框透明背景与固定链接一致。原14按钮事件保留；经理中心使用原生PortalScreen入口。三角按钮位置不变。仅修改侧栏相关gameworld VTA对象和default styles规则，原皮肤工程未改。回退以current-sidebar-version.json为准；当前旧导出包未更新。文件验证通过，游戏内效果待用户确认。

- 最新安装（2026-11-02）：按用户要求，将侧栏增量重新迁移到当时正在使用的`main-1-14-rebuild-20261102-101644`主版本后安装，记录`sidebar-approved-rebased-20261102-092833`。当前游戏为侧栏版；导航原位、侧栏top85px、14固定入口、无方框、编辑按钮20px/16px图标，三角位置未改。只安装5个必要文件，原皮肤工程未修改。该目录`non-sidebar-backup`为本次最新主版本备份，`restore-non-sidebar.ps1`回退；索引以`current-sidebar-version.json`为准。旧导出zip不是当前重迁移版本。安装校验通过，游戏显示待用户确认。

- 侧栏外观（2026-11-02）：`sidebar-borderless-20261102-090802`已安装，去掉14固定导航与原生书签按钮方框、按钮填充背景及侧栏右边框；编辑按钮高度20px、图标16px。用户随后明确“三角位置可以先不处理”，因此按钮位置保持原样，未实现底部固定。仅修改游戏gameworld VTA与default styles的相关对象；原皮肤工程未改。回退及当前状态见`current-sidebar-version.json`。安装校验通过，游戏内效果未确认；旧导出zip尚未更新。

- 最新位置调整（2026-11-02）：本聊天只维护主版本分出的侧栏分支及相关文件。`sidebar-below-navigation-20261102-084638`已安装，仅改游戏`ui-styles_assets_default.bundle`内3条侧栏样式：顶部控件margin-left与页签padding-left归零，主导航54px、分隔线1px、页签30px下方的85px处开始侧栏，侧栏顶部padding归零。正文留位、比赛补偿、14固定导航和原书签保持现状，主版本皮肤工程未改。当前回退入口以`current-sidebar-version.json`为准；本补丁`restore-position.ps1`只回退位置，`restore-non-sidebar.ps1`完整撤销侧栏。旧20261101导出zip未包含此调整。安装文件校验通过，实际界面待用户验证。

- 最新状态（2026-11-01）：用户反馈原生默认14项方案未生效，已撤销该管理模块和单项书签偏好修改，改为在原书签上方直接插入14个固定SIButton入口。当前补丁 `sidebar-fixed-navigation-20261101-123015`；固定中文标题顺序为消息、一线队、动态、战术、数据中心、职员、训练、医疗中心、赛程安排、比赛、球探、俱乐部、财政、青年。入口通过原生MenuBody根页与ReportBody目标页事件跳转，不依赖默认书签初始化。按钮宽100px、高30px，下方原生书签视区160px可滚动，保留编辑入口。仅修改TFReferenceBookmarkSidebar及其内联样式，原皮肤工程、比赛布局、字体、分辨率、存档保持原样。安装校验通过，实际显示及点击待用户验证。当前完整回退为该补丁目录的`restore-non-sidebar.ps1`，恢复侧栏植入前最新的5份资源；`restore-fixed-navigation.ps1`仅撤销固定入口。以下默认14项接入记录仅为已撤销历史，不作为当前安装状态。

- 用户确认 `reference-layout-sidebar-100px-v5/tactics-header-arrow-fix` 当前版本可用，已完整归档至 `saved-progress/FM27-sidebar-approved-20261101`；索引见 `current-sidebar-version.json`。
- 认可要求：100px竖排原生书签，从左上角贯穿到底部，顶部导航和正文在右侧；保留文字。采用参考皮肤的整体布局及比赛逆向补偿。共用战术页的点球/定位球/对手指令仅在比赛状态启用补偿；前进后退控件100px留位；编辑箭头16×16。
- 当前操作状态：认可版已归档；2026-11-01曾回退非侧栏后继续修复BUG，现按用户要求基于最新资源重新迁移并安装侧栏。当前游戏为侧栏版，独立原皮肤工程仍为非侧栏版。
- 后续BUG修复须保留两种版本的独立性：原皮肤工程不引入侧栏，更新当前游戏时须保留其已启用的侧栏增量。再次启用或迁移侧栏必须以最新BUG修复后的资源为基础，禁止用归档整包覆盖而回滚后续修复；归档安装脚本仅在基线哈希匹配时允许执行。
- 原皮肤工程保持独立，侧栏不是后续修改的默认安装基线；历史试装包仅供追溯，不得误用早期故障版本。

- 2026-11-01：默认14项书签已实际接入，取代此前仅保存源JSON的状态。安装记录 `sidebar-native-default-bookmarks-20261101-122303/manifest.json`：仅改游戏 `gamemodules_assets_gameworld.bundle` 的桌面俱乐部经理书签列表及必要预加载，使用独立原生BookmarkInfo副本保留其他模式默认值；同步HKCU `Software\Sports Interactive\Football Manager 27` 下唯一偏好值 `SelectedBookmarksKey_h3185478356` 为14个PanelUID逗号列表。顺序：消息、一线队、动态、战术、数据中心、职员、训练、医疗中心、赛程安排、比赛、球探、俱乐部、财政、青年。动态使用普通版7d9c93953e66d3d468a7acd301e08618、战术使用a69d2d19d0ea8054b82d191ecfea01be原生路由；原有其他书签仍可在编辑菜单选择。原皮肤工程、分辨率偏好及存档未改。当前完整回退入口为该记录目录的 `restore-non-sidebar.ps1`，一次恢复6个文件及原书签偏好；`restore-bookmarks.ps1`只撤销14项接入。实际游戏显示及点击仍待用户验证。

- 2026-11-01：最新侧栏安装为 `sidebar-approved-rebased-20261101-121312`。从认可归档提取差异，只修改当前游戏的gameworld VTA、default styles、match VTA、catalog.bin与catalog.hash共5文件。保留后续样式规则、FullTimeTeamReport修复及所有无关对象；Global包、字体、图片、分辨率设置和原皮肤工程未改。`non-sidebar-backup`是这次安装前的最新非侧栏资源；当前回退入口为该目录的`restore-non-sidebar.ps1`，不得使用旧归档回退而覆盖后续修复。14项默认书签仍只保存为独立源配置，本次未接入或安装，侧栏读取原生已有书签。离线与安装哈希检查通过，迁移后游戏内显示未验证。

- 开始页横幅最终为视频与TFWX左右各50%，父容器宽100%，高度112px；内部视频控件宽100%，移除旧390/240px固定宽约束。保留TFWX固定ID、等比完整显示、视频播放及点击绑定。

- 2026-11-01：GameWorldBackground 的原3D动态背景分支（SIRenderTextureImage）改为读取 backgrounds 的 TF skin V1（-910000000000149）；静态背景分支保留。迁移时恢复此UI分支，避免球员页等继续显示原黑灰动态背景。记录：player-dynamic-background-blue-20261101-rebased/manifest.json。

- 2026-11-01 新增 DY（-910000000000151）、BB（-910000000000152）至 backgrounds，RGBA32 原尺寸无损像素；只入包，未设置界面关联。后续沿用名称及 ID；记录 DY-BB图片新增-20261101/manifest.json。

- 2026-11-01：偏好设置快速页的 OnlineGamePreferencesTile_4x2、AccessibilityPreferencesTile_4x2 原生入口卡片高度改为110px；下方左侧等比完整显示 TFWX，右侧上BB、下DY，图片忽略鼠标拾取。沿用现有纹理ID与模板GUID，保留原生文字及点击绑定。基于当前非侧栏游戏包和独立皮肤包分别修改，安装记录 preferences-picture-panels-20261101-rebased/manifest.json，含备份与restore.ps1；游戏内显示未验证。更新后须迁移这两份模板及各自内联样式，并确认global包的backgrounds目录依赖。

- 2026-11-01：已按用户要求撤回13个页面外壳 Card-frame 直接显示 TF skin V1 的修改，恢复原 SIImage 及 game.BackgroundImage.BackgroundImage 绑定。该补丁不再作为更新恢复要求；游戏与皮肤中的目标文档和样式均与备份一致，保留其他并行修改。记录 card-frame-blue-20261101-rebased/manifest.json（installed=false）。
`n- 2026-11-01：上条偏好设置内部定位方案经用户反馈未显示，已改为独立网格图片单元。原设置卡片网格高度3→1；其下y=5高度2，左TFWX、右BB上DY下。新增两个图片VTA及目录GUID登记、grid description/element set/composition引用；保持原图片ID。最终安装记录 preferences-picture-grid-20261101-115123/manifest.json，原内部定位方案不再作为恢复依据。游戏实际显示待确认。

- 2026-11-01：偏好图片网格版运行报错的修复：两份新图片VTA必须加入GlobalVisualTreeAssetPreload标签的实际locations列表，仅有GUID目录登记不足以预加载；原入口缩为1行时须同步description配置、composition配置与m_minSize，图片单元同步其行高。FMC入口在y5，图片须在y6高1；普通版入口y4、图片y5高2。两版均12×7、84格覆盖且无重叠。安装记录 preferences-grid-preload-repair-20261101-115659/manifest.json。游戏运行结果尚未验证；不得再次声称仅文件校验即可代表界面成功。

- 2026-11-01：偏好设置右侧图片单元由上BB下DY改为横向DY左、BB右，各宽48%、间距4%、高100%，等比完整显示。仅修改 PreferenceBBDYPictureTile 的内联样式对象（-910700000000004），图片ID、TFWX、卡片、网格及目录登记保持原样。基于当时最新非侧栏游戏包和独立皮肤包分别安装；记录 preferences-dy-bb-horizontal-20261101-120156/manifest.json，回退 restore.ps1。除该样式外包内所有对象逐项字节一致，引用及预加载检查通过，游戏内显示尚未验证。后续迁移应采用此横向排列，不能恢复旧上下排列。

- 2026-11-02：按用户要求在当前游戏资源上重新应用置顶1–14主版本，不含侧栏；当前游戏已切回非侧栏。记录 main-1-14-rebuild-20261102-101644/manifest.json。合同模板66条完整覆盖路径通过；清理两份已移除光效的断开节点。侧栏归档保持独立，不得直接覆盖当前后续修复。

- 2026-11-02：球员页面专用外壳 Card-frame 背景改为不透明深灰蓝 #263445，取消该层 SIImage 的 game.BackgroundImage.BackgroundImage 绑定，保留名称、控件ID与布局；共用原生模板和其他页面不变。PlayerReport 使用专用外壳 -940000000023000 及样式 -940000000023001，目录GUID沿用已有专用键并确保GlobalVisualTreeAssetPreload实际登记。游戏与独立皮肤分别基于最新文件修改，保留侧栏等其他改动。安装记录 player-report-dark-grey-blue-20261102-134619/manifest.json；install.ps1安装，restore.ps1回退。颜色、绑定和文件校验通过，实际显示待用户确认。

- 2026-11-02：洗牌选秀球员悬浮页已制作修复，移除 PlayerReportPreviewTooltip 的旧选秀网格分支，直接复用当前置顶5固定悬浮布局。仅修改当前游戏与独立主皮肤各自 gameworld 包内该 VTA，其余对象逐项校验不变；GUID/资源类型/所属包首项依赖检查通过。补丁 shuffle-draft-current-hover-20261102-104742；游戏启动导致安装暂缓，已设置正常退出后自动安装。实际安装状态以该目录 manifest.json、automatic-install-status.txt 为准；当前索引 current-shuffle-draft-hover-fix.json。尚未验证游戏内显示。回退使用该目录 restore.ps1（校验当前哈希，禁止覆盖后续修改）。

- 2026-11-02：用户明确认可最新侧栏，已归档 `saved-progress/FM27-sidebar-approved-20261102-201945`（实际安装5文件及哈希、状态、转换源码）。按用户要求游戏已回退非侧栏，记录 `sidebar-to-main-20261102-201945/manifest.json`；只逆向撤销侧栏增量，保留后续通用导航字体/间距/页签颜色及页面修复，其他包内对象逐项字节不变。当前游戏为非侧栏，可继续修改通用版；主皮肤工程未改，分辨率/字体资源未改。文件安装校验5/5通过，未启动游戏。即时恢复侧栏用该目录 `restore-saved-sidebar.ps1`（哈希保护）；后续通用版有改动后必须重新迁移侧栏，禁止旧整包覆盖。最新索引以 `current-sidebar-version.json` 为准。


# 界面底色统一维护入口（2026-11-02）

- 用户要求：普通页面 Card-frame（招募、一线队、赛程安排等）及此前黑色卡片模块统一深灰蓝 #263445、不透明度100%；Card-frame保留容器/ID/布局/内容，去除背景图片和图片绑定，使用纯色填充。球员页专用不透明深灰蓝外壳保持。此规则取代这些模块此前60%和普通外壳透明方案。
- 这一步由界面配色聊天维护，唯一更新脚本 apply-page-surfaces-theme.py，状态索引 current-ui-surface-theme.json。图片维护聊天只处理图片资源、纹理及其目录，不重复修改这些 Card-frame 或模块底色；更新后先完成图片资源步骤，再在这里运行界面配色步骤。既有专用图片面板等用户指定图片关联不在普通 Card-frame 规则范围内。
- 对游戏和独立主皮肤分别基于最新资源增量应用；保留侧栏/非侧栏各自状态及并行BUG修复。禁止使用旧底色补丁或旧整包覆盖新版本；已符合要求的对象跳过。顶部Touchbar此前单独要求的60%不透明度保留。

- 2026-11-03：按用户要求，patchplayerbg 已恢复本次替换前旧图，沿用名称和 Path ID -910000000000147；仅逆向恢复纹理数据，保留预加载补齐、原关联及后续页面修改。恢复来源已更新 current-custom-textures.json，记录 patchplayerbg-old-image-restored-20261103/manifest.json；本次蓝白新图不再作为恢复来源。

- 2026-11-03：洗牌选秀球员卡改为球队位于左侧收藏按钮下方、国家位于右侧选择按钮下方；姓名/位置下方原球队国家区域显示既有FC六项评分。复制当前FC评分子树并保留IsGoalkeeper判断及所有函数输入：非门将速度/射门/传球/盘带/防守/身体，门将扑救/站位/出球/反应/神经/速度，11个现有评分函数目录及实际对象校验通过。选中后的经理文字沿用原生状态逻辑，独立复制标签到右上角，顺时针45度、红色#FF0000。仅修改游戏和独立主皮肤各自fantasydraft包内shuffle-tiles-primary draft-graded-base及其内联样式，其余对象逐项字节不变，按钮事件与原有评分绑定不变；未修改共用标签、图片、界面底色或侧栏。已安装记录 shuffle-player-tile-fc-ratings-20261103-023754/manifest.json，当前索引current-shuffle-player-tile.json，回退restore.ps1带哈希保护。离线及安装哈希校验通过，未启动游戏或操作桌面，实际显示待用户确认。

- 2026-11-03：用户截图确认洗牌卡片上半区收窄，原因是TopHalf的align-self:center令其随唯一流内头像收缩；补丁将TopHalf恢复stretch并明确width100%、flex-shrink0。收藏/选择按钮及球队/国家沿原百分比回到左右两侧，经理名字随全宽容器回到实际右上角；保留45度红字及全部绑定。按用户追加要求，两套FC评分的12个数值字体从16px缩至13px，项目名称保持10px。仅修改游戏与独立皮肤fantasydraft内联样式对象，其他对象逐项字节一致；补丁shuffle-tile-width-smaller-values-20261103-030512已在游戏退出后直接安装，两文件安装哈希校验通过。以该目录manifest.json和automatic-install-status.txt为准，索引current-shuffle-player-tile.json。未验证实际显示，未操作桌面或启动游戏。

- 2026-11-03：按用户要求重新安装侧栏，将认可归档20261102-201945相对非侧栏的增量迁移至当前最新游戏资源，记录 `sidebar-approved-rebased-20261103-032442/manifest.json`。当前游戏为侧栏版；15固定入口、图标/分隔线、top85px、400px书签、顶部编辑三角及深灰蓝底色保留。当前通用版底色、洗牌修复及无关对象保留，独立主皮肤工程未改；字体/图片/分辨率设置未改。5文件安装校验通过，GUID/预加载完整；未启动游戏，实际显示待确认。`non-sidebar-backup`保存本次安装前最新通用版，回退用本目录 `restore-non-sidebar.ps1`（哈希保护）；后续有改动须重新迁移，不可旧整包覆盖。索引current-sidebar-version.json已更新。

- 2026-11-03：用户要求“侧边栏退回”，已执行 sidebar-approved-rebased-20261103-032442 的受哈希保护回退，恢复本次安装前最新通用版5文件；目标及受保护资源校验通过。当前游戏为非侧栏，认可侧栏归档与迁移包均保留，独立主皮肤工程未改。未启动游戏或操作桌面。后续再次启用须以最新通用资源迁移，不可旧包覆盖。current-sidebar-version.json已更新。

- 2026-11-03：侧栏医疗中心图标改为原生白色医疗十字（scaling-icons-condition-level-injured---white-size-small-16px），仅改TFReferenceBookmarkSidebar内FixedIcon_医疗中心的样式类，文本、事件、尺寸、其他对象逐项不变。新侧栏归档 `saved-progress/FM27-sidebar-medical-white-20261103-055516`，aa压缩包见current-sidebar-version.json。四档原生样式存在检查及序列化/压缩包校验通过，未启动游戏；当前游戏仍为非侧栏，未安装本次改动。再次安装须迁移最新通用资源，保留旧归档。

- 2026-11-03：检查发现实际游戏被手动覆盖回医疗白图标侧栏包（5文件完全匹配），并带回修复前的比赛弹窗Anchor=2/HorizontalAlignment=2，覆盖通用版既有top-toolbar-native-popup-anchor修复。已仅对游戏MatchUITacticalOptions内1018/1048两弹窗恢复原生Anchor=1/HorizontalAlignment=0及其属性标志，文字/事件/模板GUID/样式和其他对象逐项不变；主皮肤已有正确修复，本次未改。补丁sidebar-popup-anchor-fix-20261103-063144已安装，restore-popup.ps1仅回退本次弹窗修复。侧栏更新归档saved-progress/FM27-sidebar-popup-fixed-20261103-063144，最新5文件aa压缩包exports/FM27-sidebar-popup-fixed-20261103-063144-aa.zip，索引已更新。当前游戏实际为侧栏版；旧完整非侧栏回退需重新迁移并保留共用弹窗修复，不能用旧整包覆盖。文件校验通过，实际展开待用户验证，未启动游戏。

- 2026-11-03：洗牌选秀卡片六项评分项目名10→9px、数值13→12px；每套门将/非门将评分6列之间加入5条1px灰色竖线。选中后的经理标签从右上角移到整张卡片正中间（原生状态开关移至完整卡片容器），宽160px高32px，文字11→16px；沿用顺时针45度和红字#FF0000，原标签边框改为1px红色。基于游戏及独立皮肤各自最新fantasydraft增量修改，仅该VTA及内联样式，其他对象逐项字节不变；公式、状态判断、原生事件保持。补丁shuffle-tile-columns-centered-manager-20261103-200909，已安装，2文件哈希校验通过。索引current-shuffle-player-tile.json；restore.ps1带哈希保护。未启动游戏或操作桌面，实际显示待用户确认。

- 2026-11-04：比赛内Highlight已改为上下3:2；上方五列1:1:2:1:1（主队无球竖向、当前主队模块、球场/比赛势头/xG、当前客队模块、客队无球竖向），中间内部2:1、下方两图左右平分；下方四列等宽，两端保留当前六页轮播，中间原生完整菜单默认积分榜/最新比分。24x10逻辑网格，四套桌面大屏执教/旁观、有无积分榜布局已更新。全部基于当前游戏与独立皮肤分别提取样式，新增私有模板/菜单描述，原共用MatchViewer、原轮播、报告与小屏对象逐项字节保持。安装记录highlight-top-bottom-redesign-20261104-020344/manifest.json，完整当前Highlight相关备份见同目录backup-game、backup-skin、backup-inventory.json，受哈希保护的restore.ps1回退本次；索引current-highlight-layout.json。10文件安装哈希通过，8套布局静态检查通过，未启动游戏，实际显示与交互待用户确认。不得用旧整包回退而覆盖后续改动。

- 2026-11-04：用户要求撤回侧栏且不动其他内容。实际检查当前游戏已无4个侧栏专用对象、TFReferenceBookMark模板/类、比赛补偿标记、活跃侧栏USS选择器及2个侧栏目录GUID；正文main-menu-layer-body/main-card-report-body规则与独立主版一致。故未写入任何游戏资源，保留最新Highlight与所有并行修改；只更新状态索引为非侧栏。证据sidebar-already-removed-check-20261104.json。认可侧栏归档及用户自行打包均保持；未启动游戏或操作桌面。

- 2026-11-04：用户反馈洗牌卡片样式被覆盖，实际确认游戏为上半区全宽但经理标签仍在右上角的旧版，独立主皮肤保留居中版。仅基于当前游戏fantasydraft重新应用评分标题9px/数值12px、两套评分每套5条1px竖线、经理标签全卡中心160×32px/16px红字/45度/1px红框；独立主皮肤本次未改。记录shuffle-tile-columns-centered-manager-20261104-030713，已安装并校验。包内其余对象逐项字节不变，评分绑定/状态判断/按钮事件保持；当前Highlight相关gameworld/global/match/tileslayouts/defaultstyles及catalog校验保护通过。索引current-shuffle-player-tile.json；restore.ps1带哈希保护。未启动游戏或操作桌面，实际显示待用户确认。

- 2026-11-04：Highlight越界修复改为OverviewPrototype内独立flex上下容器（3:2）、上方五列（3:3:5:3:3）、下方四列等宽。每个区域单独承载原生一格模块网格及完整原生绑定，不再用68列坐标控制整体尺寸。新增私有composition/set及1x1模块配置，目录与预加载同步。补丁highlight-independent-regions-20261104-075225已安装游戏和独立皮肤8文件，序列化回读及无关对象一致性通过。实际是否消除越界及各分辨率显示尚未游戏验证，不得声称已实测成功。回退restore.ps1带哈希保护，索引current-highlight-layout.json。

- 2026-11-04：按用户最新要求改为18×10原生Highlight网格，上排高6格、列宽3/3/6/3/3（原主队、主队副本默认第二页、原完整中间、原客队、客队副本默认第二页），下排高4格，两侧原六页模块各宽9格。副本原生选择器及绑定保留，会话选择键独立；不提取/重组中间内容。基于游戏恢复版及独立皮肤分别生成，清理皮肤残留Responsive外层入口。highlight-18x10-seven-slots-20261104-090724已安装10文件，备份/restore.ps1带哈希保护。文件检查通过，实际显示待游戏验证。当前索引current-highlight-layout.json。

- 2026-11-04：Highlight最新为20×8，上排高5格、列宽3/4/6/4/3；下排高3格、列宽5/5/5/5。两端保留原主客队六页模块，中间原生完整可选模块区默认LiveTable/LatestScores。仅增量修改游戏与独立皮肤tileslayouts，保留上轮副本及默认第二页。highlight-20x8-five-four-20261104-092506已安装2文件，8套布局覆盖/序列化/无关对象检查通过；游戏显示未实测。回退restore.ps1带哈希保护，索引current-highlight-layout.json。

- 2026-11-04：Highlight最新20×8，上排高5格、五列各4格；下排高3格，宽5/3/4/3/5。下排中央新建私有四图模块（左主队右客队、上热点下传球），使用原生layout-tile背景/边框主题类；从私有中间副本移除左右分析栏，实时球场扩宽，原共享MatchViewer及报告保持。上方四个阵型选择器使用私有副本，有球/无球全部分支Orientation0/FlipPositions0，原有选择键与副本默认第二页保留。补丁highlight-five-columns-analysis-moved-20261104-101201已安装游戏/独立皮肤及1份自定义缓存共11文件，目录/预加载、八套网格、序列化、无关对象以及四图完整SerializedData绑定独立比较通过。缓存使用原生instanceID占位及稳定m_configDescriptionKeys迁移，保留下方原生可选区与两侧选择。实际显示、数据刷新和交互尚未游戏验证。restore.ps1带哈希保护；索引current-highlight-layout.json。

- 2026-11-04：按新截图，四张分析图已移入上排中间球场下方整个区域，替换该处比赛信息、数据对比和比赛势头/活动区域/xG三图。四图保留两列两行（主队左客队右、热点上传球下）及原SerializedData绑定/点击，维持现有上下分区尺寸。下排中间三槽改为完整原生可选模块区，默认MatchMomentum / MatchStatsStandAlone / xGStory，其余槽位及20×8、上排五等宽、下排5/3/4/3/5保持。补丁highlight-maps-under-live-pitch-20261104-103148已安装游戏/独立皮肤的Global和Tiles包及1份缓存，共5文件。克隆序列化、无关对象和独立结构检查通过；实际游戏内显示、刷新和交互尚未验证。restore.ps1带哈希保护；索引current-highlight-layout.json。

- 2026-11-04：Highlight上排第1/2槽交换，缓存同步。四个上方阵型选择器的当前比赛球员行接入新私有HighlightPhaseSpecificFeetAndCondition；原生inpossession参数分支，有球体能left相对当前值减4px，无球隐藏体能改为战术TacticsDetailedCardDetailsDesktop原有左右脚10px彩色标识/提示，22×10容器置头像右下right=-8/bottom0，脚部数据映射position.MatchPlayer.Person.Footedness。共享球员行及战术原卡面不改。补丁highlight-oop-feet-and-home-order-20261104-110618已在游戏正常退出后直接安装游戏/皮肤及1缓存共9文件，私有行目录和Global预加载、序列化/无关对象、原生分支顺序、脚部可见性路径及无新增gameworld包依赖检查通过。实际显示/数值/切换尚未游戏验证。restore.ps1带哈希保护，索引current-highlight-layout.json。

- 2026-11-04：用户确认替补右侧恢复与首发相同正常尺寸，并补充小分辨率恢复原版布局、保留头像/百分比等内容。仅改游戏和独立皮肤SquadOverview入口/布局，移除1038/1041外层SubstituteCountForCompactCards及75%卡片分支，正常右侧使用当前常规卡片110步长和原生分页；小断点恢复原生容器/列表布局80步长。列表接入现有gameworld常规/小卡片GUID，W/G卡片模板、绑定及其他包全部哈希保持。substitutes-normal-size-native-small-layout-20261104-112858已安装2文件，静态回读/原生参数/无关对象及保护包校验通过。实际大小与分页待游戏验证。restore.ps1带哈希保护，索引current-substitutes-layout.json；Highlight版本索引保持。

- 2026-11-04：仅小卡片中的替补新增私有SmallSubstituteCardLowerNoRating，原生PosTitleSwitch/IsSub条件false分支完整保留当前首发小卡片，true分支完整内容下移16px、隐藏评分1050及旧Number(playerinfo.SquadNumber)，右侧MatchCardShirtNumber、头像/国旗/体能/状态绑定保留。接入M的1041/1073/1088小卡片入口，大卡片1038/1087及其分页属性不变，W共享卡片不改。补丁small-substitutes-lower-hide-rating-20261104-115026已在游戏退出后安装游戏/皮肤8文件，私有行目录/Global预加载、克隆/回读/无关对象及独立分支可见性检查通过，实际显示待用户验证。restore.ps1带哈希保护，索引current-substitutes-layout.json。

- 2026-11-04：小替补卡私有SmallSubstituteCardLowerNoRating替补分支移除顶部序号标题及占位；体能右侧复制普通卡原生BodyLanguageMorphIcon（16px、左间距6px）；下方加入原生PlayerLastFiveMatchesChartFormSmallBarsCell，22px高、上间距3px，绑定playerinfo.Person.LastFiveMatchesForm.LastFiveMatchesList及playerinfo.Person，保留原生五场顺序/颜色/提示/点击和无数据分支，数据来源与训话form列一致。此前16px下移、评分与旧号码隐藏、右侧号码保留继续。首发小卡片分支逐节点相同，W共享卡片及大卡片不改。small-substitutes-state-and-last-five-20261104-120813已安装游戏和皮肤Global共2文件，回读/克隆/无关对象及独立标题/状态/原生图表绑定和条目GUID目录检查通过。游戏实际位置/状态/历史数据未实测。restore.ps1带哈希保护，索引current-substitutes-layout.json。

- 2026-11-04：小替补卡整体相对上版上移8px，私有替补分支top16→8，只改一个节点内联top；标题/评分/旧号码隐藏、右侧号码、状态和近五场图表保留。small-substitutes-up8-20261104-122711已安装游戏/皮肤Global共2文件，其他节点/绑定及无关对象一致性通过，实际显示未验证。restore.ps1带哈希保护；索引current-substitutes-layout.json。

- 2026-11-04：Highlight网格20×8→20×9，上排仍5格，下排3→4格。上排五列各4格、下排5/3/4/3/5及模块顺序/模板引用/选择保持；补当前私有菜单3×4/4×4/5×4配置并同步1份自定义布局。highlight-20x9-upper5-lower4-20261104-202220已安装游戏与皮肤TilesLayouts及缓存共3文件。八套布局180格覆盖、上排完整组件相同、序列化及无关对象检查通过；实际显示尚未验证。restore.ps1带哈希保护；索引current-highlight-layout.json。

- 2026-11-04：按用户要求Highlight20×9→20×8，上排5→4格，下排仍4格且起点y5→y4，上下各50%。上排4/4/4/4/4、下排5/3/4/3/5及模块/资产选择保持。highlight-20x8-equal-rows-20261104-203319已安装游戏、皮肤TilesLayouts和1缓存共3文件。八套布局160格覆盖/资产顺序/回读/无关对象检查通过，实际显示未验证。restore.ps1带哈希保护，索引current-highlight-layout.json。

- 2026-11-04：Highlight上下恢复5:3，20×8网格。删除截图原1/5独立无球阵型槽，原2扩为左8格（左4为原6轮播第一页主队统计，右4保留原2阵型及选择器）；原4扩为右8格（左4为原4阵型及选择器，右4为原10轮播第一页客队统计）；中间原3仍x8宽4。下排原6—10保持5/3/4/3/5，y5高3，轮播及选择保持。新增私有组合VTA HighlightIntegratedHomeStatsAndFormation / HighlightIntegratedAwayStatsAndFormation，统计直接实例化原第一页模板，team显式match.HomeTeam/AwayTeam、ishometeam真/假，列/字号/排序/导航复用。新增描述沿用原2/4的ID并替换私有注册表引用，Overview绑定及M包未改。highlight-integrated-team-stats-20261104-210602已安装游戏/皮肤G/T/catalog及1缓存共9文件。布局160格/回读/无关对象/主客队映射/模板实例/目录VTA类型/预加载检查通过，实际显示和交互待游戏验证。restore.ps1带哈希保护，索引current-highlight-layout.json。
`n- 2026-11-04：本轮Highlight维持20×8、上5下3，上方通过左右各10格原生槽的内部flex实现3/3.5/3.5/3.5/3.5/3六列：主队统计/带左右脚无球/有球/客队有球/带左右脚无球/统计。无球使用独立私有完整选择器副本、默认第二页及独立会话键；下排五等宽4/4/4/4/4，依次原比赛势头/原比赛统计/原实时球场与四图完整模块/原xG/完整原生可选区默认LiveTable（取代原右侧六页轮播）。补丁highlight-six-top-five-bottom-20261104-215021，游戏与皮肤分别备份生成，8套网格/精确flex权重/序列化/目录及Global预加载/无关对象检查通过，球场四图、共享MatchViewer、脚部行及替补模板原始字节不变。游戏运行，已安排正常退出后安装，实际状态以该目录manifest.json和automatic-install-status.txt为准，current-highlight-layout.json由安装器成功后更新；restore.ps1有哈希保护。旧布局缓存只迁移本轮位置并保留选择，退出时若缓存重写会按原8槽结构再迁移；结构有改动则停止。未启动游戏或控制桌面，游戏内显示待用户验证。
`n- 2026-11-05：Highlight下排改为3/3/8/3/3；中央8格原模块改为横向主队热点/传球列、完整实时球场、客队热点/传球列（内部1/2/1），原3居中、原4/5分置左右，原绑定/点击保留。原6/7互换，右侧倒数第二格默认原生MatchEvents赛事，最右xGStory；上排六列及20×8、上5下3不变。highlight-pitch-flanked-analysis-20261104-235348已直接安装游戏/皮肤Global与Tiles及1份缓存共5文件，八套网格、回读、主客队图表绑定、上排和替补等无关对象逐字节一致、现有目录及预加载检查通过，安装哈希5/5。未改catalog或图片字体；备份和受哈希保护restore.ps1在补丁目录，索引current-highlight-layout.json。游戏内显示/数据刷新待用户验证，未启动游戏或操作桌面。

- 2026-11-04：职员名字旁预览图标的悬浮头像修复：检查发现实际游戏NonPlayerReportPreviewTooltip（-1465827634544911600）被覆盖回原共享PersonPicture及缩略图类，而独立皮肤保留直接头像绑定。仅将独立皮肤当前StaffPortraitResourceBinding→StaffPortraitImageFrame→StaffPortraitImage三层迁移至游戏悬浮窗，180×180、原生personBind动态资源及照片函数输入不变，绕开共享模板可见性开关；姓名/合同/职能/属性及最新Highlight等其他对象原始字节保持。游戏仅VTA与内联样式2对象变化，独立主皮肤未改；悬浮GUID、资源类型、所属包首项依赖、GameWorldVisualTreeAssetPreload及原生图片函数实际对象检查通过。记录staff-hover-current-direct-portrait-20261104-232544/manifest.json，索引current-staff-hover-portrait.json，restore.ps1受哈希保护。已安装且文件校验通过，未启动游戏或操作桌面，实际显示待用户确认；后续迁移须保留实际悬浮窗的直接头像子树，不能只修职员主页面。
`n- 2026-11-05：Highlight上排两端统计改用私有HighlightUpperGoalsAssistsTallerRows及HighlightUpperGoalsAssistsView，列序位置/姓名/评分/进球/助攻/跑动/传球成功率/关键传球/关键抢断；表格行高22→28。仅两份Integrated的Stats using接入，共用HighlightRestoredNativeEightStats、原表视图和轮播未改。下排第2格使用私有HighlightCompactMatchStatsThreeByThree，原5项比较数据/事件不变，文字9/10px，标题和横条压紧、行最小高度归零并flex等分现有可用高度；原MatchStats_4x4不改。highlight-stats-order-fit-20261105-002439已安装游戏与独立皮肤G/T/V/catalog及1缓存共11文件，布局位置/比例不变，私有目录owner与Global预加载、序列化/无关对象/原球场和替补字节一致检查通过，安装哈希11文件通过。restore.ps1哈希保护，索引current-highlight-layout.json；未启动游戏或操作桌面，实际字号/11行与底边间距待用户验证。
`n- 2026-11-05：修复Highlight下排第2格比赛数据窄宽时数字被横条挤出边界。仅改私有HighlightCompactMatchStatsThreeByThree内联样式：五项每行左右数字各固定32px且不收缩，中间各4px间距，横条flex占剩余宽度、min-width0，覆盖原固定/最小宽与外距；数字10px，绑定/进度值/状态开关均未改。highlight-comparison-number-widths-20261105-004512已安装游戏/皮肤Global共2文件，序列化回读、全部序列化绑定及无关对象字节一致检查通过，安装2文件哈希通过。其他布局、上方统计、字号行高、球场和替补保持。restore.ps1哈希保护，索引current-highlight-layout.json；实际显示待用户验证，未启动游戏或控制桌面。
`n- 2026-11-05：比赛页面右侧号码文字由kit.NumberColour改为球衣副色kit.ForegroundColour，底色kit.BackgroundColour、原生fm-club-secondary-color、号码值/布局/头像/圆角保持。仅改W普通/小卡、G私有SmallSubstituteCardLowerNoRating两分支及多替补大小卡的SIStyleSetter SecondaryColorDataLink，合计每版本6处；未改Highlight模板、样式或目录。match-card-number-secondary-kit-colour-20261105-010955分别基于游戏/皮肤当前资源制作4文件，逐节点允许差异/回读/无关对象检查通过。游戏仍运行，已设置正常退出后自动安装；以该目录manifest.json和automatic-install-status.txt为准，成功后current-match-card-number-colour.json自动更新。restore.ps1哈希保护；未控制桌面或启动游戏，实际颜色待验证。

- 2026-11-05：球员四版共用大屏底排六模块解除2行最大高度限制（最小2行保留，最大100行交由原生网格分配），五类Overview1080_Compact卡片的当前及历史同GUID模板解除根节点154布局单位max-height，改为height100%/flex-grow1。上方20×8占位、四版VTA和425px属性区、宽度2/2/2/8/2/4、现有绑定及其他对象原始字节保留。补丁player-bottom-absorb-remaining-height-20261105-033651已安装游戏/独立皮肤各W/T共4文件，序列化回读及安装哈希通过；当前未发现球员大屏保存布局缓存。原生网格运行时是否完整吸收剩余高度尚待游戏确认，未启动游戏或控制桌面，不得声称已经实测。索引current-player-bottom-height.json，备份与restore.ps1带整包哈希保护；后续有并行修改须合并回退。

- 2026-11-05：职员悬浮头像继续空白，经检查先前直接头像错误复制了原生默认/非授权图片分支，DynamicReferenceToAddressableID第4项显式useDefaultPicture=true，强制请求默认图。仅在游戏与独立皮肤NonPlayerReportPreviewTooltip的StaffPortraitImage中将其改false，每份仅1个参数字节及VTA内容哈希变化；180×180、personBind、本人资源参数、职员信息及球员弹窗/共享头像/样式/Highlight均保持。原生函数输入定义和实际调用节点核对，目录类型/首项所属包/预加载及序列化回读通过。安装记录staff-hover-real-photo-argument-20261105-005244/manifest.json，索引current-staff-hover-portrait.json，restore.ps1带哈希保护。已安装，未启动游戏或控制桌面，是否正常显示仍待用户确认；此前true参数不应恢复。

- 2026-11-05：用户确认同一职员完整个人页有头像，但悬浮窗无头像；此前单图片绑定及useDefaultPicture参数调整均经用户反馈无效，不能记作成功修复。最新将当前游戏NonPlayerReportHeader实际使用的完整PersonPictureFrame→PictureTeamRemapper→PersonPicture三层接入两套NonPlayerReportPreviewTooltip，沿用个人页完整头像组件GUID/本地PPtr及原生传参，替代截取的单一图片分支；悬浮区独立180×180。仅两套悬浮VTA及样式修改，职员主页面/共享头像/球员弹窗/Highlight等其他对象字节保持；目录类型、所属包首项与预加载检查通过。记录staff-hover-working-header-chain-20261105-011846/manifest.json，索引current-staff-hover-portrait.json；已安装，restore.ps1带哈希保护。未启动游戏或控制桌面，实际显示仍待用户确认。

- 2026-11-05：用户重置布局后仍无头像，查明此前修错入口：多数职员姓名/图标单元格（含NonPlayerIconNameCell、NonPlayerNameWNationalityCell等）实际引用私有悬浮GUID a86c2c3a1a935f6494217908265a8ce7，而非此前修改的原生435b45f976d924542ba614581a0191d1。私有GUID在W容器两份对象-990000000060050/-950000000000069均仍为旧OutsideMatchSquare头像。现仅将两套资源中这两份私有悬浮的PersonPicture引用改为职员主页面完整组件13f75dc8f7df868150944efb2b46036c及其本地PPtr，实例180×180、移除缩略图类，原姓名/合同/属性/事件及球员弹窗保持；未改共享头像。实际调用者→私有GUID→所有容器副本→头像组件、本地对象/目录类型/所属包首项/预加载均检查通过。补丁staff-hover-active-private-route-20261105-014817/manifest.json已安装，索引current-staff-hover-portrait.json；restore.ps1带哈希保护。此前参数/单图/原生模板修改未解决用户实际问题，不应视为有效修复。未启动游戏或操作桌面，实际显示待用户确认。

- 2026-11-05 新增 TFWPS（-910000000000153）至 backgrounds，RGBA32 原尺寸无损像素；只入包，未设置界面关联。后续沿用名称及 ID；记录 TFWPS图片新增-20261105/manifest.json。

- 2026-11-05：开始页横幅最新为左TFWPS、右TFWX各50%，高112px，等比完整显示；移除视频显示及原promo链接分支，左TFWPS复用原生OpenURL事件，绑定 https://www.kdocs.cn/etapps/workbench/w/2myl8aB8；固定复用TFWPS -910000000000153和TFWX -910000000000150。

- 2026-11-05：TFWPS替换为新版宽图，固定ID -910000000000153，RGBA32原尺寸无损；开始页横幅左50%现有StartScreenTFWPS引用及原kdocs链接/点击事件已验证并保留，右TFWX与布局未改。图片恢复来源 current-custom-textures.json；记录 TFWPS-replacement-20261105/manifest.json。

- 2026-11-05：按用户要求只制作独立侧栏补丁，基于制作时当前主版本5资源重新迁移认可侧栏，新增4个原生链接：一线队（用户称阵容）下方“阵容规划”，球探下方依次“转会”“职员招募”，俱乐部下方“俱乐部愿景”。固定入口共19个，原15项事件/样式、医疗白图标、400px原生书签及top85px保持。链接使用当前RecruitmentSubtabs/ClubSubtabs原生MenuBody+ReportBody事件和完整参数，目录及PanelID对象校验通过。补丁sidebar-approved-rebased-20261105-024359，zip为exports/FM27-sidebar-19-links-current-main-20261105-024359-aa.zip（仅aa下5文件）；install-sidebar.ps1与restore-non-sidebar.ps1有基线哈希保护。最新主版本Highlight及其他无关对象保留，共用比赛弹窗对象直接保留当前主版原始字节，未从旧侧栏带回旧定位。补丁未安装；当前游戏保持非侧栏，主皮肤工程未改。状态索引latest_prepared_sidebar_patch记录此版本。未启动游戏，实际显示与点击待验证。主版本后续变更后须重新迁移，不可直接用旧aa覆盖。

- 2026-11-05：按用户要求已安装19入口侧栏，使用sidebar-approved-rebased-20261105-024359补丁。安装前确认游戏退出，5目标及所有受保护文件均与补丁基线一致；5文件安装哈希通过，其他资源及主皮肤工程保持。当前游戏为侧栏版，新增阵容规划/转会/职员招募/俱乐部愿景。回退当前顶部导航版用该目录restore-non-sidebar.ps1（哈希保护），non-sidebar-backup是本次安装前主版本。索引已更新；未启动游戏，实际显示及跳转待用户测试。

- 2026-11-05：侧栏专用俱乐部高度及顶部入口补丁sidebar-club-height-native-nav-20261105-025839已按用户退出游戏确认后安装。仅改游戏gameworld内MenuBar/ClubScreen及各自内联样式4对象：隐藏顶部后增7入口（消息/比赛/赛程安排/数据中心/医疗中心/青年/职员招募），保留原生导航及19侧栏按钮；俱乐部根节点88%范围+1/0.88缩放局部补偿，嵌套flex容器补齐100%高度，保留布局内容/绑定/原生事件。其他对象逐项字节不变，独立主皮肤工程未改。full-sidebar目录为最新完整5文件侧栏及正确顶部导航主版备份，restore-non-sidebar.ps1完整回退；restore-this-fix.ps1仅撤销本次。zip exports/FM27-sidebar-club-height-native-nav-20261105-025839-aa.zip仅5资源。安装校验通过，实际俱乐部高度仍待用户验证；未启动游戏或桌面控制。索引已更新，后续主版修改后需重新迁移，不可旧整包覆盖。

- 2026-11-05：用户反馈上述俱乐部高度补偿后信息不显示，已仅撤回ClubScreen及其内联样式2对象，逐字节恢复到该补偿前资源；保留顶部七入口隐藏、19侧栏入口及全部其他对象。补丁sidebar-club-display-restored-20261105-030647已安装，序列化和1文件安装校验通过；当前完整包及顶部导航备份在full-sidebar，aa新包exports/FM27-sidebar-club-display-restored-20261105-030647-aa.zip。旧高度补偿方案已停用，不得再安装或作为新侧栏默认来源；原高度偏小问题尚未解决，显示恢复待用户验证。主皮肤工程未改，未启动游戏或操作桌面，索引已更新。

- 2026-11-05：职员悬浮头像再次检查，当前两份私有悬浮已正确引用ReportMiddleSquarePersonPicture，但两份私有及原生悬浮的AssetBundle预加载跨度均缺此新本地头像引用；之前直接头像尝试只改原生悬浮，未作用于实际私有入口。尚无运行证据能断定具体哪个加载/可见性环节导致空白，不能将文件缺项直接宣称为已实测根因。本轮在游戏及独立主皮肤各自最新W资源中，将两份OutsideMatchSquare_NonPlayerReportPreviewTooltip和原生NonPlayerReportPreviewTooltip的PersonPicture实例替换为原生正常本人照片分支1027→1039→1046的BindingVariables→VisualElement→SIImage三层，照片函数完整三参数与动态personBind数据逐字节保留，明确ScaleToFit=2、白色tint alpha1、180×180，无共享模板的可见性开关或嵌套头像依赖。移除未使用的PersonPicture using并补齐各悬浮对象实际指针闭包预加载；共享头像/职员主页面/球员弹窗/现有侧栏/Highlight等所有其他对象逐项原始字节一致，catalog及图片等其他包不变。补丁staff-hover-inline-real-portrait-20261105-083438已安装游戏与皮肤共2文件，安装哈希/序列化回读/实际目录internal GUID与类型及预加载检查通过；索引current-staff-hover-portrait.json，脚本fix-staff-hover-inline-real-portrait.py，restore.ps1受哈希保护。未启动游戏或操作桌面，实际显示仍待用户验证。后续不得将历史共享模板接入版或原生默认照片分支恢复为当前方案；后续侧栏回退应合并本次修改，不能用旧整包覆盖。

- 2026-11-05：侧栏Club Overview高度试修已安装sidebar-club-native-grid-20261105-085200，仅将ClubScreen普通FM的ScalableBindableGridLayoutElement换为同页原生MultiGridLayoutElement，保留FM完整组合/绑定、控件ID及内联样式，沿用原生互补可见条件且两支均使用FM数据。仅1个VTA对象变化，其余对象逐项字节一致；19侧栏入口和顶部7快捷入口隐藏保持。已保留后续职员悬浮卡修改并迁移到新的非侧栏回退备份，主皮肤/比赛/字体/分辨率不改。安装及5文件完整包哈希检查通过；实际高度未游戏验证，不得认定已解决。当前包/回退见current-sidebar-version.json；restore-this-fix.ps1只撤销本网格试修。

- 2026-11-06：用户要求保存侧栏后回退。当前侧栏6资源已归档 G:\Doc\ChatGPT\New project\saved-progress\FM27-sidebar-saved-20261106-192159，aa包 G:\Doc\ChatGPT\New project\exports\FM27-FM27-sidebar-saved-20261106-192159-aa.zip。已恢复顶部导航主版，保留之后的球场面板及目录注册修改。回退记录 G:\Doc\ChatGPT\New project\sidebar-to-main-20261106-192159，6文件安装校验通过，俱乐部增行试修实际高度仍未确认。后续启用侧栏须迁移最新主版增量。

- 2026-11-06：俱乐部「阵容 → 概况」一线队表格上方新增86px深灰蓝名单条，使用原生 team.Players 全队数据与横向滚动。每项112px，依次显示位置、34px头像和姓名。仅增量修改游戏和独立主皮肤各自gameworld包与目录，共6文件，保留原表格绑定和其他包内对象。安装及预加载校验通过，游戏显示尚未验证。脚本 build-squad-overview-player-strip.py，记录 squad-overview-player-strip-20261106-232429/manifest.json，同目录 restore.ps1 带哈希保护。

- 2026-11-07：洗牌选秀卡片名字下方改为左右等宽。左侧内嵌原生横向位置熟练度小球场，使用 player.positionaptitudelist。右侧保留两套六项评分，每套2行3列，项目8px、数值10px。姓名下方及两栏之间各1px白线。选秀卡和实时选秀列表内嵌20261102置顶5悬浮主体及原生触发，使用当前资源目录解析子模板。核验位置图和悬浮子模板、11个评分函数的目录类型、实际对象、所属包及FC背景依赖。仅增量修改各自fantasydraft包内两个模板及其样式。补丁shuffle-position-grid-hover-20261107-102848，已安装并校验游戏与独立皮肤两份包。索引current-shuffle-player-tile.json与current-shuffle-draft-hover-fix.json，restore.ps1带哈希保护。游戏显示尚未实测。

- 2026-11-07：用户截图显示洗牌选秀位置图圆点越过底图，底图仍用原生60×42固定尺寸，位置面板却随84×54容器填充。现将居中的容器缩到78×46，底图和面板共用左上角0,0及100%宽高。评分、悬浮入口和位置熟练度绑定保持。仅修改游戏与皮肤各自洗牌卡模板和内联样式。shuffle-position-pitch-aligned-20261107-105655，已安装并校验两份包。回退用restore.ps1，游戏显示尚未实测。

- 2026-11-07：洗牌卡名字行疑似被居中状态层压暗，将状态开关改为透明零尺寸中心锚点，红色45度经理标签仅在选中分支展开160×32。可选选秀评级收在名字上方。名字11px、行高21→18px，球队和国家组缩放85%。仅增量修改各自洗牌卡模板和样式。shuffle-name-row-clear-compact-20261107-110324，已安装并校验两份包。回退用restore.ps1。游戏显示尚未实测。

- 最新覆盖（2026-11-08）：战术板Combined及Detailed桌面/触控姓名区域y60→73，位于色框底边y71下方2px；体能条及全部状态填充y57→68，高3px，贴框底并位于姓名上方。仅改相关top，姓名字号/宽度、头像、百分比文字、星级、角色按钮、三栏比例/85%缩放和原生绑定保留。游戏与独立皮肤分别增量安装，资源回读、无关对象逐字节及安装校验通过；未启动游戏或控制桌面，实际显示待确认。脚本move-tactics-name-outside-fitness-bottom.py，记录tactics-name-outside-fitness-bottom-20261108-103443/manifest.json，restore.ps1带哈希保护，索引current-tactics-card-layout.json。

- 2026-11-08：选秀比赛的球员姓名及战术卡悬浮仍有旧FantasyDraftScalableBindableGridLayoutElement分支。游戏和独立主皮肤各自gameworld增量替换PlayerCellInMatch、InMatchTacticsFitnessPortraitName、TacticsWhitePlayerReportPreview及共用名单/战术选人入口的选秀分支，共7份模板，使用与选秀卡、实时选秀列表相同的置顶5固定主体。原生触发、选秀判断、普通比赛分支保留。资源回读、其他对象字节、实际目录GUID/类型/所属包、FC背景依赖和11个评分函数校验通过。补丁draft-match-player-hover-20261108-101314，已安装并校验两份包。restore.ps1带哈希保护，索引current-draft-match-player-hover.json。实际游戏显示尚未验证。


- 2026-11-08：战术执行力共用TacticalEffectivenessPercentageGauge改为30px圆环、圈内百分比，TacticalEffectivenessGauge横向仪表右侧新增百分比；预测范围保持双值，保留原生数值/颜色/交互绑定。分别增量修改游戏和独立主皮肤各自gameworld包中两VTA及样式，无关对象逐字节一致。补丁tactical-percent-gauges-20261108-133140已安装2文件并回读校验；索引current-tactical-percent-gauges.json，restore.ps1带哈希保护。未启动游戏或操作桌面，实际显示未验证。

- 2026-11-08：战术执行力圆环缩至24px，8段、3px轨道，数值9px与百分号6px上下分开；横条改80px宽20段圆角填充、每段代表5%，保留右侧百分比及预测范围。亮段通过原生SIStyleSetter按MaxValue查询TacticalEffectivenessGaugeDataCollection的StyleClass，颜色不写死。原圆环颜色函数和反向颜色逻辑保持。游戏和独立主皮肤分别增量修改，2文件安装及回读、无关对象逐字节检查通过；未启动游戏或操作桌面，实际显示未验证。补丁tactical-segmented-gauges-20261108-135046；索引current-tactical-percent-gauges.json，restore.ps1带哈希保护。

- 2026-11-08：根据用户截图修正战术仪表：SIRadialGauge的Num Segments由8改0，使用24px原生连续空心轨道、宽3px，保留数字和百分号上下排列及原生颜色绑定。横条由20段改10段，阈值10至100、步长10，每段6px宽、8px步距；百分比文本改auto宽度并取消相关容器flex-grow与右侧空白。游戏及独立皮肤分别增量修改，回读、无关对象逐字节及2文件安装校验通过。未启动游戏或操作桌面，空心形状与留白仍待游戏内验证。补丁tactical-hollow-ring-ten-bars-20261108-140206；索引current-tactical-percent-gauges.json；restore.ps1带哈希保护。

- 2026-11-08：用户反馈横向进度条消失：仅对TacticalEffectivenessGauge恢复此前可见版本的祖先容器样式与类，移除上轮auto/none宽度与取消祖先flex-grow的改动；10段、10%阈值和原生颜色绑定保留。百分比单值宽27px右对齐、左间距4px，按钮不额外增长，圆环和全部SerializedData绑定不改。分别增量安装游戏和独立主皮肤2文件，回读及无关对象逐字节校验通过。未启动游戏或操作桌面，实际横条可见性仍待用户验证。补丁tactical-horizontal-visible-20261108-221203，索引current-tactical-percent-gauges.json；restore.ps1带哈希保护。
- 2026-11-08：按用户要求恢复战术执行力原版横向仪表，保留右侧百分比和预测范围。增量修改游戏与独立皮肤各自gameworld包内TacticalEffectivenessGauge及其内联样式，原生控件及绑定通过比对，圆环和其他对象逐字节一致。两份包安装哈希通过，游戏内显示待验证。回退用本次restore.ps1。补丁：tactical-native-horizontal-20261108-224718

- 最新覆盖（2026-11-08）：合并及详细战术板卡片的左侧位置标签、详细卡左右脚及两种卡片体能百分比文字和底板均下移6px。位置标签底板28→36px，沿用原标签点击与样式。恢复被67px头像和底图挡住的底框为73×73px、x1/y1、62.5%不透明，沿用原位置配色。姓名y76，保留与框底2px间距；体能条保持头像底部y68–71，露出下方色框。已分别安装游戏和独立皮肤，资源回读、无关对象与安装校验通过，游戏内显示待确认。记录tactics-card-left-info-rim-20261108-234118/manifest.json，restore.ps1带哈希保护，更新脚本adjust-tactics-card-left-info-and-rim.py。

- 最新覆盖（2026-11-08）：按反馈隐藏合并及详细战术卡头像底框。位置标签36→26px、向左4px（x−8→−12），占头像宽度由24→10px；保留上次左侧信息下移6px。姓名回到y73，位于头像外下方，体能条保留y68–71。游戏和独立皮肤均已安装，回读及安装校验通过，游戏内效果待确认。记录tactics-card-narrow-role-no-rim-20261109-000034/manifest.json，restore.ps1带哈希保护，更新脚本narrow-tactics-role-hide-portrait-rim.py。

- 最新覆盖：合并及详细战术卡的位置标签原生中文短名在26px时被省略。标签左扩至48px（x−34至14，右缘保持），去除文字左右内边距并取消省略号，保持单行、原生本地化绑定和提示。头像边框维持隐藏。游戏和独立皮肤已安装，文件回读、无关对象及安装哈希通过，游戏内中文显示待确认。记录tactics-card-localized-role-fit-20261109-025748/manifest.json，更新脚本fit-tactics-card-localized-role-label.py。

- 2026-11-10 新增 patchplayerbggreen（-910000000000154）至 backgrounds，RGBA32 原尺寸无损像素；只入包，未设置界面关联。后续沿用名称及 ID；记录 patchplayerbggreen图片新增-20261110/manifest.json。

- 最新覆盖（2026-11-10）：战术板合并、详细桌面/触控卡主体76×76、居中头像60×60且内缩8px，绿盾patchplayerbggreen（-910000000000154）等比铺底，星级在顶部。头像上叠体能百分比、左右脚、右侧原位置/状态图标，体能条x8/y65、宽60高3。姓名y77，位置栏y90高22。有球/无球显示单个当前阶段位置，合并左有球右无球各38px，原生中文短名允许两行。保留球场定位与中栏85%缩放。游戏和独立主皮肤已分别安装，序列化回读、绿底跨包解析、目录及预加载、原节点绑定和无关对象检查通过。游戏内显示和操作待验证。记录tactics-green-pitch-player-card-20261110-035730/manifest.json，回退restore.ps1带哈希保护，更新脚本apply-tactics-green-pitch-player-card.py。

- 最新覆盖（2026-11-10）：按截图调整战术板合并及详细桌面/触控卡，原绿盾纹理铺满76×88px，x0/y9；头像70×70px、水平居中x3/y14。星级盾顶，体能百分比和左右脚叠在头像左上，原位置/状态图标叠在右上，体能条x3/y81、宽70高3。姓名y85贴盾下沿，位置栏y99，原两行中文与合并38/38px布局保留。保持球场定位和中栏85%缩放。游戏与独立皮肤已分别安装，回读、原绑定及无关对象校验通过，游戏内显示待确认。记录tactics-tall-green-shield-20261110-041857/manifest.json，restore.ps1带哈希保护，更新脚本resize-tactics-green-shield-and-portrait.py。

- 最新覆盖（2026-11-10）：战术板头像70→60px，水平居中x8/y14。星级下移5px至y7，绿盾缩至76×78px，体能条y81→71，姓名y85→75，位置栏y99→88，头像上的体能、左右脚和右侧图标相应上移。位置栏取消22px固定高及文字上下留白，按文字行数自然撑开；合并两个38px位置栏各自按内容定高，单阶段桌面/触控使用同一规则。游戏和独立皮肤均已安装，回读、原绑定与无关对象校验通过，游戏内显示待确认。记录tactics-compact-portrait-and-role-20261110-043148/manifest.json，restore.ps1带哈希保护，更新脚本compact-tactics-portrait-and-role-height.py。

- 最新覆盖（2026-11-10）：战术板合并及详细桌面/触控卡通过拖拽容器整体上移8px，卡面和原点击热区同步。体能百分比与左右脚左移5px，右侧位置及状态图标右移5px，隐藏两套体能轨道及全部填充。顶部五颗星改为左右脚下方24×12px徽标，复用体能半透明底和原生金星，数字读取原实心星starrating.minvalue除以2，0–5星（如3.5），保留原评级显隐与缺失文案，无效值不显示0。游戏和独立皮肤均已安装，数值分支、原生目录/函数、回读、原绑定及无关对象校验通过；游戏内显示及交互待确认。记录tactics-single-star-raise-card-20261110-050540/manifest.json，restore.ps1带哈希保护，更新脚本apply-tactics-single-star-and-raise-card.py。

- 最新覆盖（2026-11-10）：按用户澄清保留合并战术卡原矩形淡框和框位置，卡片画面与对应控件相对框顶上移7px（绿盾设计顶部相对框y9→2）；详细卡内容同步上移7px，沿用既有淡框状态。星级用原生BindIntToVisible从starrating.MinValue直接匹配11个0–10档，显示0–5星和原金星，保留原评分显隐、缺失文案、姓名/位置点击及60px头像。两轮均已分别安装游戏和独立皮肤，回读、原绑定、无关对象及安装校验通过，实际星级和间距待游戏确认。间距记录tactics-card-near-frame-top-20261110-054305/manifest.json，星级记录tactics-card-frame-star-visibility-20261110-054133/manifest.json；回退脚本带哈希保护，间距补丁回退会回到中间淡框隐藏版本。


- 2026-11-10：战术卡左侧体能百分比/左右脚及右侧位置状态图标下移10px；数字星级同步下移保持脚下2px。数字显示改用体能百分比同源原生分支控件，使用原生starrating.minvalue路径，并清除标签残留文字绑定。保留原生评分缺失判断、淡框、内容相对框上移7px、整卡上移8px及中栏85%。游戏与独立皮肤已分别安装，序列化回读/无关对象/安装哈希校验通过，实际星级显示仍待游戏确认。记录tactics-overlays-down-rating-switch-20261110-060443/manifest.json；脚本fix-tactics-overlays-and-rating-selector.py；回退使用该目录restore.ps1，禁止旧整包覆盖后续修改。
- 2026-11-10：战术板右侧战术复杂度区的标题圆环和三项明细圆环左移5px。游戏与独立主皮肤分别修改TacticalPlannerSubsBlock和该区使用的CompactComplexityFactorRow实例样式。目录映射、全部绑定及其他包内对象校验通过。安装状态以本目录manifest.json与automatic-install-status.txt为准。回退脚本restore.ps1校验哈希。 补丁 tactical-complexity-icons-left5-20261110-085659。

- 2026-11-10：基于当前更新后的游戏资源迁移11月6日侧栏归档，独立替换包 exports/FM27-sidebar-updated-20261110-093634-aa.zip，6文件。按新版默认值补齐StreamedObjectList字段，保留19入口及俱乐部增行试修。回读、目录预加载、无关对象、ZIP与当前基线哈希通过；未安装，未验证游戏内显示。记录 sidebar-updated-replacement-20261110-093634/manifest.json，non-sidebar-backup为本次基线。
- 2026-11-10：最右侧战术复杂度圆环左移5px已基于最新资源重新打包并在FM27正常退出后安装。游戏与独立皮肤各1份资源的回读、安装哈希和无关对象逐字节检查通过。实际画面待验证。补丁 tactical-complexity-icons-left5-20261110-094002 取代未安装的085659版，可通过本次restore.ps1按哈希保护回退。

- 2026-11-10：按用户要求基于现有游戏文件重新迁移并安装19入口侧栏。补丁 sidebar-updated-replacement-20261110-100017，替换包 exports/FM27-sidebar-updated-20261110-100017-aa.zip。6个资源及ZIP哈希通过，保留安装前最新顶部导航版资源与哈希保护回退脚本 restore-non-sidebar.ps1。实际游戏显示待验证。

- 2026-11-10：偏好设置游戏模式的“继续按钮”下拉空白无法展开，发现ProcessingPreferencesBlock的1146 BindingVariables仍使用旧设置键continue_button_legacy_mode；当前更新原生备份同节点使用continue_button_cycle_messages。仅将游戏与独立皮肤该节点的ValueVariables对齐新版，其他字段/样式/对象逐字节保持，未重置用户偏好。补丁continue-preference-key-fix-20261110-203659已安装两份Global包并校验，catalog/侧栏等其他资源不变；索引current-continue-preference-fix.json，回退restore.ps1带哈希保护。未启动游戏或控制桌面，实际展开待用户验证。

- 2026-11-11：按用户要求以当前独立主皮肤packages为基线迁移19入口侧栏，仅输出替换文件。目录sidebar-main-repacked-20261111-005037/aa，exports/FM27-sidebar-current-main-20261111-005037-aa.zip。6文件回读、无关对象、目录/预加载及ZIP哈希校验通过。未安装，当前游戏模式沿用先前状态；游戏内效果和既有俱乐部增行试修待验证。

- 2026-11-11：用户要求安装侧栏。核对当前游戏较独立主皮肤有新版模板结构差异，重新将既有侧栏增量迁移到当前游戏，记录sidebar-updated-replacement-20261111-005406，6文件安装和zip哈希通过，当前为侧栏。exports/FM27-sidebar-installed-20261111-005406-aa.zip与实际安装一致。restore-non-sidebar.ps1回退本次最新基线，游戏内显示待确认。

- 2026-11-11：按用户要求回退sidebar-updated-replacement-20261111-005406，6文件哈希保护回退及恢复后校验通过。当前游戏为安装前最新顶部导航版，侧栏替换包保留。

- 2026-11-11：球员概览新增“中间版大头像+隐藏”“左边版大头像+隐藏”，追加为第5/6项。分别克隆当前中间/左边FC隐藏版整体，头像区域完整复用对应大头像无隐藏版，仅保留原生头像（含缺失图分支）、左右脚/惯用脚及状态图标，移除FC图/六项评分/卡面附加资料，外围隐藏属性和其他区域样式及绑定相同。新增独立VTA、样式、描述、中文标题/人物映射，补目录、所属包首项依赖、GameWorldVisualTreeAssetPreload实际locations及共享布局集合的描述预加载。游戏与独立主皮肤分别增量安装，共9文件含现有球员大屏缓存；原四版/样式及无关对象逐字节不变，当前选中项、网格/底部自适应及缓存模块位置保持。补丁two-portrait-hidden-overviews-20261111-011540，索引current-player-overview-six-variants.json；生成脚本add-two-portrait-hidden-overviews.py，独立验证verify-two-portrait-hidden-overviews.py。资源回读、实际模板/引用解析和安装后独立校验通过，restore.ps1带哈希保护；未启动游戏或操作桌面/浏览器，实际显示待用户确认。

- 2026-11-11：以最新独立主皮肤重新生成侧栏，包含主版六种球员概览新增资源。仅输出sidebar-main-repacked-20261111-040033/aa及exports/FM27-sidebar-current-main-20261111-040033-aa.zip，共6替换文件，未安装。对象回读、无关对象、目录/预加载及zip哈希通过，实际显示及俱乐部高度待用户验证。

- 2026-11-11：按要求安装侧栏，基于当时当前游戏重新迁移，保留最新六种球员概览等资源。sidebar-updated-replacement-20261111-040334，6文件安装哈希通过，包exports/FM27-sidebar-installed-20261111-040334-aa.zip。安装前资源保存于non-sidebar-backup，restore-non-sidebar.ps1带哈希保护回退。当前游戏为侧栏，游戏内显示待验证。

- 2026-11-12：按最新原版对比建议恢复主皮肤。13个原生基线未变包采用comparison.json逐文件最新成品，包含纹理警告/Small补齐与18号总览+隐藏；common样式在新版合并皮肤规则，保留5处原生图片引用和新版AssetBundle元数据。catalog在新版上增量恢复449自定义键、依赖与实际预加载，保留新版native元信息/登记/依赖及bundle新哈希键。16文件已安装，全部534个bundle按预期/保护哈希验证；182图片禁用清单、634样式、资源归属/类型/预加载及合同66条覆盖路径通过。记录main-reviewed-update-20261112-032128/manifest.json，restore.ps1带哈希保护。当前游戏为非侧边栏主版，独立皮肤及侧边栏归档未改。未启动游戏，画面与交互待用户验证。

- 2026-11-12：等待TOTAL主版main-reviewed-update-20261112-032128迁移安装完成后，以该最终游戏文件为基线，按current-sidebar-modification-list的37条对象增量生成sidebar-after-total-20261112-032443。6文件、19固定入口、400px书签，保留新版catalog原登记/依赖及公共修复。exports/FM27-sidebar-after-TOTAL-20261112-032443-aa.zip仅替换包，未安装。对象回读/无关对象、目录预加载、ZIP和全部受保护基线哈希通过，当前游戏仍为非侧栏。实际游戏显示待验证。

- 2026-11-13：右上导航搜索等工具按钮前新增76×28“切换背景”试用按钮，复用原生布尔切换事件1564320233与独立Session/Explicit键TF27.Background.ShowStadium.v1；公共GameWorldBackground默认TF skin V1（-910000000000149），点击与kunshan stadium（-910000000000145）轮换，等比裁切铺满；退出游戏后默认TF。游戏及独立主皮肤分别按当前资源增量安装各1份gameworld包，仅两份VTA/内联样式及AssetBundle预加载修改，纹理包与catalog未改；保留各自当前侧栏/导航/悬浮等修改及不透明卡片底色。补丁background-switch-button-20261113-012354，索引current-background-switch.json，restore.ps1带哈希保护。资源回读、无关对象、图片跨包引用、目录/实际预加载、2文件安装及独立检查通过；未启动游戏或控制桌面/浏览器，按钮显示、点击切换及跨页面共享状态待用户游戏内确认。

- 2026-11-13：基于当前用户修改后资源撤销侧栏增量，保留球员页面、悬浮页面及切换背景按钮。当前侧栏6资源已归档 G:\Doc\ChatGPT\New project\saved-progress\FM27-sidebar-saved-20261113-014104，aa包 G:\Doc\ChatGPT\New project\exports\FM27-FM27-sidebar-saved-20261113-014104-aa.zip。已恢复顶部导航主版，保留之后的球场面板及目录注册修改。回退记录 G:\Doc\ChatGPT\New project\sidebar-to-main-20261113-014104，6文件安装校验通过，当前原文件及后续球员/悬浮样式已完整归档。后续启用侧栏须迁移最新主版增量。

- 2026-11-13：用户实测旧背景按钮点击后顶部导航与侧栏消失；用户已另行改回仅顶部导航版。旧方案事件1564320233只从经理资料编辑页提取，未证实为通用布尔操作，禁止继续用于背景切换，旧生成脚本已停用。按当前游戏及独立主皮肤各自最新gameworld增量更换按钮事件：原生TouchStore/1024的赋值事件624065536，仅向TFBackgroundShowStadium写const.True/const.False，布尔分支每次显示一个同外观按钮。保留用户最新顶部导航/移除侧栏状态及其他对象，背景、图片、目录均不改。修正background-switch-local-assignment-20261113-014644已安装2文件，回读、无关对象、原样式前缀及安装检查通过；根因仍属事件用途判断的推测，日志无对应异常；未启动游戏或控制桌面，修正效果待用户实测。索引current-background-switch.json；本次restore.ps1会回到故障旧按钮，不能作为正常恢复方式。

- 2026-11-13：按用户反馈将无效背景按钮改为原生SIDropdown缩略图菜单，两项224×126预览及名称，原生SelectionValueBinding选择整数0/1。独立Session Explicit命名空间TF27.BackgroundPicker，背景与菜单共用selected-image-v3键；清除前两轮自定义点击事件。新增私有缩略图行VTA/样式、目录与实际预加载及依赖，复用两张已有纹理。基于当前顶部导航游戏及独立皮肤分别安装，共6文件。记录background-thumbnail-picker-20261113-015608，索引current-background-switch.json。回读、无关对象与安装哈希通过，尚未启动游戏，菜单及背景联动待用户实测。

- 2026-11-13：新增离线Windows背景替换工具 tools/TF背景替换器/dist/TFBackgroundReplacer/TFBackgroundReplacer.exe，完整目录带运行库与config.json，无需安装Python。选择图片后仅替换TF skin V1固定ID，可选同步清单原生背景副本及独立主皮肤；RGBA32保留像素、自动备份、退出游戏检查、哈希保护回退。工具实际写入当前游戏时同步current-custom-textures.json恢复来源。索引current-background-replacement-tool.json。已验证真实资源包内存替换、无关对象一致性、临时目录完整替换回退、独立EXE无界面自检；本次制作未更换游戏图片，GUI及游戏内效果未验证。

- 2026-11-13：按用户要求撤销游戏导航背景选择器及独立主皮肤对应功能。在当前最新gameworld包内仅删除选择器子树、两份私有缩略图资源及登记/预加载；公共背景VTA/样式恢复首次试验前对象，目录仅在当前哈希与缩略图安装成品一致后恢复。未使用旧整包覆盖，其他对象逐字节校验保留，当前顶部导航及后续修改保持；图片包和离线背景替换程序未改。记录background-picker-removed-20261113-193934，6文件安装哈希通过，current-background-switch.json已标记removed。未启动游戏或操作桌面，画面待用户确认。

- 2026-11-13：新增第7项球员概览“左边版-测试版”，从当前“中间版大头像+隐藏”克隆。仅重排顶部250px：左226px大头像、右100px列上队徽下国旗（各50%高度、100px等比图），随后原左侧信息与原右侧内容平分剩余宽度；前三列间距12px，信息去除原横向偏移并左对齐。保留头像缺失图、惯用脚、状态及球队/国家绑定；下方区域与来源版一致。新页面和图标组件均独立登记GUID、所属包首项依赖及GameWorldVisualTreeAssetPreload实际locations。游戏与独立主皮肤分别增量安装8文件，当前无球员大屏自定义缓存文件；原六版、其他包内对象及受保护资源保持。记录left-test-overview-20261113-212603，索引current-player-overview-test-variant.json；生成add-left-test-overview.py，独立校验verify-left-test-overview.py；restore.ps1带哈希保护，后续资源变化时须增量合并。生成及安装后独立资源校验通过，未启动游戏或操作桌面/浏览器，实际显示待用户确认。

- 2026-11-13：按用户确认的截图编号示意调整现有“左边版-测试版”：顶部原1处放2雷达、原2处放8隐藏；下排1状态/赛季统计在最左，7属性紧靠其右，再右为3球场上4比赛/禁赛下，最右5角色评分与6队内对比并排、9优缺点在其下方。顶部头像/队徽/国旗/基本信息保留。统计区复制原顶部绑定链；专用原生选择器保留全部SerializedData、联动及m_ContentContainerId，4继续通过原生槽注入，原六版和共享选择器不改。下排425px，统计240px、属性480–640px；右组合35%球场/比赛、65%角色/对比/优缺点，角色行200px、优缺点217px、中间8px。游戏与独立主皮肤分别增量安装8文件，记录left-test-numbered-layout-20261113-221754，索引current-player-overview-test-variant.json；生成rearrange-left-test-overview.py，独立校验verify-left-test-numbered-layout.py。文件回读、节点/绑定/上下文、目录及实际预加载、原六版/其他对象/受保护包一致性与安装哈希通过。restore.ps1带哈希保护，仅回到本轮重排前；后续修改须增量合并。未启动游戏或操作桌面/浏览器，实际显示和联动待用户验证。

- 2026-11-14：用户撤回上述编号重排，8文件基线哈希匹配后已回退到left-test-overview-20261113-212603的布局；随后仅测试版赛季统计改为12维雷达，游戏/独立主皮肤分别增量安装8文件，记录left-test-season-radar-20261114-005859，索引current-player-overview-test-variant.json。沿用原生赛季上下文和IsGoalkeeper，门将/非门将各12项；原始数值及两项分子/分母保留。用户明确选择越靠外越好，门将失球/丢失球权/点球失球率/失误只反向绘图；缺失显示--并收于中心，零分母不除零。各轴采用manifest/README记录的固定参考范围，不是百分位。新增私有统计/标签VTA和Global内VisualFunction，GUID/类型/所属包首项依赖及实际对象预加载完整；函数复用原生节点，补充原生FloatToTypedValue序列化字段。原六版、共享统计、页面其他布局和对象保持。生成build-left-test-season-radar.py、season-radar-builders.py；独立检查verify-left-test-season-radar.py。回读、原布局/绑定/分支一致性、10个计算场景和安装后哈希通过；未启动游戏或控制桌面/浏览器，实际显示和刷新待确认。restore.ps1仅撤回本轮雷达，不恢复已撤销的编号重排，后续改动需增量合并。

- 2026-11-14：用户实测上述12维雷达空白。Player.log明确报BindCreateListToDestination inputs incompatible；当前元数据证实SI.Core.StructList<T>仅m_value0–m_value9，旧版一次传12项超过容量，之前离线校验漏检。已改为6+6生成两列表，再用原生CombinedLists/SetListBinding合为动态List<TypedValue>（合并参数2项、保留重复项及12项顺序），新增私有Global合并函数-941100000001055。游戏/独立皮肤8文件安装校验通过，布局、门将分支、数值及其他对象保持。记录season-radar-list-capacity-fix-20261114-012138，索引current-player-overview-test-variant.json；修正fix-season-radar-list-capacity.py，基础生成及独立校验脚本同步增加容量限制与合并检查。未启动游戏或操作桌面，修正后显示仍待用户验证；不得声称离线检查已证明显示正常。本目录restore.ps1回到故障第一版雷达，不作正常恢复；完整撤回雷达需先撤本修正再撤原雷达，或对最新资源增量逆向。

- 2026-11-14：用户反馈合并版闪退并要求两个雷达。当前日志出现ConvertToListOfTypedValue空列表NullReferenceException，未证实与进程退出的完整因果。已改为原统计区左右并排的两个独立6维图，门将/非门将各保留原12项与顺序；移除Global合并函数-941100000001055、目录键及所有预加载引用。每图用原生BindListHasItemsToSwitch延迟创建（false/0空白、true/1图表）；已读取当前原生HasItems代码确认null返回false。沿用原数值/反向/缺失和赛季上下文，其他布局与原六版保持。游戏/独立主皮肤8文件已安装，资源回读、节点/空列表门控、两个6维、目录/预加载清理、其他对象及安装哈希通过。记录season-two-six-axis-radars-20261114-014827，脚本split-season-radar-two-charts.py，独立校验verify-season-two-radars.py，索引current-player-overview-test-variant.json。未启动游戏或控制桌面/浏览器，实际显示与稳定性待用户实测，不保证已消除闪退。旧12维合并生成路径不作当前恢复来源；本目录restore.ps1会返回已反馈闪退的合并版，不作正常恢复，完整撤回数据表需按README逆序撤销或增量合并。

- 2026-11-14：用户反馈双图仍不行，改为指定六项做一个雷达，其余六项在上方3列×2行。门将雷达为ExpectedGoalsPreventedPer90/TotalSavesPer90/ConcededPer90/PossessionWonPer90/PossessionLostPer90/PassCompletedPer90（用户“预期组织进球”按现有“预期阻止进球”处理）；非门将为ExpectedGoalsPer90/ShotsOnTargetPer90/ExpectedAssistsPer90/PassCompletedPer90/TacklesCompletedPer90/KeyHeadersPer90。上方六项完整复用原生数值/缺失分支和赛季上下文；门将上方获胜场次/最佳/解围/点球失球面对/失球间隔/失误，非门将获胜场次/最佳/进球/机会/关键传球/关键抢断。改为外层计算数值、内层生成DynamicReference点和列表，避免同层计算输出与派生值的初始化依赖，HasItems门控保留；此为针对不显示的结构修正，非已证实运行根因。游戏/独立主皮肤仅2份gameworld包增量安装，其余对象、Global、catalog及原六版保持。记录season-six-values-one-radar-20261114-021409；脚本season-six-values-one-radar.py，独立校验verify-season-six-values-one-radar.py；索引current-player-overview-test-variant.json。字段/两行三列/原绑定/作用域无自依赖/门控/保护资源和安装哈希通过。未启动游戏或控制桌面，实际雷达显示仍待用户确认；restore.ps1回到未认可的双图版，不作正常恢复来源。
