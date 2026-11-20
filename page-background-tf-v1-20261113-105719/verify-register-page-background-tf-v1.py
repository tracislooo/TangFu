from pathlib import Path
import copy, hashlib, json, sys
R = Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out = Path(json.loads((R/'pending-page-background-tf-v1.json').read_text('utf8'))['patch'])
m = json.loads((out/'manifest.json').read_text('utf8')); tx = json.loads((out/'transaction.json').read_text('utf8'))
sha = lambda b:hashlib.sha256(b).hexdigest()
reports = []
for target, source in tx['sources'].items():
    old = {o.path_id:o for o in UnityPy.load(tx['before'][target]).objects}
    new = {o.path_id:o for o in UnityPy.load(source).objects}
    count = 0; retained_helpers = 0
    for pid, ob in new.items():
        if ob.get_raw_data() == old[pid].get_raw_data(): continue
        a = old[pid].read_typetree(); b = ob.read_typetree()
        if 'm_Rules' in a:
            for key in a:
                if isinstance(a[key],list): assert b[key][:len(a[key])] == a[key],key
                else: assert a[key] == b[key],key
            continue
        assert 'inlineSheet' in a
        for key in a:
            if key != 'references': assert a[key] == b[key],key
        ar = {r['rid']:r for r in a['references']['RefIds']}; br = {r['rid']:r for r in b['references']['RefIds']}
        assert set(ar) == set(br)
        targets = [r for r in ar.values() if ar.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name') == 'Card-frame']
        allowed = {r['rid'] for r in targets} | {r['data']['m_SerializedData']['rid'] for r in targets}
        for rid,r in ar.items():
            if rid not in allowed: assert br[rid] == r,(a['m_Name'],rid)
            if r.get('data',{}).get('name') == 'TFNonMatchModuleBackgroundState': retained_helpers += 1
        for r in targets:
            nr = br[r['rid']]; sr = r['data']['m_SerializedData']['rid']
            assert nr['data']['m_FullTypeName'] == 'UnityEngine.UIElements.VisualElement'
            for key in r['data']:
                if key not in ['m_RuleIndex','m_FullTypeName']: assert r['data'][key] == nr['data'][key]
            for key,value in br[sr]['data'].items():
                if key in ar[sr]['data']: assert value == ar[sr]['data'][key]
            assert 'Binding' not in br[sr]['data']
            sh = new[b['inlineSheet']['m_PathID']].read_typetree()
            rule = sh['m_Rules'][nr['data']['m_RuleIndex']]
            color = next(p for p in rule['m_Properties'] if p['m_Id']==458752)['m_Values'][0]
            assert color['m_ValueType']==4 and sh['colors'][color['valueIndex']]['a']==0
            image = next(p for p in rule['m_Properties'] if p['m_Id']==458753)['m_Values'][0]
            assert image == {'m_ValueType':1,'valueIndex':6}
            osh = old[a['inlineSheet']['m_PathID']].read_typetree()
            oldprops = osh['m_Rules'][r['data']['m_RuleIndex']]['m_Properties'] if r['data']['m_RuleIndex']>=0 else []
            assert [p for p in rule['m_Properties'] if p['m_Id'] not in [458752,458753]] == [p for p in oldprops if p['m_Id'] not in [458752,458753]]
            count += 1
    reports.append({'target':target,'verified_page_shells':count,'existing_helpers_in_changed_templates_preserved':retained_helpers})
assert sum(r['verified_page_shells'] for r in reports)==40
(out/'verification.json').write_text(json.dumps({'passed':True,'runtime_verified':False,'reports':reports},indent=2),'utf8')
statepath=R/'current-ui-surface-theme.json'; state=json.loads(statepath.read_text('utf8'))
state['page_backgrounds']={'installed':True,'default_texture':'TF skin V1','texture_path_id':-910000000000149,
    'method':'transparent Card-frame reveals existing shared GameWorldBackground',
    'page_shell_alpha':0,'module_background_alpha':.3,'background_picker_preserved':True,
    'install_record':str(out/'manifest.json'),'script':str(R/'apply-page-background-tf-v1.py'),'runtime_verified':False}
state['scope']='Page shells reveal shared TF skin V1; non-match module backgrounds at alpha 0.3'
state['opacity']=0.0; state['date']='2026-11-13'; state['install_record']=str(out/'manifest.json')
entry=R/'apply-page-surfaces-theme.py'; text=entry.read_text('utf8')
needle="if '--nonmatch-modules' in sys.argv"
block="""if '--page-backgrounds' in sys.argv or (len(sys.argv) == 1 and global_theme_index.exists() and json.loads(global_theme_index.read_text('utf8')).get('page_backgrounds', {}).get('installed', False)):
 import runpy
 runpy.run_path(str(Path(__file__).resolve().with_name('apply-page-background-tf-v1.py')),run_name='__main__')
 raise SystemExit(0)
"""
assert needle in text
if block not in text: text=text.replace(needle,block+needle,1)
guide=R/'FM27界面配色维护说明-更新后重做.md'
note='\n\n2026-11-13：页面默认底图统一显示现有TF skin V1。当前20种Card-frame外壳改为透明、取消旧背景图片绑定，透出既有GameWorldBackground默认第0项TF skin V1（-910000000000149）；不在模块内重复铺图。保留背景缩略图选择菜单及另一选项，模块30%背景、导航、球场、卡面与其他图片关联不变。这个规则取代旧页面外壳#263445/100%规则；模块30%规则继续有效。入口apply-page-surfaces-theme.py --page-backgrounds，生成脚本apply-page-background-tf-v1.py。游戏与独立皮肤按各自最新资源处理；页面元素ID和非背景样式保留，合同模板覆盖路径的ID未改。记录：'+str(out/'manifest.json')+'。离线检查通过，游戏内尚未验证。\n'
for path,content in {statepath:json.dumps(state,ensure_ascii=False,indent=2),entry:text,guide:guide.read_text('utf8')+note}.items():
    old=path.read_bytes();data=content.encode('utf8');dst=out/'workspace'/path.name;bak=out/'backup-workspace'/path.name
    dst.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);dst.write_bytes(data);bak.write_bytes(old)
    tx['sources'][str(path)]=str(dst);tx['before'][str(path)]=str(bak)
    m['before_sha256'][str(path)]=sha(old);m['after_sha256'][str(path)]=sha(data);m['protected_sha256'].pop(str(path),None)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'README.txt').write_text('20种页面外壳透出共享TF skin V1底图；保留模块30%规则与背景菜单。\n退出游戏后安装，restore.ps1带哈希保护。\n未进行游戏内验证。\n','utf8')
for name in ['apply-page-background-tf-v1.py','verify-register-page-background-tf-v1.py']:(out/name).write_bytes((R/name).read_bytes())
watch=(R/'wait-install-nonmatch-module-opacity.py').read_text('utf8').replace("out.name.startswith('nonmatch-module-opacity30-')","out.name.startswith('page-background-tf-v1-')")
(R/'wait-install-page-background-tf-v1.py').write_text(watch,'utf8')
print(json.dumps(reports,ensure_ascii=False,indent=2))
print(out)
