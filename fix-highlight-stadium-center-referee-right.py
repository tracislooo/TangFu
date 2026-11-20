from pathlib import Path
import subprocess
s=Path('inspect-highlight-referee-current.py').read_text('utf-8-sig').split("d=Doc(G,name=")[0]
s=s.replace('inspect-referee-','highlight-stadium-center-referee-right-').replace('hours=-4','hours=-6')
exec(compile(s,'boot','exec'))
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[G]=UnityPy.load(before[folder/G]);objs[G]={o.path_id:o for o in env[G].objects};changes[G]={}
 hashes[G]={i:sha(o.get_raw_data()) for i,o in objs[G].items()}
 d=Doc(G,name='MatchViewer_12x4');original=copy.deepcopy(d.d)
 host=d.named('HighlightWeatherRefereeHeader');weather=d.named('HighlightWeatherHeaderItem');stadium=d.named('HighlightStadiumHeaderItem');ref=d.named('HighlightRefereeHeaderItem');text=d.named('HighlightRefereeText')
 assert {x['rid'] for x in d.a(host)['m_Children']}=={weather,ref,stadium}
 d.a(host)['m_Children']=[{'rid':i} for i in [weather,stadium,ref]]
 for i,left,width,align in [(weather,0,25,'flex-start'),(stadium,25,50,'center'),(ref,75,25,'flex-end')]:
  d.st(i,[(131102,d.enum('absolute')),(131089,d.pct(left)),(131105,d.pct(width)),(131082,{'m_ValueType':1,'valueIndex':2}),(131095,{'m_ValueType':1,'valueIndex':3}),(131097,d.px(0)),(131104,d.px(0)),(131080,d.px(0)),(131083,d.enum('row')),(131073,d.enum('center')),(131088,d.enum(align)),(131084,d.num(0)),(131085,d.num(0))]+[(k,d.px(0)) for k in [131090,131091,131092,131093]])
 # Match the working native MatchdayInfo plain-name binding, removing the
 # person translation function and its embedded navigation semantics.
 native=Doc(G,name='MatchdayInfo_4x4')
 donor=next(i for i,a in native.r.items() if a.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText' and native.data(i).get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path')=='match.MatchReferee.Name')
 d.data(text)['TextBinding']=copy.deepcopy(native.data(donor)['TextBinding'])
 for k,v in {'TextBinding_UxmlAttributeFlags':1,'EnableEmbeddedLinks':0,'EnableEmbeddedLinks_UxmlAttributeFlags':1,'enableRichText':0,'enableRichText_UxmlAttributeFlags':1,'DisableLinkStyling':1,'DisableLinkStyling_UxmlAttributeFlags':1,'DisableContextMenu':1,'DisableContextMenu_UxmlAttributeFlags':1,'pickingMode':1,'pickingMode_UxmlAttributeFlags':1,'DebugDisplay':'','DebugDisplay_UxmlAttributeFlags':1}.items():d.data(text)[k]=v
 for i,alignment in [(text,'middle-right'),(d.named('HighlightStadiumText'),'middle-center')]:
  d.st(i,[(131105,{'m_ValueType':1,'valueIndex':2}),(131082,{'m_ValueType':1,'valueIndex':2}),(131097,d.px(0)),(131084,d.num(0)),(131085,d.num(1)),(65546,d.enum(alignment)),(458767,d.num(1))])
 d.save()
 # Only the declared layout nodes and the referee text payload may differ.
 rr=refs(original);allowed={host,weather,stadium,ref,text,d.named('HighlightStadiumText')};payload=d.a(text)['m_SerializedData']['rid']
 for i,a in rr.items():
  b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
  if i in allowed:
   a['data'].pop('m_RuleIndex',None);b['data'].pop('m_RuleIndex',None)
   if i==host:a['data']['m_Children']=b['data']['m_Children']
  if i!=payload:assert a==b,('unexpected node edit',i)
 data=env[G].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[G].keys()
 for pid,h in hashes[G].items():
  if pid not in changes[G]:assert sha(saved[pid].get_raw_data())==h
 for pid,tree in changes[G].items():assert saved[pid].read_typetree()==tree
 # GUID, catalog and all existing template IDs stay intact.
 assert [(a['rid'],a.get('data',{}).get('m_Id'),a.get('data',{}).get('uxmlAssetId')) for a in original['references']['RefIds']]==[(a['rid'],a.get('data',{}).get('m_Id'),a.get('data',{}).get('uxmlAssetId')) for a in d.d['references']['RefIds']]
 outputs[folder/G]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/G).write_bytes(data)
 checks.append({'target':str(folder/G),'name_binding':'match.MatchReferee.Name','order':['weather','stadium','referee'],'plain_text':True,'roundtrip':True,'unrelated_objects_unchanged':True})
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
manifest={'installed':False,'runtime_verified':False,'checks':checks,'before_sha256':{str(p):sha(before[p]) for p in outputs},'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
guard=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
install=list(guard);restore=list(guard)
for p in outputs:
 tag='game' if p.parent==GAME else 'skin'
 install.append("if ((Get-FileHash -LiteralPath '"+str(p)+"').Hash.ToLower() -ne '"+sha(before[p])+"') { throw 'Target changed since preparation.' }")
 restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-'+tag)/G)+"' -Destination '"+str(p)+"' -Force")
for p in outputs:
 tag='game' if p.parent==GAME else 'skin';install.append("Copy-Item -LiteralPath '"+str(OUT/('output-'+tag)/G)+"' -Destination '"+str(p)+"' -Force")
(OUT/'install.ps1').write_text('\n'.join(install),'utf-8-sig');(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if not running.stdout.strip():
 try:
  for p,b in outputs.items():p.write_bytes(b)
  for p,b in outputs.items():assert p.read_bytes()==b
  for p,h in protected.items():assert sha(p.read_bytes())==h
 except BaseException:
  for p in outputs:p.write_bytes(before[p])
  raise
 manifest.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'修改说明.md').write_text('Highlight中间信息行调整为温度—球场—主裁判；球场在该信息行中间50%区域，裁判右侧25%区域。裁判姓名使用原生MatchdayInfo_4x4的match.MatchReferee.Name直接文本绑定，关闭内嵌链接、富文本和上下文菜单。游戏/皮肤分别在各自现有Global包上修改，保留差异。未启动游戏，游戏内姓名与布局需实际验收。','utf8')
print(json.dumps({'output':str(OUT),'installed':manifest['installed'],'runtime_verified':False},ensure_ascii=False))
