from pathlib import Path
import json,copy,datetime
R=Path(__file__).parent
exec(compile((R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0],'<current-helpers>','exec'))
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={}
 source=oo[-950000000000195].read_typetree();sr=refs(source);ss=oo[source['inlineSheet']['m_PathID']].read_typetree()
 # Original native non-manager portrait branch: dynamic personBind plus resource image.
 sourceids=[1016,1024,1035];allids=set(sourceids)|{sr[i]['data']['m_SerializedData']['rid'] for i in sourceids}
 assert sr[1016]['data']['m_FullTypeName']=='SI.Bindable.BindingVariables'
 assert sr[1035]['data']['m_FullTypeName']=='SI.Bindable.SIImage'
 def remap(v,ids):
  if isinstance(v,dict):
   if set(v)=={'rid'}:return {'rid':ids.get(v['rid'],v['rid'])}
   return {k:remap(x,ids) for k,x in v.items()}
  if isinstance(v,list):return [remap(x,ids) for x in v]
  return v
 for pid,oldid,w,h in [(-1465827634544911600,1024,180,180),(-4246927470610052519,1025,226,180)]:
  o=oo[pid];d=o.read_typetree();old=copy.deepcopy(d);rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
  target=rr[oldid];assert target['type']['class']=='TemplateAsset','Direct portrait already installed'
  parent=rr[target['data']['m_Parent']['rid']];newrid=max(rr)+1;ids={i:newrid+j for j,i in enumerate(sorted(allids))};nextid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;assetids={sr[i]['data']['m_Id']:nextid+j for j,i in enumerate(sourceids)};cache={}
  for i in sorted(allids):
   r=remap(copy.deepcopy(sr[i]),ids);r['rid']=ids[i];a=r.get('data',{})
   for key in ['m_Id','uxmlAssetId']:
    if key in a:a[key]=assetids.get(a[key],a[key])
   ix=a.get('m_RuleIndex',-1)
   if ix>=0:
    if ix not in cache:
     rule=copy.deepcopy(ss['m_Rules'][ix]);rule['m_ComplexSelectors']=[]
     for p in rule['m_Properties']:
      for handle in p['m_Values']:
       if handle['m_ValueType'] in poolmap:
        pool=poolmap[handle['m_ValueType']];val=copy.deepcopy(ss[pool][handle['valueIndex']]);handle['valueIndex']=len(s[pool]);s[pool].append(val)
     cache[ix]=len(s['m_Rules']);s['m_Rules'].append(rule)
    a['m_RuleIndex']=cache[ix]
   rr[r['rid']]=r
  root=rr[ids[1016]];root['data']['m_Parent']={'rid':parent['rid']};parent['data']['m_Children']=[{'rid':root['rid']} if c['rid']==oldid else c for c in parent['data']['m_Children']]
  # Direct, visible image tree; no UseNonLicensedPicture / Person visibility gates.
  for i,name in [(1016,'StaffPortraitResourceBinding'),(1024,'StaffPortraitImageFrame'),(1035,'StaffPortraitImage')]:
   r=rr[ids[i]];sd=rr[r['data']['m_SerializedData']['rid']]['data'];sd.update(name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
   r['data']['m_Classes']=[]
   st.edit(r,[st.p(131105,st.px(w)),st.p(131087,st.px(h)),st.p(131097,st.px(w)),st.p(131096,st.px(h)),st.p(131095,st.px(w)),st.p(131094,st.px(h)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(458767,st.num(1)),st.p(131081,st.en('flex')),st.p(65551,st.en('visible')),st.p(327681,st.num(1),st.num(1)),st.p(262150,st.px(0)),st.p(262151,st.px(0))])
  image=rr[rr[ids[1035]]['data']['m_SerializedData']['rid']]['data'];image.update(tintColor={'r':1.,'g':1.,'b':1.,'a':1.},tintColor_UxmlAttributeFlags=1,ScaleMode=0,ScaleMode_UxmlAttributeFlags=1,scaleMode=0,scaleMode_UxmlAttributeFlags=1)
  assert image['Binding']==sr[sr[1035]['data']['m_SerializedData']['rid']]['data']['Binding']
  variables=rr[root['data']['m_SerializedData']['rid']]['data'];assert variables['ValueVariables']==sr[sr[1016]['data']['m_SerializedData']['rid']]['data']['ValueVariables']
  del rr[target['data']['m_SerializedData']['rid']];del rr[oldid];d['references']['RefIds']=list(rr.values())
  for i,r in refs(old).items():
   if i in [oldid,target['data']['m_SerializedData']['rid']]:continue
   actual=copy.deepcopy(rr[i])
   if i==parent['rid']:actual['data']['m_Children']=r['data']['m_Children']
   assert actual==r,('Unrelated staff data changed',i)
  for ob,data in [(o,d),(so,s)]:ob.save_typetree(data);changed[ob.path_id]=data
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'staff_header_and_actual_hover':True,'direct_native_person_resource_binding_preserved':True,'picture_visibility_gates_removed_for_staff_only':True,'original_staff_identity_contract_attributes_unchanged':True,'changed_objects':list(changed)})
out=R/('staff-direct-native-portrait-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'approach':'Inline native BindingVariables -> image frame -> SIImage in staff header and hover; bypass shared portrait template visibility gates','audits':audits,'all_other_bundles_and_catalogs_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
p=R/'FM27-职员Overview-最新修改要求与更新恢复指南.md';(out/p.name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+'\n\n## 2026-11-03 最新职员头像：直接图片绑定\n\n前两次尺寸／模板修改经用户反馈仍未显示，不能视为有效修复。本次职员主页面头部及实际职员悬浮窗改为内联原生BindingVariables→图片框→SIImage三层，沿用personBind的UniqueId／Regenerated／性别／NewgenAppearanceDescription／日期及原生图片函数输入，避开复用球员模板外层的UseNonLicensedPicture、Person等可见性判断；图像明确白色tint alpha1、opacity1、scale1、ScaleToFit和固定尺寸。主页面226×180、弹窗180×180；姓名、合同、属性及共享头像模板不改。保留缺省头像加载路径。本轮只修改两份职员VTA及样式，其他包和catalog不变。脚本staff-direct-portrait-image.py；记录'+out.name+'/manifest.json。文件读回检查通过；没有启动游戏或桌面控制，运行显示尚待确认。\n','utf8');print(json.dumps(report,ensure_ascii=True))
