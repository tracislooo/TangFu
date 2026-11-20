"""Restore the native competition context, move preference-controlled ID, hide CA/PA icons."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'));m=json.loads(Path(previous['manifest']).read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001020;STATS=-941100000001050
OUT=R/('test-season-context-id-position-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
for tag,root in roots:
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 page=obs[PAGE].read_typetree();oldpage=copy.deepcopy(page);rr=refs(page);sheet=obs[page['inlineSheet']['m_PathID']].read_typetree();st=Styles(sheet)
 # Move the entire native preference-controlled instance, not its text child.
 assert rr[1221]['data']['m_TemplateAlias']=='MovedBanner_DisplayDatabaseObjectID'
 assert rr[1221]['data']['m_Parent']=={'rid':1205}
 rr[1205]['data']['m_Children'].remove({'rid':1221});rr[1206]['data']['m_Children'].insert(0,{'rid':1221});rr[1221]['data']['m_Parent']={'rid':1206}
 st.edit(rr[1221],[st.p(131102,st.en('relative')),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131074,st.en('center'))])
 # Hide icon containers only; retain titles, live values and all rating bindings.
 for i in [5857,5863]:st.edit(rr[i],[st.p(131081,st.en('none'))])
 for i,r in refs(oldpage).items():
  if 'm_SerializedData'not in r.get('data',{}):assert rr[i]==r,('Existing binding/event changed',i)
 # Use the current shared working native league-stat component as the donor.
 native=obs[-950000000000168].read_typetree();nr=refs(native);stats=obs[STATS].read_typetree();sr=refs(stats);oldstats=copy.deepcopy(stats)
 assert sr[1041]['data']['m_FullTypeName']=='SI.Bindable.BindingRemapper'
 assert nr[1041]['data']['m_FullTypeName']=='SI.UI.ComponentElement'
 assert not any(i in sr for i in [1597,1598])
 oldchildren=copy.deepcopy(sr[1041]['data']['m_Children']);oldrule=sr[1041]['data']['m_RuleIndex']
 node=copy.deepcopy(nr[1041]);node['data']['m_Children']=[{'rid':1597}]+oldchildren;node['data']['m_RuleIndex']=oldrule
 # Keep the existing root ID, parent and layout while replacing only its scope type.
 for k in ['m_Id','m_Parent','m_Classes','m_SerializedData']:node['data'][k]=copy.deepcopy(sr[1041]['data'][k])
 root_sd=copy.deepcopy(nr[1053]);root_sd['data']['uxmlAssetId']=node['data']['m_Id']
 component=copy.deepcopy(nr[1597]);component_sd=copy.deepcopy(nr[1598])
 component['data']['m_Parent']={'rid':1041};component['data']['m_ParentId']=node['data']['m_Id']
 ids={r.get('data',{}).get('m_Id')for r in sr.values()}
 if component['data']['m_Id']in ids:
  ident=max(i for i in ids if isinstance(i,int))+1;assert ident<2147483647;component['data']['m_Id']=ident;component_sd['data']['uxmlAssetId']=ident
 sr[1041].clear();sr[1041].update(node);sr[1053].clear();sr[1053].update(root_sd);stats['references']['RefIds'].extend([component,component_sd]);sr=refs(stats)
 expected=[('competition','person.Division'),('seasonStats','person.SeasonStats.SeasonStatsSelectedCompetitionsData')]
 assert [(x['from'],x['to']['m_path'])for x in component_sd['data']['Mappings']]==expected
 assert data(sr,1041)['m_components']==[{'rid':1598}]
 for i,r in refs(oldstats).items():
  if i not in [1041,1053]:assert sr[i]==r,('Existing statistic/formatter changed',i)
 assert data(rr,1221)==data(refs(oldpage),1221)
 graph(page);graph(stats);validate_ui(page,sheet);validate_ui(stats,obs[stats['inlineSheet']['m_PathID']].read_typetree())
 changes={PAGE:page,page['inlineSheet']['m_PathID']:sheet,STATS:stats}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in baseline.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',tag,i)
 for i,d in changes.items():assert check[i].read_typetree()==d
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,native_competition_component_restored=True,mappings=expected,id_preference_binding_unchanged=True,position_row_order=[c['rid']for c in rr[1206]['data']['m_Children']],ability_potential_icons_hidden=True,numeric_bindings_and_formatters_unchanged=True,other_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Native competition context restored; preference ID before position/age; CA/PA icons hidden',protected_sha256=protected,checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'season-context-id-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
