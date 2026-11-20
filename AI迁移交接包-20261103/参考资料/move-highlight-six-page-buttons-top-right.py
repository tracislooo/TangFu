"""Move only the two existing selector strips to their module's upper right."""
from pathlib import Path
R=Path(__file__).parent
source=(R/'repair-highlight-six-page-buttons.py').read_text('utf8')
source=source.replace('highlight-six-page-buttons-repair-','highlight-six-page-buttons-top-right-')
assert '(131098,doc.px(28))' in source
source=source.replace('(131098,doc.px(28))','(131098,doc.px(0))')
old="(131089,doc.px(0)),(131103,doc.px(0)),(131080,doc.px(2)),(131105,doc.pct(100))"
new="(131089,{'m_ValueType':1,'valueIndex':2}),(131103,doc.px(8)),(131104,doc.px(4)),(131080,{'m_ValueType':1,'valueIndex':2}),(131105,doc.px(108))"
assert old in source;source=source.replace(old,new)
source=source.replace("'selector_strip_reserved_px':28","'selector_position':'top-right','right_px':8,'top_px':4,'selector_width_px':108,'bottom_reserved_px':0")
source=source.replace("'root_cause_found':'All 12 SIButton controls were created with pickingMode Ignore (1).'","'requested_change':'Move both existing six-dot strips from the bottom to the upper right.'")
start="(OUT/'修改说明.md').write_text("
beg=source.index(start);end=source.index("\nprint(",beg)
source=source[:beg]+"(OUT/'修改说明.md').write_text('仅将左右下方两个模块现有六圆点选择器移到各自右上角：距右8px、距上4px，控件区108×24px；取消底部28px预留，页面恢复使用腾出的高度。六页顺序、按钮尺寸及点击设置、Persistent选择记忆、统计表和阵型均不变。当前目录含安装前备份和restore.ps1。文件回读及无关对象检查通过，游戏内显示未验证。','utf8')"+source[end:]
exec(compile(source,'move-existing-selectors-only','exec'))
