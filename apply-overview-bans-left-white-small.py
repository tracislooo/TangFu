from pathlib import Path
import ast,sys,copy,json,datetime,hashlib,struct
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if (isinstance(n,ast.FunctionDef) and n.name=='write') or (isinstance(n,ast.ClassDef) and n.name=='Styles')],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
sha=lambda b:hashlib.sha256(b).hexdigest();loc=json.loads((R/'current-game-location.json').read_text('utf8'));W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/('overview-bans-scroll-left-white-small-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();files=[];audits=[]
values={'PersonHeightText','PlayerReputationText','PlayerPersonalityText','PersonAgentText','PersonNoAgentText','PersonMediaDescriptionText','PersonInternationalMediaOpinionText','BiographyOverallCareerStats','BiographyCareerMilestones'}
for tag,folder in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 path=folder/W;before=path.read_bytes();e=UnityPy.load(before);obs={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};changed={};audit=[]
 for pid,o in obs.items():
  if o.type.name!='MonoBehaviour':continue
  nm=o.peek_name() or '';bans=pid in [-930000000001001,-950000000000187,-941100000001000];font=pid==-941100000001010;stats=nm=='ThirdOverviewNativeLeagueSeasonStats'
  if not (bans or font or stats):continue
  d=o.read_typetree();old=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']};sid=d['inlineSheet']['m_PathID'];s=obs[sid].read_typetree();st=Styles(s);count=0
  if bans:
   sd=rr[rr[6228]['data']['m_SerializedData']['rid']]['data'];assert rr[6228]['data']['m_FullTypeName']=='SI.UI.SIScrollView'
   for k,v in [('verticalScrollerVisibility',1),('horizontalScrollerVisibility',2),('mode',0)]:sd[k]=v;sd[k+'_UxmlAttributeFlags']=1
   st.edit(rr[6228],[st.p(131087,st.px(0)),st.p(131096,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(458768,st.en('hidden'))])
   st.edit(rr[1035],[st.p(131096,st.px(240)),st.p(131085,st.num(0))]);count=1
  if stats or font:
   for r in rr.values():
    a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
    if a.get('m_FullTypeName')!='SI.Bindable.SIText':continue
    if stats and name.startswith(('SeasonStatValue_','GoalkeeperStatValue_')):st.edit(r,[st.p(65536,st.h(4,dict(r=1.,g=1.,b=1.,a=1.)))]);count+=1
    if font and name in values:st.edit(r,[st.p(65537,st.px(12))]);count+=1
  if font:
   # Nation and club include native nested text templates.
   a=rr[1295]['data'];a.setdefault('m_Classes',[]).append('tf-left-hidden-identity-small');a['m_Stylesheets'].append({'m_FileID':0,'m_PathID':sid})
   ix=len(s['m_Rules']);s['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':11,'m_Selectors':[{'m_Parts':[{'m_Value':'tf-left-hidden-identity-small','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'SIText','m_Type':1}],'m_PreviousRelationship':2}],'ruleIndex':ix}],'m_Properties':[st.p(65537,st.px(12))],'line':-1})
   assert count==9
  if stats:assert count==24
  for ar,br in zip(old['references']['RefIds'],d['references']['RefIds']):
   if 'UxmlSerializedData' in ar.get('type',{}).get('class','') and not (bans and ar['rid']==rr[6228]['data']['m_SerializedData']['rid']):assert ar==br
  o.save_typetree(d);obs[sid].save_typetree(s);changed[pid]=d;changed[sid]=s;audit.append(dict(pid=pid,name=nm,changed_text=count))
 assert any(x['pid']==-941100000001010 for x in audit)
 out=e.file.save(packer='lz4');check={x.path_id:x for x in UnityPy.load(out).objects};assert set(check)==set(obs)
 for i,h in hashes.items():
  if i not in changed:assert sha(check[i].get_raw_data())==h
  else:assert check[i].read_typetree()==changed[i]
 for sub,b in [('backup',before),('prepared',out)]:
  dr=OUT/(sub+'-'+tag);dr.mkdir();(dr/W).write_bytes(b)
 files.append(dict(target=str(path),before=sha(before),after=sha(out),backup=str(OUT/('backup-'+tag)/W),prepared=str(OUT/('prepared-'+tag)/W)));audits.append(dict(target=tag,objects=audit,unrelated_objects_unchanged=True))
report=dict(installed=False,runtime_verified=False,files=files,audits=audits)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'install-after-exit.py').write_bytes((R/'overview-left-info-correct-minus2-20261111-001315/install-after-exit.py').read_bytes())
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit game first' }"]
for f in files:restore.append("if ((Get-FileHash -LiteralPath '"+f['target']+"' -Algorithm SHA256).Hash.ToLower() -ne '"+f['after']+"') { throw 'Resources changed; merge required' }")
for f in files:restore.append("Copy-Item -LiteralPath '"+f['backup']+"' -Destination '"+f['target']+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(OUT)

