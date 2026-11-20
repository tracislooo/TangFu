"""Fix recent-form statistic columns and text to non-overlapping pixel rectangles."""
from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys, zlib
R=Path(__file__).resolve().parent
s=(R/'sync-old-left-portrait-nonhidden.py').read_text('utf8')
exec(s[:s.index("W='ui-")])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PAGES=[-941100000001100,-930000000001003,-940000000012000]
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('three-nonhidden-form-fixed-pixels-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
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
  title=named(doc,'MiddleRecentFormTitle');content=next(c['rid']for c in rr[form]['data']['m_Children']if c['rid']!=title)
  frame=rr[content]['data']['m_Children'][0]['rid'];children=[c['rid']for c in rr[frame]['data']['m_Children']]
  chart=next(i for i in children if rr[i]['data'].get('m_FullTypeName')=='SI.Bindable.StreamedObjectList');stats=next(i for i in children if i!=chart)
  changed=set();cells=[];captions=[];graphics=[];rows=[]
  auto={'m_ValueType':1,'valueIndex':2}
  def box(i,x,y,w,h):
   changed.add(i)
   st.edit(rr[i],[st.p(131102,st.en('absolute')),st.p(131089,st.px(x)),st.p(131104,st.px(y)),st.p(131103,auto),st.p(131080,auto),st.p(131105,st.px(w)),st.p(131097,st.px(w)),st.p(131095,st.px(w)),st.p(131087,st.px(h)),st.p(131096,st.px(h)),st.p(131094,st.px(h)),st.p(131082,st.px(w)),st.p(131084,st.num(0)),st.p(131085,st.num(0))]+[st.p(k,st.px(0))for k in [131090,131091,131092,131093,131098,131099,131100,131101]])
  # Entire statistic block is a fixed 242x76px rectangle below the graph.
  box(stats,0,64,242,76)
  for i in owned_refs(rr,stats):
   x=rr[i].get('data',{})
   if 'm_FullTypeName'not in x:continue
   name=data(rr,i).get('name','')
   if name in ['HasMatches','IsGoalkeeperCheck']:box(i,0,0,242,76)
   elif name in ['NoMatches','Outfield','Goalkeeper']:
    rows.append(i);box(i,0,0,242,76)
    cc=[c['rid']for c in rr[i]['data']['m_Children']]
    frames=[n for n in cc if data(rr,n).get('name')=='Frame']
    assert len(frames)in [1,3]
    for j,cell in enumerate(frames):
     cells.append(cell);left=j*81 if len(frames)==3 else 81
     box(cell,left,0,80,76)
     for ch in rr[cell]['data']['m_Children']:
      node=ch['rid'];nd=rr[node]['data']
      if nd.get('m_FullTypeName')=='SI.Bindable.SIText':
       captions.append(node);box(node,0,24,80,48)
       st.edit(rr[node],[st.p(65537,st.px(10)),st.p(65552,st.en('normal')),st.p(65546,st.en('upper-center'))])
      else:
       graphics.append(node)
       remap=nd.get('m_FullTypeName')=='SI.Bindable.BindingRemapper'
       width,height=(52,20)if remap else (16,16)
       box(node,(80-width)/2,0,width,height)
       if remap:
        for kid in nd.get('m_Children',[]):box(kid['rid'],0,0,52,20)
    separators=[n for n in cc if n not in frames]
    assert len(separators)in [0,2]
    for j,node in enumerate(separators):box(node,80+j*81,0,1,72)
  assert len(rows)==3 and len(cells)==7 and len(captions)==7 and len(graphics)==7
  graph(doc);validate_ui(doc,sheet)
  for i,old in original.items():
   if i not in changed:assert rr[i]==old,('Unrequested node changed',pid,i)
   a=copy.deepcopy(rr[i]);b=copy.deepcopy(old)
   a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None)
   assert a==b,('Data or bindings changed',pid,i)
  def value(i,key):
   prop=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']==key)
   h,=prop['m_Values'];return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
  rectangles=[]
  for i in changed:
   x,y,w,h=[value(i,k)['value']for k in [131089,131104,131105,131087]]
   parent=rr[i]['data']['m_Parent']['rid']
   if parent in changed:
    pw,ph=[value(parent,k)['value']for k in [131105,131087]]
    assert x>=0 and y>=0 and x+w<=pw and y+h<=ph,('Rectangle outside parent',pid,i,x,y,w,h,pw,ph)
   rectangles.append(dict(node=i,parent=parent,x=x,y=y,width=w,height=h))
  for rect in rectangles:
   for other in rectangles:
    if rect['node']>=other['node']or rect['parent']!=other['parent']:continue
    # Switch branches are mutually exclusive, so they share the same slot.
    if data(rr,rect['node']).get('name')in ['NoMatches','IsGoalkeeperCheck','Outfield','Goalkeeper']:continue
    if data(rr,other['node']).get('name')in ['NoMatches','IsGoalkeeperCheck','Outfield','Goalkeeper']:continue
    overlap=min(rect['x']+rect['width'],other['x']+other['width'])>max(rect['x'],other['x']) and min(rect['y']+rect['height'],other['y']+other['height'])>max(rect['y'],other['y'])
    assert not overlap,('Overlapping sibling rectangles',pid,rect,other)
  for i in captions:
   assert value(i,131105)==dict(unit=1,value=80.0)
   assert value(i,131087)==dict(unit=1,value=48.0)
  doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
  changes[pid]=doc;changes[sid]=sheet
  checks.append(dict(target=tag,page=pid,statistic_block_px=[242,76],column_px=[80,76],caption_px=[80,48],caption_top_px=24,all_pixel_rectangles_inside_parents=True,no_overlapping_sibling_rectangles=True,chart_and_outside_nodes_exact=True,all_serialized_bindings_unchanged=True,rectangles=rectangles))
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
(R/'three-nonhidden-form-fixed-pixels-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
