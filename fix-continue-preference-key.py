from pathlib import Path
import ast,copy,datetime,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in h.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'helper','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text());GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);BN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('continue-preference-key-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
protected={str(p):sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name!=BN}
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[str(f/n)]=sha((f/n).read_bytes())
native=json.loads((R/'continue-diagnosis/native.json').read_text());nr={r['rid']:r for r in native['references']['RefIds']}
expected=nr[1146]['data']['ValueVariables'];assert expected[0]['m_scopeValue']['m_serializedData']=='String|continue_button_cycle_messages|'
tx=[];audits=[]
for tag,f in [('game',GAME),('skin',SKIN)]:
 before=(f/BN).read_bytes();e=UnityPy.load(before);obs={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
 ob=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='ProcessingPreferencesBlock');d=ob.read_typetree();old=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']}
 assert rr[1146]['data']['ValueVariables'][0]['m_scopeValue']['m_serializedData']=='String|continue_button_legacy_mode|'
 rr[1146]['data']['ValueVariables']=copy.deepcopy(expected);d['m_ContentHash']+=1
 compare=copy.deepcopy(d);compare['m_ContentHash']=old['m_ContentHash'];next(r for r in compare['references']['RefIds'] if r['rid']==1146)['data']['ValueVariables']=next(r for r in old['references']['RefIds'] if r['rid']==1146)['data']['ValueVariables'];assert compare==old
 ob.save_typetree(d);data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects}
 for i,o in check.items():
  if i==ob.path_id:assert o.read_typetree()==d
  else:assert sha(o.get_raw_data())==hashes[i],i
 dest=OUT/tag/BN;backup=OUT/('backup-'+tag)/BN;dest.parent.mkdir();backup.parent.mkdir();dest.write_bytes(data);backup.write_bytes(before)
 tx.append({'target':str(f/BN),'source':str(dest),'backup':str(backup),'before':sha(before),'after':sha(data)})
 audits.append({'variant':tag,'object':str(ob.path_id),'changed_value_only':True,'all_other_objects_byte_identical':True})
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'cause':'Old migrated preference key continue_button_legacy_mode; updated native uses continue_button_cycle_messages','native_source':'main-1-14-rebuild-20261110-100537/backup-game','audits':audits,'protected_sha256':protected},indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
p=subprocess.run([sys.executable,str(OUT/'installer.py'),str(OUT)],capture_output=True,text=True);print(p.stdout,p.stderr);assert p.returncode==0
(R/'current-continue-preference-fix.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'installed':True,'runtime_verified':False},indent=2),'utf8')
with (R/'AGENTS.md').open('a',encoding='utf8') as f:f.write('\n- 2026-11-10：偏好设置游戏模式的“继续按钮”下拉空白无法展开，发现ProcessingPreferencesBlock的1146 BindingVariables仍使用旧设置键continue_button_legacy_mode；当前更新原生备份同节点使用continue_button_cycle_messages。仅将游戏与独立皮肤该节点的ValueVariables对齐新版，其他字段/样式/对象逐字节保持，未重置用户偏好。补丁'+OUT.name+'已安装两份Global包并校验，catalog/侧栏等其他资源不变；索引current-continue-preference-fix.json，回退restore.ps1带哈希保护。未启动游戏或控制桌面，实际展开待用户验证。\n')
print(OUT)
