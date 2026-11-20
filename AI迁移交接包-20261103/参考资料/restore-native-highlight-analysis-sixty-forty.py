from pathlib import Path
import json,copy,struct

R=Path(__file__).parent
source=(R/'add-highlight-team-analysis-columns.py').read_text('utf8').split('cards=[]')[0]
source=source.replace("'highlight-team-analysis-columns-'","'highlight-native-analysis-60-40-'")
replacement="""baseline=UnityPy.load(str(R/'highlight-team-analysis-columns-20261024-062136'/'backup-game'/G))
baseline_objects={o.path_id:o for o in baseline.objects}
baseline_tree=baseline_objects[-7710242645031577538].read_typetree()
d=Doc(G,pid=-7710242645031577538,tree=baseline_tree,style=baseline_objects[baseline_tree['inlineSheet']['m_PathID']].read_typetree())"""
source=source.replace("d=Doc(G,name='MatchViewer_12x4')",replacement)
exec(compile(source,'restore-before-customized-cards-and-load-native-donors','exec'))

tile=Doc(G,name='tile-figma-base-template')
T='ui-tileslayouts_assets_all.bundle'
layout_env=UnityPy.load(str(GAME/T));layout_objects={o.peek_name():o for o in layout_env.objects if o.type.name=='MonoBehaviour'}
descriptor_names={(True,'Heat'):'HeatMapMatchHomeTeamGridElementDescription',(False,'Heat'):'HeatMapMatchAwayTeamGridElementDescription',(True,'Pass'):'HomeTeamPassMapTileDescription',(False,'Pass'):'AwayTeamPassMapTileDescription'}
title_ids={key:layout_objects[name].read_typetree()['<DisplayName>k__BackingField']['GameID'] for key,name in descriptor_names.items()}

# Reuse a native translation binding with no substitution arguments.
translation_template=None
for obj in objs[G].values():
 if obj.type.name!='MonoBehaviour' or b'f97abdf5a74842647ba921d183f4a3eb' not in obj.get_raw_data():continue
 tree=obj.read_typetree()
 for record in tree.get('references',{}).get('RefIds',[]):
  binding=record.get('data',{}).get('TextBinding',{});vf=binding.get('m_visualFunction',{})
  if vf.get('m_target',{}).get('m_guid')!='f97abdf5a74842647ba921d183f4a3eb':continue
  raw=bytes(vf['m_inputs']['m_variable']['m_argumentBytes']);args=[];at=1
  for _ in range(raw[0]):
   length=struct.unpack_from('<I',raw,at)[0];at+=4;args.append(raw[at:at+length]);at+=length
  if len(args)==2 and len(args[0])==74 and args[1].endswith(b']\x00'):
   translation_template=copy.deepcopy(binding);translation_args=args;break
 if translation_template:break
assert translation_template

def native_translation(game_id):
 binding=copy.deepcopy(translation_template);args=copy.deepcopy(translation_args)
 first=bytearray(args[0]);struct.pack_into('<I',first,1+first[0],game_id);args[0]=bytes(first)
 binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))
 return binding

# The containing grid stays 12x8. Prevent internal flex shrinking and use the requested 60/40 split.
for node in [1001,1002,1004,1006,1008]:
 d.st(node,[(131087,d.pct(100)),(131096,d.pct(100)),(131085,d.num(0))])
d.st(upper,[(131104,d.pct(0)),(131087,d.pct(60))])
d.st(lower,[(131104,d.pct(60)),(131087,d.pct(40))])
# Undo the previous unrequested change to the real-time pitch's native fill behavior.
for rid in pitch_serials:
 for key in ['FillAllAvailableSpace','FillAllAvailableSpace_UxmlAttributeFlags']:
  d.r[rid]['data'][key]=copy.deepcopy(old_refs[rid]['data'][key])

