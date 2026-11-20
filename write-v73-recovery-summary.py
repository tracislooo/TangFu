import datetime,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'FM27图片恢复说明-V73-20261029';P.mkdir(exist_ok=True)
rp=R/'current-custom-textures.json';r=json.loads(rp.read_text('utf8'))
assert r['version']==73 and len(r['textures'])==180
r['restore_policy']='以 authoritative_source_bundle 为来源，按 textures 清单迁移全部180张有效自定义纹理；永久排除 reserved-texture-ids.json 中70个禁用名称及ID，且不恢复已删除原图 TF patch。以新版游戏原包为基础保留新版原生资源，再恢复 native_background_overrides 与 native_individual_replacements。界面引用及VTA/VisualFunction目录依赖须另行验证。'
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
(P/'恢复清单-V73.json').write_bytes(rp.read_bytes());(P/'永久禁用70张图片ID.json').write_bytes((R/'reserved-texture-ids.json').read_bytes())
byname={t['name']:t for t in r['textures']};names=['CA000','CA120','CA140','CA150','CA160','CA170','CA180','kunshan stadium','patchplayerbg','TF patch aligned','TF skin V1','TFWX']
rows='\n'.join('| '+n+' | `'+byname[n]['path_id']+'` | '+str(byname[n]['size'][0])+'×'+str(byname[n]['size'][1])+' | '+('RGBA32 无损' if byname[n]['texture_format_id']==4 else 'DXT5，保留透明度')+' |' for n in names)
source=r['authoritative_source_bundle'].replace('\\','/');native=r['native_individual_replacements'][0];ns=native['authoritative_source_bundle'].replace('\\','/')
text=f'''# FM27 图片修改与游戏更新恢复说明

版本基准：V73，2026-10-29（America/Denver）。本文覆盖本次图片维护和与这些图片有关的界面引用，不代替整个皮肤其他功能的迁移说明。

## 恢复依据

- 当前有效自定义图片 **180 张**，逐张核对当前游戏包对象哈希与清单一致。
- 原生背景内容覆盖 **54 张**，另有单独替换的 `fm27-background-texture` **1 张**。这55张原生纹理不计入180张自定义图片。
- 实时主清单：[current-custom-textures.json](<{rp.as_posix()}>)。这里的 `textures`、`native_background_overrides` 和 `native_individual_replacements` 必须一起处理。
- 本目录的 `恢复清单-V73.json` 为本次固定快照，包含180张图片的名称、文本Path ID、尺寸、格式、纹理对象SHA256，以及全部原生覆盖目标。
- 永久禁用清单：本目录 `永久禁用70张图片ID.json`。不得占用、复用、创建占位对象或恢复其图片。
- 旧的243张资源表和V53/V54/V55整包仅为历史资料，不能作为新版恢复清单。

## 最新图片来源

1. 自定义图片最新完整来源：[V73 common bundle](<{source}>)。
   SHA256：`{r['source_bundle_sha256']}`。
2. `fm27-background-texture` 最新来源：[V72 原生背景包](<{ns}>)。
   SHA256：`{native['source_bundle_sha256']}`。
3. common包包含当前生效的原生背景覆盖。native_background_overrides.bundle_sources 中的V68/V69路径是历史覆盖记录，不能拿其中旧common包覆盖V73的新图片。
4. 源PNG可能继续被用户修改。要精确重现V73，应从上述已验证bundle提取纹理对象；不能只按同名文件读取磁盘上未来的新PNG。

## 本次保留的关键图片和固定ID

| 名称 | Path ID（文本） | 尺寸 | 格式 |
|---|---|---|---|
{rows}

所有这些自定义图片均存放于 `ui-backgrounds_assets_common.bundle`，内部序列化文件为 `CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8`。
剩余168张的完整资料见JSON快照。TFWX以V73横版2172×688为准，不能恢复成早期1221×1221、1200×600或1200×383版本。TFWX包内解码RGBA像素已与本次源PNG逐字节比较一致。

## 已删除的图片

- ATT、DEF、FED、KIK、SPD、SPT、TCN 各10张，共70张：已删除纹理、命名目录及预加载记录，700个旧样式引用已清空。对应名称和ID永久禁止复用。
- 原图 `TF patch`，原ID `-910000000000146`：已删除，后续不得重新导入。
- `TF patch aligned` 是独立衍生图，保留，不得因名称相近而一起删除。
- 不删除用户源PNG或历史回退包。历史回退包中的已删除图片不得作为下一轮恢复来源。

## 原生背景覆盖

### 统一覆盖54张

使用 `TF skin V1` 的图像数据替换目标纹理内容，保留每个原生目标自己的名称、Path ID、容器及预加载记录。源纹理TF skin V1自身保留。

- common 包20张；`ui-backgrounds_assets_.bundle` 34张，共54张。
- 包含 `fm-skin-v2`，以及清单内实际存在的默认/赛事背景。
- 包含名称含 `fm27_skin` 的29张原生背景。
- 对目标逐项匹配新版实际名称。别名 `fm-supercup-skin-min` 对应 `fm-super-cup-skin-min`。
- 清单记录的6个旧名称在当时不存在：不可凭空恢复或新建。未来新版若出现同名资源，应重新确认目标。
- 完整目标与ID见下文附表和JSON。新版原生ID可能变化，先按实际名称核对，再对新版对象做内容替换；不得把旧原生对象硬塞回新版包。

### 单独覆盖1张

`fm27-background-texture`：原生ID `{native['path_id']}`，位于 `{native['bundle']}`，V72换为对应PNG，尺寸1672×941，DXT1。
它不使用TF skin V1的内容。后续按 `native_individual_replacements` 的独立来源恢复。

## 与图片有关的界面修改

### CA卡面七档

以下为当前实际皮肤规则，已经过后续调整；不要恢复成早期讨论过的规则。

| CA范围 | 卡面 |
|---|---|
| 0、缺失或1–109 | CA120 |
| 110–129 | CA000 |
| 130–139 | CA160 |
| 140–149 | CA140 |
| 150–159 | CA150 |
| 160–169 | CA170 |
| 170–200 | CA180 |

完整概览、不同概览版本及悬浮卡片中的图片指针应解析到当前backgrounds中的同名纹理，不保留其他包内旧卡面副本。用户没有要求改变区间时，图片替换仅改纹理内容。

### 开始页

- MainMenu：`kunshan stadium` 为全屏图片层，遮住原人物模型，菜单在图片上层。
- `MarketingBannerTile_8x2`：保留原循环视频、链接和分支绑定。视频宽390px、高112px；右侧240×112px区域等比完整显示TFWX。
- 更换TFWX时原ID不变，继续沿用已有指针。图片打包本身不能重建被游戏更新覆盖的界面层或样式。

### 战术页

- 保留 `TF patch aligned` 的战术页背景关联。
- 保留 `patchplayerbg` 的球员卡底图关联；虽然早期记录写“仅入包”，当前gameworld样式已引用它。
- 原图TF patch删除不能影响这些独立资源及其关联。保留原生球场渲染器、线条、控制、坐标和绑定。
- 关联的详细实现参考当前界面包和 `tactics-tf-pitch-card-background-v64-20261028-041800/manifest.json`，不能仅靠图片清单推算布局。

## 防止再次闪退和评分显示 --

已出现过两类目录缺失：

1. 67个当前包内存在的自定义VisualTreeAsset没有在游戏catalog登记，悬浮卡片GUID `64033a72b9925c8dad3b08826077c328` 加载失败。
2. Global包15个自定义VisualFunction缺少登记，其中11个门将/非门将卡面评分函数受影响，六项评分显示 `--`。

更新后必须核对每个实际使用资源的GUID、资源类型、实际包内对象、所属bundle为首项的目录依赖，以及需要的backgrounds跨包依赖。67和15为历史故障规模，不是以后应硬编码的检查数量。V73构建时两份catalog各检查169个自定义模板/函数登记；仍应按新版实际资源重新统计。

修复参考：`repair-fc-rating-functions-catalog.py`；原始修复记录位于 `repair-fc-rating-functions-catalog-20261027-051559/manifest.json`。只补目录和依赖时，不改评分公式或图片。

### m_FileID规则

- 同一backgrounds CAB内指针：m_FileID=0。
- 跨包外部路径：`archive:/CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8/CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8`。
- 跨包m_FileID=引用方externals中目标条目的索引+1，每个CAB分别核对，不能固定写7。
- 新增纹理要补命名资源目录和预加载；preloadIndex应按新版表重新计算。
- Path ID是标识符，按文本或64位整数处理，禁止转成Excel数字或JavaScript Number造成精度丢失。

## 游戏更新后的执行顺序

1. 退出游戏，完整备份新版原生背景包、界面包、catalog及catalog.hash，记录哈希。游戏运行时只准备待安装文件，不强制结束游戏。
2. 以更新后的原生包为基础，检查Unity版本、类型树和CAB兼容性。不要用旧整包覆盖新版。
3. 从V73来源迁移清单内180张自定义纹理，保留名称、固定ID、尺寸、格式、Alpha、mipmap及原始纹理字节。遇到ID冲突先查明原因，不占用禁用ID。
4. 在新版原生对象上恢复54张统一背景覆盖及1张独立背景覆盖，保留新版其他原生资源和资源流。
5. 按当前界面实现恢复卡面区间、MainMenu图片层、开始页TFWX区域和战术页图片关联。只迁移必要改动，保留新版UI其他内容。
6. 修复externals、资源目录、预加载、bundle依赖、VTA/VF目录登记；按新版所属包检查目录依赖首项。若catalog内容修改，按当前项目规则同步catalog.hash，并同步皮肤工作目录。
7. 校验180张纹理逐一存在、可解码、名称/ID不冲突，原始字节哈希与来源一致；禁用70张和已删TF patch不在成品对象、目录或预加载中。保留未改对象及原生资源流字节。
8. 检查每个UI指针实际解析到正确新图，且Addressables能通过目录找到资源；不能只验证PPtr而忽略catalog。
9. 核对安装前版本并安装，同步游戏和皮肤目录，更新current-custom-textures.json的来源、哈希、覆盖记录和安装状态，提供回退脚本。
10. 重启游戏实测：开始页/菜单、TFWX完整显示、球员悬浮卡片、七档卡面、门将和非门将评分、战术背景与球员卡、默认及赛事背景。检查Player.log新增报错。

静态解码、哈希及引用校验不等于游戏实测通过。V73记录尚未确认最终游戏内渲染，不能在后续迁移中省略第10步。

## 路径

- 游戏包目录：`F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64`
- 游戏目录登记：`F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/catalog.bin`
- 皮肤工作包：`G:/Doc/FM Skin Builder/skins/tf27-01/packages`
- 本次维护工作目录：`{R.as_posix()}`

## 附表：54张统一覆盖目标

此表是旧版目标定位记录；游戏更新后仍需核对新版名称、对象及ID。

| 实际名称 | 所属bundle | V73沿用的原生Path ID |
|---|---|---|
'''
text+='\n'.join('| '+t['actual_name']+' | '+t['bundle']+' | `'+str(t['path_id'])+'` |' for t in r['native_background_overrides']['textures'])+'\n'
(P/'恢复说明.md').write_text(text,'utf8')
print(str(P/'恢复说明.md'))
