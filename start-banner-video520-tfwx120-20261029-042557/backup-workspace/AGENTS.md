# FM27 自定义图片维护规则

- 用户于 2026-10-27 永久停用 ATT、DEF、FED、KIK、SPD、SPT、TCN 各 10 张图片，共 70 张。其名称及 Path ID 见 `reserved-texture-ids.json`。
- 这些名称及 ID 必须保持未占用：不得恢复旧图片，不得创建占位纹理，不得复用或分配给其他资源。新建及迁移资源前必须检查禁用清单。
- 最新有效图片来源见 `current-custom-textures.json`。V59 已安装，当前有效自定义图片为 180 张（含已打包的 CA150、CA170），不能再从 V53/V54/V55 无筛选恢复全部 243 张。
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

- V70 新增纹理 `TFWX`，Path ID `-910000000000150`，须沿用；本次仅加入 backgrounds，未设置界面关联。
