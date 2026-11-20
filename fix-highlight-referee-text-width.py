from pathlib import Path
import json
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-referee-text-width-').replace('NAMES=[W,G,M,F]','NAMES=[G]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
exec(compile(boot,'backup-current-installed-global-resource','exec'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
reserved_ids={int(x['path_id']) for x in reserved}
assert reserved_ids.isdisjoint(objs[G])
d=Doc(G,name='MatchViewer_12x4');old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
ref=d.named('HighlightRefereeHeaderItem');text=d.named('HighlightRefereeText');icon=d.named('HighlightRefereeIcon')
assert d.data(ref)['Binding']['m_direct']['Path']['m_path']=='const.True'
assert d.data(text)['TextBinding']['m_direct']['Path']['m_path']=='match.MatchReferee.Name'
assert d.a(text)['m_Parent']['rid']==ref and d.a(icon)['m_Parent']['rid']==ref
AUTO={'m_ValueType':1,'valueIndex':2}
d.st(ref,[(131105,AUTO),(131082,AUTO),(131097,d.px(120)),(131095,d.pct(50)),(131084,d.num(0)),(131085,d.num(0))])
d.st(text,[(131105,AUTO),(131082,AUTO),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
allowed={ref,text}
for rid,record in oldr.items():
 expected=copy.deepcopy(record)
 if rid in allowed:expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
 assert d.r[rid]==expected,('Unrelated node, binding, or structure changed',rid)
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
for node in allowed:
 for prop in d.s['m_Rules'][d.a(node)['m_RuleIndex']]['m_Properties']:assert all(h['m_ValueType']!=10 for h in prop['m_Values'])
d.save()

# Verify actual Addressables registrations, asset types, and bundle dependency order.
spec=importlib.util.spec_from_file_location('referee_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
meta=next(o.read_typetree() for o in objs[G].values() if o.type.name=='AssetBundle')
rows=[]
for key,entry in meta['m_Container']:
 pid=entry['asset']['m_PathID'];ob=objs[G].get(pid)
 if not ob or ob.type.name!='MonoBehaviour':continue
 tree=changes[G].get(pid,ob.read_typetree())
 if pid==d.obj.path_id:rows.append((key,pid,'UnityEngine.UIElements.VisualTreeAsset'))
 elif 'm_nodes' in tree:rows.append((key,pid,'SI.VisualScripting.VisualFunction'))
assert any(pid==d.obj.path_id for _,pid,_ in rows)
catalog_audits=[]
for cp in [GAME.parent/'catalog.bin',SKIN/'catalog.bin']:
 c=cm.Catalog(cp.read_bytes());locations={loc for _,p in c.keys() for (loc,) in c.array(p,'I')}
 gloc=next(loc for loc in locations if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].replace('\\','/').endswith('/'+G))
 for key,pid,expected in rows:
  assert pid in objs[G]
  matching=[c.location(loc) for loc in c.locations(key) if c.location(loc)['type'][1]==expected]
  assert matching,('Expected typed Addressables registration missing',str(cp),key,expected)
  for l in matching:assert l['dependencies'] and l['dependencies'][0]==gloc,(str(cp),key,l)
 catalog_audits.append({'catalog':str(cp),'checked_vta_and_visual_functions':len(rows),'owning_bundle_dependency_first':True})
data=env[G].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(objs[G]);assert reserved_ids.isdisjoint(saved)
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,tree in changes[G].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',pid)
validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
(OUT/G).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'referee_data_confirmed_available_by_user_in_native_matchday_info':True,'native_name_binding_preserved':'match.MatchReferee.Name','referee_width':'auto; basis auto; min 120px; max 50% of metadata host; no shrink','referee_text':'auto width; flexible; existing 12px/color/ellipsis/tooltip unchanged','other_metadata_and_all_charts_unchanged':True,'changed_style_nodes':sorted(allowed),'no_textures_added_or_repacked':True,'catalogs_unchanged':True,'catalog_checks':catalog_audits,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):tree.get('m_Name','') for pid,tree in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-match-ui-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('用户确认原生比赛日信息能显示裁判姓名，故保留match.MatchReferee.Name原生数据源。仅修正MatchViewer_12x4中HighlightRefereeHeaderItem的零宽起算：width/basis改auto，min-width120px、max-width50%、禁止收缩，文字使用auto宽度并在保留区域内伸缩省略。保持12px字号、暗白色、提示、图标、温度、球场、整行位置、所有图表和其余绑定不变。只修改当前已安装Global包内对应VTA及内联样式2对象，不新增资源，不改背景图/目录/其他功能。核对主VTA及Global自定义VisualFunction的目录类型、实际对象及首项所属包依赖，完成序列化回读与无关对象一致性检查。游戏内渲染尚未验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'changed_style_nodes':sorted(allowed),'native_name_binding_preserved':True,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
