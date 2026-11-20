# 当前游戏安装路径（置顶1–14统一）

- 用户于2026-10-30确认，置顶1–14及其后续修改的游戏根目录统一为 `F:/Steam/steamapps/common/Football Manager 27`。
- Addressables目录：`F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa`；资源包目录为其下的 `StandaloneWindows64`。
- `F:/Steam/steamapps/common/Project Taco` 已停用为修改/安装目标；历史脚本中的该路径须在执行前适配，禁止继续向旧目录写入。
- 历史manifest、备份及回退脚本保留真实历史路径，不批量改写；当前游戏路径以本节和 `current-game-location.json` 为准。

# FM27 自定义图片维护规则

- 用户于 2026-10-27 永久停用 ATT、DEF、FED、KIK、SPD、SPT、TCN 各 10 张图片，共 70 张。其名称及 Path ID 见 `reserved-texture-ids.json`。
- 这些名称及 ID 必须保持未占用：不得恢复旧图片，不得创建占位纹理，不得复用或分配给其他资源。新建及迁移资源前必须检查禁用清单。
- 最新有效图片来源见 `current-custom-textures.json`。V59 已安装，当前有效自定义图片为 178 张（含已打包的 CA150、CA170），不能再从 V53/V54/V55 无筛选恢复全部 243 张。
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

- 用户确认 `reference-layout-sidebar-100px-v5/tactics-header-arrow-fix` 当前版本可用，已完整归档至 `saved-progress/FM27-sidebar-approved-20261101`；索引见 `current-sidebar-version.json`。
- 认可要求：100px竖排原生书签，从左上角贯穿到底部，顶部导航和正文在右侧；保留文字。采用参考皮肤的整体布局及比赛逆向补偿。共用战术页的点球/定位球/对手指令仅在比赛状态启用补偿；前进后退控件100px留位；编辑箭头16×16。
- 当前操作状态：已归档；2026-11-01已回退至非侧栏基线，6个游戏/目录文件均已校验，可继续修补BUG。
- 后续BUG修复以当前非侧栏版本为基础。再次启用侧栏必须将认可侧栏改动迁移到最新BUG修复后的资源，禁止用归档整包覆盖而回滚后续修复；归档安装脚本仅在基线哈希匹配时允许执行。
- 原皮肤工程保持独立，侧栏不是后续修改的默认安装基线；历史试装包仅供追溯，不得误用早期故障版本。

- 开始页横幅最终为视频与TFWX左右各50%，父容器宽100%，高度112px；内部视频控件宽100%，移除旧390/240px固定宽约束。保留TFWX固定ID、等比完整显示、视频播放及点击绑定。
