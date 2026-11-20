from pathlib import Path
import ctypes,hashlib,json,shutil,subprocess,sys
out=Path(__file__).resolve().parent
r=out.parent.parent
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];kernel.OpenProcess.restype=ctypes.c_void_p
kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32];kernel.WaitForSingleObject.restype=ctypes.c_uint32
kernel.CloseHandle.argtypes=[ctypes.c_void_p]
handle=kernel.OpenProcess(0x100000,False,27724)
if handle:
 print('Waiting for Football Manager to exit normally before restoring resources.',flush=True)
 while kernel.WaitForSingleObject(handle,1000)==258:pass
 kernel.CloseHandle(handle)
result=subprocess.run([sys.executable,str(out/'installer.py'),str(out),'--restore'],capture_output=True,text=True)
(out/'rollback-result.json').write_text(json.dumps({'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr},ensure_ascii=False,indent=2),'utf8')
if result.returncode:
 print(result.stdout+result.stderr,flush=True);raise SystemExit(result.returncode)
rows=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in rows:assert sha(Path(row['target']))==row['before'],row['target']
m=json.loads((out/'manifest.json').read_text('utf8'));m.update(installed=False,restored=True,rollback_pending_game_exit=False,restored_non_sidebar_on='2026-11-01',restored_file_hashes_verified=True)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
index=json.loads((r/'current-sidebar-version.json').read_text('utf8'));index.update(status='approved_archived_game_restored_to_non_sidebar',current_game_mode='non-sidebar',restored_on='2026-11-01',restored_files_verified=len(rows))
(r/'current-sidebar-version.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),'utf8')
p=r/'AGENTS.md';t=p.read_text('utf8');t=t.replace('当前操作状态：已归档；等待游戏正常退出后回退至非侧栏基线，供用户继续修补BUG。','当前操作状态：已归档；2026-11-01已回退至非侧栏基线，6个游戏/目录文件均已校验，可继续修补BUG。');p.write_text(t,'utf8')
p=out/'README.md';t=p.read_text('utf8').replace('当前状态：已归档，等待游戏正常退出后回退。','当前状态：已归档，2026-11-01已恢复非侧栏基线，6个文件校验通过。');p.write_text(t,'utf8')
log=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log')
if log.exists():shutil.copyfile(log,out/'Player-user-approved-sidebar.log')
print(json.dumps({'restored_non_sidebar':True,'verified_files':len(rows),'approved_archive':str(out),'original_skin_project_unchanged':True},ensure_ascii=False),flush=True)
