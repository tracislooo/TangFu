import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy

BASE = ROOT / '头部加高50蓝光透明度40-v14'
OUT = ROOT / '头部与report-max高度300-v15'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
HEADER, HEADER_STYLE = 5775949770471550939, -1940069326759809061
BANNER, BANNER_STYLE = -4194025542157271532, 8045407476604796436
UNDERLAY, UNDERLAY_STYLE = -910000000000201, -910000000000202

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}

def nodes_named(doc, name):
    records = {r['rid']: r for r in doc['references']['RefIds']}
    return [r for r in records.values() if records.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name]

def dimension(sheet, value):
    item = {'unit': 1, 'value': float(value)}
    if item not in sheet['dimensions']:
        sheet['dimensions'].append(item)
    return {'m_ValueType': 3, 'valueIndex': sheet['dimensions'].index(item)}

def values(sheet, rule, pid):
    props = [p for p in rule['m_Properties'] if p['m_Id'] == pid]
    return None if not props else [sheet['dimensions'][v['valueIndex']] for v in props[0]['m_Values']]

changes, validation = [], []
OUT.mkdir(exist_ok=True)
for bundle in [GLOBAL, WORLD]:
    source = BASE / bundle
    source_hash = sha(source.read_bytes())
    env, objects = load(source)
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objects.items()}
    targets = [(BANNER, BANNER_STYLE, 'report-player-banner-max')] if bundle == GLOBAL else [
        (HEADER, HEADER_STYLE, 'report-player-full-header-max'),
        (UNDERLAY, UNDERLAY_STYLE, 'report-player-banner-max')]
    altered = {}
    for doc_id, style_id, name in targets:
        doc, sheet = objects[doc_id].read_typetree(), objects[style_id].read_typetree()
        old_sheet = copy.deepcopy(sheet)
        nodes = nodes_named(doc, name)
        assert len(nodes) == (2 if doc_id == HEADER else 1)
        records = doc['references']['RefIds']
        changed_rules = []
        for node in nodes:
            rule_index = node['data']['m_RuleIndex']
            assert sum(r.get('data', {}).get('m_RuleIndex') == rule_index for r in records) == 1
            rule = sheet['m_Rules'][rule_index]
            pids = [131087] if doc_id == HEADER else [131087, 131096]
            if doc_id == HEADER:
                assert values(sheet, rule, 131087) == [{'unit': 1, 'value': 198.0}]
            else:
                assert values(sheet, rule, 131096) == [{'unit': 1, 'value': 310.0}]
                assert values(sheet, rule, 131087) is None
            for pid in pids:
                before = values(sheet, rule, pid)
                props = [p for p in rule['m_Properties'] if p['m_Id'] == pid]
                if props:
                    assert len(props) == 1
                    props[0]['m_Values'] = [dimension(sheet, 300)]
                else:
                    rule['m_Properties'].append({'m_Id': pid, 'm_CustomName': '', 'm_Line': -1,
                                                'm_Values': [dimension(sheet, 300)]})
                changes.append({'bundle': bundle, 'style_path_id': style_id, 'node_rid': node['rid'],
                                'rule_index': rule_index, 'property_id': pid,
                                'old_inline_value': before, 'new_inline_value': values(sheet, rule, pid)})
            # All properties outside height and min-height remain byte-for-byte equal structurally.
            assert [p for p in rule['m_Properties'] if p['m_Id'] not in pids] == [p for p in old_sheet['m_Rules'][rule_index]['m_Properties'] if p['m_Id'] not in pids]
            changed_rules.append(rule_index)
        for i, old_rule in enumerate(old_sheet['m_Rules']):
            if i not in changed_rules:
                assert sheet['m_Rules'][i] == old_rule
        for key in old_sheet:
            if key not in ['m_Rules', 'dimensions']:
                assert sheet[key] == old_sheet[key], key
        objects[style_id].save_typetree(sheet)
        altered[style_id] = sheet
    destination = OUT / bundle
    destination.write_bytes(env.file.save(packer='lz4'))
    _, check = load(destination)
    assert check.keys() == objects.keys()
    for pid, digest in original_hashes.items():
        if pid not in altered:
            assert sha(check[pid].get_raw_data()) == digest, pid
    for pid, tree in altered.items():
        assert check[pid].read_typetree() == tree, pid
    for doc_id, style_id, name in targets:
        for node in nodes_named(check[doc_id].read_typetree(), name):
            sheet = check[style_id].read_typetree()
            rule = sheet['m_Rules'][node['data']['m_RuleIndex']]
            assert values(sheet, rule, 131087) == [{'unit': 1, 'value': 300.0}]
            if doc_id != HEADER:
                assert values(sheet, rule, 131096) == [{'unit': 1, 'value': 300.0}]
    assert sha(source.read_bytes()) == source_hash
    validation.append({'bundle': bundle, 'source_sha256': source_hash, 'output_sha256': sha(destination.read_bytes()),
                       'modified_styles': list(altered), 'untouched_assets_verified': len(objects) - len(altered)})

readme = '''头部与report-max统一高度300px v15

基于v14，替换本包global和gameworld两个同名bundle，重启游戏。

PlayerReportHeader height：198px → 300px，底层装饰副本同步。
report-player-banner-max height：新增300px；min-height：310px → 300px。
底层装饰模板同步为height:300px、min-height:300px。
report-max上一版最小高度是310px，本次统一300px，因此比上一版最小高度少10px。
BlueLight不透明度0.4、缩放200%、国旗队徽间距80px、其他布局与资源保持原值。

修改记录.json记录具体样式规则及恢复前值。
若需恢复本次修改，使用之前交付的v14压缩包中的两个同名bundle。
源packages和旧版成品未覆盖。
已重读验证目标参数和无关资源；游戏内效果待确认。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({'changes': changes, 'validation': validation}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        if path.is_file():
            z.write(path, path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'validation': validation, 'height': 300}, ensure_ascii=True))
