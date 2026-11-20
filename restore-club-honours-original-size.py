"""Restore only the honours card layout, preserving the AI transfer layout."""
import ast,copy,datetime,hashlib,json,sys
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
for file,names in [('add-card-six-ratings.py',{'write'}),('build-club-stadium-overlay-local.py',{'stage'})]:
 for n in ast.parse((R/file).read_text('utf8')).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:exec(compile(ast.Module([n],[]),file,'exec'),globals())
TypeTreeHelper.write_value=write
previous=R/'club-trophies-three-columns-20261118-111607'
out=R/('club-honours-original-size-'+datetime.datetime.now(ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S'))
out.mkdir();tx=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for tag,entry in zip(['game','skin'],json.loads((previous/'transaction.json').read_text('utf8'))):
 path=Path(entry['target']);before=path.read_bytes();env=UnityPy.load(before);af=env.assets[0]
 backup=UnityPy.load(str(entry['backup'])).assets[0].objects
 installed=UnityPy.load(str(entry['source'])).assets[0].objects
 pid=-991114000001000;sid=backup[pid].read_typetree()['inlineSheet']['m_PathID']
 baseline={i:sha(o.get_raw_data()) for i,o in af.objects.items()}
 for i in [pid,sid]:
  assert af.objects[i].get_raw_data()==installed[i].get_raw_data(),('Honours modified after patch',tag,i)
  af.objects[i].save_typetree(backup[i].read_typetree())
 after=env.file.save(packer='lz4');check=UnityPy.load(after).assets[0].objects
 assert set(check)==set(baseline)
 for i,o in check.items():
  if i in [pid,sid]:assert o.get_raw_data()==backup[i].get_raw_data()
  else:assert sha(o.get_raw_data())==baseline[i]
 stage(tag,path,before,after)
for name,value in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},restored='original two-column trophy size',ai_transfer_layout_preserved=True))]:
 (out/(name+'.json')).write_text(json.dumps(value,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out,flush=True)
