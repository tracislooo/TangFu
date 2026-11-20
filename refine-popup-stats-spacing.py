from pathlib import Path
import json,copy,datetime
R=Path(__file__).parent
exec(compile((R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0],'<current-helpers>','exec'))
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={};counts=[]
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032]:
  d=oo[pid].read_typetree();rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();root=next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='PopupFourRowsSeasonStats');todo=[root['rid']];count=0
  while todo:
   r=rr[todo.pop()];a=r['data'];todo.extend(c['rid'] for c in a.get('m_Children',[]));ix=a.get('m_RuleIndex',-1)
   if a.get('m_FullTypeName')!='SI.Bindable.SIText' or ix<0:continue
   rule=s['m_Rules'][ix];font=next((p for p in rule['m_Properties'] if p['m_Id']==65537),None)
   if not font:continue
   h=font['m_Values'][0];assert h['m_ValueType']==3;old=s['dimensions'][h['valueIndex']]['value'];assert old in [12,18],old
   # Give titles room above the text without changing fonts or the four-row canvas.
   updates={131087:18 if old==12 else 22,131096:18 if old==12 else 22,131094:18 if old==12 else 22,131084:0,131085:0}
   if old==12:updates[131101]=5
   for key,value in updates.items():
    prop=next((p for p in rule['m_Properties'] if p['m_Id']==key),None)
    if key in [131084,131085]:
     s['floats'].append(float(value));handle={'m_ValueType':2,'valueIndex':len(s['floats'])-1}
    else:
     s['dimensions'].append({'unit':1,'value':float(value)});handle={'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}
    if prop is None:rule['m_Properties'].append({'m_Id':key,'m_CustomName':'','m_Line':-1,'m_Values':[handle]})
    else:prop['m_Values']=[handle]
   count+=1
  assert count>=24,count;so.save_typetree(s);changed[so.path_id]=s;counts.append({'name':d['m_Name'],'enlarged_texts':count})
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True)
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'routes':counts})
out=R/('popup-season-stats-spacing-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'title_design_font_unchanged':12,'value_design_font_unchanged':18,'title_top_spacing':5,'title_box_height':18,'value_box_height':22,'four_rows_three_columns_preserved':True,'audits':audits,'bindings_and_other_bundles_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+'\n\n2026-11-03：四行统计标题与横线间距优化。保留标题12／数值18设计字号；每个标题加顶部5px间距，标题框18px、数值框22px，关闭这两个框的flex伸缩，保持200px高四行三列和原始绑定。新增顶部单横线保留，各行现有分隔线不再紧贴下一行标题。五份实际入口同步，主页面源数据模块不改。脚本refine-popup-stats-spacing.py；记录'+out.name+'/manifest.json。文件校验通过，游戏内视觉待确认。\n','utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));oo={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=oo[a['path_id_reference_only']].read_typetree();a['tree']=t;st=t['inlineSheet'];a['inline_style']=oo[st['m_PathID']].read_typetree() if st['m_PathID'] and not st['m_FileID'] else None
snap['bundles'][W]=sha(outputs[GAME/W]);snap['stats_spacing']={'title_margin_top':5,'title_height':18,'value_height':22};snap['runtime_verified']=False;p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
