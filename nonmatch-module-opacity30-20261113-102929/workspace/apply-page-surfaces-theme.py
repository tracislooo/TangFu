from pathlib import Path
import ast,copy,json,datetime
import sys
if '--repair-light' in sys.argv:
 import runpy
 runpy.run_path(str(Path(__file__).resolve().with_name('fix-light-theme-readability.py')),run_name='__main__')
 raise SystemExit(0)
global_theme_index = Path(__file__).resolve().with_name('current-ui-surface-theme.json')
global_theme_active = global_theme_index.exists() and json.loads(global_theme_index.read_text('utf8')).get('global_light_theme', {}).get('installed', False)
if '--light-all' in sys.argv or (global_theme_active and len(sys.argv) == 1):
 import runpy
 runpy.run_path(str(Path(__file__).resolve().with_name('build-global-light-theme.py')),run_name='__main__')
 raise SystemExit(0)
if '--light-trial' in sys.argv:
 import runpy
 runpy.run_path(str(Path(__file__).resolve().with_name('build-light-ui-trial.py')),run_name='__main__')
 raise SystemExit(0)
if '--nonmatch-modules' in sys.argv or (len(sys.argv) == 1 and global_theme_index.exists() and json.loads(global_theme_index.read_text('utf8')).get('nonmatch_module_backgrounds', {}).get('installed', False)):
 import runpy
 runpy.run_path(str(Path(__file__).resolve().with_name('apply-nonmatch-module-opacity.py')),run_name='__main__')
 raise SystemExit(0)
R=Path(__file__).resolve().parent
src=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8').split('payloads={};changes={}')[0].replace('F:/Steam/steamapps/common/Project Taco','F:/Steam/steamapps/common/Football Manager 27')
exec(compile(src,'<audit>','exec'))
source=ast.parse((R/'unify-lake-blue-controls.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['append_rule','color'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='f32' for t in n.targets)],type_ignores=[]),'<style>','exec'))
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<styles>','exec'))
source=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selectors>','exec'))
import struct
poolmap={2:"floats",3:"dimensions",4:"colors",5:"strings",6:"assets",7:"strings",8:"strings"}


W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';B='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';C='ui-styles_assets_common.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,B,S,C]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[];fill=color('263445',1.)
def same(c):return isinstance(c,dict) and all(abs(c[k]-fill[k])<1e-6 for k in ['r','g','b','a'])
for folder in [GAME,SKIN]:
 for bn in [B,W,S,C]:
  e=UnityPy.load(before[folder/bn]);oo={o.path_id:o for o in e.objects};expected={}
  for ob in oo.values():
   if ob.type.name!='MonoBehaviour':continue
   name=ob.peek_name() or '';d=ob.read_typetree()
   if bn in [S,C]:
    if 'm_Rules' not in d:continue
    count=0
    for rule in d['m_Rules']:
     for p in rule['m_Properties']:
      if p['m_Id']!=458752 and p.get('m_CustomName','') not in {'--layout-ui-tiles-dark-background','--layout-modules-tiles-background','--layout-ui-cards-light-background','--layout-ui-cards-dark-background','--cards-background','--layout-ui-tiles-light-background','--layout-modules-block-surface','--layout-surfaces-cards-surface','--layout-modules-tiles-interaction-surface-default','--layout-modules-tiles-interaction-surface-hover','--layout-modules-tiles-interaction-surface-pressed'}:continue
      hs=p['m_Values']
      if len(hs)!=1 or hs[0]['m_ValueType']!=4:continue
      c=d['colors'][hs[0]['valueIndex']]
      if all(abs(c[k]-fill[k])<1e-6 for k in ['r','g','b']) and abs(c['a']-.6)<1e-5:
       p['m_Values']=[Styles(d).h(4,fill)];count+=1
    if count:ob.save_typetree(d);expected[ob.path_id]=d;changes.append({'target':str(folder/bn),'sheet':name,'backgrounds_to_opaque':count})
    continue
   if 'inlineSheet' not in d:continue
   framescope=name.startswith(('FigmaBase','OutsideMatchSquare_FigmaBase')) or name in ['FigmaFullscreenBlockTemplate','RecruitmentScreen','ClubScreen','NationalPoolScreen','NationScreen']
   tilescope=name.startswith('tile-figma-') and 'fixture-background' not in name or name in ['NewsTileStatic_4x4','NewsTileStatic_8x4','GenericNoInfoTile']
   if not framescope and not tilescope:continue
   rr={r['rid']:r for r in d['references']['RefIds']};so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree();st=Styles(sh);edits=[]
   for r in rr.values():
    a=r.get('data',{});sdid=a.get('m_SerializedData',{}).get('rid');sd=rr.get(sdid,{}).get('data',{});frame=framescope and sd.get('name')=='Card-frame';tile=tilescope and 'layout-tile-interaction-button-background' in a.get('m_Classes',[])
    if not frame and not tile:continue
    i=a.get('m_RuleIndex',-1);bg=next((p for p in sh['m_Rules'][i]['m_Properties'] if p['m_Id']==458752),None) if i>=0 else None
    if bg and len(bg['m_Values'])==1 and bg['m_Values'][0]['m_ValueType']==4 and same(sh['colors'][bg['m_Values'][0]['valueIndex']]) and (not frame or a.get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement'):continue
    if frame and a.get('m_FullTypeName')=='SI.Bindable.SIImage':
     donor=next(z for z in rr.values() if z.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');new=copy.deepcopy(rr[donor['data']['m_SerializedData']['rid']]);oldsd=copy.deepcopy(rr[sdid]);new['rid']=sdid
     for k in new['data']:
      if k in oldsd['data']:new['data'][k]=copy.deepcopy(oldsd['data'][k])
     new['data']['uxmlAssetId']=a['m_Id'];rr[sdid].clear();rr[sdid].update(new);a['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
    props=[st.p(458752,st.h(4,fill))]
    if frame:props.append(st.p(458753,st.h(7,'none')))
    st.edit(r,props);edits.append({'node':sd.get('name'),'background':'#263445','alpha':1.,'image_removed':frame})
   if edits:
    for obj,t in [(ob,d),(so,sh)]:obj.save_typetree(t);expected[obj.path_id]=t
    changes.append({'target':str(folder/bn),'template':name,'edits':edits})
  if not expected:continue
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/bn]).objects};assert set(check)==set(orig)
  for pid,o in check.items():
   if pid in expected:assert o.read_typetree()==expected[pid]
   else:assert o.get_raw_data()==orig[pid].get_raw_data()
  payloads[folder/bn]=data
for p,b in before.items():assert p.read_bytes()==b,p
for p,b in before.items():
 if p not in payloads:protected[str(p)]=sha(b)
before={p:b for p,b in before.items() if p in payloads}
out=R/('ui-surfaces-greyblue-opaque-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)
