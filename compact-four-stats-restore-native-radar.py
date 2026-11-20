"""Wide identity, compact native KPIs, two radars and directly bound axis labels."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,math,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-left-test-overview.py',{'prune'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('radar',R/'season-radar-builders.py');rb=importlib.util.module_from_spec(spec);spec.loader.exec_module(rb)
loc=json.loads((R/'current-game-location.json').read_text('utf8'));index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'));m=json.loads(Path(previous['manifest']).read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';OUT=R/('test-four-kpis-two-radars-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))];protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
for tag,root in roots:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
 page=obs[-941100000001020].read_typetree();oldpage=copy.deepcopy(page);pr=refs(page);ps=obs[-941100000001021].read_typetree();pst=Styles(ps)
 # Restore the header width from before the full match-data insertion.
 pst.edit(pr[1173],[pst.p(131105,pst.px(540)),pst.p(131082,pst.px(540))])
 # The original native radar remains in its original binding scope.
 pst.edit(pr[1026],[pst.p(131081,pst.en('flex')),pst.p(131102,pst.en('absolute')),pst.p(131089,pst.px(308)),pst.p(131103,{'m_ValueType':1,'valueIndex':2}),pst.p(131104,pst.px(90)),pst.p(131105,pst.px(200)),pst.p(131087,pst.px(159)),pst.p(131096,pst.px(159)),pst.p(131094,pst.px(159))])
 pst.edit(pr[1043],[pst.p(131087,pst.pct(100)),pst.p(131096,pst.px(0)),pst.p(131094,{'m_ValueType':1,'valueIndex':3})])
 stats=obs[-941100000001050].read_typetree();oldstats=copy.deepcopy(stats);rr=refs(stats);sheet=obs[-941100000001051].read_typetree();st=Styles(sheet)
 def edit(i,props):st.edit(refs(stats)[i],[st.p(k,v)for k,v in dict(props).items()])
 def box(i,w,h,grow=0,direction='column'):
  edit(i,[(131102,st.en('relative')),(131089,{'m_ValueType':1,'valueIndex':2}),(131104,{'m_ValueType':1,'valueIndex':2}),(131105,w),(131097,st.px(0)),(131087,h),(131096,st.px(0)),(131094,{'m_ValueType':1,'valueIndex':3}),(131084,st.num(grow)),(131085,st.num(0)),(131082,st.px(0)if grow else{'m_ValueType':1,'valueIndex':2}),(131083,st.en(direction)),(131073,st.en('stretch'))])
 def move(i,parent):
  r=refs(stats);r[r[i]['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});r[i]['data']['m_Parent']={'rid':parent};r[parent]['data']['m_Children'].append({'rid':i})
 # Retain precisely the top native row and the four screenshot LHS modules.
 for i in [1127,1130,1086,1089,1147,1054,1052,1051,1059]:prune(stats,i)
 move(1063,1048);move(1065,1048);prune(stats,1050)
 rr=refs(stats);column=named(stats,'WorkingNativeSeasonDataColumn');case=named(stats,'WorkingSeasonRadarGoalkeeperSwitch')
 box(1041,st.pct(100),st.px(249));box(column,st.pct(100),st.px(90));box(1046,st.pct(100),st.px(22));box(1055,st.pct(100),st.px(22),direction='row');box(1048,st.pct(100),st.px(64),direction='row')
 for i in [1058,1060,1063,1065]:box(i,st.px(0),st.pct(100),1,'row')
 for i in [1047,1049]:box(i,st.pct(100),st.px(1))
 box(case,st.px(300),st.px(159));edit(case,[(131097,st.px(300)),(131095,st.px(300)),(131091,st.px(0))])
 for i in range(1073,1080):
  for j in owned_refs(rr,i):
   if rr[j].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':edit(j,[(65537,st.px(8)),(131087,st.px(10)),(131096,st.px(10)),(131094,st.px(10))])
 # The stock chart labels do not expose our custom raw/valid fields reliably.
 # Bind names and raw values directly within each numeric setter's own scope.
 label=obs[-941100000001052].read_typetree();lr=refs(label)
 def pair(r,i):return copy.deepcopy(r[i]),copy.deepcopy(r[r[i]['data']['m_SerializedData']['rid']])
 plain=pair(rr,1046);titleproto=pair(lr,1003);numberproto=pair(lr,1011);missingproto=pair(lr,1007);switchproto=pair(lr,1005)
 def add(parent,name,proto):return add_node(stats,proto,parent,name)
 casechildren=list(rr[case]['data']['m_Children']);axis_records=[]
 for branch in casechildren:
  outer=branch['rid'];rr=refs(stats);sd=data(rr,outer);functions=copy.deepcopy(sd['BindFunction']);assert len(functions)==6
  overlay=add(outer,'SeasonRadarDirectAxisLabels',plain);rr=refs(stats)
  box(overlay,st.px(300),st.px(159));edit(overlay,[(131102,st.en('absolute')),(131089,st.px(0)),(131104,st.px(0))])
  for axis,fn in enumerate(functions):
   # Source names already follow the six requested metric order.
   raw=bytes(fn['m_inputs']['m_variable']['m_argumentBytes']);p=1;args=[]
   for _ in range(raw[0]):
    n=struct.unpack_from('<I',raw,p)[0];args.append(raw[p+4:p+4+n]);p+=4+n
   arg=args[4];q=1+arg[0];assert arg[q]==1;length=arg[q+1];name=arg[q+2:q+2+length].decode();assert name.startswith('seasonRadar')and name.endswith('Raw');prefix=name[:-3]
   angle=-math.pi/2+axis*math.pi/3;radius=159*.32+8
   x=struct.unpack('<f',struct.pack('<f',150+radius*math.cos(angle)-44))[0];y=struct.unpack('<f',struct.pack('<f',79.5+radius*math.sin(angle)-10))[0]
   block=add(overlay,'AxisLabel_'+prefix,plain);box(block,st.px(88),st.px(20));edit(block,[(131102,st.en('absolute')),(131089,st.px(x)),(131104,st.px(y))])
   title=add(block,'AxisTitle_'+prefix,titleproto);rr=refs(stats);ts=data(rr,title);ts['TextBinding']['m_direct']['Path']['m_path']=prefix+'Title'
   gate=add(block,'AxisValueAvailable_'+prefix,switchproto);rr=refs(stats);data(rr,gate)['Binding']['m_direct']['Path']['m_path']=prefix+'Valid'
   missing=add(gate,'AxisMissing_'+prefix,missingproto);rr=refs(stats);ms=data(rr,missing);ms.update(text='--',text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=1);ms['TextBinding']['m_kind']=0
   number=add(gate,'AxisValue_'+prefix,numberproto);rr=refs(stats);ns=data(rr,number);ns['TextBinding']=rb.rewrite_argument_text(ns['TextBinding'],{'binding.MeanStatValue':prefix+'Raw'})
   for i in [title,gate,missing,number]:box(i,st.pct(100),st.px(10))
   for i in [title,missing,number]:edit(i,[(65537,st.px(9 if i==title else 10)),(65546,st.en('middle-center'))])
   axis_records.append(dict(branch=outer,raw=prefix+'Raw',valid=prefix+'Valid',number=number,title=title))
  assert data(rr,outer)['BindFunction']==functions
 rr=refs(stats)
 for i,r in rr.items():
  if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMSpiderChart':
   cd=data(rr,i);cd.update(SpiderChartRadiusPercentage=32.,LabelDistanceFromChart=8.)
 # Hide only the old label template's presentation, keep chart rendering intact.
 ls=obs[-941100000001053].read_typetree();lst=Styles(ls);lst.edit(lr[1001],[lst.p(131081,lst.en('none'))])
 orr=refs(oldstats)
 for i in [1053,1597,1598]:assert rr[i]==orr[i],'Working season context changed'
 for i,r in rr.items():
  if i in orr and 'm_SerializedData'not in r.get('data',{})and i not in [rr[c]['data']['m_SerializedData']['rid']for c in rr if rr[c].get('data',{}).get('m_FullTypeName')=='FM.UI.FMSpiderChart']:assert r==orr[i],('Existing data changed',i)
 assert data(pr,1043)==data(refs(oldpage),1043),'Original attribute radar binding changed'
 graph(stats);graph(page);validate_ui(stats,sheet);validate_ui(page,ps)
 changes={-941100000001020:page,-941100000001021:ps,-941100000001050:stats,-941100000001051:sheet,-941100000001053:ls}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h
 for i,d in changes.items():assert check[i].read_typetree()==d,('Roundtrip',i)
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,wide_identity_header_width=540,top_native_row=True,card_roots=[1058,1060,1063,1065],original_radar_restored=True,direct_axis_records=axis_records,working_context_unchanged=True,unrelated_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Compact four native cards and top row; wide identity; two radars with directly scoped raw labels',protected_sha256=protected,checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'four-kpis-two-radars-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
