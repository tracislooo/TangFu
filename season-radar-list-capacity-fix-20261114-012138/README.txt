赛季12维雷达空白修正

Player.log明确记录：
Cannot execute visual function BindCreateListToDestination as the inputs are incompatible.
原生SI.Core.StructList<T>在当前游戏元数据中只有m_value0到m_value9，共10个元素槽。
上一版一次传入12条BindingPath，导致原生函数拒绝执行，图表得不到数据。

修正为两个原生列表各6项，第三步仅传2条列表路径，使用原生CombinedLists节点
合并成可增长的List<TypedValue>；保留重复项，最终12项顺序保持。
门将/非门将分支、原始数值、反向轴、缺失分支、图表外观和其他布局不变。
游戏与独立主皮肤分别安装8文件。未启动游戏或操作桌面/浏览器。

修正脚本：工作区fix-season-radar-list-capacity.py。
基础生成脚本build-left-test-season-radar.py和辅助season-radar-builders.py也已修正，
新增原生列表参数容量检查，防止再次生成超过10项的StructList参数。
独立检查verify-left-test-season-radar.py，可加--installed检查实际安装。

已通过资源回读、列表容量/两组各6项及合并顺序、原值/反向/缺失/零分母计算场景、
目录与实际对象预加载、其他资源一致性及安装哈希检查。
尚未再次进入游戏，实际显示与运行日志仍需用户验证。

restore.ps1只撤销本次容量修正，会回到已经确认空白的第一版雷达，不能作为正常恢复。
若要完整撤回雷达回到数据表，游戏退出后需先执行本目录restore.ps1，
再执行left-test-season-radar-20261114-005859/restore.ps1。
任一步哈希不匹配均应停止并增量合并，不能强制用旧整包覆盖。
