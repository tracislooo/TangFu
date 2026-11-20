import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');N='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';B=-4194025542157271532;S=8045407476604796436;OUT=R/'报告右侧三行图标排版-V40'
sha=lambda b:hashlib.sha256(b).hexdigest();source=(AA/'StandaloneWindows64'/N).read_bytes();assert sha(source)=='3c9e616f58f5471a6378d60077b1aa6e9cff0d970fe71170c67718022ad95ad4'
oldwrite=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':oldwrite(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return oldwrite(v,n,w,c)
TypeTreeHelper.write_value=write
e=UnityPy.load(str(AA/'StandaloneWindows64'/N));objects={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in objects.items()};doc=objects[B].read_typetree();sheet=objects[S].read_typetree();old_doc=copy.deepcopy(doc);old_sheet=copy.deepcopy(sheet);refs={r['rid']:r for r in doc['references']['RefIds']};oldrefs=copy.deepcopy(refs)
# Only styles and visual hierarchy change. Binding data and functions stay identical.
def val(pool,typ,value):
 if value not in sheet[pool]:sheet[pool].append(value)
 return {'m_ValueType':typ,'valueIndex':sheet[pool].index(value)}
def px(v):return val('dimensions',3,{'unit':1,'value':float(v)})
def pct(v):return val('dimensions',3,{'unit':2,'value':float(v)})
def deg(v):return val('dimensions',3,{'unit':5,'value':float(v)})
def en(v):return val('strings',7,v)
def num(v):return val('floats',2,float(v))
def col(c):return val('colors',4,dict(zip(['r','g','b','a'],c)))
def p(k,*vs):return {'m_Id':k,'m_CustomName':'','m_Line':-1,'m_Values':list(vs)}
def rule(ps):
 i=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':ps,'line':-1});return i
zero=[p(262150,px(0)),p(262151,px(0))]
def replace_rule(i,ps):sheet['m_Rules'][i]['m_Properties']=ps
# Root stays inside the existing right-hand third and original header height.
replace_rule(15,zero+[p(131084,num(1)),p(131085,num(1)),p(131082,px(0)),p(131097,px(0)),p(131074,en('stretch')),p(131083,en('row')),p(131073,en('stretch')),p(131088,en('flex-start')),p(131099,px(6)),p(131100,px(8)),p(131101,px(2)),p(131098,px(2))]);refs[1008]['data']['m_Classes']=[]
# Badge group occupies all room beside a fixed-width stack of original controls.
gridrule=rule(zero+[p(131084,num(1)),p(131085,num(1)),p(131082,px(0)),p(131097,px(248)),p(131087,pct(100)),p(131083,en('column')),p(131073,en('stretch')),p(131088,en('space-between')),p(131092,px(8))])
rowrule=rule(zero+[p(131105,pct(100)),p(131087,px(58)),p(131085,num(0)),p(131083,en('row')),p(131073,en('center')),p(131088,en('space-around'))])
cellrule=rule(zero+[p(131105,px(58)),p(131087,px(58)),p(131084,num(0)),p(131085,num(0))])
# Reuse the old seven-badge group as the full three-row group.
refs[1214]['data'].update(m_Parent={'rid':1008},m_RuleIndex=gridrule,m_Children=[]);refs[1215]['data']['name']='ReportBadgeGrid4_3_4'
# Reuse the old scout/contract wrapper, now a vertical stack: Actions / scout+ability / contract.
stackrule=rule(zero+[p(131105,px(160)),p(131097,px(160)),p(131084,num(0)),p(131085,num(0)),p(131087,pct(100)),p(131083,en('column')),p(131073,en('stretch')),p(131088,en('space-between'))])
refs[1212]['data'].update(m_RuleIndex=stackrule,m_Children=[{'rid':1013},{'rid':1022},{'rid':1020}]);refs[1213]['data']['name']='ReportOriginalManagementModulesColumn'
refs[1008]['data']['m_Children']=[{'rid':1214},{'rid':1212}]+[{'rid':i} for i in [1015,1017,1019,1021]]
refs[1013]['data'].update(m_Parent={'rid':1212},m_Children=[{'rid':1028}]);refs[1022]['data']['m_Parent']={'rid':1212};refs[1020]['data']['m_Parent']={'rid':1212}
# The modules' descendants and bindings are untouched. Override only their outer flex allocation.
actionrule=rule(zero+[p(131105,pct(100)),p(131087,px(36)),p(131096,px(36)),p(131084,num(0)),p(131085,num(0)),p(131083,en('row')),p(131073,en('center')),p(131088,en('flex-end'))]);refs[1013]['data']['m_RuleIndex']=actionrule
module_rules={}
for i in [1022,1020]:
 ri=refs[i]['data']['m_RuleIndex'];ps=copy.deepcopy(sheet['m_Rules'][ri]['m_Properties']);remove={131105,131082,131084,131085,131074,131096,131087};ps=[q for q in ps if q['m_Id'] not in remove]+[p(131105,pct(100)),p(131084,num(0)),p(131085,num(0)),p(131074,en('stretch'))];module_rules[i]=rule(ps);refs[i]['data']['m_RuleIndex']=module_rules[i]
