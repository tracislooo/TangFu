from pathlib import Path
import copy,json,datetime
R=Path(__file__).parent
source=(R/'scale-all-player-popups-75.py').read_text('utf8')
exec(compile(source.split('expected={};routes=[]')[0],'<read-and-style-helpers>','exec'))
expected={};routes=[]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for pid,viewport,canvas,height in [(-3760232355926433866,1010,120002,620),(-498859349613660051,70007,120002,620),(-1857952619964471988,120002,80013,676)]:
 d=obs[pid].read_typetree();rr=refs(d);so=obs[d['inlineSheet']['m_PathID']];s=so.read_typetree();old=copy.deepcopy(s);st=Styles(s)
 vr=s['m_Rules'][rr[viewport]['data']['m_RuleIndex']];cr=s['m_Rules'][rr[canvas]['data']['m_RuleIndex']]
 for key,beforevalue,newvalue in [(131105,1006.5,1140.7),(131097,1006.5,1140.7),(131095,1006.5,1140.7),(131087,height*.75,height*.85),(131096,height*.75,height*.85),(131094,height*.75,height*.85)]:
  prop=next(p for p in vr['m_Properties'] if p['m_Id']==key);h=prop['m_Values'][0]
  assert h['m_ValueType']==3 and abs(s['dimensions'][h['valueIndex']]['value']-beforevalue)<.001
  prop['m_Values']=[st.px(f32(newvalue))]
 scale=next(p for p in cr['m_Properties'] if p['m_Id']==327681)
 assert [s['floats'][h['valueIndex']] for h in scale['m_Values']]==[.75,.75]
 scale['m_Values']=[st.num(.85),st.num(.85)]
 # Modify only the existing viewport size and its single canvas scale.
 allowed={rr[viewport]['data']['m_RuleIndex']:{131105,131097,131095,131087,131096,131094},rr[canvas]['data']['m_RuleIndex']:{327681}}
 for i,rule in enumerate(s['m_Rules']):
  oldrule=old['m_Rules'][i]
  if i not in allowed:assert rule==oldrule
  else:assert [p for p in rule['m_Properties'] if p['m_Id'] not in allowed[i]]==[p for p in oldrule['m_Properties'] if p['m_Id'] not in allowed[i]]
 so.save_typetree(s);expected[so.path_id]=s
 routes.append({'name':d['m_Name'],'display_size':[1140.7,round(height*.85,2)],'scale':.85,'existing_single_wrapper_reused':True})
outbytes=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(outbytes).objects};assert set(check)==set(obs)
for i,o in check.items():
 if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True)
 else:assert sha(o.get_raw_data())==hashes[i],i
exec(compile(source[source.index('# Validate current installed registrations'):source.index('stamp=datetime.datetime.now')],'<current-catalog-and-texture-audit>','exec'))
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S');out=R/('player-popups-scale85-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
(out/W).write_bytes(outbytes)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p in before:p.write_bytes(outbytes);assert p.read_bytes()==outbytes
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'routes':routes,'only_three_inline_styles_changed':list(expected),'all_visual_trees_bindings_and_main_pages_unchanged':True,'unrelated_objects_unchanged':len(obs)-len(expected),'catalog_audits':audits,'active_texture_count':176,'retired_70_absent':True,'protected_bundles_and_catalogs_unchanged':True,'after_sha256':sha(outbytes)}
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for name in ['球员弹窗最终版本说明.md','球员位置模块统一恢复顺序.md','球员弹窗最终版本资源快照.json']:(out/name).write_bytes((R/name).read_bytes())
for name in ['球员弹窗最终版本说明.md','球员位置模块统一恢复顺序.md']:
 p=R/name;s=p.read_text('utf8').replace('75%','85%').replace('0.75','0.85').replace('1006.5','1140.7').replace('×465','×527').replace('x465','x527').replace('×507','×574.6').replace('x507','x574.6').replace('150×245.25','170×277.95')
 s=s.replace('卡面区域300×447；球场模块150×447，实际球场170×277.95；右侧520.5×447，Small属性高285，底部三模块高96，间隔9px。','卡面区域340×506.6；球场模块170×506.6，实际球场170×277.95；右侧589.9×506.6，Small属性高323，底部三模块高108.8，间隔10.2px。')
 s+='\n\n### 2026-10-28：缩放最终改为85%\n\n复用现有单层缩放容器，仅将scale直接设为0.85并更新视口：悬浮1140.7×527px，比赛点击报告含标题栏1140.7×574.6px。不在75%基础上再乘85%。`PlayerPopupCanvas75`／`PlayerPopupViewport75`是保留的历史节点名称，实际比例已为85%，不要因名称再增加缩放层。当前调整脚本为 `resize-player-popups-85.py`，安装记录为 `'+out.name+'/manifest.json`。旧75%脚本只作为建立容器的历史参考，更新恢复时P06直接使用最终85%，不先做75%再调整。文件校验通过，游戏内显示待确认。\n'
 p.write_text(s,'utf8')
p=R/'球员弹窗最终版本资源快照.json';snap=json.loads(p.read_text('utf8'))
for a in snap['assets']:
 if a['bundle']!=W:continue
 tree=check[a['path_id_reference_only']].read_typetree();a['tree']=tree;style=tree['inlineSheet'];a['inline_style']=check[style['m_PathID']].read_typetree() if style['m_PathID'] and not style['m_FileID'] else None
snap['bundles'][W]=sha(outbytes);snap.update(revision='All three player popup routes at 85%; hover 1140.7x527; match click 1140.7x574.6; same single transform wrappers',runtime_verified=False)
snap['popup_scale'].update(factor=.85,hover_display_size=[1140.7,527],click_shell_display_size=[1140.7,574.6],pitch_display_size=[170,277.95])
p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(report,ensure_ascii=True))
