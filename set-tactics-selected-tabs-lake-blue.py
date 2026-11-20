from pathlib import Path
import subprocess
source=Path('build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
source=source.replace('NAMES=[W,G,M,F]',"G='ui-styles_assets_default.bundle'\nNAMES=[G]").replace('match-ui-avatars-layout-','tactics-selected-tabs-lake-blue-').replace('hours=-4','hours=-7')
source=source.replace("if SKIN/n in before:assert before[SKIN/n]==before[GAME/n],('game/skin diverged',n)",'pass').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'pass')
exec(compile(source,'current-non-sidebar-style-backup','exec'))
outputs={};checks=[]
blue={'r':48/255,'g':184/255,'b':197/255,'a':1.}
blue={k:struct.unpack('<f',struct.pack('<f',v))[0] for k,v in blue.items()}
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 e=UnityPy.load(before[folder/G]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};edited={};hits=0
 for pid,o in oo.items():
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree();count=0
  for rule in list(d.get('m_Rules',[])):
   sels=rule['m_ComplexSelectors']
   if not sels or not all(any(p['m_Value']=='tactics-collapsable-pitch-header-button-group' for s in sel['m_Selectors'] for p in s['m_Parts']) and any(p['m_Value']=='buttongroup__button--active' for s in sel['m_Selectors'] for p in s['m_Parts']) for sel in sels):continue
   d['colors'].append(copy.deepcopy(blue));prop=next(p for p in rule['m_Properties'] if p['m_Id']==458752);prop['m_Values']=[{'m_ValueType':4,'valueIndex':len(d['colors'])-1}]
   # The private pitch switch ID has a higher priority base-background rule.
   # Supply its active variant so it cannot hide the selection colour.
   scoped=copy.deepcopy(rule)
   for sel in scoped['m_ComplexSelectors']:
    sel['m_Selectors'][0]['m_Parts']=[{'m_Value':'TFPitchSwitches','m_Type':6}]
    sel['m_Specificity']+=100;sel['ruleIndex']=len(d['m_Rules'])
   d['m_Rules'].append(scoped);count+=1
  if count:o.save_typetree(d);edited[pid]=d;hits+=count
 assert hits==2,(folder,hits)
 data=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==oo.keys()
 for pid,o in saved.items():
  if pid in edited:assert o.read_typetree()==edited[pid]
  else:assert sha(o.get_raw_data())==hh[pid]
 outputs[folder/G]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/G).write_bytes(data)
 checks.append({'target':str(folder/G),'selected_color':'#30B8C5','active_and_active_hover':True,'native_and_private_switch_scopes':True,'modified_style_objects':list(edited),'unrelated_objects_unchanged':True})
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('常规战术与比赛内战术球场切换按钮：原生tactics-collapsable-pitch-header-button-group下的buttongroup__button--active及其hover统一湖水蓝#30B8C5。补充TFPitchSwitches选中范围以覆盖原私有黑底规则。只改当前非侧栏基线中两份样式对象，游戏和皮肤分别处理，未修改模板、图片、catalog或比赛数据。资源回读与无关对象校验通过，游戏内实际显示待确认。','utf8')"+tail[end:]
exec(compile(tail,'validate-backup-install','exec'))
