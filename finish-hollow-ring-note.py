from pathlib import Path
import json
r=Path.cwd();out=Path(json.loads((r/'current-tactical-percent-gauges.json').read_text('utf8'))['patch'])
note='根据用户截图修正战术仪表：SIRadialGauge的Num Segments由8改0，使用24px原生连续空心轨道、宽3px，保留数字和百分号上下排列及原生颜色绑定。横条由20段改10段，阈值10至100、步长10，每段6px宽、8px步距；百分比文本改auto宽度并取消相关容器flex-grow与右侧空白。游戏及独立皮肤分别增量修改，回读、无关对象逐字节及2文件安装校验通过。未启动游戏或操作桌面，空心形状与留白仍待游戏内验证。'
(out/'修改说明.md').write_text(note,'utf8')
with (r/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n- 2026-11-08：'+note+'补丁'+out.name+'；索引current-tactical-percent-gauges.json；restore.ps1带哈希保护。\n')