cards=[];caption_checks=[];native_text_checks=[]
for home,column,turn in [(True,left,90),(False,right,-90)]:
 side='Home' if home else 'Away'
 for kind,top,donor,plot_src in [('Heat',0,heat,1023),('Pass',50,passes,1019)]:
  prefix='HighlightNative'+side+kind
  card=plain(column,prefix+'Card')
  d.st(card,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.pct(top)),(131105,d.pct(100)),(131087,d.pct(50)),(131097,d.px(0)),(131096,d.px(0))])
  scope=d.add(d,1004,card,prefix+'Bindings');d.a(scope)['m_Classes']=[]
  mappings=[('team','match.HomeTeam' if home else 'match.AwayTeam',1145176088),('isHomeTeam' if kind=='Heat' else 'ishometeam','const.True' if home else 'const.False',0),('fixture','fixturetouse',1718188148),('isonmainscreen','const.False',0)]
  d.data(scope).update(Mappings=[{'m_serialisedType':0,'from':key,'to':{'m_path':value},'type':{'id':typ}} for key,value,typ in mappings],Mappings_UxmlAttributeFlags=1)
  fit_fill(scope)
  cloned={};base_cloned={}

  def original_node(src,rid,parent):
   node=copy_node(src,rid,parent,src.data(rid).get('name',''))
   d.a(node)['m_Properties']=copy.deepcopy(src.a(rid).get('m_Properties',[]))
   if 'name_UxmlAttributeFlags' in src.data(rid):d.data(node)['name_UxmlAttributeFlags']=src.data(rid)['name_UxmlAttributeFlags']
   return node

  def clone_tile(rid,parent):
   node=original_node(tile,rid,parent);base_cloned[rid]=node
   for child in tile.a(rid).get('m_Children',[]):clone_tile(child['rid'],node)
   return node

  def clone_module(rid,parent):
   # Inline the unchanged native tile chrome so its real title-text element is addressable.
   if donor.a(rid).get('m_TemplateAlias')=='tile-figma-base-template':
    root=clone_tile(1001,parent);fit_fill(root)
    content=base_cloned[1012]
    for child in donor.a(rid).get('m_Children',[]):clone_module(child['rid'],content)
    return root
   if rid==plot_src:
    slot=plain(parent,prefix+'PlotSlot')
    d.st(slot,[(131105,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131073,d.enum('center')),(131088,d.enum('center')),(131102,d.enum('relative'))])
    fit=copy_node(fitter,1145,slot,prefix+'LandscapeFit');d.a(fit)['m_Classes']=[]
    d.data(fit).update(AspectMode=3,AspectMode_UxmlAttributeFlags=1,AspectRatio=1.5,AspectRatio_UxmlAttributeFlags=1)
    d.st(fit,[(131102,d.enum('relative')),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,d.pct(100)),(131094,d.pct(100)),(131084,d.num(0)),(131085,d.num(1)),(131074,d.enum('center'))])
    node=original_node(donor,rid,fit);cloned[rid]=node
    d.data(node).update(Orientation=0,Orientation_UxmlAttributeFlags=1)
    d.st(node,[(131102,d.enum('absolute')),(131089,d.pct(f32(100/6))),(131104,d.pct(-25)),(131105,d.pct(f32(100/1.5))),(131087,d.pct(150)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131091,d.px(0)),(131092,d.px(0)),(131093,d.px(0)),(131090,d.px(0)),(ROTATE,angle(turn))])
    return node
   node=original_node(donor,rid,parent);cloned[rid]=node
   for child in donor.a(rid).get('m_Children',[]):clone_module(child['rid'],node)
   return node

  root=clone_module(1001,scope);fit_fill(root)
  caption=base_cloned[1020];game_id=title_ids[home,kind]
  d.data(caption)['TextBinding']=native_translation(game_id)
  d.data(caption)['TextBinding_UxmlAttributeFlags']=1
  assert d.a(caption)['m_Classes']==tile.a(1020)['m_Classes']
  caption_checks.append({'side':side,'kind':kind,'original_descriptor':descriptor_names[home,kind],'native_title_game_id':game_id,'native_caption_style_preserved':True})
  plot=cloned[plot_src]
  if kind=='Pass':
   marker_scope='highlight-'+side.lower()+'-native-pass-plot';d.a(plot)['m_Classes'].append(marker_scope)
   index=len(d.s['m_Rules'])
   d.s['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':21,'m_Selectors':[{'m_Parts':[{'m_Value':marker_scope,'m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'match-simulation-player-10px-bold','m_Type':3}],'m_PreviousRelationship':2}],'ruleIndex':index}],'m_Properties':[{'m_Id':ROTATE,'m_CustomName':'','m_Line':-1,'m_Values':[angle(-turn)]}],'line':-1})
  for srcid,node in cloned.items():
   typ=donor.r[donor.a(srcid)['m_SerializedData']['rid']]['type']['class']
   if typ=='SIText/UxmlSerializedData':
    actual_text=copy.deepcopy(d.data(node));actual_text['uxmlAssetId']=donor.data(srcid)['uxmlAssetId']
    assert actual_text==donor.data(srcid),('Native module text changed',side,kind,srcid)
    assert d.a(node)['m_Classes']==donor.a(srcid)['m_Classes']
    native_text_checks.append({'side':side,'kind':kind,'source_record':srcid,'serialized_text_and_style_identical':True})
  for required in ([1015,1022,1024,1025] if kind=='Heat' else [1013]):assert required in cloned,('Native title or legend missing',side,kind,required)
  setter=cloned[1004 if kind=='Heat' else 1002]
  assert d.data(setter)['BindFunction']==donor.data(1004 if kind=='Heat' else 1002)['BindFunction']
  assert d.data(plot)['DataBinding']==donor.data(plot_src)['DataBinding']
  cards.append({'side':side,'kind':kind,'card':card,'plot':plot,'rotation_degrees':turn,'full_native_module':donor.d['m_Name'],'cloned_module_nodes':len(cloned),'cloned_native_chrome_nodes':len(base_cloned),'native_empty_state_preserved':True,'custom_titles_removed':True})

pointer={'m_FileID':0,'m_PathID':d.sid}
assert pointer not in d.a(1001)['m_Stylesheets'];d.a(1001)['m_Stylesheets'].append(pointer)
assert d.data(1002)==sd(old_refs,1002)
assert d.r[1009]==old_refs[1009] and d.r[1013]==old_refs[1013]
assert d.data(1009)==sd(old_refs,1009) and d.data(1013)==sd(old_refs,1013)
allowed={1001,1002,1004,1006,1008,upper,lower,left,right,1022,d.a(left)['m_SerializedData']['rid'],d.a(right)['m_SerializedData']['rid']}|set(pitch_serials)
for rid,value in old_refs.items():
 if rid not in allowed:assert d.r[rid]==value,('Unrelated previous UI record changed',rid)
assert not any(x.get('data',{}).get('name','').endswith('HeatTitle') or x.get('data',{}).get('name','').endswith('PassTitle') for x in d.r.values())
d.save()

output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected,('Roundtrip mismatch',pid)
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.') or p.name==W:protected[p]=sha(before[p])
report={'passed':True,'upper_lower_percent':[60,40],'columns_percent':[25,50,25],'containing_grid_unchanged':[12,8],'root_full_height_and_no_flex_shrink':True,'main_pitch_native_fill_restored':True,'native_modules':cards,'native_captions':caption_checks,'native_text_checks':native_text_checks,'all_native_heatmap_headers_direction_keys_legend_and_description_present':True,'all_native_passmap_headers_and_date_template_present':True,'selector_and_stats_only_page_unchanged':True,'shared_donors_catalog_and_unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 恢复原生图表内容，改为 60%/40%

先撤回上一版自定义精简卡片，恢复原生热点图、传球图及原生卡片外观，再仅对绘图区做原方向变换。
原生标题取对应模块原有本地化 ID；字体样式取原生标题组件，不使用新拟的中文标题。
热点图原有对阵/日期、方向提示、色阶图例、说明文本全部复制保留，传球图原对阵/日期模板保留；文字及其样式与原生逐条比较一致。
中间区域上方 60%，下方 40%；上方左右/球场仍为 25%/50%/25%，左右两个原生模块各占一半。
根容器保持完整高度，禁止内部 flex 收缩；实时球场恢复之前原生的铺满方式。
选择器原位置、选项、操作以及下方原生“仅数据”页面保持原样。
没有更改外层网格和自定义布局缓存，也没有修改共用图表模板。

通过序列化回读、原生文字与样式逐条比较、选择器及无关对象一致性检查。尚未在游戏中验证实际显示。
退出游戏后运行 install.ps1 安装；restore.ps1 仅恢复本次修改。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'native_module_text_checks':len(native_text_checks),'native_title_ids':title_ids.__str__(),'upper_lower_percent':[60,40]},ensure_ascii=False))
