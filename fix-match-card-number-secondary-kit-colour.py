from pathlib import Path
import json,copy
R=Path(__file__).parent
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','match-card-number-secondary-kit-colour-')
exec(compile(prefix,'backup-current-number-colours','exec'))
audits=[];tx=[]
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 W,G=[n+suffix for n in bases]
 for bn,names in [(W,['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']),(G,['SmallSubstituteCardLowerNoRating','MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard'])]:
  for name in names:
   d=Doc(bn,name=name);original=copy.deepcopy(d.d);holders=[];numbers=[];permitted=set()
   for i,r in d.r.items():
    if 'm_Parent' not in r.get('data',{}):continue
    s=d.data(i)
    if s.get('name')=='MatchCardNumberKitColourBinding':
     assert s['PrimaryColorDataLink']['m_path']=='kit.BackgroundColour'
     old=s['SecondaryColorDataLink']['m_path'];assert old in ['kit.NumberColour','kit.ForegroundColour']
     s['SecondaryColorDataLink']['m_path']='kit.ForegroundColour';s['SecondaryColorDataLink_UxmlAttributeFlags']=1;holders.append(i);permitted.add(d.a(i)['m_SerializedData']['rid'])
     for p in d.a(i).get('m_Properties',[]):
      if p.get('name')=='secondary-color-data-link':p['value']='kit.ForegroundColour'
    if s.get('name')=='MatchCardShirtNumber':
     assert 'fm-club-secondary-color' in d.a(i)['m_Classes'];numbers.append(i)
     rule=d.s['m_Rules'][d.a(i)['m_RuleIndex']];assert not any(p['m_Id']==65536 for p in rule['m_Properties']),'Fixed text color masks native secondary color'
   assert holders and len(holders)==len(numbers),(tag,name,len(holders),len(numbers))
   for i,r in refs(original).items():
    if i not in permitted:
     expected=copy.deepcopy(r)
     if i in holders:
      for p in expected['data'].get('m_Properties',[]):
       if p.get('name')=='secondary-color-data-link':p['value']='kit.ForegroundColour'
     assert d.r[i]==expected,('Unrelated node changed',tag,name,i)
    else:
     expected=copy.deepcopy(r);expected['data']['SecondaryColorDataLink']['m_path']='kit.ForegroundColour';expected['data']['SecondaryColorDataLink_UxmlAttributeFlags']=1;assert d.r[i]==expected
   oldstyle=copy.deepcopy(d.s);d.save();assert d.s==oldstyle
   audits.append({'variant':tag,'template':name,'holders':holders,'number_nodes':numbers,'background_unchanged':'kit.BackgroundColour','text_before':old,'text_after':'kit.ForegroundColour','number_text_geometry_other_bindings_unchanged':True})
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base;tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
previous_path=R/'current-match-card-number-colour.json';previous=previous_path.read_text('utf8') if previous_path.exists() else '{}';(OUT/'previous-colour-state.json').write_text(previous,'utf8')
state={'status':'prepared','patch':str(OUT),'source_script':str(Path(__file__)),'restore':str(OUT/'restore.ps1'),'game_root':'F:/Steam/steamapps/common/Football Manager 27','background':'kit.BackgroundColour','number_text':'kit.ForegroundColour','runtime_verified':False};(OUT/'number-colour-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8');installer+="\nstate=json.loads((out/('previous-colour-state.json' if restore else 'number-colour-state.json')).read_text('utf8'))\nif not restore:state.update(status='installed',installed_files=len(tx))\n(out.parent/'current-match-card-number-colour.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')\n";(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes());(OUT/'修改说明.md').write_text('比赛球员卡右侧号码：底色保持kit.BackgroundColour；文字由kit.NumberColour切换为球衣副色kit.ForegroundColour，沿用原生SIStyleSetter及fm-club-secondary-color。覆盖当前普通、小卡、私有小替补两分支和多替补卡副本；不改头像、布局、绑定值或Highlight。游戏和独立皮肤分别备份/增量修改。静态回读及无关对象检查通过，实际颜色待游戏验证。restore.ps1哈希保护。','utf8');print(OUT)
