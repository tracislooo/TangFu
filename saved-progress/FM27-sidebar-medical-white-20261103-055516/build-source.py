from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,sys,zipfile
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
tree=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='write'],type_ignores=[]),'write-helper','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
index=R/'current-sidebar-version.json';state=json.loads(index.read_text('utf8'));src=Path(state['approved_version']);manifest=json.loads((src/'manifest.json').read_text('utf8'))
assert state['current_game_mode']=='non-sidebar'
game=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root'])
protected={str(p):sha(p.read_bytes()) for p in [game/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',game/'ui-styles_assets_default.bundle',game.parent/'catalog.bin',game.parent/'catalog.hash']}
for x in manifest['files']:assert sha((src/'aa'/x['path']).read_bytes())==x['sha256']
white='scaling-icons-condition-level-injured---white-size-small-16px'
for scale in [1,2,3,4]:
 env=UnityPy.load(str(game/f'ui-styles_assets_{scale}x.bundle'))
 assert any(white in str(o.read_typetree().get('m_Rules',[])) for o in env.objects if o.type.name=='MonoBehaviour'),scale
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');out=R/'saved-progress'/('FM27-sidebar-medical-white-'+stamp);out.mkdir()
shutil.copytree(src/'aa',out/'aa')
name='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';p=out/'aa/StandaloneWindows64'/name
env=UnityPy.load(str(p));a=env.assets[0];raw={i:o.get_raw_data() for i,o in a.objects.items()}
obj=a.objects[-980000000041003];doc=obj.read_typetree();original=copy.deepcopy(doc);refs={x['rid']:x for x in doc['references']['RefIds']};matches=[]
for x in refs.values():
 d=x.get('data',{});sd=refs.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if sd.get('name')=='FixedIcon_医疗中心':matches.append(x)
assert len(matches)==1
node=matches[0];assert node['data']['m_Classes']==['game-concepts-medical-centre_medium']
node['data']['m_Classes']=[white]
comparison=copy.deepcopy(doc);next(x for x in comparison['references']['RefIds'] if x['rid']==node['rid'])['data']['m_Classes']=['game-concepts-medical-centre_medium'];assert comparison==original
obj.save_typetree(doc);payload=env.file.save(packer='lz4');checked=UnityPy.load(payload).assets[0]
for i,o in checked.objects.items():
 if i==obj.path_id:assert o.read_typetree()==doc
 else:assert o.get_raw_data()==raw[i]
p.write_bytes(payload)
manifest.update(medical_icon_white=True,medical_icon_style=white,source_approved_archive=str(src),runtime_verified=False,game_installed=False,change_scope='only medical fixed navigation icon class; events, labels, layout and all other objects unchanged')
for x in manifest['files']:x['sha256']=sha((out/'aa'/x['path']).read_bytes())
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
shutil.copy2(__file__,out/'build-source.py')
zipout=R/'exports'/('FM27-sidebar-medical-white-'+stamp+'-aa.zip')
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in (out/'aa').rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out).as_posix())
with zipfile.ZipFile(zipout) as z:assert len(z.namelist())==5 and z.testzip() is None
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
state.update(approved_version=str(out),medical_icon_white=True,medical_icon_style=white,sidebar_aa_export=str(zipout),sidebar_aa_export_folder=str(out/'aa'),sidebar_aa_export_status='approved sidebar with white medical icon; not installed; current game remains non-sidebar')
index.write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
with (R/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n- 2026-11-03：侧栏医疗中心图标改为原生白色医疗十字（'+white+'），仅改TFReferenceBookmarkSidebar内FixedIcon_医疗中心的样式类，文本、事件、尺寸、其他对象逐项不变。新侧栏归档 `'+str(out.relative_to(R)).replace('\\','/')+'`，aa压缩包见current-sidebar-version.json。四档原生样式存在检查及序列化/压缩包校验通过，未启动游戏；当前游戏仍为非侧栏，未安装本次改动。再次安装须迁移最新通用资源，保留旧归档。\n')
print(json.dumps({'archive':str(out),'zip':str(zipout),'game_mode':'non-sidebar','only_medical_icon_changed':True},ensure_ascii=False))
