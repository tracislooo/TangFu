"""Sidebar-only club geometry compensation and removal of duplicate header shortcuts."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,shutil,struct,sys,zipfile
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for file,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 tree=ast.parse((R/file).read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),file+':helpers','exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest();f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
index=json.loads((R/'current-sidebar-version.json').read_text('utf8'));BASE=Path(index['installed_variant']);assert index['current_game_mode']=='sidebar'
path=GAME/W;before=path.read_bytes();env=UnityPy.load(before);a=env.assets[0];raw={i:o.get_raw_data() for i,o in a.objects.items()};expected={};audit=[]
assert -980000000041003 in a.objects
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def get(name):
 ob=next(o for o in a.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name);d=ob.read_typetree();sid=d['inlineSheet']['m_PathID'];s=a.objects[sid].read_typetree();return ob,d,refs(d),sid,s,Styles(s)
ob,d,rr,sid,s,st=get('MenuBar');original=copy.deepcopy(d)
names=['PrimaryNavMessagesButton','PrimaryNavCompetitionsButton','PrimaryNavFixtureScheduleButton','PrimaryNavDataHubButton','PrimaryNavMedicalCentreButton','PrimaryNavYouthButton','PrimaryNavStaffButton'];hidden=[]
for n in names:
 matches=[x for x in rr.values() if rr.get(x.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==n];assert len(matches)==1,n
 node=matches[0];st.edit(node,[st.p(131081,st.en('none'))]);hidden.append(node['rid'])
for rid,x in refs(original).items():
 old=copy.deepcopy(x)
 if rid in hidden:old['data']['m_RuleIndex']=rr[rid]['data']['m_RuleIndex']
 assert rr[rid]==old,('Navigation data changed',rid)
validate_ui(d,s);expected[ob.path_id]=d;expected[sid]=s;audit.append(dict(template='MenuBar',hidden_shortcuts=names,original_navigation_bindings_and_events_unchanged=True))
ob,d,rr,sid,s,st=get('ClubScreen');original=copy.deepcopy(d)
# Counter the parent sidebar scale locally, with matching extents to retain its allocated bounds.
# Unlike the match compensation this keeps the sidebar's horizontal reservation intact.
scale=f32(1/.88);root=1001
st.edit(rr[root],[st.p(131105,st.pct(88)),st.p(131097,st.px(0)),st.p(131087,st.pct(88)),st.p(131096,st.px(0)),st.p(131094,st.en('none')),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(327682,st.en('left'),st.en('top')),st.p(327681,st.num(scale),st.num(scale))])
# Make the nested flex containers allocate vertical space rather than use content height.
fill=[1004,1006,1010,1014,1016,1021,1025,1026]
for rid in fill:
 st.edit(rr[rid],[st.p(131087,st.pct(100)),st.p(131096,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1))])
for rid,x in refs(original).items():
 old=copy.deepcopy(x)
 if rid in [root]+fill:old['data']['m_RuleIndex']=rr[rid]['data']['m_RuleIndex']
 assert rr[rid]==old,('Club content changed',rid)
assert abs(f32(.88)*scale-1)<0.00001
validate_ui(d,s);expected[ob.path_id]=d;expected[sid]=s;audit.append(dict(template='ClubScreen',root_extent_percent=88,local_scale=scale,combined_sidebar_scale=scale*f32(.88),fill_containers=fill,content_bindings_and_nested_templates_unchanged=True,runtime_verified=False))
for pid,value in expected.items():a.objects[pid].save_typetree(value)
payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
for pid,o in check.objects.items():
 if pid in expected:assert o.read_typetree()==expected[pid]
 else:assert o.get_raw_data()==raw[pid],('Unrelated object changed',pid)
out=R/('sidebar-club-height-native-nav-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();(out/'packages').mkdir();(out/'backup-game').mkdir();source=out/'packages'/W;backup=out/'backup-game'/W;source.write_bytes(payload);backup.write_bytes(before)
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+list(SKIN.glob('*')) if p.is_file() and p!=path}
tx=[dict(target=str(path),source=str(source),backup=str(backup),before=sha(before),after=sha(payload))]
manifest=dict(installed=False,runtime_verified=False,sidebar_only=True,independent_main_skin_modified=False,checks=audit,changed_objects=[dict(path_id=pid,name=x.get('m_Name')) for pid,x in expected.items()],other_objects_byte_identical=True,protected_sha256=protected)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for name,flag in [('install',''),('restore-this-fix',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
# Composite independent sidebar package and full rollback preserve the main installation baseline.
full=out/'full-sidebar';full.mkdir();(full/'packages').mkdir();(full/'non-sidebar-backup').mkdir();ftx=[];aa=out/'aa';(aa/'StandaloneWindows64').mkdir(parents=True)
for row in json.loads((BASE/'transaction.json').read_text('utf8')):
 target=Path(row['target']);name=target.name;current=target.read_bytes();assert sha(current)==row['after'],('Concurrent resource change since sidebar install',name)
 data=payload if name==W else current;src=full/'packages'/name;bak=full/'non-sidebar-backup'/name;src.write_bytes(data);base=Path(row['backup']).read_bytes();assert sha(base)==row['before'];bak.write_bytes(base)
 ftx.append(dict(target=str(target),source=str(src),backup=str(bak),before=sha(base),after=sha(data)))
 dest=aa/('StandaloneWindows64' if name.endswith('.bundle') else '')/name;dest.write_bytes(data)
fm=dict(installed=False,runtime_verified=False,sidebar_only=True,fixed_navigation_count=19,club_height_adjustment=True,top_custom_shortcuts_hidden=names,protected_sha256={p:h for p,h in protected.items() if p not in {x['target'] for x in ftx}})
(full/'transaction.json').write_text(json.dumps(ftx,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps(fm,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',full/'installer.py')
for name,flag in [('install-sidebar',''),('restore-non-sidebar',' --restore')]:
 (full/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
zipout=R/'exports'/('FM27-'+out.name+'-aa.zip')
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in aa.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out).as_posix())
with zipfile.ZipFile(zipout) as z:assert len(z.namelist())==5 and z.testzip() is None
manifest['full_sidebar_variant']=str(full);manifest['aa_export']=str(zipout);(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
assert path.read_bytes()==before
(out/'README.md').write_text('侧栏专用：顶部新增消息/比赛/赛程/数据中心/医疗中心/青年/职员招募7入口隐藏，原主导航和19个侧栏入口保留。俱乐部页单独抵消外层88%缩放并补齐纵向flex分配，保持当前布局内容及数据绑定。主皮肤工程未改。\n\ninstall.ps1仅安装本次4对象修改；restore-this-fix.ps1撤销本次。full-sidebar目录可安装完整侧栏或回退顶部导航主版，均有基线哈希保护。aa压缩包仅5资源。未验证实际游戏高度，需用户测试。\n','utf8')
print(json.dumps(dict(output=str(out),full_sidebar=str(full),zip=str(zipout),changed_objects=len(expected),installed=False),ensure_ascii=False),flush=True)
