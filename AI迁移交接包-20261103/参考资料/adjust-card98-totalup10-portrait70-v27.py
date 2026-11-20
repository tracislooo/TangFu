from pathlib import Path
import re

root = Path('G:/Doc/ChatGPT/New project')
source = (root / 'adjust-card100-portrait90-banner-v24.py').read_text(encoding='utf-8')
start = source.index("readme = '''")
end = source.index("'''", start + len("readme = '''")) + 3
source = source[:start] + """readme = '''卡面98%、总共上移10px、头像最终70% v27

基于v26。替换global bundle后重启游戏；gameworld未变，随包提供以便保持版本一致。
实际仅修改global的report-player-banner-max内联样式8045407476604796436：
- ReportMiddleCA000Layer：scale 105% → 98%。
- 卡面top -25px → -10px，即相对原始位置总共上移10px。
- PersonPictureFrame：banner外层scale 86.666667% → 93.333333%。

PersonPicture内部原有75%缩放保持原值，模板与样式没有改动。
头像最终缩放为75% × 93.333333% = 70%，调整仅在report-player-banner-max。
新CA000图片640×680、栏目185px、BlueLight、国旗队徽与左右信息保持原值。
PersonPicture资源和非目标资源字节已校验未改变。
源packages与旧版成品没有覆盖，游戏内效果待确认。
恢复本次修改可替换v26中的global文件。
'''""" + source[end:]
replacements = {
    "BASE = ROOT / '卡面110同步新图片-v23'": "BASE = ROOT / '卡面105再上移10头像65-v26'",
    "OUT = ROOT / '卡面100头像90-banner-v24'": "OUT = ROOT / '卡面98总上移10头像70-v27'",
    "[(1162, f32(1.1), 1.0), (1132, None, 1.2)]": "[(1162, f32(1.05), .98), (1132, f32(.65 / .75), .70 / .75)]",
    "assert decoded(sheet, rule, 131104) == [{'unit': 1, 'value': -15.0}]": """assert decoded(sheet, rule, 131104) == [{'unit': 1, 'value': -25.0}]
        top_prop, = [p for p in rule['m_Properties'] if p['m_Id'] == 131104]
        new_top = {'unit': 1, 'value': -10.0}
        if new_top not in sheet['dimensions']:
            sheet['dimensions'].append(new_top)
        top_prop['m_Values'] = [{'m_ValueType': 3, 'valueIndex': sheet['dimensions'].index(new_top)}]
        assert decoded(sheet, rule, 131104) == [new_top]""",
    "if p['m_Id'] != 327681": "if p['m_Id'] not in [327681, 131104]",
    "['m_Rules', 'floats']": "['m_Rules', 'floats', 'dimensions']",
    " - .9) < 1e-6": " - .70) < 1e-6",
    "'portrait_final_scale': .9": "'portrait_final_scale': .70",
    "'card_scale': 1.0, 'banner_portrait_scale': 1.2": "'card_scale': .98, 'card_top_px': -10, 'banner_portrait_scale': .70 / .75",
}
for old in replacements:
    assert old in source, old
pattern = re.compile('|'.join(re.escape(s) for s in sorted(replacements, key=len, reverse=True)))
patched = pattern.sub(lambda match: replacements[match.group(0)], source)
exec(compile(patched, str(root / 'adjust-card98-totalup10-portrait70-v27.py'), 'exec'))
