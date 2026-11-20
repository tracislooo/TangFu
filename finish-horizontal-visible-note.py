from pathlib import Path
import json
r=Path.cwd();out=Path(json.loads((r/'current-tactical-percent-gauges.json').read_text('utf8'))['patch'])
note='用户反馈横向进度条消失：仅对TacticalEffectivenessGauge恢复此前可见版本的祖先容器样式与类，移除上轮auto/none宽度与取消祖先flex-grow的改动；10段、10%阈值和原生颜色绑定保留。百分比单值宽27px右对齐、左间距4px，按钮不额外增长，圆环和全部SerializedData绑定不改。分别增量安装游戏和独立主皮肤2文件，回读及无关对象逐字节校验通过。未启动游戏或操作桌面，实际横条可见性仍待用户验证。'
(out/'修改说明.md').write_text(note,'utf8')
with (r/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n- 2026-11-08：'+note+'补丁'+out.name+'，索引current-tactical-percent-gauges.json；restore.ps1带哈希保护。\n')
