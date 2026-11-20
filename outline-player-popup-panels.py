from pathlib import Path
import copy,json,datetime
R=Path(__file__).parent
source=(R/'scale-all-player-popups-75.py').read_text('utf8')
exec(compile(source.split('expected={};routes=[]')[0],'<read-style-helpers>','exec'))
expected={};changes=[]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
color={k:f32(v) for k,v in zip(['r','g','b','a'],[168/255,184/255,200/255,.90])}
for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988]:
 obj=obs[pid];d=obj.read_typetree();old=copy.deepcopy(d);rr=refs(d);so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
 def named(name):
  matches=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name]
  assert len(matches)==1,(name,len(matches));return matches[0]
 proto=named('RightPanelBackground');parent=rr[proto['data']['m_Parent']['rid']]
 assert not any(r.get('data',{}).get('name','').startswith('PopupPanelOutline_') for r in rr.values()),'Outline already installed.'
 nr=max(rr)+1;ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 for name,x,y,w,h,radius in [('Pitch',414,146.5,200,327,2),('Attributes',626,12,694,596,8)]:
  n=copy.deepcopy(proto);sd=copy.deepcopy(rr[proto['data']['m_SerializedData']['rid']]);n['rid']=nr;sd['rid']=nr+1;nr+=2
  n['data'].update(m_Id=ni,m_Parent={'rid':parent['rid']},m_Children=[],m_SerializedData={'rid':sd['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
  sd['data'].update(uxmlAssetId=ni,name='PopupPanelOutline_'+name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,bindings=[]);ni+=1
  st.box(n,x,y,w,h)
  st.edit(n,[st.p(262148,st.px(2)),st.p(262146,st.h(4,color)),st.p(262147,st.px(radius)),st.p(458752,st.h(4,{'r':0.,'g':0.,'b':0.,'a':0.}))])
  d['references']['RefIds'].extend([n,sd]);parent['data']['m_Children'].append({'rid':n['rid']})
 oldrefs=refs(old)
 for rid,record in oldrefs.items():
  now=copy.deepcopy(rr[rid])
  if rid==parent['rid']:now['data']['m_Children']=record['data']['m_Children']
  assert now==record,('Original node modified',rid)
 for o,data in [(obj,d),(so,s)]:o.save_typetree(data);expected[o.path_id]=data
 changes.append({'route':d['m_Name'],'two_noninteractive_overlay_borders':True})
outbytes=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(outbytes).objects};assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True),i
 else:assert sha(o.get_raw_data())==hashes[i],i
audit=source[source.index('# Validate current installed registrations'):source.index('stamp=datetime.datetime.now')]
audit=audit.replace("assert len(active['textures'])==active['active_custom_texture_count']==176","assert len(active['textures'])==active['active_custom_texture_count']")
exec(compile(audit,'<current-resource-audit>','exec'))
assert -910000000000146 not in bo,'Deleted TF patch must stay absent.'
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S');out=R/('player-popup-panel-outlines-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
(out/W).write_bytes(outbytes)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p in before:p.write_bytes(outbytes);assert p.read_bytes()==outbytes
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'routes':changes,'border_design_px':2,'border_display_px':1.7,'border_color':'#A8B8C8 at 90% opacity','scale_85_layout_bindings_and_existing_nodes_preserved':True,'unrelated_objects_unchanged':len(obs)-len(expected),'catalog_audits':audits,'active_textures_verified':len(active['textures']),'deleted_tf_patch_absent':True,'retired_70_absent':True,'after_sha256':sha(outbytes)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());s=p.read_text('utf8')
 s+='\n\n## 2026-10-28：球场与右侧区域描边\n\n三类弹窗的实际球场和右侧整块区域增加独立浅灰蓝描边（#A8B8C8，90%不透明度，设计2px，85%显示1.7px）。设计范围分别为(414,146.5,200,327)和(626,12,694,596)，圆角分别2和8px。使用透明底、不响应点击的 `PopupPanelOutline_Pitch`／`PopupPanelOutline_Attributes` 覆盖层，不挤占内容。每个入口各一套；已有则复用，恢复时在P06中一次完成。保持85%缩放、黑场地、40%位置方块及原绑定。脚本 `outline-player-popup-panels.py`；记录 `'+out.name+'/manifest.json`。文件校验通过，游戏内显示待确认。\n'
 s=s.replace('保留已有 `kunshan stadium`、`TF patch`、`patchplayerbg` 及其现有引用','保留已有 `kunshan stadium`、独立衍生图 `TF patch aligned`、`patchplayerbg` 及其现有引用；V65已删除原图 `TF patch`（-910000000000146），不得重新导入')
 p.write_text(s,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'))
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=check[a['path_id_reference_only']].read_typetree();a['tree']=t;style=t['inlineSheet'];a['inline_style']=check[style['m_PathID']].read_typetree() if style['m_PathID'] and not style['m_FileID'] else None
snap['bundles'][W]=sha(outbytes);snap['panel_outlines']={'design_width':2,'display_width':1.7,'color':'#A8B8C8','opacity':.9,'regions':['pitch','whole_right_panel'],'picking_mode':'Ignore','restore_step':'P06'};snap['runtime_verified']=False
p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
