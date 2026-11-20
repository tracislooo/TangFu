from pathlib import Path
import re

root = Path('G:/Doc/ChatGPT/New project')
source = (root / 'adjust-card100-portrait90-banner-v24.py').read_text(encoding='utf-8')
readme_start = source.index("readme = '''")
readme_end = source.index("'''", readme_start + len("readme = '''")) + 3
source = source[:readme_start] + """readme = '''卡面90%、头像最终75%，缩放设置在report-player-banner-max v25

基于v24。替换global bundle后重启游戏；gameworld未变，随包提供以便保持版本一致。
实际只修改global的report-player-banner-max内联样式8045407476604796436：
- ReportMiddleCA000Layer：scale 100% → 90%，top仍为-15px。
- PersonPictureFrame：banner外层scale 120% → 100%。

PersonPicture内部原先已有75%缩放，本次模板和样式保持原值。
头像最终缩放为75% × 100% = 75%，调整仅位于report-player-banner-max。
新CA000图片640×680、栏目185px、BlueLight、国旗队徽与左右信息保持原值。
PersonPicture资源和其他非目标资源字节已校验未改变。
源packages与旧版成品没有覆盖，游戏内效果待确认。
恢复本次修改可替换v24中的global文件。
'''""" + source[readme_end:]
replacements = {
    "BASE = ROOT / '卡面110同步新图片-v23'": "BASE = ROOT / '卡面100头像90-banner-v24'",
    "OUT = ROOT / '卡面100头像90-banner-v24'": "OUT = ROOT / '卡面90头像75-banner-v25'",
    "[(1162, f32(1.1), 1.0), (1132, None, 1.2)]": "[(1162, f32(1.0), .9), (1132, f32(1.2), 1.0)]",
    " - .9) < 1e-6": " - .75) < 1e-6",
    "'portrait_final_scale': .9": "'portrait_final_scale': .75",
    "'card_scale': 1.0, 'banner_portrait_scale': 1.2": "'card_scale': .9, 'banner_portrait_scale': 1.0",
}
for old in replacements:
    assert old in source, old
pattern = re.compile('|'.join(re.escape(s) for s in sorted(replacements, key=len, reverse=True)))
patched = pattern.sub(lambda match: replacements[match.group(0)], source)
exec(compile(patched, str(root / 'adjust-card90-portrait75-banner-v25.py'), 'exec'))
