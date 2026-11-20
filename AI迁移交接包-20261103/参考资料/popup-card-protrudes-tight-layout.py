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
 for pid in [-3760232355926433866,-498859349613660051,-1857952619964471988,-970000000012000,-990000000060032]:
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
     for source,target in [(756,620),(732,596),(812,676),(642.6,527),(690.2,574.6)]:
      if abs(oldval-source)<.001:new=target
     if name=='Fixed_FCPlayerCard' and oldval==520:new=520
     if name=='Fixed_SmallAttributes' and oldval==516:new=380
    if key==131104:
     if name=='Fixed_FCPlayerCard' and oldval==0:new=-136
     if name in ['Fixed_VerticalPositionPitch','PopupPanelOutline_Pitch'] and oldval==532:new=396
     if name in ['Fixed_CoachScoutReport','Fixed_PlayerMood','Fixed_PlayerPosition'] and oldval==604:new=468
    if new is not None:setvalue(r,key,new);count+=1
  assert count>0,(pid,count)
  so.save_typetree(s);changed[so.path_id]=s;routes.append(d['m_Name'])
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in changed:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(changed[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 outputs[folder/W]=b;audits.append({'folder':str(folder),'routes_and_private_card':routes,'only_modified_style_objects':list(changed),'all_visual_trees_and_other_objects_unchanged':len(oo)-len(changed)})
out=R/('popup-card-protrudes-tight-layout-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'frame_display_size':[970.7,527],'click_shell_display_size':[970.7,574.6],'design_frame':[1142,620],'card_protrusion_display_px':115.6,'card_and_pitch_sizes_unchanged':True,'right_attributes_design_height':380,'bottom_modules_top_in_right_column':468,'all_five_actual_routes':True,'audits':audits,'catalogs_and_other_bundles_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
note='\n\n## 2026-11-02 按图收紧：卡面上突、属性下去空白\n\n五份实际弹窗入口统一：主框设计1142×620（85%显示970.7×527），点击含标题栏1142×676（970.7×574.6）。左右栏与整体背景高596。Small槽高380、在右栏Y=76；下方三个模块Y=468、高128，属性结束后间隔12。左栏卡面保持400×520，Y=-136（显示向上突出115.6px）；横向球场400×200、Y=396，底端与右侧模块对齐。完整卡面与球场尺寸、85%缩放、字体及位置提示不变。上突部分不算进背景框高度，含突出卡面的整体可见范围仍约642.6px；祖先原visible溢出规则保留。恢复直接使用本节最终坐标，不叠加前次减高值。脚本popup-card-protrudes-tight-layout.py；记录'+out.name+'/manifest.json。文件校验通过，游戏内显示待确认。\n'
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md','球员位置模块统一恢复顺序.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+note,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));current={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for a in snap['assets']:
 if a['bundle']!=W:continue
 t=current[a['path_id_reference_only']].read_typetree();a['tree']=t;st=t['inlineSheet'];a['inline_style']=current[st['m_PathID']].read_typetree() if st['m_PathID'] and not st['m_FileID'] else None
snap['bundles'][W]=sha(outputs[GAME/W]);snap['popup_scale'].update(hover_design_size=[1142,620],hover_display_size=[970.7,527],click_shell_design_size=[1142,676],click_shell_display_size=[970.7,574.6]);snap.update(revision='Tight attributes frame, card protrudes 136 design px above left column, all five actual routes',runtime_verified=False);snap['card_protrusion']={'design_px':136,'display_px':115.6,'complete_visible_height':642.6};p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
