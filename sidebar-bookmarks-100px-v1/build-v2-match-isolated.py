"""Restore V2 appearance while retaining native shared layers and match templates."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,struct,sys
V=Path(__file__).resolve().parent;R=V.parent
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 tree=ast.parse((R/name).read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),name,'exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
location=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(location['bundle_root'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle';S='settings_assets_all.bundle'
v3=json.loads((V/'content-v3/manifest.json').read_text('utf8'));tx3=json.loads((V/'content-v3/transaction.json').read_text('utf8'))
for row in tx3:assert sha(Path(row['target']).read_bytes())==row['after'],row['target']
for n in [D,S]:assert (G/n).read_bytes()==(V/'baseline'/n).read_bytes(),('Shared configuration must be native',n)
headerheights=[]
for o in UnityPy.load(str(G/D)).objects:
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree()
 if d.get('m_Name')!='AlwaysAppliedStyleSheet':continue
 for rule in d.get('m_Rules',[]):
  for p in rule['m_Properties']:
   if p.get('m_CustomName')=='--main-card-report-height':
    assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==3
    dim=d['dimensions'][p['m_Values'][0]['valueIndex']];assert dim['unit']==1
    headerheights.append(dim['value'])
assert len(headerheights)==1
height=headerheights[0]
before=(G/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};expected={}
def save(o,d):o.save_typetree(d);expected[o.path_id]=copy.deepcopy(d)
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def serial(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(name):return next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
for page in v3['management_pages']:
 obj=oo[page['path_id']];d=obj.read_typetree();rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
 sidebar=next(i for i in rr if serial(rr,i).get('name')=='TFManagementSidebar100')
 wrapper=next(i for i in rr if serial(rr,i).get('name')=='TFManagementContentLayout')
 st.edit(rr[sidebar],[st.p(131104,st.px(-height))])
 # Absolute positioning keeps the sidebar outside the minimum-size calculation.
 st.edit(rr[wrapper],[st.p(458768,st.en('visible'))])
 assert all(p['m_Id'] not in [131090,131093] for p in sheet['m_Rules'][rr[sidebar]['data']['m_RuleIndex']]['m_Properties'])
 validate_ui(d,sheet);save(obj,d);save(oo[sid],sheet)
title=named('OverviewTitleBar');td=title.read_typetree();rr=refs(td);sid=td['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
assert serial(rr,1004)['name']=='NavBarBindingSetter'
# Local header inset recreates the V2 two-column appearance without resizing MenuTitle.
st.edit(rr[1004],[st.p(131099,st.px(100))])
validate_ui(td,sheet);save(title,td);save(oo[sid],sheet)
raw=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(oo)
for i,o in saved.items():
 if i in expected:assert o.read_typetree()==expected[i],i
 else:assert sha(o.get_raw_data())==hashes[i],i
# Compare every native object against the actual pre-sidebar bundle, including match assets.
baseline=UnityPy.load(str(V/'baseline'/W));native={o.path_id:o for o in baseline.objects}
changed_native=[]
for i,o in native.items():
 if sha(saved[i].get_raw_data())!=sha(o.get_raw_data()):changed_native.append(i)
allowed={x['path_id'] for x in v3['management_pages']}|{native[x['path_id']].read_typetree()['inlineSheet']['m_PathID'] for x in v3['management_pages']}|{title.path_id,sid}|{o.path_id for o in native.values() if o.type.name=='AssetBundle'}
assert set(changed_native)<=allowed
for name in ['BookmarkButton','SecondaryNavigationBar','TeamSelectionTitleBar','FullScreenTeamSelection','MatchPreviewCard','MatchPreparationCard']:
 ids=[o.path_id for o in native.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name]
 for i in ids:
  assert sha(saved[i].get_raw_data())==sha(native[i].get_raw_data()),name
  d=native[i].read_typetree()
  if 'inlineSheet' in d:
   si=d['inlineSheet']['m_PathID'];assert sha(saved[si].get_raw_data())==sha(native[si].get_raw_data()),name+' stylesheet'
for p,h in v3['match_bundles_unchanged'].items():assert sha(Path(p).read_bytes())==h
out=V/'v2-match-isolated';out.mkdir(exist_ok=False);(out/'backup-game').mkdir();(out/'packages').mkdir();source=out/'packages'/W;source.write_bytes(raw);backup=out/'backup-game'/W;backup.write_bytes(before)
tx=[{'target':str(G/W),'source':str(source),'backup':str(backup),'before':sha(before),'after':sha(raw)}]
protected={p:sha(Path(p).read_bytes()) for p in json.loads((V/'manifest.json').read_text('utf8'))['protected_sha256'] if Path(p)!=G/W}
record={'version':'V2 appearance with native match templates and shared settings','installed':False,'runtime_verified':False,'width_px':100,'native_header_height_logical_px':height,'sidebar_top_relative_to_management_body':-height,'public_settings_bundle_identical_to_pre_sidebar':True,'default_styles_bundle_identical_to_pre_sidebar':True,'resolution_configuration_changes':False,'native_match_template_checks_passed':True,'native_bookmark_templates_unchanged':True,'management_pages':len(v3['management_pages']),'protected_sha256':protected,'known_limitations':['Runtime rendering, clipping, pointer events above the content boundary and resolution choices still require an in-game test.']}
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(R/'install-independent-resource-patch.py',out/'installer.py')
for name,flag in [('install',''),('restore-v3',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
full=out/'full-rollback';full.mkdir();fulltx=json.loads((V/'content-v3/full-rollback/transaction.json').read_text('utf8'))
for row in fulltx:
 if Path(row['target']).name==W:row.update(source=str(source),after=sha(raw))
targets={Path(x['target']) for x in fulltx};fullprotected={p:h for p,h in protected.items() if Path(p) not in targets}
(full/'transaction.json').write_text(json.dumps(fulltx,ensure_ascii=False,indent=2),'utf8');(full/'manifest.json').write_text(json.dumps({'installed':False,'protected_sha256':fullprotected},ensure_ascii=False,indent=2),'utf8');shutil.copyfile(out/'installer.py',full/'installer.py')
(out/'restore-original.ps1').write_text("$ErrorActionPreference = 'Stop'\n$rollbackDir = Join-Path $PSScriptRoot 'full-rollback'\n& '"+sys.executable+"' (Join-Path $rollbackDir 'installer.py') $rollbackDir --restore\nif ($LASTEXITCODE -ne 0) { throw 'Rollback failed.' }\n",'utf-8-sig')
(out/'README.md').write_text('V2外观修订：100px竖排书签从整屏左上方开始，普通管理页与顶部两栏向右留位。公共settings/default styles保持试装前文件；比赛模板和原生书签模板保持原始内容。未修改原皮肤工程。\n\nrestore-v3.ps1恢复安装前V3；restore-original.ps1完全撤销侧栏。退出游戏后运行。\n\n离线验证通过，尚需游戏内验证显示、点击及分辨率选项。\n','utf8')
print(json.dumps({k:v for k,v in record.items() if k not in ['protected_sha256','known_limitations']},ensure_ascii=False))
