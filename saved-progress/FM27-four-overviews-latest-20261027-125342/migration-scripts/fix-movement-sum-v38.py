import copy,hashlib,json,struct,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');N='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';P=AA/'StandaloneWindows64'/N
OUT=R/'速度爆发灵活数值修正-V38';OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
before=P.read_bytes();assert sha(before)=='13e650735b42e6e1c6f35457c347f73677f6a61cbbc263cc537b5be46f5c1543'
oldwrite=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':oldwrite(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return oldwrite(v,n,w,c)
TypeTreeHelper.write_value=write
env=UnityPy.load(str(P));obs={o.path_id:o for o in env.objects};pid=-4194025542157271532
hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
t=obs[pid].read_typetree();orig=copy.deepcopy(t)
text=next(r for r in t['references']['RefIds'] if r.get('data',{}).get('name')=='ReportMovementSumValue')
paths=['person.attributepace.AttributeMinValue','person.attributeacceleration.AttributeMinValue','person.attributeagility.AttributeMinValue']
def string(s):
 b=s.encode();assert len(b)<128;return bytes([len(b)])+b
b=bytearray([3])
for p in paths:
 data=string('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]')+b'\x01'+string(p);b.extend(struct.pack('<i',len(data)));b.extend(data)
text['data']['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(b)
changed=[(a['rid']) for a,z in zip(orig['references']['RefIds'],t['references']['RefIds']) if a!=z];assert changed==[text['rid']]
obs[pid].save_typetree(t)
dest=OUT/'aa/StandaloneWindows64';dest.mkdir(parents=True,exist_ok=True);(dest/N).write_bytes(env.file.save(packer='lz4'))
check={o.path_id:o for o in UnityPy.load(str(dest/N)).objects};assert check[pid].read_typetree()==t
for i,h in hashes.items():
 if i!=pid:assert sha(check[i].get_raw_data())==h,i
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(before)
newsha=sha((dest/N).read_bytes())
for rollback in [False,True]:
 expected=newsha if rollback else sha(before);src='回退/'+N if rollback else 'aa/StandaloneWindows64/'+N
 script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{P}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
Write-Host 'Complete.'
'''
 (OUT/('回退.ps1' if rollback else '安装.ps1')).write_text(script,encoding='utf-8-sig')
manifest={'version':38,'paths':paths,'source_sha256':sha(before),'sha256':newsha,'changed_asset':pid,'changed_reference':text['rid'],'unchanged_objects_verified':len(hashes)-1,'catalog_sha256':sha((AA/'catalog.bin').read_bytes()),'runtime_verified':False,'installed':False}
(OUT/'修改记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'说明.txt').write_text('V38：改用原生 PlayerTableFactory 排序使用的 AttributeMinValue 数值字段求和。\n仅改变三个输入路径，沿用 V37 求和函数和 catalog，布局不变。\n已知属性 12、13、13 时应为 38。若属性只显示范围，求和取范围下限；未知属性未在游戏中验证。\n退出游戏后运行安装.ps1。回退.ps1 恢复 V37。\n本补丁要求已安装 V37。游戏运行结果仍需验证。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(OUT))
print(json.dumps(manifest))
