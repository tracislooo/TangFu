from pathlib import Path
import json,copy,datetime,importlib.util
R=Path(__file__).parent
exec(compile((R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0],'<current-helpers>','exec'))
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={}
 obj=oo[-4246927470610052519];d=obj.read_typetree();rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();old=copy.deepcopy(s)
 # Use the existing rules so bindings, template IDs and every VTA byte remain unchanged.
 sizes={1016:{131105:226,131087:180,131097:226,131096:180,131095:226,131094:180},1019:{131105:226,131087:180,131097:0,131096:0,131095:226,131094:180},1025:{131105:226,131087:180,131097:0,131096:0,131095:226,131094:180}}
 for rid,props in sizes.items():
  rule=s['m_Rules'][rr[rid]['data']['m_RuleIndex']]
  for key,value in list(props.items())+[(131084,0),(131085,0)]:
   if key in [131084,131085]:s['floats'].append(float(value));h={'m_ValueType':2,'valueIndex':len(s['floats'])-1}
   else:s['dimensions'].append({'unit':1,'value':float(value)});h={'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}
   p=next((p for p in rule['m_Properties'] if p['m_Id']==key),None)
   if p:p['m_Values']=[h]
   else:rule['m_Properties'].append({'m_Id':key,'m_CustomName':'','m_Line':-1,'m_Values':[h]})
 portrait=next(u for u in d['m_Usings'] if u['alias']=='PersonPicture');pd=oo[portrait['asset']['m_PathID']].read_typetree();pr=refs(pd);ps=oo[pd['inlineSheet']['m_PathID']].read_typetree();branches=[]
 for r in pr.values():
  a=r.get('data',{})
  if a.get('m_FullTypeName')!='SI.Bindable.SIImage':continue
  p=next(p for p in ps['m_Rules'][a['m_RuleIndex']]['m_Properties'] if p['m_Id']==262153);assert ps['strings'][p['m_Values'][0]['valueIndex']]=='scale-to-fit';branches.append(r['rid'])
 assert len(branches)==4
 c=cm.Catalog((GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin').read_bytes())
 v=[c.location(i) for i in c.locations(portrait['path']) if c.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert v
 assert all(c.location(x['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W) for x in v)
 so.save_typetree(s);b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i==so.path_id:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(s,sort_keys=True)
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'header':'NonPlayerReportHeader','only_style_changed':so.path_id,'explicit_frame':[226,180],'inner_height_px':180,'all_4_image_sources_and_fallback_bindings_preserved':True,'portrait_catalog_valid':True,'other_objects_byte_identical':len(oo)-1})
out=R/('staff-popup-portrait-height-fix-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'fix':'Replace staff picture frame percent max-height and percentage inner heights with explicit 180px height, disable flex shrink','audits':audits,'all_other_bundles_and_catalogs_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
p=R/'FM27-职员Overview-最新修改要求与更新恢复指南.md';(out/p.name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+'\n\n## 2026-11-03 职员弹窗头像高度修复\n\nNonPlayerReportHeader的PersonPictureFrame（1016）改为明确226×180px，min/max高度均180；PictureTeamRemapper（1019）和PersonPicture实例（1025）改为明确226×180px，取消flex伸缩。解决百分比最大高度及多层100%高度在弹窗头部可能折叠的问题；此处覆盖旧226×226且max-height100%的方案。照片仍等比完整显示，保留当前PersonPicture模板GUID、实际对象及四条图像／回退分支；职员姓名、合同、属性和球员共享头像模块不改。本次仅修改两边各一个职员头部样式对象，其他对象原始字节一致，目录有效；未进行游戏内显示验证。脚本fix-staff-header-portrait-height.py；记录'+out.name+'/manifest.json。\n','utf8');print(json.dumps(report,ensure_ascii=True))
