import datetime,hashlib,json,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'删除TF-patch原图-V65-20261028';F=O/'删除及校验记录.json';m=json.loads(F.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
if '--commit' in sys.argv:
 assert all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
 assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
 (R/'current-custom-textures.json').write_bytes((O/'更新后的有效图片恢复来源.json').read_bytes())
 m.update(installed=True,installed_hash_verified=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 p=R/'AGENTS.md';s=p.read_text('utf8');s=s.replace('- V62 新增纹理 `TF patch`，Path ID `-910000000000146`，须沿用；本次仅加入 backgrounds，未设置界面关联。','- V65 已删除原图 `TF patch`（原 Path ID `-910000000000146`），后续恢复不得重新导入；独立衍生图 `TF patch aligned` 保留。')
 p.write_text(s,'utf8');print('V65 installed: original TF patch removed.');sys.exit(0)
(O/'说明.txt').write_text('V65：只删除原图 TF patch（Path ID -910000000000146）及对应资源目录、预加载记录。\n当前实装来源V64含179张自定义图片，删除后178张；TF patch aligned 是独立的战术页衍生背景，保留不变。\n原图未被当前gameworld/global界面引用，无需更改布局、样式、评分函数或catalog。剩余资源对象、原生资源流和目录跨度依赖均验证保留。\n70个永久停用ID未占用，游戏及皮肤catalog各85个自定义模板/函数登记验证通过。\n安装前退出游戏，运行安装.ps1 同步删除游戏和皮肤中的原图，并更新恢复清单。含原包及恢复清单备份，回退.ps1用于故障回退。源PNG和历史备份保留。','utf-8-sig')
with zipfile.ZipFile(O.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in O.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(O))
with zipfile.ZipFile(O.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'packaged':True,'installed':m['installed'],'active_after_install':m['active_custom_texture_count']}))
