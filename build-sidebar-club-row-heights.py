from pathlib import Path
import ast, copy, datetime, hashlib, json, shutil, subprocess, sys, zipfile
root = Path(__file__).resolve().parent
sys.path.insert(0,str(root/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
source=ast.parse((root/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module([n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],[]),'writer','exec'))
TypeTreeHelper.write_value=write
def read(p): return json.loads(p.read_text('utf8'))
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def transaction(folder, target, original, edited, backup_dir):
    source=folder/'packages'/target.name
    backup=folder/backup_dir/target.name
    for path, payload in ((source,edited),(backup,original)):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(payload)
    return dict(target=str(target),source=str(source),backup=str(backup),before=digest(backup),after=digest(source))
state_path=root/'current-sidebar-version.json'
state=read(state_path)
previous=Path(state['installed_variant'])
prior=read(previous/'transaction.json')
assert state['current_game_mode']=='sidebar' and len(prior)==5
for row in prior:
    assert digest(Path(row['target']))==row['after'] and digest(Path(row['backup']))==row['before']
location=read(root/'current-game-location.json')
game=Path(location['bundle_root'])
target=game/'ui-tileslayouts_assets_all.bundle'
original=target.read_bytes()
env=UnityPy.load(original)
assets=env.assets[0]
stored={i:o.get_raw_data() for i,o in assets.objects.items()}
changes={}
sizes=[]
key='<Configurations>k__BackingField'
for name,previous_height in [('Large',9),('Standard',7),('Small',7)]:
    obj=next(o for o in assets.objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='ClubComposition-'+name)
    tree=obj.read_typetree()
    overview,actions=tree['m_gridComponents']
    assert overview['m_elementID']=='ClubScreenOverviewBlock' and actions['m_elementID']=='HumanActionsControlPanelBlock'
    loc=overview['m_location']
    assert loc['height']==overview['m_minSize']['y']==overview['m_maxSize']['y']==previous_height and loc['y']==1
    cfg,=overview['m_gridElementConfigs']
    pid=cfg['Description']['m_PathID']
    desc=changes.get(pid) or assets.objects[pid].read_typetree()
    configs=desc[key]
    assert cfg in configs
    # Keep both native sizes and the intermediate one so shorter windows have valid configurations.
    for h in (previous_height+1,previous_height+2):
        new=copy.deepcopy(cfg)
        new['Size']['y']=h
        if new not in configs: configs.append(new)
    loc['height']=overview['m_maxSize']['y']=previous_height+2
    overview['m_gridElementConfigs']=[new]
    tree['m_compositionVersion']+=1
    changes[obj.path_id]=tree
    changes[pid]=desc
    sizes.append([name,previous_height,loc['height']])
for pid,tree in changes.items(): assets.objects[pid].save_typetree(tree)
payload=env.file.save(packer='lz4')
check=UnityPy.load(payload).assets[0]
assert set(stored)==set(check.objects) and len(changes)==4
for pid,obj in check.objects.items():
    if pid in changes: assert obj.read_typetree()==changes[pid]
    else: assert obj.get_raw_data()==stored[pid]
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
out=root/('sidebar-club-row-heights-'+stamp)
full=out/'full-sidebar'
out.mkdir(); full.mkdir()
protected_paths=[Path(r['target']) for r in prior]+list(Path(location['skin_packages']).glob(target.name))
protected={str(p):digest(p) for p in protected_paths}
row=transaction(out,target,original,payload,'backup-game')
fullrows=[transaction(full,Path(r['target']),Path(r['backup']).read_bytes(),Path(r['target']).read_bytes(),'non-sidebar-backup') for r in prior]
fullrows.append(transaction(full,target,original,payload,'non-sidebar-backup'))
for folder,rows,backup_name in ((out,[row],'restore-this-fix'),(full,fullrows,'restore-non-sidebar')):
    save(folder/'transaction.json',rows)
    save(folder/'manifest.json',dict(installed=False,runtime_verified=False,sizes=sizes,changed_object_ids=list(changes),protected_sha256={p:h for p,h in protected.items() if p not in {x['target'] for x in rows}}))
    shutil.copy2(root/'install-independent-resource-patch.py',folder/'installer.py')
    for script,arg in [(('install' if folder==out else 'install-sidebar'),''),(backup_name,' --restore')]:
        (folder/(script+'.ps1')).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+arg+"\nexit $LASTEXITCODE\n",'utf-8-sig')
z=root/'exports'/('FM27-'+out.name+'-aa.zip')
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
    for r in fullrows:
        p=Path(r['source']);archive.write(p,('aa/StandaloneWindows64/' if p.suffix=='.bundle' else 'aa/')+p.name)
with zipfile.ZipFile(z) as archive: assert len(archive.namelist())==6 and archive.testzip() is None
shutil.copy2(state_path,out/'state-before.json')
assert target.read_bytes()==original
subprocess.run([sys.executable,str(out/'installer.py'),str(out)],check=True)
assert all(digest(Path(r['target']))==r['after'] for r in fullrows)
m=read(full/'manifest.json');m.update(installed=True,installed_verified=True);save(full/'manifest.json',m)
for k in list(state):
    if state[k]==state['latest_prepared_sidebar_export'] and k!='latest_prepared_sidebar_export': state[k]=str(z)
state.update(installed_variant=str(full),latest_prepared_sidebar_export=str(z),latest_aa_zip=str(z),latest_prepared_sidebar_patch=str(full),current_non_sidebar_backup=str(full/'non-sidebar-backup'),rollback_script=str(full/'restore-non-sidebar.ps1'),club_row_heights_patch=str(out),sidebar_club_original_height_issue_pending=True,runtime_verified=False)
save(state_path,state)
print(out)
