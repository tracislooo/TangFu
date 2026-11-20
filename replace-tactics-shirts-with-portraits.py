from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('tactics-overview-player-portraits-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
before={p/W:(p/W).read_bytes() for p in [GAME,SKIN]};assert before[GAME/W]==before[SKIN/W]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/W).write_bytes(b)
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name!=W}
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:protected[p]=sha(p.read_bytes())
env=UnityPy.load(before[GAME/W]);objs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in objs.items()};changed={}
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
donor=objs[-4028782843705546248].read_typetree();dr=refs(donor)
audits=[]
for pid,shirtid,veid,remapid,size in [(-8273082868742719783,1025,1018,1002,35),(3127595210179668386,1030,1021,1004,34)]:
 doc=objs[pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 def add(node,sd,parent,name):
  global next_rid,next_id
  a=copy.deepcopy(node);s=copy.deepcopy(sd);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
  a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':s['rid']},m_Classes=[],m_Properties=[])
  s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);next_id+=1
  rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
 shirt=rr[shirtid]['data'];assert shirt['m_FullTypeName']=='FM.UI.FMTacticsShirt'
 parent=shirt['m_Parent']['rid'];siblings=copy.deepcopy(rr[parent]['data']['m_Children']);original_children=copy.deepcopy(shirt['m_Children'])
 frame=add(rr[veid],serial(rr,veid),parent,'TacticsPlayerPortraitFrame');rr[frame]['data']['m_RuleIndex']=shirt['m_RuleIndex']
 override(rr[frame]['data'],[prop(131105,px(size)),prop(131087,px(size)),prop(131084,num(0)),prop(131085,num(0)),prop(131102,en('relative'))])
 rr[parent]['data']['m_Children']=[{'rid':frame} if x['rid']==shirtid else x for x in siblings]
 shirt['m_Parent']={'rid':frame};shirt['m_Children']=[];rr[frame]['data']['m_Children']=[{'rid':shirtid}]
 override(shirt,[prop(458767,num(0)),prop(131102,en('absolute')),prop(131104,px(0)),prop(131089,px(0)),prop(131105,pct(100)),prop(131087,pct(100))])
 mapper=add(rr[remapid],serial(rr,remapid),frame,'TacticsPlayerPortraitBinding')
 md=serial(rr,mapper)['data'];md.update(Mappings=[{'m_serialisedType':0,'from':'person','to':{'m_path':'position.Player'},'type':{'id':0}}],Mappings_UxmlAttributeFlags=1)
 override(rr[mapper]['data'],[prop(131102,en('absolute')),prop(131104,px(0)),prop(131089,px(0)),prop(131105,pct(100)),prop(131087,pct(100))])
 picture=add(dr[1007],serial(dr,1007),mapper,'TacticsPlayerPortrait')
 override(rr[picture]['data'],[prop(131105,pct(100)),prop(131087,pct(100)),prop(131084,num(1)),prop(131085,num(0))])
 # Keep instruction hit targets and swapped-wing markers above the portrait.
 for c in original_children:rr[c['rid']]['data']['m_Parent']={'rid':frame};rr[frame]['data']['m_Children'].append(c)
 doc['m_Usings'].append(copy.deepcopy(next(u for u in donor['m_Usings'] if u['alias']=='PersonPicture')))
 # Every existing serialized binding and event remains byte-for-byte equivalent.
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('existing binding altered',pid,i)
 validate_ui(doc,sheet)
 for i,d in [(pid,doc),(sid,sheet)]:objs[i].save_typetree(d);changed[i]=copy.deepcopy(d)
 (OUT/(doc['m_Name']+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
 audits.append({'template':doc['m_Name'],'shirt_opacity':0,'portrait_binding':'position.Player','portrait_size':size,'frame':frame,'mapper':mapper,'portrait':picture,'shirt':shirtid,'original_bindings_unchanged':True})
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs)
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h,('unrelated object altered',i)
for i,d in changed.items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
(OUT/W).write_bytes(output)
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
report={'installed':False,'runtime_verified':False,'templates':audits,'changed_objects':list(changed),'unrelated_objects_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p in before:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'templates':audits}))

