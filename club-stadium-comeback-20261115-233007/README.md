球场图片读取改为 Comeback 的 DatabaseObjectWithColourReplacementFallback，ResourceType=7，KitType=fmetstadium。沿用现有球场照片铺底、资料上层的布局。
原生 ResolveResourceID 已核对为 kit2d_{club_id}_fmetstadium；通过当前2700数据库 team表的球场索引关联现有球场ID照片，登记 15142 个俱乐部图片键（7056 张不同照片）。图片不复制、不重新压缩。本地图片目录移动后需重建登记。
仅修改两套 gameworld 的 ClubOverviewStadiumStack 对象及各自 catalog/hash。奖杯、其他对象及受保护资源校验保持。游戏运行时不安装；install.ps1 必须正常退出游戏后运行。restore.ps1 受哈希保护，仅撤回本次，后续资源变化不能整包覆盖。
覆盖基于本地初始数据库，存档后新建或更换球场不一定与初始对应；无照片不显示图片。未启动游戏，实际显示待用户确认。
