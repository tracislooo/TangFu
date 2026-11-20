"""Reduce each recent-form statistic column from 75px to 65px."""
from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys, zlib
R=Path(__file__).resolve().parent
s=(R/'sync-old-left-portrait-nonhidden.py').read_text('utf8')
exec(s[:s.index("W='ui-")])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PAGES=[-941100000001100,-930000000001003,-940000000012000]
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('three-nonhidden-stat-columns65-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()};changes={}
 for pid in PAGES:
  doc=oo[pid].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();rr=refs(doc);original=copy.deepcopy(rr);st=Styles(sheet)
  form=named(doc,'MiddleNonHiddenRecentForm')
  changed=set();cells=[];rows=[]
  title=named(doc,'MiddleRecentFormTitle');content=next(c['rid']for c in rr[form]['data']['m_Children']if c['rid']!=title)
  frame=rr[content]['data']['m_Children'][0]['rid'];children=[c['rid']for c in rr[frame]['data']['m_Children']]
  chart=next(i for i in children if rr[i]['data'].get('m_FullTypeName')=='SI.Bindable.StreamedObjectList');stats=next(i for i in children if i!=chart)
  def value(i,k):
   prop=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']==k)
   h,=prop['m_Values'];return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
  def width(i,w):
   changed.add(i);st.edit(rr[i],[st.p(k,st.px(w))for k in [131105,131097,131095,131082]])
  def left(i,x):
   changed.add(i);st.edit(rr[i],[st.p(131089,st.px(x))])
  assert value(stats,131105)==dict(unit=1,value=227.0)
  width(stats,197)
  for i in owned_refs(rr,stats):
   x=rr[i].get('data',{})
   if 'm_FullTypeName'not in x:continue
   name=data(rr,i).get('name','')
   if name in ['HasMatches','IsGoalkeeperCheck']:width(i,197)
   elif name in ['NoMatches','Outfield','Goalkeeper']:
    rows.append(i);width(i,197)
    cc=[c['rid']for c in rr[i]['data']['m_Children']];frames=[n for n in cc if data(rr,n).get('name')=='Frame']
    assert len(frames)in [1,3]
    for j,cell in enumerate(frames):
     cells.append(cell);assert value(cell,131105)==dict(unit=1,value=75.0)
     width(cell,65);left(cell,j*66 if len(frames)==3 else 66)
     for child in rr[cell]['data']['m_Children']:
      node=child['rid']
      if rr[node]['data'].get('m_FullTypeName')=='SI.Bindable.SIText':width(node,65)
      else:left(node,value(node,131089)['value']-5)
    for j,node in enumerate(n for n in cc if n not in frames):left(node,65+j*66)
  assert len(rows)==3 and len(cells)==7
  for i in cells:assert value(i,131105)==dict(unit=1,value=65.0)
  graph(doc);validate_ui(doc,sheet)
  for i,old in original.items():
   if i not in changed:assert rr[i]==old,('Unrequested node changed',pid,i)
   a=copy.deepcopy(rr[i]);b=copy.deepcopy(old)
   a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None)
   assert a==b,('Data or bindings changed',pid,i)
  doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
  changes[pid]=doc;changes[sid]=sheet
  checks.append(dict(target=tag,page=pid,column_width_before_px=75,column_width_after_px=65,three_column_block_width_px=197,average_rating_scale_preserved=True,all_other_nodes_exact=True,all_serialized_bindings_unchanged=True))
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
(R/'three-nonhidden-stat-columns65-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
