# FM27 皮肤：Claude Code 接手说明

整理日期：2026-11-14（America/Denver）。本次覆盖 Codex 当前全部 **34 条置顶聊天**。目标是继续维护现有唐夫皮肤，而不是从旧发布包重建。本次逐条读取最近4个回合（不足4个则全部），不声称完整重读全部历史；更早沿革结合现有交接与事务记录。本文、置顶聊天摘录和当前索引快照共同交接；工作目录内完整历史资源仍需保留。

## 1. 先读与操作边界

1. 工作目录：`G:/Doc/ChatGPT/New project`。先读该目录实时 `AGENTS.md`，再读本文；附件是本次交接时的快照。
2. 用户明确要求：**没有允许，不得使用电脑控制打开程序或浏览器。** 本次仅读取聊天和项目文件、生成交接材料，未启动游戏、浏览器或修改游戏资源。
3. 游戏唯一安装目标：`F:/Steam/steamapps/common/Football Manager 27`。Addressables 为 `fm_Data/StreamingAssets/aa`，bundle 为 `aa/StandaloneWindows64`。旧 `F:/Steam/steamapps/common/Project Taco` 禁止作为写入目标；历史记录保留原路径。
4. 独立主皮肤：`G:/Doc/FM Skin Builder/skins/tf27-01/packages`。游戏与独立主皮肤是分别维护的两套资源，不能假定相同，也不能无条件相互覆盖。侧栏另作可选分支。
5. 旧脚本可能直接安装、监听退出或硬编码历史路径。执行前先读源码、核实目标、基线哈希和运行进程；不要一次运行所有脚本。游戏运行时不替换资源，不强制结束游戏。
6. 本文中的“已安装”指最新聊天或索引记录；**本次没有重新解析或校验全部游戏资源。** 文件校验通过不等于游戏里显示或交互正常。

## 2. 接手时最重要的状态

| 项目 | 交接结论 | 依据与注意 |
|---|---|---|
| 当前主线 | 无侧栏、顶部导航 | 11月13日撤侧栏，保留当时球员页及悬浮修改；后续继续叠加补丁 |
| 最近整版导出 | `FM27-当前游戏主版本-无侧栏-20261113-194722.zip`，16个游戏文件 | 是当时发布快照，**早于11月14日测试版新改动**；不要覆盖现在资源 |
| 纹理 | `current-custom-textures.json` 为 V79、182张有效自定义纹理 | 旧文档的V78/181张已过时；增加了 patchplayerbggreen |
| 球员概览 | 原六版保留，新增第七项“左边版-测试版” | 见 `current-player-overview-test-variant.json`；测试版雷达显示仍待验收 |
| 球员悬浮 | 当前 FC 卡面版，整体不透明深灰蓝 `#263445` | 大头像版为独立可选导出；不要默认切换 |
| 页面背景 | 20种页面外壳内容下铺100%不透明 TF skin V1；非比赛模块背景alpha=0.3 | 取代旧“普通外壳纯色100%”的最终外壳方案；文字图标不随之变透明 |
| 游戏内背景切换 | 已按用户要求删除 | `current-background-switch.json`: `installed=false`、`removed_at_user_request`；保留离线替换器 |
| 侧栏 | 当前未启用 | 最新保存归档11月13日014104；再次使用须迁移到最新主线 |
| 浅色UI | 历史试验已保存，回到深色 | 浅色存档不是当前默认 |
| 最新主版迁移 | 11月12日032128安装后，又有多轮改动 | `current-main-skin-install.json` 仅指那次事务，不能当最新整包状态 |

**新旧说明发生冲突时**：结合最新用户决定、实际对象和当前事务记录判断。不要仅凭目录名日期、`installed=true` 或整个共享bundle旧哈希判定功能仍在。索引可能保留过期字段；例如侧栏索引的旧 `latest_aa_zip`、回退字段与较新的保存记录并存。

## 3. 34条置顶维护线与采用内容

下列标题与当前置顶列表一致；聊天ID及最近回合原文在本目录另外两份文件中。表内相对路径均以工作目录为根。

