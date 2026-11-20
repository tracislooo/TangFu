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

W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';B='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,B]};protected={p:h for p,h in protected.items() if Path(p) not in before};payloads={};changes=[]
fill=color('263445',.6);clear=color('263445',0.)
for folder in [GAME,SKIN]:
 for bn in [B,W]:
  e=UnityPy.load(before[folder/bn]);oo={o.path_id:o for o in e.objects};expected={}
  for ob in oo.values():
   if ob.type.name!='MonoBehaviour':continue
   name=ob.peek_name() or '';d=ob.read_typetree()
   if 'inlineSheet' not in d:continue
   framescope=name.startswith(('FigmaBase','OutsideMatchSquare_FigmaBase')) or name in ['FigmaFullscreenBlockTemplate','RecruitmentScreen','ClubScreen','NationalPoolScreen','NationScreen']
   tilescope=name.startswith('tile-figma-') and 'fixture-background' not in name or name in ['NewsTileStatic_4x4','NewsTileStatic_8x4','GenericNoInfoTile']
   if not framescope and not tilescope:continue
   rr={r['rid']:r for r in d['references']['RefIds']};so=oo[d['inlineSheet']['m_PathID']];sh=so.read_typetree();st=Styles(sh);edits=[]
   for r in rr.values():
    a=r.get('data',{});sdid=a.get('m_SerializedData',{}).get('rid');sd=rr.get(sdid,{}).get('data',{})
    if framescope and sd.get('name')=='Card-frame' and a.get('m_FullTypeName')=='SI.Bindable.SIImage':
     donor=next(z for z in rr.values() if z.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');new=copy.deepcopy(rr[donor['data']['m_SerializedData']['rid']]);oldsd=copy.deepcopy(rr[sdid]);new['rid']=sdid
     for k in new['data']:
      if k in oldsd['data']:new['data'][k]=copy.deepcopy(oldsd['data'][k])
     new['data']['uxmlAssetId']=a['m_Id'];rr[sdid].clear();rr[sdid].update(new);a['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
     st.edit(r,[st.p(458753,st.h(7,'none')),st.p(458752,st.h(4,clear))]);edits.append({'node':'Card-frame','background_image_removed':True,'container_preserved':True})
    if tilescope and 'layout-tile-interaction-button-background' in a.get('m_Classes',[]):
     st.edit(r,[st.p(458752,st.h(4,fill))]);edits.append({'node':sd.get('name'),'background':'#263445','alpha':.6})
   if edits:
    for obj,t in [(ob,d),(so,sh)]:obj.save_typetree(t);expected[obj.path_id]=t
    changes.append({'folder':str(folder),'bundle':bn,'template':name,'edits':edits})
  assert expected,(folder,bn)
  data=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(data).objects};orig={o.path_id:o for o in UnityPy.load(before[folder/bn]).objects};assert set(check)==set(orig)
  for pid,o in check.items():
   if pid in expected:assert o.read_typetree()==expected[pid]
   else:assert o.get_raw_data()==orig[pid].get_raw_data()
  # Player shell, menus, child trees and all asset registrations retain their existing bytes unless explicitly listed above.
  payloads[folder/bn]=data
out=R/('modules-greyblue60-remove-page-image-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx={'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,b in payloads.items():
 tag='game' if p.parent==GAME else 'skin';dst=out/tag/p.name;dst.parent.mkdir(exist_ok=True);dst.write_bytes(b);bak=out/('backup-'+tag)/p.name;bak.parent.mkdir(exist_ok=True);bak.write_bytes(before[p]);tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
print(out)
