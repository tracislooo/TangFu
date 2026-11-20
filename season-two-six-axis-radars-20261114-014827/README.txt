赛季统计：两个独立6维雷达

已按用户要求将12项分成左右并排的两个6维图，门将/非门将各自沿用原12项数据及顺序。
其他布局、原始标签数值、门将判断和反向绘图规则不变。
删除上一版合并函数、目录键和所有相关预加载引用。

本次Player.log包含ConvertToListOfTypedValue读取空列表的NullReferenceException。
两个图分别读取radarPointsFirstHalf和radarPointsSecondHalf。
各自先通过原生BindListHasItemsToSwitch判断：索引0为空白等待分支，索引1才创建图表。
已检查当前原生HasItems实现：null返回false，非空再判断Count，因此空列表阶段不创建图表。
离线检查不能证明闪退因果已完全解决或画面已正常，仍需游戏内验证。

生成/修正脚本：工作区split-season-radar-two-charts.py。
独立检查：verify-season-two-radars.py；--installed检查实际安装。
游戏及独立主皮肤8文件安装哈希、资源回读、两个图各6维、延迟创建、合并函数清理、
原六版/共享模块/其他对象和受保护包一致性检查通过。未启动游戏、未控制桌面/浏览器。

restore.ps1只撤销本次拆图，会返回用户已反馈闪退的合并版，不作正常恢复。
若完整恢复雷达之前的数据表，需在游戏退出且各阶段哈希匹配时依次撤销：
本目录 → season-radar-list-capacity-fix-20261114-012138 → left-test-season-radar-20261114-005859。
后续资源有改动时须增量逆向，不得强制旧整包覆盖。
