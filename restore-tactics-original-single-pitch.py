from pathlib import Path
import subprocess

bootstrap = Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(compile(bootstrap.replace('inspect-fitness-backdrop-', 'tactics-original-single-pitch-'), 'helpers', 'exec'))
original_world = R/'tactics-three-columns-20261107-051029'
original_styles = R/'tactics-columns-25-35-40-20261107-051921'
latest = R/'tactics-centered-phase-titles-20261107-060344'
outputs, checks = {}, []
S = 'ui-styles_assets_default.bundle'
for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    for name in [W, S]:
        path = folder/name
        if path not in before:
            before[path] = path.read_bytes()
            (OUT/('backup-'+tag)/name).write_bytes(before[path])
        protected.pop(path, None)
        current = UnityPy.load(before[path])
        current_objects = {o.path_id:o for o in current.objects}
        original = original_world if name == W else original_styles
        old_objects = {o.path_id:o for o in UnityPy.load(str(original/('backup-'+tag)/name)).objects}
        bad_objects = {o.path_id:o for o in UnityPy.load(str(latest/('output-'+tag)/name)).objects}
        assert old_objects.keys() == bad_objects.keys()
        targets = [i for i in old_objects if old_objects[i].get_raw_data() != bad_objects[i].get_raw_data()]
        assert len(targets) in ([2, 3] if name == W else [2]), (name, targets)
        for i in targets:
            obj = old_objects[i]
            if obj.type.name == 'AssetBundle':
                assert name == W
            elif name == W:
                assert obj.peek_name() in ['TacticalPlannerTeamShape', 'inlineStyle'], (i, obj.peek_name())
            else:
                assert obj.peek_name() in ['AlwaysAppliedStyleSheet', 'FigmaGeneratedStyles']
        for i in targets:
            assert current_objects[i].get_raw_data() == bad_objects[i].get_raw_data(), ('Subsequent edit requires merge', name, i)
            current_objects[i].set_raw_data(old_objects[i].get_raw_data())
        data = current.file.save(packer='lz4')
        saved = {o.path_id:o for o in UnityPy.load(data).objects}
        baseline = {o.path_id:o for o in UnityPy.load(before[path]).objects}
        assert saved.keys() == baseline.keys()
        for i in saved:
            assert saved[i].get_raw_data() == (old_objects[i] if i in targets else baseline[i]).get_raw_data(), (name, i)
        outputs[path] = data
        (OUT/('output-'+tag)).mkdir(exist_ok=True)
        (OUT/('output-'+tag)/name).write_bytes(data)
        checks.append({'target':str(path), 'restored_objects':targets, 'source':str(original), 'unrelated_objects_byte_identical':True})

G = W
tail = Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail = "for p,b in before.items():\n if p.name.startswith('catalog.')" + tail
tail = tail.replace("OUT/('backup-'+tag)/G", "OUT/('backup-'+tag)/p.name").replace("OUT/('output-'+tag)/G", "OUT/('output-'+tag)/p.name")
tail = tail.replace(' restore.append("Copy-Item', ' restore.append("if ((Get-FileHash -LiteralPath \'"+str(p)+"\').Hash.ToLower() -ne \'"+sha(outputs[p])+"\') { throw \'Target changed since installation.\' }")\n restore.append("Copy-Item')
start = tail.index("(OUT/'修改说明.md').write_text(")
end = tail.index('\nprint(', start)
tail = tail[:start] + "(OUT/'修改说明.md').write_text('撤销三栏改造及后续调整，恢复改造前原生单球场入口、切换按钮和模块位置。分别应用到游戏及皮肤，逐项验证无关对象。','utf8')" + tail[end:]
exec(compile(tail, 'verify-and-install', 'exec'))