| 序号／聊天标题 | 应保留的内容、入口与未完成项 |
|---|---|
| 1 TOTAL 主版更新恢复与发布打包 | 无侧栏主版；`package-current-snapshot.py` 从当前游戏导出bundle及配套catalog。11月13日194722整包为发布快照，不包含此后测试版改动。 |
| 2 100.定制主页 | 朗尼克、王沐川、绿船三份仅替换 kunshan stadium 的导出，位于 `exports/主页面背景定制-20261111`，未安装到本机。已关联菜单的皮肤只需保留名称/ID替换纹理；原版游戏仍需菜单关联。 |
| 3 99.BUG 修复｜合同页与职员悬浮头像 | 合同模板66条完整覆盖路径；职员私有悬浮入口直接接本人照片并补预加载，显示待验；继续按钮偏好键应为新版 `continue_button_cycle_messages`，禁止带回 `continue_button_legacy_mode`。入口 `current-continue-preference-fix.json`、`current-staff-hover-portrait.json`。 |
| 4 1.自定义纹理、背景与资源目录 | V79/182张；保留禁用清单、固定ID、原生背景覆盖及23张纹理RGBA32修复。入口 `current-custom-textures.json`、`reserved-texture-ids.json`。不要使用聊天简介里过时的“恢复243张”。 |
| 5 2.游戏字体｜当前版本与候选字体包 | 最新候选三套 UOS黑体M、霞鹭文楷、FM圆体位于 `font-bundle-variants-20261110-095915`，仅导出未安装，每套production/fmuniverse两包。实际当前字体需核对现有两包哈希，不凭候选目录推定。 |
| 6 3.主题配色｜页面底色与模块样式 | 保留深灰蓝、状态色及Touchbar专项；页面/模块最终背景以第33条更新覆盖本聊天早期纯色与60%方案。入口 `current-ui-surface-theme.json`。 |
| 7 4.球员概览｜四版布局、FC 卡面与评分 | 原1/3版FC卡按CA七档，2/4版大头像；底排宽2:2:2:8:2:4，允许吸收剩余高度。后续六版和测试版是增量扩展。入口 `current-player-bottom-height.json`。 |
| 8 4-1.四版图示颜色和字体 | 两个中间版禁赛区常显纵向滚动条；三个左边版赛季统计数值白色；左边大头像+隐藏的资料标题12→10、内容14→12，国家/俱乐部同步。以 `overview-bans-scroll-left-white-small-20261113-011704` 为最近事务。 |
| 9 4-2.新增两版大头像布局 | 新增“中间版大头像+隐藏”“左边版大头像+隐藏”，保留原四版与选择。入口 `current-player-overview-six-variants.json`、`two-portrait-hidden-overviews-20261111-011540`。 |
| 10 5.球员悬浮卡｜头像、球场与属性布局 | 共用悬浮布局、85%缩放、球场、右侧属性及描边；选秀路由复用。最新版式选择以第11条FC为准。 |
| 11 5-1.悬浮窗版式分支文件 | 已切回FC，游戏及独立皮肤均深灰蓝不透明底；可选大头像/FC包 `exports/球员悬浮窗-大头像与FC-深灰蓝-20261113-001934.zip`。入口 `current-hover-versions.json`；最新切换 `hover-switch-back-fc-20261113-004832`。 |
| 12 6.战术界面｜草坪、阶段按钮与状态配色 | 原生草坪、有球墨绿/无球酒红、白边、星级及疲劳/体能配色。外层用单球场；卡片几何以后续第14条为准。恢复指南 `FM27-战术页面-最新修改要求与更新恢复指南.md`。 |
| 13 6-1.战术执行力｜圆环、横向仪表与百分比 | 横向恢复原生仪表，保留百分比与预测范围；圆环空心；最右四个圆环左移5px。入口 `current-tactical-percent-gauges.json`；不要恢复失败的自定义分段横条。 |
| 14 6-2.战术板球员卡｜头像、姓名与体能条 | 以 `current-tactics-card-layout.json` 最终参数为准：卡76×76、头像60×60/top17、姓名top75、位置top88/自动高，绿盾宽76、底随位置区，左信息x−15、右图标x+5、体能条隐藏。评分灰/金半星分段规则及左右脚保持；实际中文/盾边对齐待验。 |
| 15 6-3.战术右侧表格与单球场布局 (2) | 保留单球场、紧凑士气/数字疲劳、Detailed非拖动淡框隐藏；有球/无球右表“效果”最终75px（100px、95px均非最终值）。其它列以实际对象和相关manifest核对。 |
| 16 7-1比赛界面｜赛前流程、替补栏与 Highlight 布局 | 当前大屏Highlight 20×8，上5下3；顶排六区主队统计/无球/有球/客有球/无球/统计，下排五区宽3/3/8/3/3：势头/统计/中间球场分析/赛事/xG。常规右替补步距110、小屏原生80，小卡上移8。入口 `current-highlight-layout.json`、`current-substitutes-layout.json`。 |
| 17 7-2比赛卡号码、对比条与赛事文字 (2) | 号码底/字取kit.BackgroundColour/ForegroundColour；比较数字两端各32px、间隔4px；下排赛事姓名14→9.8px。入口 `current-match-card-number-colour.json`，`highlight-event-text-70-20261109-093220`。 |
| 18 7-3.调整赛后阵型为横向 | 仅中场/赛后总结横向阵型，使用私有模板；中央改为Highlight“比赛赛事”，两侧分析保留，比赛页竖向阵型不动。入口 `current-summary-formations.json`、`current-summary-events-centre.json`。 |
| 19 8.经理中心｜消息头像与概览布局 | PortalMessagesContentBlock消息头像48→144px；大屏6:10:4，左6×6收件箱/6×2球队报告/6×2数据中心；中小屏左4×4/4×2/4×2，手机不改。见 `Portal-最新修改与游戏更新后恢复说明.md`。 |
| 20 9.职员概览｜能力数值与完整头像 | 完整职员页能力原生1–20，保留颜色/角色切换；头像226×226基准、等比完整显示，不能拉伸裁切。独立于第3条职员悬浮路由。见 `FM27-职员Overview-最新修改要求与更新恢复指南.md`。 |
| 21 10.开始页｜昆山球场与双横幅链接 | kunshan stadium全屏覆盖人物；最终左TFWPS右TFWX，各50%、高112px，左保留文档链接。旧视频+TFWX仅历史。见 `start-banner-tfwps-link-20261105-022919`。 |
| 22 11.隐藏属性页｜居中退出按钮 | IGEEditDetailsBlock/MainBlock顶部居中紫底白字“X 退出 Exit”，170×36，原生全局回退事件。`add-ige-centered-exit.py`；更新后按资源名重定位ID。 |
| 23 12.顶部导航｜快捷入口、度假与页签样式 | 导航85%/13.6字号、细竖线、紧间距、下拉区域50%、页签#263445；度假/快捷入口见 `current-header-holiday-shortcut.json`、`current-primary-navigation-shortcuts.json`、`current-secondary-navigation-style.json`。 |
| 24 13.列表头像｜新闻、收件箱与原图轮廓 | 除已有头像轮廓维护，后续新增原生菜单tangfu A/B、隐藏、选择信息，前四项按此顺序；A球探五星，B实际CA/PA，其余栏目一致、原分组名保留、移除重复标题。不要沿用旧交接仅记录“全局新增头像已撤回”的不完整结论。具体最新视图按聊天摘录和对象核对。 |
| 25 14 偏好设置｜TFWX、DY 与 BB 图片网格 | 左TFWX，右DY左/BB右，各48%、间距4%；普通/FMC行位置不同，网格覆盖、minSize、实际preload必须一致。见 `preferences-grid-preload-repair-20261101-115659`、`preferences-dy-bb-horizontal-20261101-120156`。 |
| 26 15.洗牌选秀｜球员卡、FC 评分与悬浮窗 | 名字11px/行18px，队徽国家85%；姓名下左位置熟练度球场、右2×3FC评分，标题8px/数值10px；经理状态层透明、选中才展开红框，评级在姓名上；多入口共用球员悬浮。入口 `current-shuffle-player-tile.json`、`current-draft-match-player-hover.json`、`current-shuffle-draft-hover-fix.json`。 |
| 27 16.阵容概况｜横向滚动球员名单 | 一线队表格上方86px深灰蓝单行横滚，卡片位置/头像/姓名。`squad-overview-player-strip-20261106-232429`；与全局列表加头像是不同功能。 |
| 28 17.俱乐部概览｜队徽、球场图与布局 | AI页头队徽160×166跨两行，队名球衣赛季置右；首发攻防评分及两次取数试修已撤回，禁止恢复。入口 `current-club-overview.json`、`FM27-ClubOverview-最终恢复清单.md`。 |
| 29 18.添加总览+隐藏球员列表 | 数据库“总览”后加“总览+隐藏”，CA/PA换实际数值；两版知识后加俱乐部平均评分；效果125px、知识130、俱乐部170。入口 `current-player-database-views.json`；与第24条tangfu A/B是不同视图。 |
| 30 排查游戏纹理警告与资源引用 | 清理无效图片/伪类、Small布局补齐、23张纹理RGBA32等记录已入差异清单；此前本机相关五类警告报告0不等于全日志无警告。对方比赛点战术退出，用户最终定位个人缓存、非共性，不再因此改皮肤。 |
| 31 侧边栏分支｜固定导航、书签与俱乐部布局 | 可选100px侧栏、top85、19固定入口、400px原生书签、顶部编辑箭头、白医疗十字；当前已撤回。最新归档 `saved-progress/FM27-sidebar-saved-20261113-014104`，撤回 `sidebar-to-main-20261113-014104`。重装必须迁移最新主线。 |
| 32 新增球员概览左边测试版 | 第七版。从“中间版大头像+隐藏”复制；编号大重排已撤回。最新 `test-hidden-two-halves-20261114-060452`：左半CA/PA/声望及13隐藏单列，右半优点上/缺点下，另一状态转会上/欣赏的人下。赛季统计为上六项3×2、下一个六维雷达；实际雷达仍未验收。 |
| 33 调整非比赛模块背景透明度 | 最终 `page-background-tf-v1-opaque-20261113-192156` 为不透明TF skin V1底图；`nonmatch-module-opacity30-20261113-102929` 对非比赛模块背景alpha0.3，保留RGB与文字图标。背景选择器之后已删除，不要被此聊天旧回复中的“保留菜单”误导。 |
| 34 整理Bundle修改与原始文件记录 | 主/侧栏差异与游戏更新审查。入口 `current-original-bundle-diff.json`、`current-sidebar-modification-list.json`、`current-game-update-comparison.json`、`current-database-modification-list.json`。最新审查已由TOTAL实施，不能再当“尚未安装”整体重做。 |

