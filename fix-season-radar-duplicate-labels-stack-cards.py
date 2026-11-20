"""One set of direct labels, cards over new radar, independent native radar."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,math,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'}),('add-left-test-overview.py',{'prune'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'));idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'));m=json.loads(Path(previous['manifest']).read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';OUT=R/('test-cards-over-radar-single-labels-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))];protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
for tag,root in roots:
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
 page=obs[-941100000001020].read_typetree();oldpage=copy.deepcopy(page);pr=refs(page);ps=obs[-941100000001021].read_typetree();pst=Styles(ps)
 pst.edit(pr[2242],[pst.p(131105,pst.px(300)),pst.p(131095,pst.px(300)),pst.p(131087,pst.px(249)),pst.p(131084,pst.num(0))])
 pst.edit(pr[1026],[pst.p(131104,pst.px(0)),pst.p(131089,pst.px(308)),pst.p(131087,pst.px(249)),pst.p(131096,pst.px(249)),pst.p(131094,pst.px(249))])
 pst.edit(pr[6288],[pst.p(131081,pst.en('flex')),pst.p(131102,pst.en('absolute')),pst.p(131089,pst.px(304)),pst.p(131104,pst.px(4)),pst.p(131105,pst.px(1)),pst.p(131087,pst.px(242))])
 stats=obs[-941100000001050].read_typetree();oldstats=copy.deepcopy(stats);sheet=obs[-941100000001051].read_typetree();st=Styles(sheet);rr=refs(stats)
 for i in [1046,1047,1049]:prune(stats,i)
 rr=refs(stats);column=named(stats,'WorkingNativeSeasonDataColumn');case=named(stats,'WorkingSeasonRadarGoalkeeperSwitch')
 def edit(i,props):st.edit(refs(stats)[i],[st.p(k,v)for k,v in dict(props).items()])
 def height(i,h):edit(i,[(131087,st.px(h)),(131096,st.px(h)),(131094,st.px(h)),(131084,st.num(0)),(131085,st.num(0))])
 height(column,64);height(case,185)
 labels=0;charts=0
 for i,r in list(rr.items()):
  v=r.get('data',{})
  if not rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data'):continue
  sd=data(rr,i);name=sd.get('name','')
  if v.get('m_FullTypeName')=='FM.UI.FMSpiderChart':
   sd.update(LabelsTemplate=dict(m_AssetGUID=m['label_guid'],m_SubObjectName='',m_SubObjectType=''),LabelsTemplate_UxmlAttributeFlags=1,SpiderChartRadiusPercentage=34.,SpiderChartRadiusPercentage_UxmlAttributeFlags=1);charts+=1
  if name=='SeasonRadarDirectAxisLabels':height(i,185)
 # Axis order comes from the same six scalar-function outputs; native vertices
 # begin at (0,-1) and rotate clockwise in 60-degree increments.
 branches=rr[case]['data']['m_Children']
 for branch in branches:
  outer=branch['rid'];overlays=[c['rid']for c in rr[outer]['data']['m_Children']if data(rr,c['rid']).get('name')=='SeasonRadarDirectAxisLabels'];assert len(overlays)==1
  blocks=rr[overlays[0]]['data']['m_Children'];assert len(blocks)==6
  for axis,c in enumerate(blocks):
   angle=-math.pi/2+axis*math.pi/3;radius=185*.34+8
   f=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
   x=f(150+radius*math.cos(angle)-44);y=f(92.5+radius*math.sin(angle)-10)
   assert 0<=x<=212 and 0<=y<=165
   edit(c['rid'],[(131089,st.px(x)),(131104,st.px(y))]);labels+=1
 assert charts==2 and labels==12
 # All surviving number bindings and all real-data contexts stay unchanged.
 oldrr=refs(oldstats)
 for i,r in rr.items():
  if i not in oldrr or 'm_SerializedData'in r.get('data',{}):continue
  expected=copy.deepcopy(oldrr[i])
  if expected.get('type',{}).get('class')=='FMSpiderChart/UxmlSerializedData':
   expected['data'].update(LabelsTemplate=dict(m_AssetGUID=m['label_guid'],m_SubObjectName='',m_SubObjectType=''),LabelsTemplate_UxmlAttributeFlags=1,SpiderChartRadiusPercentage=34.,SpiderChartRadiusPercentage_UxmlAttributeFlags=1)
  assert r==expected,('Existing binding changed',i)
 assert data(pr,1043)==data(refs(oldpage),1043)
 assert rr[1048]['data']['m_Children']==[{'rid':i}for i in [1058,1060,1063,1065]]
 # Keep the real registered label asset and its native BindingRoot contract.
 # Remove its old text descendants, rather than clearing the AssetReference or
 # relying on display:none which the native chart can overwrite at runtime.
 label=obs[-941100000001052].read_typetree();lr=refs(label)
 assert lr[1001]['data']['m_FullTypeName']=='SI.Bindable.BindingRoot'
 assert data(lr,1001)['Parameters'][0]['name']=='binding'
 for child in list(lr[1001]['data']['m_Children']):prune(label,child['rid'])
 ls=obs[-941100000001053].read_typetree();lst=Styles(ls);lr=refs(label)
 lst.edit(lr[1001],[lst.p(131081,lst.en('flex')),lst.p(131105,lst.px(1)),lst.p(131097,lst.px(1)),lst.p(131095,lst.px(1)),lst.p(131087,lst.px(1)),lst.p(131096,lst.px(1)),lst.p(131094,lst.px(1)),lst.p(131084,lst.num(0)),lst.p(131085,lst.num(0))],reset=True)
 graph(stats);graph(page);graph(label);validate_ui(stats,sheet);validate_ui(page,ps);validate_ui(label,ls)
 changes={-941100000001020:page,-941100000001021:ps,-941100000001050:stats,-941100000001051:sheet,-941100000001052:label,-941100000001053:ls}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h
 for i,d in changes.items():assert check[i].read_typetree()==d
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,cards_height=64,season_radar_height=185,season_radar_width=300,native_radar_region=[308,0,200,249],valid_registered_label_template_retained=True,duplicate_label_text_removed=True,direct_labels=12,top_row_removed=True,contexts_and_values_unchanged=True,other_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Four cards above season radar; native radar independent; top row removed; valid label asset retained without duplicate text',protected_sha256=protected,checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'single-label-radars-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
