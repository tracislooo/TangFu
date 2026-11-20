from pathlib import Path
import ast,copy,json,datetime
R=Path(__file__).resolve().parent
src=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8').split('payloads={};changes={}')[0].replace('F:/Steam/steamapps/common/Project Taco','F:/Steam/steamapps/common/Football Manager 27')
exec(compile(src,'<audit>','exec'))
source=ast.parse((R/'unify-lake-blue-controls.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['append_rule','color'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='f32' for t in n.targets)],type_ignores=[]),'<style>','exec'))
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<styles>','exec'))
source=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selectors>','exec'))
import struct
poolmap={2:"floats",3:"dimensions",4:"colors",5:"strings",6:"assets",7:"strings",8:"strings"}

W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,S]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
fill=color('263445',.6);clear=color('263445',0.)
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};expected={}
 for ob in oo.values():
  if ob.type.name!='MonoBehaviour':continue
  n=ob.peek_name() or '';header=n=='PlayerReportHeader'
  bottom=any(n.startswith(k) for k in ['PlayerHappinessTile_','PlayerFitnessTile_','PlayerSeasonStatsTile_','CareerStatsTile_','TrainingOverviewTile_','TacticalEffectivenessTile_']) or n.startswith('Overview1080_Compact_') and any(k in n for k in ['CareerStats','PlayerSeasonStats','PlayerTrainingOverview'])
  if not header and not bottom:continue
  d=ob.read_typetree()
  if 'inlineSheet' not in d:continue
  rr={r['rid']:r for r in d['references']['RefIds']};so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree();st=Styles(sh);count=0
  if header:
   for r in rr.values():
    a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
    iscell=name.startswith('tile-states-') or name.startswith('HeaderStatus_')
    if not iscell and name!='FrameActions':continue
    if a.get('m_FullTypeName') not in ['UnityEngine.UIElements.VisualElement','SI.Bindable.BindingRemapper']:continue
    st.edit(r,[st.p(458752,st.h(4,clear if name=='FrameActions' else fill))]);count+=1
   assert count>=11,count
  else:
   for r in rr.values():
    a=r.get('data',{})
    if a.get('m_Parent',{}).get('rid')==1000 and 'm_Classes' in a:
     if 'fm27-player-bottom-surface' not in a['m_Classes']:a['m_Classes'].append('fm27-player-bottom-surface')
     count+=1
  if count:
   ob.save_typetree(d);expected[ob.path_id]=d
   if header:so.save_typetree(sh);expected[so.path_id]=sh
   changes.append({'folder':str(folder),'template':n,'nodes':count})
 data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/W]).objects};assert set(check)==set(orig)
 for pid,o in check.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert o.get_raw_data()==orig[pid].get_raw_data()
 payloads[folder/W]=data
 e=UnityPy.load(before[folder/S]);oo={o.path_id:o for o in e.objects};ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');sh=ob.read_typetree()
 append_rule(sh,['.fm27-player-bottom-surface .layout-tile-interaction-button-background','.fm27-player-bottom-surface .layout-tile-interaction-button-background:hover','.fm27-player-bottom-surface .layout-tile-interaction-button-background:active'],[(458752,fill)])
 ob.save_typetree(sh);data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/S]).objects}
 for pid,o in check.items():
  if pid==ob.path_id:assert o.read_typetree()==sh
  else:assert o.get_raw_data()==orig[pid].get_raw_data()
 payloads[folder/S]=data
out=R/('player-touchbar-bottom-greyblue60-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)
