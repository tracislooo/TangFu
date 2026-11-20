from pathlib import Path
import ast,copy,json,sys,hashlib,shutil
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
for fn,names in [('verify-two-portrait-hidden-overviews.py',{'canonical'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),fn,'exec'))
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
out=Path(json.loads((R/'old-left-portrait-hidden-match-fc-prepared.json').read_text('utf8'))['output']);m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'));assert m['installed'];sha=lambda b:hashlib.sha256(b).hexdigest();files=[]
for row in tx:
 p=Path(row['target']);assert sha(p.read_bytes())==row['after'];files.append(dict(target=str(p),sha256=row['after'],passed=True))
 if p.suffix!='.bundle':continue
 old={o.path_id:o for o in UnityPy.load(row['backup']).objects};new={o.path_id:o for o in UnityPy.load(str(p)).objects}
 page=-941100000001010;fc=-950000000000162;d=new[page].read_typetree();ds=new[d['inlineSheet']['m_PathID']].read_typetree();f=new[fc].read_typetree();fs=new[f['inlineSheet']['m_PathID']].read_typetree();prior=old[page].read_typetree();ps=old[prior['inlineSheet']['m_PathID']].read_typetree()
 assert canonical(d,ds,skip_portrait=True)==canonical(f,fs,skip_portrait=True)
 assert canonical(d,ds,portrait_only=True)==canonical(prior,ps,portrait_only=True)
 assert new[fc].get_raw_data()==old[fc].get_raw_data()
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
report=dict(passed=True,installed=True,files=files,checks=m['checks'],runtime_verified=False)
(out/'verification-installed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
shutil.copy2(R/'sync-old-left-portrait-hidden-to-fc.py',out/'sync-old-left-portrait-hidden-to-fc.py')
state=dict(title='左边大头像+隐藏（旧版）',page=-941100000001010,source_page=-950000000000162,guid='4874947676d35ad2bcc95789754f22e0',manifest=str(out/'manifest.json'),verification=str(out/'verification-installed.json'),script=str(R/'sync-old-left-portrait-hidden-to-fc.py'),installed=True,installed_verified=True,runtime_verified=False,layout_outside_portrait_matches_current_old_left_fc=True,portrait_and_feet_preserved=True,switch_route_verified=True)
(R/'current-old-left-portrait-hidden-overview.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
p=R/'current-player-overview-six-variants.json';index=json.loads(p.read_text('utf8'));index['old_left_portrait_hidden_layout_update']=state;p.write_text(json.dumps(index,ensure_ascii=False,indent=2),'utf8')
(out/'README.txt').write_text('左边大头像+隐藏（旧版）：保留现有大头像、左右脚和头像状态绑定，其余使用当前左边FC卡面+隐藏（旧版）的完整布局、内容及绑定。\n已核对切换描述、布局集合、模板唯一GUID、实际预加载和子模板引用。\n游戏和独立主皮肤均已安装；离线检查通过，实际游戏显示待用户确认。\nrestore.ps1为哈希保护回退，禁止旧整包覆盖后续修改。\n','utf8')
print(json.dumps(dict(passed=True,files=len(files),output=str(out)),ensure_ascii=False))
