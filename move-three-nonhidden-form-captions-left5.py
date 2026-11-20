"""Move only recent-form statistic captions five pixels left."""
from pathlib import Path
import ast, copy, datetime, hashlib, json, struct, sys, zlib
R=Path(__file__).resolve().parent
s=(R/'sync-old-left-portrait-nonhidden.py').read_text('utf8')
exec(s[:s.index("W='ui-")])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PAGES=[-941100000001100,-930000000001003,-940000000012000]
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('three-nonhidden-form-caption-left5-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
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
  changed=set();offsets=[]
  for i in owned_refs(rr,form):
   x=rr[i].get('data',{})
   if x.get('m_FullTypeName')!='SI.Bindable.SIText' or data(rr,i).get('name')=='MiddleRecentFormTitle':continue
   rule=sheet['m_Rules'][x['m_RuleIndex']]
   prop=next(p for p in rule['m_Properties']if p['m_Id']==131089)
   handle,=prop['m_Values'];assert handle['m_ValueType']==3
   dim=sheet['dimensions'][handle['valueIndex']];assert dim['unit']==1
   old=dim['value'];st.edit(rr[i],[st.p(131089,st.px(old-5))]);changed.add(i)
   offsets.append(dict(node=i,before_px=old,after_px=old-5))
  assert len(changed)==7
  graph(doc);validate_ui(doc,sheet)
  for i,old in original.items():
   if i not in changed:assert rr[i]==old,('Unrequested node changed',pid,i)
   a=copy.deepcopy(rr[i]);b=copy.deepcopy(old)
   a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None)
   assert a==b,('Data or bindings changed',pid,i)
  doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
  changes[pid]=doc;changes[sid]=sheet
  checks.append(dict(target=tag,page=pid,caption_left_shift_px=5,offsets=offsets,all_other_nodes_exact=True,all_serialized_bindings_unchanged=True))
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
(R/'three-nonhidden-form-caption-left5-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
