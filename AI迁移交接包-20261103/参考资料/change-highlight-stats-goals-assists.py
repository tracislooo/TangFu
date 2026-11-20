from pathlib import Path
import json
R=Path(__file__).parent
previous=(R/'build-highlight-lower-oop-eightstats-footer.py').read_text('utf8')
prefix=previous.split('# Native eight-field data')[0].replace('highlight-lower-oop-eightstats-footer-','highlight-stats-goals-assists-')
exec(compile(prefix,'backup-current-independent-packages','exec'))
ids=['picked-position','player','rating','condition','goals','assists','keyPasses','keyTackles']
factory_obj=objs[F][-981028000001000];factory=factory_obj.read_typetree();old=copy.deepcopy(factory);cols={c['m_id']:c for c in factory['m_rowData']}
donor=objs[F][-981025000003500].read_typetree();native={c['m_id']:c for c in donor['m_rowData']}
new=[]
for ident in ids:
 c=copy.deepcopy(cols[ident] if ident in cols else native[ident])
 if ident in ['goals','assists']:c.update(m_defaultWidth=36.,m_minimumWidth=36.,m_allowWidthAutoResizing=0)
 new.append(c)
factory['m_rowData']=new
assert [c for c in old['m_rowData'] if c['m_id'] not in ['tactics-fatigue-value','clearCutChances']]==[c for c in new if c['m_id'] not in ['goals','assists']]
factory_obj.save_typetree(factory);changes[F][factory_obj.path_id]=factory
for bn in [V,VS]:
 ob=objs[bn][-981028000001200];tree=ob.read_typetree();original=copy.deepcopy(tree);cfg=tree['m_tableView']['m_tableConfig'];byid={c['m_columnID']:c for c in cfg}
 newcfg=[]
 for ident in ids:
  c=copy.deepcopy(byid[ident] if ident in byid else byid['clearCutChances']);c['m_columnID']=ident
  if ident in ['goals','assists']:
   c['m_columnMetadata'].update(m_widthOverride=36.,m_minWidthOverride=36.);c['m_columnMetadata']['m_titleTranslationIdOverride']['GameID']=0
  newcfg.append(c)
 tree['m_tableView']['m_tableConfig']=newcfg
 ob.save_typetree(tree);changes[bn][ob.path_id]=tree
outputs={};selected=[F,V,VS]
for bn in selected:
 data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree
 dest=OUT/('output-skin' if bn==VS else 'output-game')/(V if bn==VS else bn);dest.parent.mkdir(exist_ok=True);dest.write_bytes(data);outputs[bn]=dest
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name not in [F,V]:protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for name in [F,V]:
  p=folder/name;src=outputs[VS if name==V and tag=='skin' else name]
  tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[p]),'after':sha(src.read_bytes())})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'column_order':ids,'removed':['tactics-fatigue-value','clearCutChances'],'added':['goals','assists'],'first_four_columns_and_existing_keys_preserved':True,'original_factory_and_all_other_views_unchanged':True,'no_new_assets_or_texture_changes':True,'catalogs_unchanged':True,'serialization_roundtrip':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅改Highlight左右下方当前八列表格的私有工厂和私有视图：删除疲劳、绝佳机会，加入进球和助攻。最终位置、姓名、评分、体能/状态、进球、助攻、关键传球、关键抢断。新增两列沿用原生Goals/Assists绑定和既有70%字号数字模板，宽度36px，其他六列保持不变。不改菜单、阵型、卡片、裁判、背景图、资源目录或其他页面。游戏/皮肤视图分别处理，所有其他对象原始字节不变，序列化回读通过。游戏内未验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'columns':ids,'roundtrip':True},ensure_ascii=False),flush=True)
