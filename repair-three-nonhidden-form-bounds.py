"""Restore native 56px form bars and explicitly bound the local form wrappers."""
from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys, zlib
R=Path(__file__).resolve().parent
s=(R/'sync-old-left-portrait-nonhidden.py').read_text('utf8')
exec(s[:s.index("W='ui-")])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PAGES=[-941100000001100,-930000000001003,-940000000012000]
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('three-nonhidden-form-native-height-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()};changes={}
 for pid in PAGES:
  doc=oo[pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();rr=refs(doc);original=copy.deepcopy(rr);st=Styles(sheet)
  form=named(doc,'MiddleNonHiddenRecentForm');title=named(doc,'MiddleRecentFormTitle')
  content=next(c['rid']for c in rr[form]['data']['m_Children']if c['rid']!=title)
  frame=rr[content]['data']['m_Children'][0]['rid'];children=[c['rid']for c in rr[frame]['data']['m_Children']]
  chart=next(i for i in children if rr[i]['data'].get('m_FullTypeName')=='SI.Bindable.StreamedObjectList');stats=next(i for i in children if i!=chart)
  auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
  def p(k,v):return st.p(k,v)
  def margins():return [p(k,st.px(0))for k in [131090,131091,131092,131093,131098,131099,131100,131101]]
  def fixed_height(i,h):
   st.edit(rr[i],[p(131087,st.px(h)),p(131096,st.px(h)),p(131094,st.px(h)),p(131080,auto),p(131082,auto),p(131084,st.num(0)),p(131085,st.num(0))])
  def inset(i,left,top,right,bottom):
   st.edit(rr[i],margins()+[p(131102,st.en('absolute')),p(131089,st.px(left)),p(131104,st.px(top)),p(131103,st.px(right)),p(131080,st.px(bottom)),p(131105,auto),p(131087,auto),p(131096,st.px(0)),p(131097,st.px(0)),p(131094,none),p(131095,none),p(131082,auto),p(131084,st.num(0)),p(131085,st.num(0))])
  # Keep the form in the lower half; its bottom is anchored to the same panel.
  st.edit(rr[form],[p(131104,st.pct(50)),p(131080,st.px(0)),p(131087,auto),p(131096,st.px(0)),p(131094,none)])
  inset(title,6,4,6,0);fixed_height(title,22)
  # Every wrapper has explicit top/bottom constraints, with no nested 100% heights.
  inset(content,6,28,6,4);inset(frame,0,0,0,0)
  inset(chart,0,0,0,0);fixed_height(chart,56)
  inset(stats,0,64,0,0);fixed_height(stats,80)
  rows=[];captions=[]
  for i in owned_refs(rr,stats):
   x=rr[i].get('data',{})
   if 'm_FullTypeName'not in x:continue
   name=data(rr,i).get('name','')
   if name in ['NoMatches','Outfield','Goalkeeper','HasMatches','IsGoalkeeperCheck']:
    fixed_height(i,80)
    st.edit(rr[i],[p(131102,st.en('relative')),p(131104,auto),p(131080,auto),p(131090,st.px(0)),p(131093,st.px(0))])
    if name in ['NoMatches','Outfield','Goalkeeper']:
     rows.append(i);st.edit(rr[i],[p(131083,st.en('row')),p(131074,st.en('flex-start'))])
   elif name=='Frame':
    fixed_height(i,80);st.edit(rr[i],[p(131083,st.en('column')),p(131088,st.en('flex-start')),p(131074,st.en('center'))])
   elif x.get('m_FullTypeName')=='SI.Bindable.SIText':
    captions.append(i);st.edit(rr[i],[p(131093,st.px(2)),p(131085,st.num(0)),p(65552,st.en('normal'))])
  assert len(rows)==3 and len(captions)==7
  graph(doc);validate_ui(doc,sheet)
  for i,old in original.items():
   a=copy.deepcopy(rr[i]);b=copy.deepcopy(old)
   a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None)
   assert a==b,('Binding or other data changed',pid,i)
  # Verify actual serialized layout properties, including an explicit gap.
  def dim(i,key):
   idx=rr[i]['data'].get('m_RuleIndex',-1)
   props=sheet['m_Rules'][idx]['m_Properties']if idx>=0 else []
   prop=next((p for p in props if p['m_Id']==key),None)
   if prop is None:return {}
   h,=prop['m_Values'];return sheet['dimensions'][h['valueIndex']]if h['m_ValueType']==3 else {}
  assert dim(chart,131087)==dict(unit=1,value=56.0)
  assert dim(chart,131104)==dict(unit=1,value=0.0)
  assert dim(stats,131104)==dict(unit=1,value=64.0)
  assert dim(stats,131087)==dict(unit=1,value=80.0)
  # The current parent heights are 425/425/390px. Derive this from the
  # actual fixed ancestor; title, graph, gap, stats and clearance use 176px.
  main=rr[form]['data']['m_Parent']['rid']
  while main!=-2:
   h=dim(main,131087)
   if h.get('unit')==1 and h.get('value',0)>0 and h==dim(main,131096)==dim(main,131094):break
   main=rr[main]['data'].get('m_Parent',{}).get('rid',-2)
  assert main!=-2,('No definite parent height',pid)
  available=dim(main,131087)['value']/2
  assert 176<=available,('Recent form exceeds its lower-half bounds',pid,available)
  doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
  changes[pid]=doc;changes[sid]=sheet
  checks.append(dict(target=tag,page=pid,native_chart_height_px=56,statistics_offset_px=64,statistics_height_px=80,chart_statistics_gap_px=8,total_form_content_height_px=176,available_lower_half_height_px=available,all_serialized_bindings_unchanged=True))
 for i,v in changes.items():oo[i].save_typetree(v)
 output=env.file.save(packer='lz4');co={o.path_id:o for o in UnityPy.load(output).objects};assert co.keys()==oo.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(co[i].get_raw_data())==h,('Unrelated object changed',i)
 for i,v in changes.items():assert co[i].read_typetree()==v,('Roundtrip mismatch',i)
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 print('Verified '+tag,flush=True)
manifest=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for n,v in [('manifest.json',manifest),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'three-nonhidden-form-native-height-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
