"""300px radar with native BindingRoot label input and larger name/value labels."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'));m=json.loads(Path(previous['manifest']).read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('test-season-radar300-labels-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
for tag,root in roots:
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 d=obs[-941100000001050].read_typetree();old=copy.deepcopy(d);rr=refs(d);s=obs[-941100000001051].read_typetree();st=Styles(s)
 case=named(d,'WorkingSeasonRadarGoalkeeperSwitch')
 st.edit(rr[case],[st.p(131105,st.px(300)),st.p(131097,st.px(300)),st.p(131095,st.px(300)),st.p(131085,st.num(0))])
 charts=[]
 for i,r in rr.items():
  if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMSpiderChart':
   charts.append(i);cd=data(rr,i);cd.update(SpiderChartRadiusPercentage=32.,LabelDistanceFromChart=10.,SpiderChartRadiusPercentage_UxmlAttributeFlags=1,LabelDistanceFromChart_UxmlAttributeFlags=1)
 assert len(charts)==2
 # The native chart passes its 'binding' parameter through BindingRoot. A plain
 # VisualElement at the label root cannot receive that parameter correctly.
 native=obs[-4069184508898986273].read_typetree();nr=refs(native)
 label=obs[-941100000001052].read_typetree();lr=refs(label);oldlabel=copy.deepcopy(label);sid=lr[1001]['data']['m_SerializedData']['rid']
 rootdata=copy.deepcopy(nr[nr[1001]['data']['m_SerializedData']['rid']]);rootdata['rid']=sid;rootdata['data'].update(uxmlAssetId=lr[1001]['data']['m_Id'],name='SeasonRadarAxisLabel',name_UxmlAttributeFlags=1)
 lr[1001]['data']['m_FullTypeName']='SI.Bindable.BindingRoot';lr[sid].clear();lr[sid].update(rootdata)
 assert rootdata['data']['Parameters'][0]['name']=='binding'
 ls=obs[-941100000001053].read_typetree();lst=Styles(ls)
 lst.edit(lr[1001],[lst.p(131105,lst.px(88)),lst.p(131087,lst.px(30)),lst.p(131083,lst.en('column')),lst.p(131073,lst.en('stretch'))])
 for i,r in lr.items():
  v=r.get('data',{})
  if v.get('m_FullTypeName')=='SI.Bindable.SIText':
   title=data(lr,i).get('name')=='AxisTitle'
   lst.edit(r,[lst.p(131105,lst.pct(100)),lst.p(131087,lst.px(15)),lst.p(131096,lst.px(15)),lst.p(131094,lst.px(15)),lst.p(65537,lst.px(10 if title else 11)),lst.p(65546,lst.en('middle-center'))])
 # Existing scopes, fields, range/reversal rules and raw-value formatting remain.
 oldrr=refs(old)
 for i,r in oldrr.items():
  if i in charts:
   expected=copy.deepcopy(r);ed=expected['data'];assert ed==rr[i]['data']
  if 'm_SerializedData'not in r.get('data',{})and i not in [rr[c]['data']['m_SerializedData']['rid']for c in charts]:assert rr[i]==r
 for i,r in refs(oldlabel).items():
  if i not in [1001,sid]and 'm_SerializedData'not in r.get('data',{}):assert lr[i]==r
 graph(d);graph(label);validate_ui(d,s);validate_ui(label,ls)
 changes={-941100000001050:d,-941100000001051:s,-941100000001052:label,-941100000001053:ls}
 for i,t in changes.items():obs[i].save_typetree(t)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in baseline.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h
 for i,t in changes.items():assert check[i].read_typetree()==t
 # Geometry bound: 32% of min(300,249) plus label offset and half-width fits.
 radius=min(300,249)*.32;assert radius+10+88/2<300/2 and radius+10+30/2<249/2
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,width=300,label_binding_root=True,axis_names_and_raw_value_bindings_preserved=True,label_size=[88,30],chart_radius_percent=32,working_season_context_unchanged=True,unrelated_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='300px radar with native label BindingRoot, axis titles and raw values',protected_sha256=protected,checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'radar300-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
