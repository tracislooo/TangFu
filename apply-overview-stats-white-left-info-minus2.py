from pathlib import Path
import sys,ast,copy,hashlib,json,datetime,subprocess,time
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if (isinstance(n,ast.FunctionDef) and n.name=='write') or (isinstance(n,ast.ClassDef) and n.name=='Styles')],type_ignores=[]),'helpers','exec'))
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('overview-stats-white-left-info-minus2-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
report={'installed':False,'runtime_verified':False,'targets':[]};files=[]
titles={'PersonHeightTitleText','PlayerReputationTitleText','PlayerPersonalityTitleText','AgentFrameText','MediaDescriptionFrameText','InternationalMediaOpinionFrameText','BiographyOverallCareerStatsTitle','BiographyCareerMilestonesTitle'}
values={'PersonHeightText','PlayerReputationText','PlayerPersonalityText','PersonAgentText','PersonNoAgentText','PersonMediaDescriptionText','PersonInternationalMediaOpinionText','BiographyOverallCareerStats','BiographyCareerMilestones'}
for tag,folder in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 path=folder/W;before=path.read_bytes();e=UnityPy.load(before);obs={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};changed={};audit=[]
 for pid,o in obs.items():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name() or ''
  stats=name in ['OverviewSeasonTwelveStats','OverviewSeasonTwelveStatsCompact','LargePortraitOverviewRightMiddleTwelveSeasonStats']
  left=pid in [-950000000000162,-950000000000156]
  if not (stats or left):continue
  d=o.read_typetree();original=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']};sid=d['inlineSheet']['m_PathID'];s=obs[sid].read_typetree();st=Styles(s);count=0
  for r in rr.values():
   a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});nm=sd.get('name','')
   if a.get('m_FullTypeName')!='SI.Bindable.SIText':continue
   if stats and nm.startswith(('SeasonStatValue_','GoalkeeperStatValue_')):
    st.edit(r,[st.p(65536,st.h(4,dict(r=1.,g=1.,b=1.,a=1.)))]);count+=1
   elif left and nm in titles|values:
    st.edit(r,[st.p(65537,st.px(15 if nm in titles else 16))]);count+=1
  if left:
   # Limit descendant styling to the bottom nation/club rows, including nested native text templates.
   for rid in [6268,6270]:
    a=rr[rid]['data'];a.setdefault('m_Classes',[]).append('tf-left-info-small');ptr={'m_FileID':0,'m_PathID':sid}
    if ptr not in a['m_Stylesheets']:a['m_Stylesheets'].append(ptr)
   ix=len(s['m_Rules']);s['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':11,'m_Selectors':[{'m_Parts':[{'m_Value':'tf-left-info-small','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'SIText','m_Type':1}],'m_PreviousRelationship':2}],'ruleIndex':ix}],'m_Properties':[st.p(65537,st.px(16))],'line':-1})
  assert count==24 if stats else count==17,(pid,name,count)
  # Serialized data contains bindings, content, and control flags; all remain identical.
  for a,b in zip(original['references']['RefIds'],d['references']['RefIds']):
   if 'UxmlSerializedData' in a.get('type',{}).get('class',''):assert a==b
  o.save_typetree(d);obs[sid].save_typetree(s);changed[pid]=d;changed[sid]=s;audit.append({'id':pid,'name':name,'text_nodes':count})
 assert len([x for x in audit if x['id'] in [-950000000000162,-950000000000156]])==2
 output=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(obs)
 for i,h in hashes.items():
  if i not in changed:assert sha(check[i].get_raw_data())==h,(tag,i)
  else:assert check[i].read_typetree()==changed[i],(tag,i)
 for sub,b in [('backup',before),('prepared',output)]:
  dr=OUT/(sub+'-'+tag);dr.mkdir();(dr/W).write_bytes(b)
 files.append({'target':str(path),'before':sha(before),'after':sha(output),'backup':str(OUT/('backup-'+tag)/W),'prepared':str(OUT/('prepared-'+tag)/W)})
 report['targets'].append({'tag':tag,'objects':audit,'unrelated_objects_unchanged':True,'bindings_unchanged':True})
report['files']=files
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
installer='''from pathlib import Path
import json,hashlib,subprocess,time
root=Path(__file__).parent
p=root/'manifest.json'
m=json.loads(p.read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
while subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():time.sleep(10)
try:
 for f in m['files']:assert sha(Path(f['target']).read_bytes())==f['before'],'Baseline changed: '+f['target']
 for f in m['files']:assert sha(Path(f['prepared']).read_bytes())==f['after']
 for f in m['files']:Path(f['target']).write_bytes(Path(f['prepared']).read_bytes())
 for f in m['files']:assert sha(Path(f['target']).read_bytes())==f['after']
 m.update(installed=True,installed_verified=True)
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 (root/'automatic-install-status.txt').write_text('Installed and verified','utf8')
except Exception as ex:
 (root/'automatic-install-status.txt').write_text(str(ex),'utf8')
 raise
'''
(OUT/'install-after-exit.py').write_text(installer,'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for f in files:restore.append("if ((Get-FileHash -LiteralPath '"+f['target']+"' -Algorithm SHA256).Hash.ToLower() -ne '"+f['after']+"') { throw 'Resource changed; merge required' }")
for f in files:restore.append("Copy-Item -LiteralPath '"+f['backup']+"' -Destination '"+f['target']+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
print(OUT)
