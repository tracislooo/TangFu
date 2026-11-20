"""Compact native match-data body in the header; retain hidden native radar."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'));priorout=Path(previous['manifest']).parent;m=json.loads((priorout/'manifest.json').read_text('utf8'));ptx=json.loads((priorout/'transaction.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001020
OUT=R/('test-full-native-season-header-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for root in [Path(loc['bundle_root']),Path(loc['skin_packages'])]for p in root.glob('*.bundle')if p.name!=W}
for root in [Path(loc['bundle_root']).parent,Path(loc['skin_packages'])]:
 for name in ['catalog.bin','catalog.hash']:protected[str(root/name)]=sha((root/name).read_bytes())
for tag,root in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();prior=next(row for row in ptx if Path(row['target'])==root/W)
 env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 expected={o.path_id:o for o in UnityPy.load(prior['source']).objects}
 for i in [PAGE,-941100000001021,-941100000001050,-941100000001051]:assert obs[i].get_raw_data()==expected[i].get_raw_data(),('Test-page baseline changed',tag,i)
 page=obs[PAGE].read_typetree();original=copy.deepcopy(page);ps=obs[page['inlineSheet']['m_PathID']].read_typetree();st=Styles(ps);pr=refs(page)
 auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
 def edit(i,props):st.edit(pr[i],[st.p(k,v)for k,v in dict(props).items()])
 def box(i,w,h,grow=0,direction='column'):
  edit(i,[(131102,st.en('relative')),(131089,auto),(131103,auto),(131104,auto),(131080,auto),(131105,w),(131097,st.px(0)),(131095,none),(131087,h),(131096,st.px(0)),(131094,none),(131084,st.num(grow)),(131085,st.num(1)),(131082,st.px(0)if grow else auto),(131083,st.en(direction)),(131073,st.en('stretch'))])
 def move(i,parent,index=None):
  pr[pr[i]['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});pr[i]['data']['m_Parent']={'rid':parent}
  if index is None:pr[parent]['data']['m_Children'].append({'rid':i})
  else:pr[parent]['data']['m_Children'].insert(index,{'rid':i})
 # Give the complete module the whole former status/statistics/radar region.
 box(1173,st.px(660),st.px(250));edit(1173,[(131082,st.px(660))])
 box(2242,st.pct(100),st.pct(100),1);edit(2242,[(458768,st.en('hidden'))])
 box(6304,st.pct(100),st.pct(100),1)
 # Reversible hide: the radar's node, serialized data and native bindings remain.
 for i in [1026,6288]:edit(i,[(131081,st.en('none'))])
 # Fitness indicators follow the name in the existing name row.
 move(2986,1205);box(2986,st.px(210),st.px(42));edit(2986,[(131085,st.num(0)),(131091,st.px(8)),(131074,st.en('center'))])
 for i in [1175,1188]:edit(i,[(131105,st.pct(100)),(131097,st.px(0)),(131085,st.num(1))])
 edit(1205,[(131073,st.en('center')),(131105,st.pct(100))]);edit(1219,[(131097,st.px(0)),(131085,st.num(1))])
 # Carry the original localteam/player scope when moving the scout header.
 a,b=copy.deepcopy(pr[1116]),copy.deepcopy(pr[pr[1116]['data']['m_SerializedData']['rid']])
 newrid=max(pr)+1;newid=max(r.get('data',{}).get('m_Id',0)for r in pr.values())+1
 a.update(rid=newrid);a['data'].update(m_Id=newid,m_Parent={'rid':6298},m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':newrid+1})
 b.update(rid=newrid+1);b['data'].update(uxmlAssetId=newid,name='ScoutHeaderPreservedContext',name_UxmlAttributeFlags=1)
 page['references']['RefIds'].extend([a,b]);pr=refs(page);pr[6298]['data']['m_Children'].insert(0,{'rid':newrid})
 move(1349,newrid);box(newrid,st.pct(100),st.px(75));edit(newrid,[(131085,st.num(0))])
 box(1349,st.pct(100),st.px(70));edit(1349,[(131085,st.num(0)),(131090,st.px(5))])
 for i in [1351,1186,1203]:edit(i,[(131105,st.pct(100)),(131097,st.px(0)),(131095,none)])
 box(6310,st.pct(100),st.px(0),1)
 # Extract only the screenshot's complete match-data body. Keep its native
 # season remapper, translations, formatters, gauges and goalkeeper switches.
 native=obs[-648337528654704265].read_typetree();stats=copy.deepcopy(native);nr=refs(stats)
 nr[1000]['data']['m_Children']=[{'rid':1041}];nr[1041]['data']['m_Parent']={'rid':1000}
 keep=owned_refs(nr,1000);stats['references']['RefIds']=[r for r in stats['references']['RefIds']if r['rid']in keep]
 nr=refs(stats);native_roots=refs(native)
 ss=obs[native['inlineSheet']['m_PathID']].read_typetree();sst=Styles(ss)
 mapping=data(nr,1041)['Mappings'];assert len(mapping)==1 and mapping[0]['from']=='SeasonStats'
 mapping[0]['to']['m_path']='person.SeasonStats.SeasonStatsSelectedCompetitionsData'
 for r in nr.values():
  sd=r.get('data',{});binding=sd.get('Binding',{})
  if binding.get('m_kind')==1 and binding.get('m_direct',{}).get('Path',{}).get('m_path')=='player.IsGoalkeeper':binding['m_direct']['Path']['m_path']='person.IsGoalkeeper'
 def se(i,props,reset=False):sst.edit(nr[i],[sst.p(k,v)for k,v in dict(props).items()],reset)
 def sb(i,w=None,h=None,direction='column',grow=0):
  props=[(131102,sst.en('relative')),(131089,auto),(131103,auto),(131104,auto),(131080,auto),(131097,sst.px(0)),(131095,none),(131096,sst.px(0)),(131094,none),(131084,sst.num(grow)),(131085,sst.num(1)),(131082,sst.px(0)if grow else auto),(131083,sst.en(direction)),(131073,sst.en('stretch')),(131091,sst.px(0)),(131092,sst.px(0)),(131093,sst.px(0)),(131090,sst.px(0)),(131099,sst.px(0)),(131100,sst.px(0)),(131101,sst.px(0)),(131098,sst.px(0))]
  if w is not None:props.append((131105,w))
  if h is not None:props.append((131087,h))
  se(i,props)
 # Remove fixed large-screen dimensions while retaining native classes/colours.
 for i,r in nr.items():
  v=r.get('data',{});typ=v.get('m_FullTypeName','')
  if 'm_SerializedData'not in v or typ=='UnityEngine.UIElements.UXML':continue
  sd=data(nr,i)
  if typ=='SI.Bindable.SIText':
   hero=sd.get('name')in ['OutfielderStatsGoalsText','ChancesCreatedText','KeyPassesText','KeyTacklesText','GoalkeeperStatsGoalsText']
   sb(i,sst.pct(100),sst.px(18 if hero else 11))
   se(i,[(65537,sst.px(14 if hero else 9)),(65552,sst.en('nowrap')),(458768,sst.en('hidden'))])
  elif typ=='SI.Bindable.SIRadialGauge':sb(i,sst.px(22),sst.px(22))
  elif 'game-concepts-'in ' '.join(v.get('m_Classes',[])):sb(i,sst.px(18),sst.px(18))
  elif typ:sb(i,None,auto,'row'if 'row-direction-normal'in v.get('m_Classes',[])else'column')
 sb(1041,sst.pct(100),sst.px(249));se(1041,[(131085,sst.num(0))])
 sb(1046,sst.pct(100),sst.px(42));sb(1054,sst.pct(100),sst.px(12));sb(1055,sst.pct(100),sst.px(30),'row')
 for i in range(1073,1080):sb(i,sst.px(0),sst.pct(100),grow=1)
 for i in [1048,1050]:sb(i,sst.pct(100),sst.px(76),'row')
 for i in [1058,1060,1063,1065]:sb(i,sst.px(0),sst.pct(100),'row',1)
 for i in [1081,1082,1092]:sb(i,sst.pct(100),sst.pct(100),'row',1)
 for i in [1126,1127,1129,1130,1085,1086,1088,1089,1146,1147]:sb(i,sst.px(0),sst.pct(100),'column',1)
 sb(1052,sst.pct(100),sst.px(52))
 for i in [1068,1069]:sb(i,sst.pct(100),sst.px(26),'row')
 for i in [1094,1095,1096,1097,1099,1100,1101,1102]:sb(i,sst.px(0),sst.pct(100),grow=1)
 for i in [1047,1049,1051]:sb(i,sst.pct(100),sst.px(1));se(i,[(131085,sst.num(0))])
 for i in [1059,1064]:sb(i,sst.px(1),sst.pct(100));se(i,[(131085,sst.num(0))])
 for i in [1046,1048,1050,1052]:se(i,[(131085,sst.num(0))])
 stats.update(m_Name='LeftTestFullNativeSeasonMatchData',inlineSheet=dict(m_FileID=0,m_PathID=-941100000001051),m_ContentContainerId=0,m_ContentHash=struct.unpack('<i',struct.pack('<I',zlib.crc32(b'full-native-season-header-v1')))[0]);ss['m_Name']=stats['m_Name']+'Style'
 # Preserve the complete working native competition scope, not just the final
 # selected-competition data reference. Without this the detached report body
 # receives the default zero-stat record.
 working=refs(obs[-950000000000168].read_typetree())
 content=copy.deepcopy(nr[1041]['data']['m_Children']);rule=nr[1041]['data']['m_RuleIndex']
 scope=copy.deepcopy(working[1041]);scope['data']['m_Children']=[{'rid':1597}]+content;scope['data']['m_RuleIndex']=rule
 nr[1041].clear();nr[1041].update(scope)
 nr[1053].clear();nr[1053].update(copy.deepcopy(working[1053]))
 assert 1597 not in nr and 1598 not in nr
 stats['references']['RefIds'].extend([copy.deepcopy(working[1597]),copy.deepcopy(working[1598])]);nr=refs(stats)
 # Original number/formatter binding definitions must all remain identical.
 value_count=0
 for i,r in nr.items():
  if 'TextBinding'in r.get('data',{}):assert r['data']['TextBinding']==native_roots[i]['data']['TextBinding'];value_count+=1
 assert value_count>50
 graph(page);graph(stats);validate_ui(page,ps);validate_ui(stats,ss)
 changes={PAGE:page,-941100000001021:ps,-941100000001050:stats,-941100000001051:ss}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in baseline.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h
 for i,d in changes.items():assert check[i].read_typetree()==d,('Roundtrip',tag,i)
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,native_bound_text_elements=value_count,full_module_source=-648337528654704265,fitness_parent=1205,scout_parent=6298,radar_hidden_not_deleted=True,other_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Complete native match-data body in header; fitness after name; scout above pros/cons; reversible radar hide',checks=checks,protected_sha256=protected)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'full-season-header-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
