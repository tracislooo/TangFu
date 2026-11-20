from pathlib import Path
import struct
source=Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig')
exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-','tactics-condition-percent-rings-'),'backup-and-helpers','exec'))
F='ui-tablefactories_assets_all.bundle';V='ui-tableviews_assets_all.bundle';B='ui-backgrounds_assets_common.bundle';CELL=-970000000001000
extraenv={};extraobjs={};extrahashes={};expected={W:{},F:{},V:{}};missing_before=[]
for n in [F,V]:
 for folder in [GAME,SKIN]:
  p=folder/n
  if not p.exists():missing_before.append(p);continue
  before[p]=p.read_bytes();protected.pop(p,None);(OUT/('backup-game' if folder==GAME else 'backup-skin')/n).write_bytes(before[p])
 if SKIN/n in before:assert before[GAME/n]==before[SKIN/n]
 extraenv[n]=UnityPy.load(before[GAME/n]);extraobjs[n]={o.path_id:o for o in extraenv[n].objects};extrahashes[n]={i:sha(o.get_raw_data()) for i,o in extraobjs[n].items()}
bge=UnityPy.load(str(GAME/B));bgo={o.path_id:o for o in bge.objects};textures={o.peek_name():o.path_id for o in bgo.values() if o.type.name=='Texture2D' and o.peek_name().startswith('FM27StatusRingCW')};missing=next(o.path_id for o in bgo.values() if o.type.name=='Texture2D' and o.peek_name()=='FM27StatusRingMissing000')
assert len(textures)==101
fileid=next(i+1 for i,e in enumerate(objs[CELL].assets_file.externals) if e.name.lower()==bge.assets[0].name.lower())
doc=objs[CELL].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[sid].read_typetree()
def sd(i):return serial(rr,i)['data']
leaves=[i for i,a in rr.items() if a.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and sd(i).get('name','').startswith('TacticsConditionPercent')]
assert len(leaves)==52
proto=copy.deepcopy(rr[1006]);protosd=copy.deepcopy(serial(rr,1006));next_rid=max(rr)+1;next_id=max(a.get('data',{}).get('m_Id',0) for a in rr.values())+1
handles={};leafgroups={};ringids={}
def add(parent,name):
 global next_rid,next_id
 a=copy.deepcopy(proto);s=copy.deepcopy(protosd);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':s['rid']},m_Classes=[],m_Properties=[])
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);next_id+=1
 rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
for leaf in leaves:
 text=sd(leaf)['text'];percent=None if text=='--' else int(text[:-1]);parent=rr[leaf]['data']['m_Parent']['rid'];siblings=copy.deepcopy(rr[parent]['data']['m_Children'])
 group=add(parent,'TacticsConditionRingAndPercent'+str(percent));rr[parent]['data']['m_Children']=[{'rid':group} if c['rid']==leaf else c for c in siblings]
 override(rr[group]['data'],[prop(131105,pct(100)),prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('center')),prop(131084,num(1)),prop(131085,num(1)),prop(262150,px(0)),prop(262151,px(0))])
 ring=add(group,'TacticsConditionRing'+str(percent));texture=missing if percent is None else textures[f'FM27StatusRingCW{percent:03}']
 sheet['assets'].append({'m_FileID':fileid,'m_PathID':texture});handle={'m_ValueType':6,'valueIndex':len(sheet['assets'])-1};handles[leaf]=texture;ringids[leaf]=ring
 override(rr[ring]['data'],[prop(131105,px(18)),prop(131087,px(18)),prop(131097,px(18)),prop(131096,px(18)),prop(131095,px(18)),prop(131094,px(18)),prop(131084,num(0)),prop(131085,num(0)),prop(131093,px(4)),prop(458753,handle),prop(262153,en('scale-to-fit'))])
 rr[leaf]['data']['m_Parent']={'rid':group};rr[group]['data']['m_Children'].append({'rid':leaf});leafgroups[leaf]=group
 override(rr[leaf]['data'],[prop(131105,px(32)),prop(131097,px(32)),prop(131095,px(32)),prop(131084,num(0)),prop(131085,num(0)),prop(65546,en('middle-center'))])
 # The number, lookup thresholds and percentage formula stay exactly as installed.
 assert sd(leaf)==serial(old,leaf)['data']
