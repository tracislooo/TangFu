from pathlib import Path
import json
r=Path.cwd();out=Path(json.loads((r/'current-tactical-percent-gauges.json').read_text('utf8'))['patch'])
note='战术执行力圆环缩至24px，8段、3px轨道，数值9px与百分号6px上下分开；横条改80px宽20段圆角填充、每段代表5%，保留右侧百分比及预测范围。亮段通过原生SIStyleSetter按MaxValue查询TacticalEffectivenessGaugeDataCollection的StyleClass，颜色不写死。原圆环颜色函数和反向颜色逻辑保持。游戏和独立主皮肤分别增量修改，2文件安装及回读、无关对象逐字节检查通过；未启动游戏或操作桌面，实际显示未验证。'
(out/'修改说明.md').write_text(note,'utf8')
with (r/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n- 2026-11-08：'+note+'补丁'+out.name+'；索引current-tactical-percent-gauges.json，restore.ps1带哈希保护。\n')
