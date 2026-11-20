"""Prepare a guarded alpha-only change to the current non-match module rules."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

parser = argparse.ArgumentParser()
parser.add_argument('--alpha', type=float)
options = parser.parse_args()
statepath = R / 'current-ui-surface-theme.json'
state = json.loads(statepath.read_text('utf8'))
alpha = options.alpha if options.alpha is not None else state['nonmatch_module_backgrounds']['background_opacity']
assert 0 <= alpha <= 1
alpha_f32 = struct.unpack("<f", struct.pack("<f", alpha))[0]
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
S = 'ui-styles_assets_default.bundle'
# Keep the installed class name: existing native state bindings refer to it.
MARK = 'tf27-nonmatch-module-alpha30'
sha = lambda b: hashlib.sha256(b).hexdigest()
out = R / ('nonmatch-module-opacity50-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
out.mkdir()
payloads = {}; before = {}; protected = {}; reports = []
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    for p in folder.glob('*.bundle'):
        if p.name != S: protected[str(p)] = sha(p.read_bytes())
    for n in ['catalog.bin', 'catalog.hash']:
        p = (GAME.parent if tag == 'game' else SKIN) / n
        if p.exists(): protected[str(p)] = sha(p.read_bytes())
    p = folder / S; raw = p.read_bytes(); before[p] = raw
    env = UnityPy.load(raw); objects = {o.path_id:o for o in env.objects}; expected = {}; edits = []
    for ob in objects.values():
        if ob.type.name != 'MonoBehaviour': continue
        d = ob.read_typetree()
        if 'm_Rules' not in d: continue
        original = copy.deepcopy(d); indices = []
        for index, rule in enumerate(d['m_Rules']):
            if not any(q.get('m_Value') == MARK for c in rule.get('m_ComplexSelectors', []) for s in c['m_Selectors'] for q in s['m_Parts']): continue
            prop = next(p for p in rule['m_Properties'] if p['m_Id'] == 458752)
            hs = prop['m_Values']; assert len(hs) == 1 and hs[0]['m_ValueType'] == 4
            previous = d['colors'][hs[0]['valueIndex']]
            color = dict(previous, a=alpha_f32)
            d['colors'].append(color); hs[0]['valueIndex'] = len(d['colors']) - 1
            indices.append(index)
            edits.append({'sheet':d['m_Name'], 'rule':index, 'before_alpha':previous['a'], 'after_alpha':alpha})
        if not indices: continue
        # Reconstruct the expected differences independently: only each matched
        # background color handle and appended alpha-adjusted color may change.
        verify = copy.deepcopy(d)
        verify['colors'] = copy.deepcopy(original['colors'])
        for index in indices:
            a = original['m_Rules'][index]; b = d['m_Rules'][index]
            ap = next(p for p in a['m_Properties'] if p['m_Id'] == 458752)
            bp = next(p for p in b['m_Properties'] if p['m_Id'] == 458752)
            ac = original['colors'][ap['m_Values'][0]['valueIndex']]
            bc = d['colors'][bp['m_Values'][0]['valueIndex']]
            assert all(ac[k] == bc[k] for k in ['r','g','b']) and bc['a'] == alpha_f32
            verify['m_Rules'][index] = copy.deepcopy(a)
        assert verify == original
        ob.save_typetree(d); expected[ob.path_id] = d
    assert edits, ('No installed non-match background rules', str(p))
    packed = env.file.save(packer='lz4')
    check = {o.path_id:o for o in UnityPy.load(packed).objects}
    old = {o.path_id:o for o in UnityPy.load(raw).objects}
    assert set(check) == set(old)
    for pid, ob in check.items():
        if pid in expected: assert ob.read_typetree() == expected[pid]
        else: assert ob.get_raw_data() == old[pid].get_raw_data()
    payloads[p] = packed
    reports.append({'target':tag, 'backgrounds':len(edits), 'edits':edits, 'only_background_alpha_changed':True})
    print(tag, len(edits), 'backgrounds ->', alpha, flush=True)

tx = {'game':str(GAME), 'skin':str(SKIN), 'workspace':str(R), 'sources':{}, 'before':{}}
state['date'] = '2026-11-17'
state['scope'] = 'Opaque TF skin V1 page backgrounds; non-match module backgrounds at alpha ' + str(alpha)
state['nonmatch_module_backgrounds'].update(background_opacity=alpha, install_record=str(out/'manifest.json'),
    script=str(R/'set-nonmatch-module-opacity.py'), runtime_verified=False,
    counts={r['target']:r['backgrounds'] for r in reports})
state['page_backgrounds']['module_background_alpha'] = alpha
entry = R / 'apply-page-surfaces-theme.py'
newentry = entry.read_text('utf8').replace("with_name('apply-nonmatch-module-opacity.py')", "with_name('set-nonmatch-module-opacity.py')")
base = R / 'apply-nonmatch-module-opacity.py'
newbase = base.read_text('utf8').replace("c['a'] = f32(.3)", "c['a'] = f32(json.loads((R/'current-ui-surface-theme.json').read_text('utf8')).get('nonmatch_module_backgrounds',{}).get('background_opacity',.5))")
guide = R / 'FM27界面配色维护说明-更新后重做.md'
note = '\n\n2026-11-17：非比赛模块背景不透明度由30%调整为50%，只改现有tf27-nonmatch-module-alpha30条件规则的背景色alpha，类名沿用以保留原比赛状态绑定。TF skin V1页面底图仍100%不透明。游戏与独立主皮肤分别基于当天最新资源增量修改，各1011处；比赛背景、文字/图标、页面布局、图片和catalog保持。原模块30%规则被本条取代。维护入口apply-page-surfaces-theme.py --nonmatch-modules，实际脚本set-nonmatch-module-opacity.py；原始模块生成脚本从current-ui-surface-theme.json读取目标alpha。安装记录：' + str(out/'manifest.json') + '。文件校验不代表游戏内验证。\n'
for p, text in {statepath:json.dumps(state,ensure_ascii=False,indent=2), entry:newentry, base:newbase, guide:guide.read_text('utf8')+note}.items():
    before[p] = p.read_bytes(); payloads[p] = text.encode('utf8')
for p, data in payloads.items():
    assert p.read_bytes() == before[p], ('Concurrent change', p)
    tag = 'game' if p.parent == GAME else 'skin' if p.parent == SKIN else 'workspace'
    dst = out/tag/p.name; bak = out/('backup-'+tag)/p.name
    dst.parent.mkdir(exist_ok=True); bak.parent.mkdir(exist_ok=True)
    dst.write_bytes(data); bak.write_bytes(before[p]); tx['sources'][str(p)] = str(dst); tx['before'][str(p)] = str(bak)
manifest = {'installed':False, 'runtime_verified':False, 'background_alpha':alpha,
    'before_sha256':{str(p):sha(before[p]) for p in payloads}, 'after_sha256':{str(p):sha(b) for p,b in payloads.items()},
    'protected_sha256':protected, 'reports':reports, 'page_background_alpha':1, 'desktop_control_used':False}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps({'passed':True,'only_background_alpha_changed':True,'runtime_verified':False}),'utf8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
for name, flag in [('install.ps1',''), ('restore.ps1','--restore')]:
    (out/name).write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' "+flag+'\n','utf8')
(R/'pending-nonmatch-module-opacity50.json').write_text(json.dumps({'patch':str(out)},indent=2),'utf8')
print(out)
