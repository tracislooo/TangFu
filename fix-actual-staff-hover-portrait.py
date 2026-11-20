from pathlib import Path
import json,copy,datetime,importlib.util
R=Path(__file__).parent
exec(compile((R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0],'<current-helpers>','exec'))
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};o=oo[-1465827634544911600];d=o.read_typetree();old=copy.deepcopy(d);rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
 # The hover is independent from NonPlayerReportHeader: patch its real template instance.
 header=oo[-4246927470610052519].read_typetree();source=next(u for u in header['m_Usings'] if u['alias']=='PersonPicture');portrait=oo[source['asset']['m_PathID']].read_typetree();assert portrait['m_Name']=='ReportMiddleSquarePersonPicture'
 using=next(u for u in d['m_Usings'] if u['alias']=='PersonPicture');using.update(copy.deepcopy(source));using['alias']='PersonPicture'
 assert rr[1024]['data']['m_TemplateAlias']=='PersonPicture'
 rr[1024]['data']['m_Classes']=[]
 st.edit(rr[1024],[st.p(k,st.px(v)) for k,v in [(131105,180),(131087,180),(131097,180),(131096,180),(131095,180),(131094,180)]]+[st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(262150,st.px(0)),st.p(262151,st.px(0)),st.p(65551,st.en('visible')),st.p(458768,st.en('visible'))])
 # Preserve the native hover person remapping, contract data, role selector and attributes.
 for rid,record in refs(old).items():
  v=copy.deepcopy(rr[rid])
  if rid==1024:
   for key in ['m_Classes','m_RuleIndex']:v['data'][key]=record['data'][key]
  assert v==record,('Unexpected hover binding change',rid)
 pr=refs(portrait);ps=oo[portrait['inlineSheet']['m_PathID']].read_typetree();n=0
 for r in pr.values():
  a=r.get('data',{})
  if a.get('m_FullTypeName')=='SI.Bindable.SIImage':
   prop=next(p for p in ps['m_Rules'][a['m_RuleIndex']]['m_Properties'] if p['m_Id']==262153);assert ps['strings'][prop['m_Values'][0]['valueIndex']]=='scale-to-fit';n+=1
 assert n==4
 c=cm.Catalog((GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin').read_bytes());locations=[c.location(i) for i in c.locations(source['path']) if c.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert locations
 assert all(c.location(v['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W) for v in locations)
 changed={o.path_id:d,so.path_id:s}
 for ob,data in [(o,d),(so,s)]:ob.save_typetree(data)
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,ob in check.items():
  if i in changed:assert json.dumps(ob.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(ob.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'actual_hover':d['m_Name'],'portrait_instance':1024,'portrait_guid':source['path'],'portrait_object':source['asset']['m_PathID'],'size':[180,180],'native_hover_context_and_attributes_preserved':True,'other_objects_unchanged':len(oo)-2})
out=R/('actual-staff-hover-portrait-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'previous_patch_targeted_main_header_instead_of_hover':True,'audits':audits,'player_popups_shared_portraits_and_other_bundles_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
p=R/'FM27-职员Overview-最新修改要求与更新恢复指南.md';(out/p.name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+'\n\n## 2026-11-03 实际职员悬浮窗入口修复\n\n职员悬浮窗是独立NonPlayerReportPreviewTooltip（-1465827634544911600，样式-8026882932926063856），使用独立的PersonPicture实例1024；前次NonPlayerReportHeader高度修改针对主页面，不能代表弹窗已修复。本次将实际悬浮窗PersonPicture导入改为现有ReportMiddleSquarePersonPicture（沿用职员头部当前GUID及实际W对象），去掉旧thumbnails-alt-person-picture-player-report缩略图类，实例固定180×180，禁用flex伸缩、保留溢出可见。保留原生person/contract映射、职能切换及属性区，只改悬浮窗VTA与样式；共享头像组件及球员弹窗不改。四条等比图像分支和目录登记检查通过；运行显示尚未验证。脚本fix-actual-staff-hover-portrait.py；记录'+out.name+'/manifest.json。更新恢复必须分别核对职员主页面头部与实际职员悬浮窗。\n','utf8');print(json.dumps(report,ensure_ascii=True))
