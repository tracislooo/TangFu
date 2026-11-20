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
ob,d,rr,sid,s,st=get('ClubScreen')
original=copy.deepcopy(d)
fm=rr[1030]['data']
assert fm['name']=='FM' and rr[1025]['data']['m_Parent']=={'rid':1021}
binding=fm['GridCompositionSets'][0]['m_gridCompositionSetBindings']
assert all(x['m_gridCompositionSetBindings']==binding for x in fm['GridCompositionSets'])
visibility=next(x['m_itemB'] for x in binding['m_gridElementVisiblityFunctions'] if x['m_itemA']=='HumanActionsControlPanelBlock')
assert visibility['m_target']['m_guid']
source=a.objects[1984155051551838433].read_typetree()
donor=refs(source)
old_id=rr[1025]['data']['m_Id']
rr[1025]['data']['m_FullTypeName']=rr[1016]['data']['m_FullTypeName']
rr[1030]['type']=copy.deepcopy(rr[1022]['type'])
rr[1030]['data']=copy.deepcopy(rr[1022]['data'])
rr[1030]['data'].update(name='FM',uxmlAssetId=old_id)
# Anchor to all four edges of the active branch's parent, independently of intrinsic tile sizes.
st.edit(rr[1025],[st.p(131102,st.en('absolute'))]+[st.p(k,st.px(0)) for k in [131104,131080,131089,131103]]+[st.p(131083,st.en('column'))])
def add_pair(src,idx,parent,name):
    node=copy.deepcopy(src[idx]); data=copy.deepcopy(src[node['data']['m_SerializedData']['rid']])
    rid=max(rr)+1
    id_used={x.get('data',{}).get('m_Id') for x in rr.values()}
    uid=1700000000+rid
    assert uid not in id_used
    node['rid']=rid;data['rid']=rid+1
    node['data'].update(m_Parent={'rid':parent},m_SerializedData={'rid':rid+1},m_Children=[],m_RuleIndex=-1,m_Id=uid,m_Classes=[])
    data['data'].update(name=name,uxmlAssetId=uid)
    for obj in (node,data):
        rr[obj['rid']]=obj;d['references']['RefIds'].append(obj)
    rr[parent]['data']['m_Children'].append({'rid':rid})
    return node,data['data']
gate,gd=add_pair(rr,1017,1025,'SidebarClubActionsVisible')
gd.update(InvertDirectBinding=0,VisibilityType=0)
gd['Binding'].update(m_kind=2,m_direct={'Path':{'m_path':''},'Nullable':0},m_visualFunction=visibility)
# Screen exposes team, club and ActionsSection at this point. Template binding names are identical.
catalog=(GAME.parent/'catalog.bin').read_bytes()
for alias,guid,parent in [('HumanActionsControlPanelBlock','d0c7f4cf2bbf02d40a088eae7a768a42',gate['rid']),('ClubScreenOverviewBlock','6b0f1bffd62c7c74baf0c0a7df280b9e',1025)]:
    node,sd=add_pair(donor,1231,parent,alias)
    node['data']['m_TemplateAlias']=alias;sd['templateId']=alias
    assert any(o.peek_name()==alias for k,v in a.objects[1].read_typetree()['m_Container'] if k==guid for o in [a.objects[v['asset']['m_PathID']]])
    assert guid.encode() in catalog
    d['m_Usings'].append(dict(alias=alias,path=guid,asset=dict(m_FileID=0,m_PathID=0)))
    is_body=parent==1025
    st.edit(node,[st.p(131087,st.px(0 if is_body else 68)),st.p(131096,st.px(0)),st.p(131084,st.num(1 if is_body else 0)),st.p(131085,st.num(1 if is_body else 0)),st.p(131105,st.pct(100))])
d['m_Usings'].sort(key=lambda u:u['alias'])
assert all(rr[k]==v for k,v in refs(original).items() if k not in [1025,1030])
validate_ui(d,s);expected[ob.path_id]=d;expected[sid]=s
names=index['top_custom_shortcuts_hidden'];audit.append(dict(template='ClubScreen',layout='FM: edge-pinned column; native actions, then growing overview',native_action_visibility=True))
for pid,value in expected.items():a.objects[pid].save_typetree(value)
payload=env.file.save(packer='lz4');check=UnityPy.load(payload).assets[0]
for pid,o in check.objects.items():
 if pid in expected:assert o.read_typetree()==expected[pid]
 else:assert o.get_raw_data()==raw[pid],('Unrelated object changed',pid)
