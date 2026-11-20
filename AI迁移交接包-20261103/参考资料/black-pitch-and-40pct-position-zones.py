from pathlib import Path
import json,copy,datetime
R=Path(__file__).parent
# Reuse the established read/backup checks and serialization helpers, not its installer.
source=(R/'soften-popup-pitch-colors.py').read_text('utf8')
exec(compile(source.split('expected={}')[0],'<bundle-and-style-helpers>','exec'))
expected={};edits=[];geometry=[]
black={'r':0.,'g':0.,'b':0.,'a':1.}
line={'r':f32(.60),'g':f32(.64),'b':f32(.68),'a':f32(.65)}
# Both copies keep their numbers, borders, positioning and native click events byte-identical.
for pid in [-940000000018000,-960000000003040]:
 d=obs[pid].read_typetree();rr=refs(d);so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();old=copy.deepcopy(s);changes=[]
 for r in rr.values():
  a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if not sd.get('name','').startswith('PositionZoneColourFill_'):continue
  p=next(p for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties'] if p['m_Id']==458767)
  h=p['m_Values'][0];assert h['m_ValueType']==2
  idx=h['valueIndex'];v=s['floats'][idx];assert abs(v-.266)<.0001,(pid,sd['name'],v)
  s['floats'][idx]=f32(.4);changes.append({'node':sd['name'],'index':idx,'before':v,'after':.4})
 assert len(changes)==14 and len({c['index'] for c in changes})==14
 wanted=copy.deepcopy(old)
 for c in changes:wanted['floats'][c['index']]=f32(.4)
 assert wanted==s
 so.save_typetree(s);expected[so.path_id]=s;edits.append({'template':d['m_Name'],'fill_count':14,'opacity':.4})

# Draw the field with UI Toolkit borders over black. This keeps the field truly black
# instead of blending residual green from the native raster. No new texture or GUID.
proto=refs(obs[-960000000003040].read_typetree())
proto_node=next(r for r in proto.values() if r.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement')
proto_sd=proto[proto_node['data']['m_SerializedData']['rid']]
for pid in [-940000000005000,-940000000008000,-940000000010020,-960000000003030]:
 obj=obs[pid];d=obj.read_typetree();old=copy.deepcopy(d);rr=refs(d)
 so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
 image=rr[1022];sd=rr[image['data']['m_SerializedData']['rid']]['data']
 assert image['data']['m_FullTypeName']=='SI.Bindable.SIImage' and not image['data']['m_Children']
 assert not any(r.get('data',{}).get('name','').startswith('BlackPitchLine_') for r in rr.values())
 sd['tintColor']={'r':1.,'g':1.,'b':1.,'a':0.};sd['tintColor_UxmlAttributeFlags']=1
 st.edit(image,[st.p(458752,st.h(4,black)),st.p(458767,st.num(1))])
 # Remove the previous blue frame behind the popup image; the image owns the field bounds.
 if pid==-960000000003030:st.edit(rr[2014],[st.p(458752,st.h(4,black))])
 nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 def add(name,x,y,w,h,circle=False):
  global nr,ni
  n=copy.deepcopy(proto_node);a=copy.deepcopy(proto_sd);n['rid']=nr;a['rid']=nr+1;nr+=2
  n['data'].update(m_Id=ni,m_Parent={'rid':1022},m_Children=[],m_SerializedData={'rid':a['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
  a['data'].update(uxmlAssetId=ni,name='BlackPitchLine_'+name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
  ni+=1
  st.edit(n,[st.p(131102,st.en('absolute')),st.p(131089,st.pct(f32(x))),st.p(131104,st.pct(f32(y))),st.p(131105,st.pct(f32(w))),st.p(131087,st.pct(f32(h))),st.p(262150,st.px(0)),st.p(262151,st.px(0)),st.p(262148,st.px(1)),st.p(262146,st.h(4,line)),st.p(262147,st.px(1000 if circle else 0)),st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.}))])
  d['references']['RefIds'].extend([n,a]);image['data']['m_Children'].append({'rid':n['rid']})
 add('Outline',1,1,98,98)
 portrait=pid==-960000000003030
 if portrait:
  add('Halfway',1,50,98,0)
  add('CentreCircle',35,50-30*(200/327)/2,30,30*(200/327),True)
  for end,y in [('Top',1),('Bottom',83)]:add(end+'PenaltyArea',28,y,44,16)
  for end,y in [('Top',1),('Bottom',93)]:add(end+'GoalArea',40,y,20,6)
 else:
  add('Halfway',50,1,0,98);add('CentreCircle',42.5,35,15,30,True)
  for end,x in [('Left',1),('Right',83)]:add(end+'PenaltyArea',x,28,16,44)
  for end,x in [('Left',1),('Right',93)]:add(end+'GoalArea',x,40,6,20)
 # All original bindings, lists, native events, dimensions and position selection survive.
 oldrr=refs(old)
 for rid,record in oldrr.items():
  current=copy.deepcopy(rr[rid])
  if 'm_RuleIndex' in current.get('data',{}):current['data']['m_RuleIndex']=record['data']['m_RuleIndex']
  if rid==1022:current['data']['m_Children']=record['data']['m_Children']
  if rid==image['data']['m_SerializedData']['rid']:
   for key in ['tintColor','tintColor_UxmlAttributeFlags']:current['data'][key]=record['data'][key]
  assert current==record,('Unexpected preexisting node change',pid,rid)
 for o,data in [(obj,d),(so,s)]:o.save_typetree(data);expected[o.path_id]=data
 geometry.append({'template':d['m_Name'],'orientation':'portrait' if portrait else 'landscape','new_lines':7,'native_binding_retained':True,'black_background':'#000000'})

outbytes=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(outbytes).objects}
assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True),i
 else:assert sha(o.get_raw_data())==hashes[i],i
# Validate real VTA / function registration and image retirement policies without changing catalogs.
audit=source[source.index('# Catalog audit'):source.index('stamp=datetime.datetime.now')]
exec(compile(audit,'<catalog-and-retired-image-audit>','exec'))
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('black-pitch-40pct-zones-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/G])
(out/G).write_bytes(outbytes)
docpath=R/'球员弹窗最终版本说明.md';snpath=R/'球员弹窗最终版本资源快照.json'
for p in [docpath,snpath]:(out/p.name).write_bytes(p.read_bytes())
snapshot=json.loads(snpath.read_text('utf8'))
meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle')
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 if not any(a['bundle']==G and a['path_id_reference_only']==pid for a in snapshot['assets']):
  snapshot['assets'].append({'bundle':G,'name':obs[pid].peek_name(),'path_id_reference_only':pid,'container_keys':[k for k,v in meta['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':pid}]})
for a in snapshot['assets']:
 if a['bundle']!=G:continue
 d=check[a['path_id_reference_only']].read_typetree();a['tree']=d;a['inline_style']=check[d['inlineSheet']['m_PathID']].read_typetree()
snapshot.update(recorded_date='2026-10-27',revision='Black pitch and 40% aptitude fills on all four player overviews and all three player popup routes; unchanged layout and interaction',runtime_verified=False)
snapshot['bundles'][G]=sha(outbytes)
snapshot['pitch_colors']={'zone_fill_opacity':.4,'field_backdrop_hex':'#000000','native_image_tint_alpha':0,'pitch_lines':'UI Toolkit borders, background stays black','player_overviews':4,'popup_routes':3,'numbers_borders_click_bindings_unchanged':True}
note='''

## 2026-10-27 最新配色：球员主页面与弹窗统一黑色球场、40%方块

本节覆盖前一节的深蓝灰球场与26.6%方块设置。

- 四个球员overview版本使用的共用 `OverviewFourteenPositionRectangleRow` 与弹窗独立的 `TooltipPortraitFourteenPositionZones`：各14个 `PositionZoneColourFill_*` 的opacity统一为0.40。数字、边框、选中和点击事件不变。
- 三个主页面球场模块 `OverviewHorizontalPitchComparisonHalfLayout`、`LargePortraitOverviewPitchAboveRolesAndComparison`、`ThirdOverviewPortraitPitchRolesComparison`，以及弹窗 `TooltipVerticalPositionPitch` 的球场区域背景统一为纯黑 `#000000`。
- 为避免原生图片的绿色／主题色叠加到黑底，将球场SIImage的图像tint alpha设0，元素opacity保持1；在同一球场边界内加入7个不响应点击的UI Toolkit场地线条元素（边线、中线、中圈、两端禁区及球门区）。仍保留原图像资源绑定，不修改或新增纹理，不影响场外背景。
- 各模块现有尺寸、横竖方向、熟练度覆盖范围、角色列表、比较面板和弹窗内部布局保持原样；弹窗球场仍200×327px。
- 最新实施脚本：`black-pitch-and-40pct-position-zones.py`；同步游戏与皮肤Global包，更新本说明与资源快照。目录注册、禁用图片、有效图片和其他资源读回校验通过；游戏内显示待重启确认。
'''
for p,b in before.items():assert p.read_bytes()==b
for p,hsh in protected.items():assert sha(p.read_bytes())==hsh,p
try:
 for p in before:p.write_bytes(outbytes);assert p.read_bytes()==outbytes
 snpath.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),'utf8')
 docpath.write_text(docpath.read_text('utf8')+note,'utf8')
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 for p in [docpath,snpath]:p.write_bytes((out/p.name).read_bytes())
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'zone_fill_opacity':.4,'fill_templates':edits,'pitch_templates':geometry,'player_overviews':4,'popup_routes':3,'geometry_and_bindings_unchanged':True,'catalog_audits':audits,'retired_70_absent':True,'active_173_verified':True,'modified_objects':list(expected),'unrelated_objects_unchanged':len(obs)-len(expected),'catalogs_and_texture_bundles_unchanged':True,'bundle_sha256':sha(outbytes)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
