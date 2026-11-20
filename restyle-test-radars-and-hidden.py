"""Two equal radar cells, stacked summary and locally coloured hidden rows."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('add-left-test-overview.py',{'prune'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('build-seven-badges-v39.py',{'string','encode','decode'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'));m=json.loads(Path(previous['manifest']).read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('test-equal-radars-hidden-bars-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
tx=[];checks=[]
for tag,root in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 doc=obs[-941100000001020].read_typetree();original=copy.deepcopy(doc);sheet=obs[doc['inlineSheet']['m_PathID']].read_typetree();st=Styles(sheet);rr=refs(doc)
 plain=(copy.deepcopy(rr[1291]),copy.deepcopy(rr[rr[1291]['data']['m_SerializedData']['rid']]))
 swproto=(copy.deepcopy(rr[5898]),copy.deepcopy(rr[rr[5898]['data']['m_SerializedData']['rid']]))
 textproto=(copy.deepcopy(rr[6072]),copy.deepcopy(rr[rr[6072]['data']['m_SerializedData']['rid']]))
 def style(i,ps,reset=False):
  rr=refs(doc);st.edit(rr[i],[st.p(k,v)for k,v in ps],reset)
 def box(i,w,h,grow=0,direction='column',reset=False):
  style(i,[(131102,st.en('relative')),(131089,{'m_ValueType':1,'valueIndex':2}),(131103,{'m_ValueType':1,'valueIndex':2}),(131104,{'m_ValueType':1,'valueIndex':2}),(131080,{'m_ValueType':1,'valueIndex':2}),(131105,w),(131097,st.px(0)),(131095,{'m_ValueType':1,'valueIndex':3}),(131087,h),(131096,st.px(0)),(131094,{'m_ValueType':1,'valueIndex':3}),(131084,st.num(grow)),(131085,st.num(1)),(131082,st.px(0)if grow else {'m_ValueType':1,'valueIndex':2}),(131083,st.en(direction)),(131073,st.en('stretch'))],reset)
 def color(r,g,b,a=1):
  f=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
  return st.h(4,dict(r=f(r/255),g=f(g/255),b=f(b/255),a=f(a)))
 # The native attribute chart and season chart keep their original data scopes.
 radarrow=add_node(doc,plain,1173,'TestOverviewEqualRadarRow');rr=refs(doc)
 for i in [2242,1026]:
  rr[1173]['data']['m_Children'].remove({'rid':i});rr[i]['data']['m_Parent']={'rid':radarrow};rr[radarrow]['data']['m_Children'].append({'rid':i})
 box(1173,st.px(620),st.px(250),1)
 style(1173,[(131082,st.px(620)),(131097,st.px(480))])
 box(radarrow,st.pct(100),st.pct(100),1,'row',True)
 for i in [2242,1026]:
  box(i,st.px(0),st.pct(100),1,reset=True)
  style(i,[(131091,st.px(3)),(131092,st.px(3)),(131099,st.px(4)),(131100,st.px(4)),(458752,color(16,26,43,.48)),(131078,st.px(1)),(131079,st.px(1)),(131076,st.px(1)),(131077,st.px(1)),(458758,color(91,108,133,.55)),(458761,color(91,108,133,.55)),(458762,color(91,108,133,.55)),(458763,color(91,108,133,.55))]+[(k,st.px(7))for k in [458759,458760,458764,458765]])
 box(1043,st.pct(100),st.pct(100),1)
 style(1043,[(327681,st.num(1),)])
 rr=refs(doc);data(rr,1043).update(SpiderChartRadiusPercentage=36.,SpiderChartRadiusPercentage_UxmlAttributeFlags=1)
 # Main season module follows its cell width instead of the old fixed 240px.
 style(6304,[(131105,st.pct(100)),(131103,st.px(0))])
 # Three summary lines, with the existing CA/PA gauge below them.
 box(5854,st.pct(100),st.px(100));style(5854,[(131085,st.num(0)),(131096,st.px(100)),(131094,st.px(100))])
 box(5856,st.pct(100),st.px(72),0,'column')
 for i in [6260,6262,5869]:
  box(i,st.pct(100),st.px(24),0,'row');style(i,[(131088,st.en('flex-start')),(131073,st.en('center')),(131085,st.num(0))])
 style(5892,[(131104,st.px(75))])
 # Explicit name + value layout, keeping the original live number bindings.
 for title in [5859,5865,5870]:style(title,[(131105,st.px(74)),(131084,st.num(0)),(131085,st.num(0)),(65546,st.en('middle-left'))])
 for value in [5860,5866,5871]:style(value,[(131084,st.num(0)),(131105,st.px(64)),(131087,st.px(24)),(131102,st.en('relative'))])
 # Reuse the local native > comparator to avoid any shared colour changes.
 comparison=decode(swproto[1]['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
 assert struct.unpack('<i',comparison[0][1])[0]==4
 def threshold(parent,name,limit):
  i=add_node(doc,swproto,parent,name);rr=refs(doc);sd=data(rr,i);args=copy.deepcopy(comparison)
  args[1]=(args[1][0],struct.pack('<i',limit));args[2]=('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+string('propertyValue'))
  sd['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
  box(i,st.pct(100),st.pct(100),1,reset=True);return i
 def number(parent,name,rgb):
  i=add_node(doc,textproto,parent,name);rr=refs(doc);sd=data(rr,i)
  sd.update(text='',text_UxmlAttributeFlags=0,TextBinding_UxmlAttributeFlags=1)
  sd['TextBinding']['m_kind']=1;sd['TextBinding']['m_direct']={'Path':{'m_path':'propertyValue'},'Nullable':0}
  box(i,st.pct(100),st.pct(100),1,reset=True)
  style(i,[(458752,color(*rgb)),(65536,color(255,255,255)),(65537,st.px(13)),(65546,st.en('middle-center'))]+[(k,st.px(4))for k in [458759,458760,458764,458765]]);return i
 rr=refs(doc);rows=[i for i,r in rr.items()if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','').startswith('RightHiddenRow_')]
 assert len(rows)==13
 for j,row in enumerate(rows):
  rr=refs(doc);nm=data(rr,row)['name'].removeprefix('RightHiddenRow_')
  label=named(doc,'RightHiddenLabel_'+nm);mapper=named(doc,'RightHiddenValueMapping_'+nm);badge=named(doc,'RightHiddenBadge_'+nm)
  box(row,st.pct(100),st.px(22),0,'row');style(row,[(131085,st.num(0)),(131096,st.px(22)),(131094,st.px(22)),(458752,color(*( (43,57,85)if j%2==0 else(30,45,65) ))),(131099,st.px(7)),(131100,st.px(3)),(131090,st.px(1))])
  style(label,[(131084,st.num(1)),(131082,st.px(0)),(131087,st.px(22)),(65537,st.px(12))])
  box(mapper,st.px(36),st.px(20))
  prune(doc,badge)
  gate=threshold(mapper,'HiddenBadgeAboveNine_'+nm,9)
  number(gate,'HiddenBadgeLow_'+nm,(153,48,67))
  excellent=threshold(gate,'HiddenBadgeAboveSixteen_'+nm,16)
  number(excellent,'HiddenBadgeMedium_'+nm,(57,80,121));number(excellent,'HiddenBadgeHigh_'+nm,(35,119,48))
  rr=refs(doc)
 # A fixed 1px rule separates the two lower halves without changing their data.
 style(5852,[(131078,st.px(1)),(458762,color(117,137,165,.6)),(131100,st.px(9))])
 style(6298,[(131099,st.px(9))])
 graph(doc)
 # Existing non-layout serialized bindings must survive unchanged.
 oldrr=refs(original);newrr=refs(doc)
 for i,r in oldrr.items():
  if i in newrr and 'm_SerializedData'not in r.get('data',{}) and i!=oldrr[1043]['data']['m_SerializedData']['rid']:assert newrr[i]==r,('Existing binding changed',tag,i)
 sid=doc['inlineSheet']['m_PathID'];obs[-941100000001020].save_typetree(doc);obs[sid].save_typetree(sheet)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(obs)
 assert check[-941100000001020].read_typetree()==doc;assert check[sid].read_typetree()==sheet
 for i,h in baseline.items():
  if i not in [-941100000001020,sid]:assert sha(check[i].get_raw_data())==h
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,hidden_rows=13,colour_thresholds=[9,16],original_bindings_preserved=True,other_objects_byte_identical=True))
 print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Equal native radar cells, three summary rows, thirteen striped colour badges and vertical separator',checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'equal-radars-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
