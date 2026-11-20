from pathlib import Path
import json,copy,datetime
R=Path(__file__).parent
boot=(R/'enforce-popup-two-column-stack.py').read_text('utf8').split('for folder in [GAME,SKIN]:')[0]
exec(compile(boot,'<current-bundle-helpers>','exec'))
def collect(rr,start):
 seen=set()
 def scan(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    i=v['rid']
    if i!=-2 and i not in seen:seen.add(i);scan(rr[i]['data'])
   else:
    for k,x in v.items():
     if k!='m_Parent':scan(x)
  elif isinstance(v,list):
   for x in v:scan(x)
 scan({'rid':start});return seen
def rename(v,ids):
 if isinstance(v,dict):
  if set(v)=={'rid'}:return {'rid':ids.get(v['rid'],v['rid'])}
  return {k:rename(x,ids) for k,x in v.items()}
 if isinstance(v,list):return [rename(x,ids) for x in v]
 return v
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={}
 # Resolve the exact source imported by overview one, rather than relying on duplicate catalog names.
 page=oo[-930000000001001].read_typetree();key=next(u['path'] for u in page['m_Usings'] if u['alias']=='OverviewNativeSeasonFourGauges')
 meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle');sourceids=[v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==key and v['asset']['m_FileID']==0 and 'inlineSheet' in oo[v['asset']['m_PathID']].read_typetree()]
 assert sourceids;source=oo[sourceids[0]].read_typetree();sr=refs(source);ss=oo[source['inlineSheet']['m_PathID']].read_typetree();root=sr[source['m_VisualTree']['rid']]['data']['m_Children'][0]['rid'];keep=collect(sr,root)
 assert sum('SeasonStatsRow' in r.get('data',{}).get('name','') for r in sr.values())==8,'Expect two four-row GK/outfield branches'
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032]:
  o=oo[pid];d=o.read_typetree();rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();st=Styles(s)
  def named(name):
   a=[r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name];assert len(a)==1,name;return a[0]
  pitch=named('Fixed_VerticalPositionPitch');left=named('PopupStackedLeftColumn');right=named('PopupAttributesRightColumn');bg=named('RightPanelBackground');outline=named('PopupPanelOutline_Attributes');po=named('PopupPanelOutline_Pitch');body=rr[left['data']['m_Parent']['rid']]
  nr=max(rr)+1;ids={i:nr+j for j,i in enumerate(sorted(keep))};ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1;assetids={}
  for i in keep:
   if 'm_Id' in sr[i].get('data',{}):assetids[sr[i]['data']['m_Id']]=ni;ni+=1
  cache={}
  for i in sorted(keep):
   n=rename(copy.deepcopy(sr[i]),ids);n['rid']=ids[i];a=n.get('data',{})
   for k in ['m_Id','uxmlAssetId']:
    if k in a:a[k]=assetids.get(a[k],a[k])
   ix=a.get('m_RuleIndex',-1)
   if ix>=0:
    if ix not in cache:
     rule=copy.deepcopy(ss['m_Rules'][ix]);rule['m_ComplexSelectors']=[]
     for p in rule['m_Properties']:
      for h in p['m_Values']:
       if h['m_ValueType'] in poolmap:
        pool=poolmap[h['m_ValueType']];v=copy.deepcopy(ss[pool][h['valueIndex']]);h['valueIndex']=len(s[pool]);s[pool].append(v)
     cache[ix]=len(s['m_Rules']);s['m_Rules'].append(rule)
    a['m_RuleIndex']=cache[ix]
   if i==root:a['m_Parent']={'rid':left['rid']}
   rr[n['rid']]=n
  new=rr[ids[root]];st.box(new,0,396,400,200);rr[new['data']['m_SerializedData']['rid']]['data'].update(name='PopupFourRowsSeasonStats',name_UxmlAttributeFlags=1)
  left['data']['m_Children']=[{'rid':new['rid']} if c['rid']==pitch['rid'] else c for c in left['data']['m_Children'] if c['rid']!=po['rid']]
  for n in [pitch,po]:del rr[n['data']['m_SerializedData']['rid']];del rr[n['rid']]
  # The entire-popup border draws before the left column, so the FC card covers its top line.
  kids=body['data']['m_Children'];body['data']['m_Children']=[c for c in kids if c['rid']!=left['rid']]+[{'rid':left['rid']}]
  d['m_Usings']=[u for u in d['m_Usings'] if u['alias']!='VerticalPositionPitch']
  for u in source['m_Usings']:
   found=[v for v in d['m_Usings'] if v['alias']==u['alias']]
   if found:assert found[0]==u
   else:d['m_Usings'].append(copy.deepcopy(u))
  d['references']['RefIds']=list(rr.values());seen=set();elementids=set()
  def walk(i):
   assert i not in seen;seen.add(i);a=rr[i]['data'];assert a['m_Id'] not in elementids;elementids.add(a['m_Id'])
   sd=a.get('m_SerializedData',{}).get('rid',-2)
   if sd!=-2:assert rr[sd]['data']['uxmlAssetId']==a['m_Id']
   for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']=={'rid':i};walk(c['rid'])
  walk(d['m_VisualTree']['rid']);assert all(r['rid'] in seen for r in rr.values() if 'm_Parent' in r.get('data',{}))
  for i in keep:
   original=sr[i].get('data',{})
   if 'm_Parent' not in original and 'uxmlAssetId' in original:
    actual=copy.deepcopy(rr[ids[i]]['data']);actual['uxmlAssetId']=original['uxmlAssetId']
    if i==sr[root]['data']['m_SerializedData']['rid']:
     actual['name']=original.get('name','');actual['name_UxmlAttributeFlags']=original.get('name_UxmlAttributeFlags',0)
    assert actual==rename(original,ids),('Stats bindings changed',i)
  for ob,data in [(o,d),(so,s)]:ob.save_typetree(data);changed[ob.path_id]=data
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'source_stats':source['m_Name'],'source_pid':sourceids[0],'five_actual_routes_modified':True,'main_page_stats_and_other_objects_unchanged':len(oo)-len(changed)})
out=R/('popup-season-stats-and-card-border-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'lower_left':'Overview one native four-row three-column season stats with GK branch and reporting bindings','stats_design_size':[400,200],'stats_display_size':[340,170],'border_behind_card':True,'existing_dimensions_and_scale_preserved':True,'audits':audits,'other_bundles_and_catalogs_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
note='\n\n## 2026-11-02 最新：卡面下方改四行数据\n\n移除五份实际弹窗左下的横向位置球场及其描边，原位置(左栏0,396,400,200)改为第一版头像右侧的四行三列赛季统计，85%显示340×170。直接复制当前第一版OverviewNativeSeasonFourGauges实际引用的完整原生统计组件，包括GK切换、competition和seasonStats映射、原生标题及数值绑定，主页面源模块不改。保留当前整体尺寸／上突卡面／85%缩放。左栏在整个背景与描边之后绘制，顶横线在卡面后方。原位置球场资源可保留供历史回退，但弹窗不再引用，恢复不可重新装回。脚本replace-popup-pitch-with-season-stats.py；记录'+out.name+'/manifest.json。文件及布局树检查通过，游戏内数据与视觉待确认。\n'
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md','球员位置模块统一恢复顺序.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+note,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));current={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=current[a['path_id_reference_only']].read_typetree();a['tree']=t;st=t['inlineSheet'];a['inline_style']=current[st['m_PathID']].read_typetree() if st['m_PathID'] and not st['m_FileID'] else None
snap['bundles'][W]=sha(outputs[GAME/W]);snap.update(revision='Five actual popup routes: FC card above four-row season stats, top border drawn behind card',runtime_verified=False);p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
