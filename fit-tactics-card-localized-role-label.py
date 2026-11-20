"""Give localized role abbreviations more room to the left of the portrait."""
from pathlib import Path


source = Path(__file__).with_name('narrow-tactics-role-hide-portrait-rim.py').read_text('utf8')
source = source.replace('tactics-card-narrow-role-no-rim-', 'tactics-card-localized-role-fit-')
source = source.replace(
    'LEFT, TOP, WIDTH, MAX_WIDTH, OPACITY = 131089, 131104, 131105, 131095, 458767\n'
    'ROLE_WIDTH, ROLE_LEFT, NAME_TOP = 26, -12, 73',
    'LEFT, WIDTH, MAX_WIDTH = 131089, 131105, 131095\n'
    'ROLE_WIDTH, ROLE_LEFT, NAME_TOP = 48, -34, 73',
)
start = source.index('    for template, name_node in [')
end = source.index('        if template == \'TacticsPositionCombined\':', start)
source = source[:start] + """    for template in (
        'TacticsPositionCombined',
        'TacticsDetailedCardDetailsDesktop',
        'TacticsDetailedCardDetailsTouch',
        'TacticsDetailedCardPositionButton',
    ):
        doc = Doc(W, name=template)
        original = copy.deepcopy(doc.d)
        edits = {}
        label_nodes = {
            'TacticsPositionCombined': (1119, 1122),
            'TacticsDetailedCardPositionButton': (1011,),
        }.get(template, ())
        for node in label_nodes:
            binding = doc.data(node)['TextBinding']['m_visualFunction']
            assert b'tactical_role' in bytes(binding['m_inputs']['m_variable']['m_argumentBytes'])
            edits[node] = [
                (196609, doc.enum('clip')),
                (131099, doc.px(0)),
                (131100, doc.px(0)),
            ]

""" + source[end:]
start = source.index('description = (')
end = source.index('installer = ', start)
source = source[:start] + """description = (
    '战术板位置标签给中文原生短名留出48px，向左扩展，右缘仍为x14。'
    '清除文本左右内边距和省略号样式，保留单行、原生短名绑定及提示。'
    '资源回读及无关对象校验通过。'
)
""" + source[end:]
exec(compile(source, str(Path(__file__).resolve()), 'exec'))
