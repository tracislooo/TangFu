"""Undo the equal radar redesign, restore native season table, keep row bars."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for filename,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'})]:
 t=ast.parse((R/filename).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),filename,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'));prevout=Path(previous['manifest']).parent;m=json.loads(Path(previous['manifest']).read_text('utf8'));prior=json.loads((prevout/'transaction.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001020
OUT=R/('test-restore-season-table-hidden-bars-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
for tag,root in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 before=(root/W).read_bytes();p=next(r for r in prior if Path(r['target'])==root/W);assert sha(before)==p['after'],'Installed page changed; refuse historical replacement'
 env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 priorobs={o.path_id:o for o in UnityPy.load(p['backup']).objects}
 doc=priorobs[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=priorobs[sid].read_typetree();original=copy.deepcopy(doc)
 originalobs={o.path_id:o for o in UnityPy.load(str(R/'left-test-season-radar-20261114-005859'/('backup-'+tag)/W)).objects}
 nativepage=originalobs[PAGE].read_typetree();nr=refs(nativepage);rr=refs(doc)
 using=next(u for u in nativepage['m_Usings']if u['alias']=='OverviewNativeSeasonFourGauges')
 current=next(u for u in doc['m_Usings']if u['alias']=='OverviewNativeSeasonFourGauges');current.clear();current.update(copy.deepcopy(using))
 data(rr,6304).clear();data(rr,6304).update(copy.deepcopy(data(nr,6304)))
 assert data(rr,6304).get('template',{}).get('m_PathID',0)!=-941100000001050
 st=Styles(sheet)
 def color(r,g,b,a=1):
  f=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
  return st.h(4,dict(r=f(r/255),g=f(g/255),b=f(b/255),a=f(a)))
 rows=[i for i,r in rr.items()if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','').startswith('RightHiddenRow_')]
 assert len(rows)==13
 for j,i in enumerate(rows):
  st.edit(rr[i],[st.p(458752,color(*( (43,57,85)if j%2==0 else(30,45,65) ))),st.p(131099,st.px(7)),st.p(131100,st.px(3))])
 # Keep the vertical separator requested for the two lower halves.
 st.edit(rr[5852],[st.p(131078,st.px(1)),st.p(458762,color(117,137,165,.6)),st.p(131100,st.px(9))])
 st.edit(rr[6298],[st.p(131099,st.px(9))])
 graph(doc)
 # All bindings apart from the deliberate season-template restoration are exact.
 oldrr=refs(original)
 for i,r in oldrr.items():
  if i!=rr[6304]['data']['m_SerializedData']['rid']:assert rr[i]==r or 'm_SerializedData'in r.get('data',{})
 assert [data(rr,c['rid'])['name']for c in rr[6064]['data']['m_Children']]==[data(oldrr,c['rid'])['name']for c in oldrr[6064]['data']['m_Children']]
 for i in rows:
  key=data(rr,i)['name'].removeprefix('RightHiddenRow_');badge=named(doc,'RightHiddenBadge_'+key)
  assert rr[badge]==oldrr[badge]
 # Validate live shared module remains the original 12-stat, 4-by-3 table.
 native=obs[-950000000000168].read_typetree();nrr=refs(native)
 for panel in ['SeasonStatsOutfielderPanel','SeasonStatsGoalkeeperPanel']:
  pi=named(native,panel);rowids=nrr[pi]['data']['m_Children'];assert len(rowids)==4
  assert all(sum('StatCell_'in data(nrr,a['rid']).get('name','')for a in nrr[c['rid']]['data']['m_Children'])==3 for c in rowids)
 obs[PAGE].save_typetree(doc);obs[sid].save_typetree(sheet);output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
 assert set(check)==set(obs);assert check[PAGE].read_typetree()==doc;assert check[sid].read_typetree()==sheet
 for i,h in baseline.items():
  if i not in [PAGE,sid]:assert sha(check[i].get_raw_data())==h,('unrelated',tag,i)
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,season_stats=[3,3,3,3],hidden_original_badges=13,hidden_background_bars=True,native_top_layout_restored=True,other_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Restore four-row season table and prior top layout, restore hidden badge styling, retain bars and divider',checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'restore-season-table-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