out=R/('sidebar-club-fill-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();(out/'packages').mkdir();(out/'backup-game').mkdir();source=out/'packages'/W;backup=out/'backup-game'/W;source.write_bytes(payload);backup.write_bytes(before)
protected={str(p):sha(p.read_bytes()) for p in list(GAME.glob('*.bundle'))+[GAME.parent/'catalog.bin',GAME.parent/'catalog.hash']+list(SKIN.glob('*')) if p.is_file() and p!=path}
tx=[dict(target=str(path),source=str(source),backup=str(backup),before=sha(before),after=sha(payload))]
manifest=dict(installed=False,runtime_verified=False,sidebar_only=True,independent_main_skin_modified=False,checks=audit,changed_objects=[dict(path_id=pid,name=x.get('m_Name')) for pid,x in expected.items()],other_objects_byte_identical=True,protected_sha256=protected)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copy2(R/'install-independent-resource-patch.py',out/'installer.py');shutil.copy2(__file__,out/'build-source.py')
for name,flag in [('install',''),('restore-this-fix',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
# Composite independent sidebar package and full rollback preserve the main installation baseline.
full=out/'full-sidebar';full.mkdir();(full/'packages').mkdir();(full/'non-sidebar-backup').mkdir();ftx=[];aa=out/'aa';(aa/'StandaloneWindows64').mkdir(parents=True)
for row in json.loads((BASE/'transaction.json').read_text('utf8')):
 target=Path(row['target']);name=target.name;current=target.read_bytes();assert name==W or sha(current)==row['after'],('Concurrent resource change since sidebar install',name)
 data=payload if name==W else current;src=full/'packages'/name;bak=full/'non-sidebar-backup'/name;src.write_bytes(data);base=Path(row['backup']).read_bytes();assert sha(base)==row['before'];# Migrate unrelated post-sidebar edits into the non-sidebar rollback baseline.
 if sha(current)!=row['after']:
  olda=UnityPy.load(str(Path(row['source']))).assets[0];cure=UnityPy.load(current);cura=cure.assets[0];be=UnityPy.load(base);ba=be.assets[0]
  assert set(olda.objects)==set(cura.objects)
  for pid,obj in cura.objects.items():
   if obj.get_raw_data()==olda.objects[pid].get_raw_data():continue
   assert pid in ba.objects,('New object needs migration',pid)
   if obj.type.name!='AssetBundle':
    assert ba.objects[pid].get_raw_data()==olda.objects[pid].get_raw_data(),('Overlapping sidebar change',pid)
    ba.objects[pid].set_raw_data(obj.get_raw_data())
   else:
    old=olda.objects[pid].read_typetree();new=obj.read_typetree();back=ba.objects[pid].read_typetree()
    assert new['m_PreloadTable'][:len(old['m_PreloadTable'])]==old['m_PreloadTable']
    offset=len(back['m_PreloadTable'])-len(old['m_PreloadTable'])
    back['m_PreloadTable']+=copy.deepcopy(new['m_PreloadTable'][len(old['m_PreloadTable']):])
    assert len(new['m_Container'])==len(old['m_Container'])
    for oe,ne in zip(old['m_Container'],new['m_Container']):
     if oe==ne:continue
     matches=[i for i,x in enumerate(back['m_Container']) if x==oe];assert matches
     item=copy.deepcopy(ne);v=item[1]
     assert v['preloadIndex']>=len(old['m_PreloadTable']);v['preloadIndex']+=offset
     for i in matches:back['m_Container'][i]=item
    for k in old:
     if k not in ['m_PreloadTable','m_Container']:assert old[k]==new[k]
    ba.objects[pid].save_typetree(back)
  base=be.file.save(packer='lz4')
 bak.write_bytes(base)
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
print(json.dumps(dict(output=str(out),full_sidebar=str(full),zip=str(zipout),changed_objects=len(expected),installed=False),ensure_ascii=False),flush=True)

