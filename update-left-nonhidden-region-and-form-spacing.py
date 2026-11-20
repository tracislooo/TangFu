"""Use the middle nonhidden information region and separate form bars from statistics."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, zlib
R=Path(__file__).resolve().parent
# Load only reusable definitions, without running a historical installer.
s=(R/'sync-old-left-portrait-nonhidden.py').read_text('utf8')
exec(s[:s.index("W='ui-")])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
NEW,MIDDLE,OLD=-941100000001100,-930000000001003,-940000000012000
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('left-nonhidden-region-form-spacing-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
def add_tx(tag,target,output,before):
 src=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name
 src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True)
 src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
def normalized(doc,sheet,node):
 temp=copy.deepcopy(doc);temp['m_VisualTree']={'rid':node};return canonical(temp,sheet)
def fix_form(doc,sheet):
 rr=refs(doc);st=Styles(sheet);form=named(doc,'MiddleNonHiddenRecentForm')
 title=named(doc,'MiddleRecentFormTitle')
 content=next(x['rid']for x in rr[form]['data']['m_Children']if x['rid']!=title)
 frame=rr[content]['data']['m_Children'][0]['rid']
 children=[c['rid']for c in rr[frame]['data']['m_Children']]
 chart=next(i for i in children if rr[i]['data'].get('m_FullTypeName')=='SI.Bindable.StreamedObjectList')
 stats=next(i for i in children if i!=chart)
 before=copy.deepcopy(rr)
 # Give the heading its own row and the remaining content the available height.
 st.edit(rr[content],[st.p(131102,st.en('relative')),st.p(131087,st.px(0)),st.p(131082,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(131096,st.px(0))])
 st.edit(rr[frame],[st.p(131102,st.en('relative')),st.p(131087,st.pct(100)),st.p(131105,st.pct(100)),st.p(131083,st.en('column'))])
 def area(i,top,height):
  st.edit(rr[i],[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.pct(top)),st.p(131105,st.pct(100)),st.p(131087,st.pct(height)),st.p(131096,st.px(0)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131082,{'m_ValueType':1,'valueIndex':2}),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131089+1,st.px(0)),st.p(131091,st.px(0)),st.p(131092,st.px(0)),st.p(131093,st.px(0)),st.p(131101,st.px(0)),st.p(131098,st.px(0)),st.p(131099,st.px(0)),st.p(131100,st.px(0))])
 # Five percent clearance between graph and the independent statistics region.
 area(chart,0,55);area(stats,60,40)
 st.edit(rr[stats],[st.p(131088,st.en('flex-start')),st.p(131083,st.en('column'))])
 rows=[];texts=[]
 for i in owned_refs(rr,stats):
  x=rr[i].get('data',{})
  if 'm_FullTypeName'not in x:continue
  sd=data(rr,i);name=sd.get('name','')
  if name in ['NoMatches','Outfield','Goalkeeper']:
   rows.append(i)
   st.edit(rr[i],[st.p(131102,st.en('relative')),st.p(131087,st.pct(100)),st.p(131096,st.px(0)),st.p(131085,st.num(0)),st.p(131083,st.en('row')),st.p(131090,st.px(0))])
  elif name in ['HasMatches','IsGoalkeeperCheck']:
   st.edit(rr[i],[st.p(131087,st.pct(100)),st.p(131105,st.pct(100)),st.p(131096,st.px(0))])
  elif name=='Frame':
   st.edit(rr[i],[st.p(131083,st.en('column')),st.p(131088,st.en('flex-start')),st.p(131073,st.en('stretch')),st.p(131096,st.px(0))])
  elif x.get('m_FullTypeName')=='SI.Bindable.SIText':
   texts.append(i)
   st.edit(rr[i],[st.p(131102,st.en('relative')),st.p(131104,st.px(0)),st.p(131093,st.px(4)),st.p(131085,st.num(0)),st.p(65552,st.en('normal')),st.p(65546,st.en('upper-center'))])
 assert len(rows)==3 and len(texts)==7
 # Layout edits must leave every serialized value, function and event unchanged.
 for i,old in before.items():
  a=copy.deepcopy(rr[i]);b=copy.deepcopy(old)
  a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None)
  assert a==b,('Data changed while adjusting form spacing',i)
 return dict(chart_top_percent=0,chart_height_percent=55,statistics_top_percent=60,statistics_height_percent=40,branch_count=len(rows),caption_count=len(texts),all_data_and_bindings_unchanged=True)
for tag,root in roots:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 donor=oo[MIDDLE].read_typetree();ds=oo[donor['inlineSheet']['m_PathID']].read_typetree()
 doc=oo[NEW].read_typetree();sheet=oo[doc['inlineSheet']['m_PathID']].read_typetree();original=copy.deepcopy(doc)
 existing={u['alias']:u for u in doc['m_Usings']}
 renames={u['alias']:'LeftNonHidden_'+u['alias']for u in donor['m_Usings']if u['alias']in existing and u!=existing[u['alias']]}
 def rename(v):
  if isinstance(v,list):return [rename(x)for x in v]
  if isinstance(v,dict):return {k:rename(x)for k,x in v.items()}
  return renames.get(v,v)if isinstance(v,str)else v
 donor=rename(donor)
 newroot=named(donor,'InfoBlockFrame');detail=graft(doc,sheet,donor,ds,named(doc,'InfoBlockFrame'),newroot)
 for i,v in refs(original).items():
  if i not in detail['removed']and i!=detail['parent']:assert refs(doc)[i]==v,('Unrelated page region changed',i)
 assert normalized(doc,sheet,detail['root'])==normalized(donor,ds,newroot)
 changes={}
 for pid in [NEW,MIDDLE,OLD]:
  if pid==NEW:d,sh=doc,sheet
  else:
   d=oo[pid].read_typetree();sh=oo[d['inlineSheet']['m_PathID']].read_typetree()
  layout=fix_form(d,sh);graph(d);validate_ui(d,sh)
  d['m_ContentHash']=zlib.crc32(json.dumps([d,sh],ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
  changes[pid]=d;changes[d['inlineSheet']['m_PathID']]=sh
  checks.append(dict(target=tag,page=pid,**layout))
 ab=next(o for o in oo.values()if o.type.name=='AssetBundle');meta=ab.read_typetree()
 def entry(pid):return next((k,e)for k,e in meta['m_Container']if e['asset']=={'m_FileID':0,'m_PathID':pid})
 key,en=entry(NEW);dk,de=entry(MIDDLE)
 span=copy.deepcopy(meta['m_PreloadTable'][en['preloadIndex']:en['preloadIndex']+en['preloadSize']])
 for ptr in meta['m_PreloadTable'][de['preloadIndex']:de['preloadIndex']+de['preloadSize']]:
  p=copy.deepcopy(ptr)
  if p['m_FileID']==0:p['m_PathID']={MIDDLE:NEW,donor['inlineSheet']['m_PathID']:doc['inlineSheet']['m_PathID']}.get(p['m_PathID'],p['m_PathID'])
  if p not in span:span.append(p)
 assert not any(p['m_PathID']in reserved for p in span)
 en.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span);changes[ab.path_id]=meta
 cp=(root.parent if tag=='game'else root)/'catalog.bin';cb=cp.read_bytes();cat=cm.Catalog(cb)
 cl=next(i for i in cat.locations(key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 dl=next(i for i in cat.locations(dk)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 deps=list(dict.fromkeys(cat.location(cl)['dependencies']+cat.location(dl)['dependencies']))
 assert cat.location(deps[0])['internal'].endswith(W)and cl in cat.locations('GameWorldVisualTreeAssetPreload')
 if deps!=cat.location(cl)['dependencies']:
  raw=b''.join(struct.pack('<I',i)for i in deps);off=cat.append(raw,True);struct.pack_into('<2I',cat.data,cl+12,off,zlib.crc32(raw))
 co=bytes(cat.data);hp=cp.with_name('catalog.hash')
 if co!=cb:add_tx(tag,cp,co,cb);add_tx(tag,hp,hashlib.md5(co).hexdigest().encode('ascii'),hp.read_bytes())
 else:protected[str(cp)]=sha(cb);protected[str(hp)]=sha(hp.read_bytes())
 for i,v in changes.items():oo[i].save_typetree(v)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==oo.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
 for i,v in changes.items():assert check[i].read_typetree()==v,('Roundtrip mismatch',i)
 add_tx(tag,root/W,output,before)
 checks.append(dict(target=tag,new_region_matches_middle_except_form_layout=True,outside_requested_region_unchanged=True,other_objects_byte_identical=True,catalog_preload_dependencies_verified=True))
 print('Verified '+tag,flush=True)
for row in tx:assert sha(Path(row['target']).read_bytes())==row['before']
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
manifest=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for n,v in [('manifest.json',manifest),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'left-nonhidden-region-form-spacing-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
