参考皮肤公共导航挂载方式的100px书签侧栏 V4

参考：K:/桌面/Skin files。其PrimaryNavigationBar/MainNav增加FMETSideBar模板实例，内容来自MenuBar固定链接；本版沿用公共模板实例挂载方式，内容改为用户自己的原生书签列表，含文字、原生点击、选中和编辑入口。

保留完整bookmark-drag-key上下文，新模板和书签行同时登记GUID与GameWorldVisualTreeAssetPreload标签。没有修改各页面模板，没有导入参考皮肤的整页缩放或比赛反向缩放，没有修改settings包、分辨率配置和原皮肤工程。

此为独立待测试成品，尚未安装。install.ps1试装，退出游戏后restore.ps1回退。需要实际验证公共根绑定、连续书签跳转和赛前/赛中/赛后状态，不能将静态校验视为运行验证。
