from pathlib import Path
import json,copy,datetime
R=Path(__file__).parent
exec(compile((R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0],'<current-helpers>','exec'))
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={}
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032]:
  o=oo[pid];d=o.read_typetree();old=copy.deepcopy(d);rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
  def named(name):
   a=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name];assert len(a)==1,name;return a[0]
  left=named('PopupStackedLeftColumn');proto=named('RightPanelBackground');stats=named('PopupFourRowsSeasonStats')
  assert not any(r.get('data',{}).get('name')=='PopupStatsTopSeparator' for r in rr.values()),'Already installed'
  nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;n=copy.deepcopy(proto);sd=copy.deepcopy(rr[proto['data']['m_SerializedData']['rid']]);n['rid']=nr;sd['rid']=nr+1
  n['data'].update(m_Id=ni,m_Parent={'rid':left['rid']},m_Children=[],m_SerializedData={'rid':sd['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
  sd['data'].update(uxmlAssetId=ni,name='PopupStatsTopSeparator',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,focusable=0,focusable_UxmlAttributeFlags=1)
  st.box(n,0,390,400,1.5);st.edit(n,[st.p(458752,st.h(4,{k:f32(v) for k,v in zip(['r','g','b','a'],[168/255,184/255,200/255,.9])}))])
  left['data']['m_Children'].append({'rid':nr});d['references']['RefIds'].extend([n,sd])
  for rid,record in refs(old).items():
   v=copy.deepcopy(rr[rid])
   if rid==left['rid']:v['data']['m_Children']=record['data']['m_Children']
   assert v==record,('Existing binding or layout changed',rid)
  for ob,data in [(o,d),(so,s)]:ob.save_typetree(data);changed[ob.path_id]=data
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'five_actual_popup_routes':True,'existing_nodes_bindings_and_enlarged_fonts_unchanged':True,'unrelated_objects_unchanged':len(oo)-len(changed)})
out=R/('popup-stats-top-separator-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'new_lines_per_popup':1,'line_position':'between FC card and four-row stats, left-column y390','line_design_rect':[0,390,400,1.5],'line_display_width':340,'audits':audits,'other_bundles_and_catalogs_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());text=p.read_text('utf8').replace('新增横线位置尚待用户答复，未安装横线。','横线最终位置见后续已确认记录。')
 text+='\n\n2026-11-02 用户确认只加一条分隔线：四行数据顶部与FC卡面之间，左栏(0,390,400,1.5)，颜色#A8B8C8／90%，85%显示宽340px、高约1.275px；独立PopupStatsTopSeparator忽略鼠标拾取。五份实际入口各一条，不在卡面顶部或头像内部额外加线。保持已放大的12／18字号和所有绑定。脚本add-popup-stats-top-separator.py；记录'+out.name+'/manifest.json。文件校验通过，游戏内显示待确认。\n';p.write_text(text,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));oo={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=oo[a['path_id_reference_only']].read_typetree();a['tree']=t;st=t['inlineSheet'];a['inline_style']=oo[st['m_PathID']].read_typetree() if st['m_PathID'] and not st['m_FileID'] else None
snap['bundles'][W]=sha(outputs[GAME/W]);snap['stats_top_separator']={'design_rect':[0,390,400,1.5],'one_line_per_popup':True};snap['runtime_verified']=False;p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
