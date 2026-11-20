import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');N='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';B=-4194025542157271532;S=8045407476604796436;OUT=R/'右侧图标紧凑排版-V41'
sha=lambda b:hashlib.sha256(b).hexdigest();source=(AA/'StandaloneWindows64'/N).read_bytes();assert sha(source)=='4d2350995192123a1c70064f90e300371c024bbfda11a4ab04d2d3dd061c5b24'
e=UnityPy.load(str(AA/'StandaloneWindows64'/N));obs={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};doc=obs[B].read_typetree();sheet=obs[S].read_typetree();old=copy.deepcopy(sheet);refs={r['rid']:r for r in doc['references']['RefIds']}
oldwrite=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':oldwrite(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return oldwrite(v,n,w,c)
TypeTreeHelper.write_value=write
def val(pool,typ,v):
 if v not in sheet[pool]:sheet[pool].append(v)
 return {'m_ValueType':typ,'valueIndex':sheet[pool].index(v)}
def px(v):return val('dimensions',3,{'unit':1,'value':float(v)})
def pct(v):return val('dimensions',3,{'unit':2,'value':float(v)})
def en(v):return val('strings',7,v)
def num(v):return val('floats',2,float(v))
def node(name):
 sd=next(r for r in refs.values() if r.get('data',{}).get('name')==name)
 return next(r for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid'])
changes={}
def patch_rule(i,values,remove=()):
 ps=sheet['m_Rules'][i]['m_Properties'];keys=set(values)|set(remove);sheet['m_Rules'][i]['m_Properties']=[p for p in ps if p['m_Id'] not in keys]+[{'m_Id':k,'m_CustomName':'','m_Line':-1,'m_Values':[v]} for k,v in values.items()];changes.setdefault(i,set()).update(keys)
def patch(n,values,remove=()):patch_rule(node(n)['data']['m_RuleIndex'],values,remove)
patch_rule(15,{131073:en('center')})
patch('ReportBadgeGrid4_3_4',{131084:num(0),131085:num(1),131082:px(256),131105:px(256),131097:px(256),131087:px(156),131088:en('flex-start'),131092:px(6)})
patch('ReportAttributeBadgesFirstRow',{131087:px(52),131088:en('center')})
patch('ReportATTBadge',{131105:px(50),131087:px(50),131091:px(2),131092:px(2)})
patch('ATTTitle',{65537:px(8),131105:pct(60)})
for code in ['ATT','DEF','TCN','SPT','SPD','KIK','FED']:patch(code+'Total',{65537:px(10),131105:pct(40)})
patch('ReportOriginalManagementModulesColumn',{131088:en('flex-start')},remove=[131087])
for i in [1013,1022]:patch_rule(refs[i]['data']['m_RuleIndex'],{131090:px(3)})
for cell,value,title in [(1188,1192,1190),(1194,1198,1196),(1200,1204,1202),(1206,1210,1208)]:
 patch_rule(refs[cell]['data']['m_RuleIndex'],{131087:px(52)})
 patch('ReportStatDiamondFrame'+str(cell),{131105:px(50),131087:px(50)})
 patch('ReportStatDiamondOutline'+str(cell),{131089:px(10),131104:px(4),131105:px(30),131087:px(30)})
 patch_rule(refs[value]['data']['m_RuleIndex'],{131105:px(50),131104:px(5),131087:px(28),65537:px(14)})
 patch('ReportStatTitleBanner'+str(cell),{131104:px(31),131087:px(20)})
 patch_rule(refs[title]['data']['m_RuleIndex'],{65537:px(6.5)})
obs[S].save_typetree(sheet);OUT.mkdir(exist_ok=True);(OUT/N).write_bytes(e.file.save(packer='lz4'));saved={o.path_id:o for o in UnityPy.load(str(OUT/N)).objects};assert saved[S].read_typetree()==sheet
for i,h in hashes.items():
 if i!=S:assert sha(saved[i].get_raw_data())==h,i
assert saved[B].read_typetree()==doc
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(source)
m={'version':41,'source_sha256':sha(source),'sha256':sha((OUT/N).read_bytes()),'grid_width_px':256,'grid_height_px':156,'badge_size_px':50,'row_height_px':52,'management_width_px':160,'only_inline_style_changed':True,'unchanged_assets_verified':len(hashes)-1,'changed_rule_ids':sorted(changes),'installed':False,'game_runtime_verified':False};(OUT/'修改记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for rollback in [False,True]:
 src='回退/'+N if rollback else N;expected=m['sha256'] if rollback else m['source_sha256'];script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{AA/'StandaloneWindows64'/N}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
Write-Host 'Complete.'
''';(OUT/('回退.ps1' if rollback else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V41：图标区域收紧至256×156px，三行每行52px，属性徽章58→50px。取消铺满可用宽高及space-between布局。右侧原模块靠拢纵向排列，内部内容保持不变。只修改inlineStyle，不改变数据绑定、函数和图标图片。回退.ps1恢复V40。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in OUT.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(OUT))
print(json.dumps(m))
