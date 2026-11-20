# Club → Overview 最终恢复清单

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
