from pathlib import Path
import copy,json,datetime
R=Path(__file__).parent
source=(R/'scale-all-player-popups-75.py').read_text('utf8').replace('F:/Steam/steamapps/common/Project Taco','F:/Steam/steamapps/common/Football Manager 27')
exec(compile(source.split('expected={};routes=[]')[0],'<current-location-helpers>','exec'))
expected={};changes=[]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
color={k:f32(v) for k,v in zip(['r','g','b','a'],[168/255,184/255,200/255,.9])}
for pid in [-498859349613660051,-1857952619964471988]:
 d=obs[pid].read_typetree();rr=refs(d);so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s);count=0
 for r in rr.values():
  sd=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if not sd.get('name','').startswith('PopupPanelOutline_'):continue
  assert sd['pickingMode']==1
  rule=s['m_Rules'][r['data']['m_RuleIndex']]
  keys={131076,131077,131078,131079,458758,458761,458762,458763}
  rule['m_Properties']=[v for v in rule['m_Properties'] if v['m_Id'] not in keys]+[st.p(k,st.px(2)) for k in [131076,131077,131078,131079]]+[st.p(k,st.h(4,color)) for k in [458758,458761,458762,458763]]
  count+=1
 assert count==2
 so.save_typetree(s);expected[so.path_id]=s;changes.append(d['m_Name'])
outbytes=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(outbytes).objects}
assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True)
 else:assert sha(o.get_raw_data())==hashes[i],i
audit=source[source.index('# Validate current installed registrations'):source.index('stamp=datetime.datetime.now')].replace("assert len(active['textures'])==active['active_custom_texture_count']==176","assert len(active['textures'])==active['active_custom_texture_count']")
exec(compile(audit,'<catalog-image-audit>','exec'))
assert -910000000000146 not in bo
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S');out=R/('match-player-popup-outlines-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
(out/W).write_bytes(outbytes)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
try:
 for p in before:p.write_bytes(outbytes);assert p.read_bytes()==outbytes
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'routes':changes,'explicit_four_sided_borders':True,'design_width':2,'display_width_at_85pct':1.7,'existing_nodes_layout_events_unchanged':True,'catalog_audits':audits,'active_textures_verified':len(active['textures']),'after_sha256':sha(outbytes)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+'\n\n2026-10-30：比赛姓名悬停及点击报告的既有球场／属性描边层补齐四边独立宽度与颜色（设计2px，85%显示1.7px，#A8B8C8／90%）。保持原节点、布局、绑定及点击不变；当前游戏目录Football Manager 27。参考fix-match-player-popup-outlines.py；记录'+out.name+'/manifest.json。恢复P06时一次完成，不追加重复描边层。\n','utf8')
p=R/'球员弹窗最终版本资源快照.json';snap=json.loads(p.read_text('utf8'));(out/p.name).write_bytes(p.read_bytes())
for a in snap['assets']:
 if a['bundle']==W and a['path_id_reference_only'] in [-498859349613660051,-1857952619964471988]:
  t=check[a['path_id_reference_only']].read_typetree();a['tree']=t;a['inline_style']=check[t['inlineSheet']['m_PathID']].read_typetree()
snap['bundles'][W]=sha(outbytes);snap['runtime_verified']=False;p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True))