## 4. 资源约束与迁移方法

### 图片与固定ID

- ATT/DEF/FED/KIK/SPD/SPT/TCN各10张共70张永久禁用，禁止恢复、占用ID或放占位。以 `reserved-texture-ids.json` 为准。
- PlayerTopBackground / PlayerTopBlueLight、TF patch原图已删除，不能重新导入；TF patch aligned可保留。
- 关键固定Path ID：kunshan stadium `-910000000000145`，patchplayerbg `-910000000000147`，TF skin V1 `-910000000000149`，TFWX `-910000000000150`，DY `-910000000000151`，BB `-910000000000152`，TFWPS `-910000000000153`，patchplayerbggreen `-910000000000154`。
- CA150 `-910000000000143`、CA170 `-910000000000144`必须复用；其它CA图沿原ID。七档为1–109/0/缺失→CA120，110–129→CA000，130–139→CA160，140–149→CA140，150–159→CA150，160–169→CA170，170–200→CA180。
- 图片恢复不仅迁自定义纹理，还须在新版原包上恢复原生背景图像覆盖：fm-skin-v2及索引的 `native_background_overrides`、`native_individual_replacements`；保留原生名称、ID、容器、预加载。patchplayerbg当前为用户退回的旧图。
- 不能从V53/V54/V55无筛选恢复243张。背景格式修复后的RGBA32、尺寸与解码像素都要保持。