validate_ui(doc,sheet)
for i,a in old.items():
 if a.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  assert sd(i)==serial(old,i)['data'];assert len(rr[i]['data']['m_Children'])==len(a['data']['m_Children'])
for pid,d in [(CELL,doc),(sid,sheet)]:objs[pid].save_typetree(d);expected[W][pid]=copy.deepcopy(d)
metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==CELL);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for texture in handles.values():
 ptr={'m_FileID':fileid,'m_PathID':texture}
 if ptr not in span:span.append(ptr)
entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span);metaobj.save_typetree(meta);expected[W][metaobj.path_id]=meta
# Allow room for an 18px ring, a gap, and a full 100% label.
factory=extraobjs[F][-7014073910555419620];d=factory.read_typetree();oldfactory=copy.deepcopy(d);col=next(c for c in d['m_rowData'] if c['m_id']=='condition');col.update(m_defaultWidth=60.0,m_minimumWidth=60.0);factory.save_typetree(d);expected[F][factory.path_id]=d
assert sum(a!=b for a,b in zip(oldfactory['m_rowData'],d['m_rowData']))==1
views=[]
for o in extraobjs[V].values():
 if o.type.name!='MonoBehaviour' or not o.peek_name().startswith('TacticTeamSelection') or 'InMatch' in o.peek_name():continue
 d=o.read_typetree();oldview=copy.deepcopy(d);hit=False
 for c in d.get('m_tableView',{}).get('m_tableConfig',[]):
  if c['m_columnID']=='condition':c['m_columnMetadata'].update(m_widthOverride=60.0,m_minWidthOverride=60.0);hit=True
 if hit:o.save_typetree(d);expected[V][o.path_id]=d;views.append(d['m_Name'])
assert len(views)==6
# Validate source texture transparency and red/green endpoints.
for percent in [0,50,100]:
 im=bgo[textures[f'FM27StatusRingCW{percent:03}']].read().image.convert('RGBA');assert im.getpixel((0,0))[3]==0
 colors=[(red,green,blue) for red,green,blue,alpha in im.getdata() if alpha>200 and max(red,green,blue)-min(red,green,blue)>60];assert colors
 if percent==0:assert max(c[0]-c[1] for c in colors)>100
 if percent==100:assert max(c[1]-c[0] for c in colors)>100
 if percent in [0,100]:im.save(OUT/f'ring-{percent}.png')
outputs={W:env.file.save(packer='lz4'),**{n:e.file.save(packer='lz4') for n,e in extraenv.items()}}
allobjs={W:objs,**extraobjs};allhashes={W:hashes,**extrahashes}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert check.keys()==allobjs[n].keys()
 for i,h in allhashes[n].items():
  if i not in expected[n]:assert sha(check[i].get_raw_data())==h,(n,i)
 for i,d in expected[n].items():assert check[i].read_typetree()==d,(n,i)
 (OUT/n).write_bytes(b)
report={'installed':False,'runtime_verified':False,'ring_size':18,'condition_column_width':60,'colour':'0% red,50% yellow,100% green','percent_formula_unchanged':'raw5000=>0%,raw10000=>100% (UI50=>0%,UI100=>100%)','leaves_with_rings':len(leaves),'changed_views':views,'background_textures_reused':True,'avatars_and_other_cells_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
for p in missing_before:restore.append("Remove-Item -LiteralPath '"+str(p)+"' -Force -ErrorAction SilentlyContinue")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for n,b in outputs.items():
  for f in [GAME,SKIN]:(f/n).write_bytes(b);assert (f/n).read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 for p in missing_before:
  if p.exists():p.unlink()
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'ring_size':18,'column_width':60,'leaves':len(leaves)}))

