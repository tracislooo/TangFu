# 当前实际资源的完整记录

snapshot/current-game/aa：当前游戏全部bundle及catalog等顶层文件，完整独立快照。snapshot/independent-main/aa：独立主皮肤实际资源，单独保留。

all-installed-bundles.json覆盖全部游戏bundle。原版同名文件完全一致者标为unchanged，其余完整导出新增、删除、修改对象。native-baseline为有差异的包保留原版；baseline-index.json为全部原版文件提供内容来源，其中完全未改的文件直接引用已验证相同哈希的当前快照，避免重复存储。构成完整原始内容来源，不把当前修改版当成原版。

每个差异对象有完整original/modified.bin、JSON.gz、字段changes.json.gz及修改位置.md。JSON中的字节使用可逆base64编码；Texture2D额外比较实际图像载荷并导出，包含.resS数据。完整bundle仍是数据流、对象类型、外部引用的最终恢复来源。若只是二进制布局变化而字段一致会单独标明semantic_equal。

.uxml为从序列化树重建的阅读文件，完整绑定、属性覆盖、节点ID等以JSON.gz和BIN为准，不可将重建UXML直接导回游戏。USS样式使用样式对象的完整序列化数据记录，包括选择器、规则、值表和资源引用。函数、布局、表格、字体、图片及容器/预加载也包括在内。

两种资源内容相同时复用同一套对象导出，来源在manifest.shared_export_from记录；原始快照仍各自保存。归档侧边栏只保存最新历史来源，不冒充今天主版，也未在本任务中迁移或安装。

目录语义记录覆盖键、类型、位置及按顺序排列的依赖和预加载标签location列表。extraData等二进制字段不由摘要完整解释，完整catalog.bin/hash保留供新版目录结构迁移使用。不能把语义摘要直接当成可安装目录。

当前索引及其拥有者manifest、验证说明在context保留；其中状态和运行验证结论各自有来源。本次只证明文件读取、导出与哈希一致，没有启动游戏验证显示。

补充：bundle-internals保留序列化类型/schema及managed reference类型的前后数据；对象之外的.resS等资源条目也逐项比较哈希并导出完整二进制，覆盖不限于Texture2D的数据流变化。

当前游戏版为本次主记录与compare-update.py默认模式。独立工程有6个同名bundle与游戏不同，完整名称见independent-versus-game.json；两者必须分别选择，不能混合catalog或将独立工程自动当作当前游戏的最新版本。