new=[];rid=max(refs)+1;eid=1904000000
node_template=oldrefs[1174];sd_template=oldrefs[1175]
def pair(parent,name,ri,nt=None,st=None):
 global rid,eid
 n,s=copy.deepcopy(nt or node_template),copy.deepcopy(st or sd_template);n['rid'],s['rid']=rid,rid+1;rid+=2;n['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=ri,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SkipClone=0);s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);eid+=1;refs[n['rid']]=n;refs[s['rid']]=s;new.extend([n,s]);refs[parent]['data']['m_Children'].append({'rid':n['rid']});return n,s
r1,_=pair(1214,'ReportAttributeBadgesFirstRow',rowrule);r2,_=pair(1214,'ReportAttributeBadgesSecondRow',rowrule)
# Preserve each badge sum, tier-switch graph and title/value labels.
codes=['ATT','DEF','TCN','SPT','SPD','KIK','FED']
for i,code in enumerate(codes):
 sd=next(r for r in refs.values() if r.get('data',{}).get('name')=='Report'+code+'Badge');n=next(r for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid']);parent=r1 if i<4 else r2;n['data'].update(m_Parent={'rid':parent['rid']},m_RuleIndex=cellrule);parent['data']['m_Children'].append({'rid':n['rid']})
# Existing ComponentElement continues to own the same seasonStats/competition remapper and four numbers.
refs[1184]['data'].update(m_Parent={'rid':1214},m_RuleIndex=rowrule);refs[1214]['data']['m_Children'].append({'rid':1184});refs[1185]['data']['name']='ReportLeagueStatsDiamondRow'
statcellrule=rule(zero+[p(131084,num(1)),p(131085,num(1)),p(131082,px(0)),p(131097,px(0)),p(131087,px(58)),p(131073,en('center')),p(131083,en('column'))])
# Four simple diamond frames rendered with UI Toolkit borders; no pictogram behind a number.
shapeholder=rule(zero+[p(131105,px(58)),p(131087,px(58)),p(131085,num(0))])
colors=[(1,.4375,.4375,1),(.25,.75,1,1),(1,.8125,.25,1),(.875,.375,1,1)]
stat_spec=[(1188,1190,1192,'Expected Goal/\n90 mins'),(1194,1196,1198,'ExpectedAssists/\n90 mins'),(1200,1202,1204,'Passes Completed/\n90 mins'),(1206,1208,1210,'tackles won\nper game')]
# Banner has two slanted ends, built from squares rotated 45 degrees behind a central panel.
for (cell,title,value,label),color in zip(stat_spec,colors):
 refs[cell]['data']['m_RuleIndex']=statcellrule;refs[cell]['data']['m_Children']=[]
 holder,_=pair(cell,'ReportStatDiamondFrame'+str(cell),shapeholder)
 diamondrule=rule(zero+[p(131102,en('absolute')),p(131089,px(12)),p(131104,px(5)),p(131105,px(34)),p(131087,px(34)),p(327680,deg(45)),p(458752,col((.03125,.0625,.09375,.9375))),p(262148,px(1.5)),p(262146,col(color))])
 pair(holder['rid'],'ReportStatDiamondOutline'+str(cell),diamondrule)
 # Original numeric text and its full native decimal-formatting binding remain byte-for-byte equal.
 valrule=rule(zero+[p(131102,en('absolute')),p(131089,px(0)),p(131104,px(7)),p(131105,px(58)),p(131087,px(30)),p(65537,px(15)),p(65546,en('middle-center')),p(65552,en('nowrap')),p(65536,col(color))])
 refs[value]['data'].update(m_Parent={'rid':holder['rid']},m_RuleIndex=valrule,m_Classes=[]);refs[holder['rid']]['data']['m_Children'].append({'rid':value})
 # Banner is wider than the diamond to fit full English titles.
 bannerbg=rule(zero+[p(131102,en('absolute')),p(131089,px(2)),p(131104,px(38)),p(131105,pct(94)),p(131087,px(20)),p(458752,col((.03125,.046875,.0703125,1))),p(262148,px(1)),p(262146,col((.25,.3125,.40625,1)))])
 panel,_=pair(cell,'ReportStatTitleBanner'+str(cell),bannerbg)
 titlerule=rule(zero+[p(131105,pct(100)),p(131087,pct(100)),p(131097,px(0)),p(65537,px(7)),p(65546,en('middle-center')),p(65552,en('normal')),p(65536,col((1,1,1,1)))])
 refs[title]['data'].update(m_Parent={'rid':panel['rid']},m_RuleIndex=titlerule,m_Classes=[]);refs[panel['rid']]['data']['m_Children'].append({'rid':title})
 tsd=refs[refs[title]['data']['m_SerializedData']['rid']]['data'];tsd.update(text=label,text_UxmlAttributeFlags=1,DebugDisplay=label);tsd['TextBinding']['m_kind']=0
 tsd['TextBinding']['m_visualFunction']={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
doc['references']['RefIds'].extend(new)
# Verify unchanged existing bindings and original control descendants.
for i in [1193,1199,1205,1211,1187,1003,1005,1053]:assert refs[i]==oldrefs[i],i
protected=set()
def protect(i):
 protected.add(i);a=oldrefs[i]['data'];sid=a.get('m_SerializedData',{}).get('rid')
 if sid in oldrefs:protected.add(sid)
 for c in a.get('m_Children',[]):protect(c['rid'])
for i in [1028,1040,1041,1037]:protect(i)
for i in protected:assert refs[i]==oldrefs[i],i
# Left/portrait/reference subtrees cannot change; only known moved nodes or title SDs are allowed.
allowed={1008,1212,1213,1214,1215,1013,1022,1020,1184,1185}|{x for row in stat_spec for x in row[:3]}|{refs[row[1]]['data']['m_SerializedData']['rid'] for row in stat_spec}
allowed|={next(r['rid'] for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==next(s['rid'] for s in refs.values() if s.get('data',{}).get('name')=='Report'+code+'Badge')) for code in codes}
for i,r in oldrefs.items():
 if i not in allowed:assert refs[i]==r,i
seen=set()
def visit(i):
 assert i not in seen;seen.add(i)
 for c in refs[i].get('data',{}).get('m_Children',[]):assert refs[c['rid']]['data']['m_Parent']['rid']==i;visit(c['rid'])
visit(doc['m_VisualTree']['rid']);assert len(r1['data']['m_Children'])==4 and len(r2['data']['m_Children'])==3;assert len(refs[1184]['data']['m_Children'])==5
objects[B].save_typetree(doc);objects[S].save_typetree(sheet);OUT.mkdir(exist_ok=True);dest=OUT/N;dest.write_bytes(e.file.save(packer='lz4'))
saved={o.path_id:o for o in UnityPy.load(str(dest)).objects};assert saved[B].read_typetree()==doc;assert saved[S].read_typetree()==sheet
for i,h in hashes.items():
 if i not in [B,S]:assert sha(saved[i].get_raw_data())==h,i
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(source)
m={'version':40,'source_sha256':sha(source),'sha256':sha(dest.read_bytes()),'rows':[4,3,4],'badge_size_px':58,'management_column_px':160,'unchanged_objects_verified':len(hashes)-2,'catalog_unchanged':sha((AA/'catalog.bin').read_bytes()),'native_stat_values_unchanged':True,'native_management_descendants_unchanged':len(protected),'game_runtime_verified':False,'installed':False};(OUT/'修改记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'report-player-banner-max.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8');(OUT/'inlineStyle.json').write_text(json.dumps(sheet,ensure_ascii=False,indent=2),encoding='utf8')
for rollback in [False,True]:
 src='回退/'+N if rollback else N;expected=m['sha256'] if rollback else m['source_sha256'];script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{AA/'StandaloneWindows64'/N}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
Write-Host 'Complete.'
''';(OUT/('回退.ps1' if rollback else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V40：头像右侧三行图标 4+3+4。\n第一行进攻防守技术精神；第二行身体定位球合作；第三行四项原生联赛数据，数字位于菱形内，英文标题位于下方横幅。\n最右侧纵向放 Actions、原有球探/能力潜力模块、原有合同模块；各模块内部样式和内容保留。\n整体高度沿用185px，徽章58px，右列160px。\n只替换global bundle，catalog、visualfunctions、backgrounds不变。\n退出游戏后运行安装.ps1；回退.ps1恢复V39。游戏内排版需实测确认。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in OUT.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(OUT))
print(json.dumps(m))
