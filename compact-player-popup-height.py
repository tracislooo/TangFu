from pathlib import Path
import sys,json,copy,ast,struct,datetime,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
oldwrite=TypeTreeHelper.write_value;h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in h.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<writer>','exec'));TypeTreeHelper.write_value=write
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']};sha=lambda b:hashlib.sha256(b).hexdigest();f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
before={p/W:(p/W).read_bytes() for p in [GAME,SKIN]};outputs={};audits=[]
protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name!=W}
for folder in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:
  p=folder/n
  if p.exists():protected[p]=sha(p.read_bytes())
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={};routes=[]
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032,-960000000003010]:
  d=oo[pid].read_typetree();rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();old=copy.deepcopy(s)
  def setvalue(r,key,new):
   rule=s['m_Rules'][r['data']['m_RuleIndex']];p=next(p for p in rule['m_Properties'] if p['m_Id']==key)
   s['dimensions'].append({'unit':1,'value':f32(new)});p['m_Values']=[{'m_ValueType':3,'valueIndex':len(s['dimensions'])-1}]
  count=0
  for r in rr.values():
   a=r.get('data',{});ix=a.get('m_RuleIndex',-1)
   if ix<0:continue
   sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
   if pid==-960000000003010:
    if name=='ReportPortraitLayerStage':setvalue(r,131087,520);count+=1
    continue
   for prop in list(s['m_Rules'][ix]['m_Properties']):
    key=prop['m_Id'];v=prop['m_Values']
    if len(v)!=1 or v[0]['m_ValueType']!=3:continue
    oldval=s['dimensions'][v[0]['valueIndex']]['value'];new=None
    if key in [131087,131096,131094]:
     for source,target in [(832,756),(808,732),(888,812),(707.2,642.6),(754.8,690.2)]:
      if abs(oldval-source)<.001:new=target
     if name=='Fixed_FCPlayerCard' and oldval==596:new=520
     if name=='Fixed_SmallAttributes' and oldval==592:new=516
    if key==131104:
     if name in ['Fixed_VerticalPositionPitch','PopupPanelOutline_Pitch'] and oldval==608:new=532
     if name in ['Fixed_CoachScoutReport','Fixed_PlayerMood','Fixed_PlayerPosition'] and oldval==680:new=604
    if new is not None:setvalue(r,key,new);count+=1
  assert count>0,(pid,count)
  so.save_typetree(s);changed[so.path_id]=s;routes.append(d['m_Name'])
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'routes_and_private_card':routes,'only_modified_style_objects':list(changed),'all_visual_trees_and_other_objects_unchanged':len(oo)-len(changed)})
out=R/('compact-player-popup-height-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'display_size':[970.7,642.6],'click_shell_display_size':[970.7,690.2],'design_size':[1142,756],'design_click_shell':[1142,812],'card_stage_whitespace_trimmed_from_550_to_520':True,'card_image_portrait_text_and_pitch_sizes_unchanged':True,'scale':.85,'audits':audits,'catalogs_and_other_bundles_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
note='\n\n## 2026-11-01 最新高度收紧\n\n保持85%缩放及卡框图片／头像／文字／球场大小，FC卡面Stage只去掉底部留白：550→520；外层卡面槽596→520。横向球场在左栏内Y=532（原608），右侧底部三个模块Y=604（原680），Small槽高516（原592）。左右栏与整体背景高732（原808）。悬浮设计1142×756，显示970.7×642.6；点击含标题栏设计1142×812，显示970.7×690.2。5份实际入口统一处理，不恢复旧高度，不重复减76。脚本compact-player-popup-height.py；记录'+out.name+'/manifest.json。只改6份私有样式，绑定、内容尺寸及其他包／目录不变；游戏内效果待确认。\n'
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md','球员位置模块统一恢复顺序.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+note,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));current={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=current[a['path_id_reference_only']].read_typetree();a['tree']=t;st=t['inlineSheet'];a['inline_style']=current[st['m_PathID']].read_typetree() if st['m_PathID'] and not st['m_FileID'] else None
snap['bundles'][W]=sha(outputs[GAME/W]);snap['popup_scale'].update(hover_design_size=[1142,756],hover_display_size=[970.7,642.6],click_shell_design_size=[1142,812],click_shell_display_size=[970.7,690.2]);snap.update(revision='Five actual popup routes compact height 756, FC card whitespace trimmed without scaling content; 85%',runtime_verified=False);p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
