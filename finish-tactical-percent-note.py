from pathlib import Path
import json
r=Path.cwd();idx=json.loads((r/'current-tactical-percent-gauges.json').read_text('utf8'));out=Path(idx['patch'])
(out/'修改说明.md').write_text('战术执行力页面及共用悬浮模板：圆形分段图改为30px百分比圆环，圈内8px白字；横向仪表保持原样，右侧增加11px百分比。预测范围保留双值百分比。保留原生0–100数值、颜色映射、反向颜色、点击及刷新绑定。分别基于当前游戏和独立主皮肤增量修改，仅两个VTA及其内联样式，其他对象逐字节一致。安装2文件及回读校验通过，未启动游戏、未操作桌面，实际显示待用户确认。restore.ps1提供哈希保护回退。','utf8')
with (r/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n\n- 2026-11-08：战术执行力共用TacticalEffectivenessPercentageGauge改为30px圆环、圈内百分比，TacticalEffectivenessGauge横向仪表右侧新增百分比；预测范围保持双值，保留原生数值/颜色/交互绑定。分别增量修改游戏和独立主皮肤各自gameworld包中两VTA及样式，无关对象逐字节一致。补丁'+out.name+'已安装2文件并回读校验；索引current-tactical-percent-gauges.json，restore.ps1带哈希保护。未启动游戏或操作桌面，实际显示未验证。\n')
print(out)