### 新版游戏逻辑必须留在对象内部

更新时以新版原生bundle为底，按字段合并外观增量。**禁止把旧模板整对象覆盖新版**：过去 `ProcessingPreferencesBlock` 就因此带回旧偏好键，虽通过引用检查却破坏继续按钮。需保留新版控件ID、绑定、事件、偏好键及SerializedData。

不变包可复用的结论只适用于当次审查证明的基线。11月12日审查为534包中530不变/4变化；不是下一次更新的通用结论。common样式当时需保留5处原生图片引用修正；全局对象和两更衣室场景保留新版。

Addressables检查至少包括：实际对象存在、GUID、资源类型、所属bundle是首项依赖、跨包背景依赖、实际preload locations及标签。11个FC评分VisualFunction也要核对。仅PPtr可解析不能证明能加载。catalog.bin/catalog.hash必须与bundle配套，保留新版原生登记、依赖与元信息；不能直接覆盖旧catalog。合同模板还要验证66条完整 `m_ElementIdsPath`，不只GUID。

每次变更分开生成游戏/独立皮肤成品，记录原文件SHA256、修改对象、无关对象一致性、目录差异及安装后哈希；保留可审查的manifest、校验结果和哈希保护回退。共享包变化后，旧整包restore可能覆盖后续修改；应逆向撤销目标字段或重迁增量。

