from pathlib import Path
import sys,json,copy,ast,hashlib,datetime,subprocess,os
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'writer','exec'));TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));folders=[Path(loc['bundle_root']),Path(loc['skin_packages'])];W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
assert 'Football Manager 27' in str(folders[0]) and 'Project Taco' not in str(folders[0])
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('staff-portrait-preserve-aspect-'+stamp);out.mkdir()
before={f/W:(f/W).read_bytes() for f in folders};outputs={};audits=[];protected={}
for folder in folders:
 for n in ['ui-backgrounds_assets_common.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle']:
  p=folder/n;protected[p]=sha(p.read_bytes())
 for p in [folder.parent/'catalog.bin',folder.parent/'catalog.hash'] if folder==folders[0] else [folder/'catalog.bin',folder/'catalog.hash']:
  if p.exists():protected[p]=sha(p.read_bytes())
for tag,folder in zip(['game','skin'],folders):
 p=folder/W;e=UnityPy.load(before[p]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 o=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='NonPlayerReportHeader');d=o.read_typetree();old=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']};hits=[]
 for r in rr.values():
  a=r.get('data',{})
  if a.get('m_FullTypeName')!='SI.Bindable.SIImage':continue
  s=rr[a['m_SerializedData']['rid']]['data']
  if s.get('name')!='StaffPortraitImage':continue
  assert s['ScaleMode']==0 and s['scaleMode']==0
  s.update(ScaleMode=2,scaleMode=2,ScaleMode_UxmlAttributeFlags=1,scaleMode_UxmlAttributeFlags=1);hits.append(a['m_SerializedData']['rid'])
 assert len(hits)==1,hits
 oldrr={r['rid']:r for r in old['references']['RefIds']}
 for rid,r in rr.items():
  z=copy.deepcopy(r)
  if rid in hits:
   for k in ['ScaleMode','scaleMode','ScaleMode_UxmlAttributeFlags','scaleMode_UxmlAttributeFlags']:z['data'][k]=oldrr[rid]['data'][k]
  assert z==oldrr[rid],rid
 o.save_typetree(d);b=e.file.save(packer='lz4');check={x.path_id:x for x in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,x in check.items():
  if i==o.path_id:assert x.read_typetree()==d
  else:assert sha(x.get_raw_data())==hashes[i],i
 backup=out/('backup-'+tag);backup.mkdir();(backup/W).write_bytes(before[p]);dest=out/('output-'+tag);dest.mkdir();(dest/W).write_bytes(b);outputs[p]=b
 audits.append({'target':str(p),'header_path_id':str(o.path_id),'changed_serialized_records':hits,'changed_fields':['ScaleMode','scaleMode'],'old':0,'new':2,'other_objects_byte_identical':len(oo)-1,'layout_and_bindings_unchanged':True})
report={'installed':False,'runtime_verified':False,'fix':'StaffPortraitImage ScaleMode StretchToFill(0) to ScaleToFit(2), both base Image and SIImage properties','audits':audits,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in outputs.items()}}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
# Restore only when the installed output still matches; never overwrite later changes.
lines=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first.' }"]
for tag,p in zip(['game','skin'],outputs):lines.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(outputs[p])+"') { throw 'Resource changed after this patch; migrate rollback first.' }")
for tag,p in zip(['game','skin'],outputs):lines.append("Copy-Item -LiteralPath '"+str(out/('backup-'+tag)/W)+"' -Destination '"+str(p)+"' -Force")
(out/'restore.ps1').write_text('\n'.join(lines),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
 print(json.dumps({'prepared':True,'installed':False,'game_running':True,'output':str(out)}));sys.exit(0)
try:
 for p,b in outputs.items():
  temp=p.with_suffix('.staff-aspect.tmp');temp.write_bytes(b);os.replace(temp,p);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
p=R/'FM27-职员Overview-最新修改要求与更新恢复指南.md';p.write_text(p.read_text('utf8')+'\n\n## 2026-11-10 职员头像压缩修复（最新）\n\n当前实际职员页已使用内嵌 StaffPortraitImage 图片控件，不能只检查未使用的共享 PersonPicture 模板。发现其基类 Image.scaleMode 和 SIImage.ScaleMode 均显式为 0（StretchToFill），导致226×180头像框内照片变形；本次仅把这两个字段改为2（ScaleToFit），属性标志保持启用。保持226×180框、原生照片资源绑定、属性数值和其他布局。游戏与独立皮肤分别基于最新包修改，其他对象字节不变。游戏根目录使用 current-game-location.json 的 Football Manager 27，旧 Project Taco 不得作为安装目标。更新后必须检查实际使用的图片控件两个ScaleMode字段，不能只凭USS中scale-to-fit判断。记录 '+out.name+'/manifest.json，回退restore.ps1有哈希保护。文件校验与安装校验通过，未启动游戏或操作桌面，实际显示待用户确认。\n','utf8')
print(json.dumps({'installed':True,'output':str(out),'targets':len(outputs),'only_changed_fields':['Image.scaleMode','SIImage.ScaleMode'],'runtime_verified':False}))