## 5. 最新测试版雷达：接手优先排查项

目前可证实的修复与用户结果：

1. 初版12维雷达空白，日志 `BindCreateListToDestination inputs incompatible`；原生StructList只有value0–value9，12项超容量，旧离线检查漏检。
2. 6+6合并列表方案用户反馈闪退；日志有 `ConvertToListOfTypedValue` 空列表NullReferenceException，尚未证明完整退出因果。旧Global合并函数 `-941100000001055` 已移除，不得恢复该方案。
3. 双6维仍未显示，之后改为上六项原生数值3×2，下一个指定六维，门将/非门将分开；保留HasItems门控与季赛上下文。
4. 最近又查到克隆图表丢失原生 `fmspiderchartlarge` 绘图样式，已补回：`season-radar-native-paint-style-20261114-023143`。用户在补回后尚未确认显示成功，不能宣称唯一根因已解决。
5. 最新隐藏信息左右布局 `test-hidden-two-halves-20261114-060452` 已安装，保留雷达方案。以该manifest和 `current-player-overview-test-variant.json` 为起点，不能运行旧12维或编号布局生成脚本覆盖。

当前雷达轴（均沿用每90分钟数据绑定）：门将为预期阻止进球、扑救、失球、赢得球权、丢失球权、传球成功；非门将为预期进球、射正、预期助攻、传球成功、抢断成功、关键头球。门将失球/丢失球权反向画图；用户要求越向外越好。参考范围为固定范围，非百分位；缺失值/零分母要保护。原始数值和标签按最新manifest核对。

部分历史restore会退回“已反馈闪退/空白”的前版，不是可推荐的正常恢复来源。需要回到原数据表时，应在最新资源上逆向撤销雷达增量，同时保留隐藏信息新布局及其它修改。

## 6. 差异档案、工具与接手顺序

重要档案：

- `saved-progress/FM27-warning-updated-diff-20261111-220803/修改总清单.md`：原版与修复后对象差异，父档案链需保留；不包含所有11月13–14日后续变化。
- `saved-progress/FM27-sidebar-change-record-20261111-222154/侧边栏专属修改清单.md`：37条侧栏对象增量；完整差异另含3256条，不等于当前基线可整包覆盖。
- `saved-progress/FM27-18-database-change-record-20261112-031011/修改清单.md`：两套32条对象记录。
- `saved-progress/FM27-new-update-main-review-20261112-031740/主皮肤修改建议.md` 与 `main-reviewed-update-20261112-032128/manifest.json`：新版迁移审查及实施依据。
- `FM Skin-逐对话交接与当前版本-20261109.md`：早期28聊天的深入沿革，附带副本仅供历史查询；当前数量、卡片参数、主题、视图和发布包以本次新材料为准。
- 离线背景替换器：`tools/TF背景替换器/dist/TFBackgroundReplacer/TFBackgroundReplacer.exe`，必须连同config.json与_internal目录使用；源码 `tools/TF背景替换器/tf_background_tool.py`，索引 `current-background-replacement-tool.json`。已做临时目录替换/回退与EXE自检，GUI和游戏画面未验。

建议接手顺序：先读实时AGENTS和本说明，再读任务对应实时current索引、manifest与源码；只在需要时读逐对象差异和历史摘录。收到新需求后，先比较当前实际对象与目标基线，制作增量与回退，退出游戏后安装，再做文件验证；画面/点击/稳定性由用户游戏内验收，或取得明确授权后再进行所需电脑控制。

本目录只包含说明、索引/规则/关键记录快照及聊天文字摘录，**不包含完整bundle、原始图片、游戏、字体文件或存档**。Claude Code在同一台电脑上应直接使用原工作目录；迁到别的机器须另行复制需要的资源与历史基线，不能仅凭本小包恢复完整皮肤。
