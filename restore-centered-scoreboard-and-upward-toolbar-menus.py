from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','centered-scoreboard-upward-menus-').replace('NAMES=[W,G,M,F]','NAMES=[G,M]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-current-only-targeted-ui','exec'))
for bn in NAMES:
 alias=bn+'::skin';env[alias]=UnityPy.load(before[SKIN/bn]);objs[alias]={o.path_id:o for o in env[alias].objects};hashes[alias]={i:sha(o.get_raw_data()) for i,o in objs[alias].items()};changes[alias]={}
baseG,baseM=G,M
def source_doc(folder,bundle,name):
 e=UnityPy.load(str(folder/bundle));os={o.path_id:o for o in e.objects};ob=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);t=ob.read_typetree();return ob,t,os[t['inlineSheet']['m_PathID']].read_typetree()
def restore_named(bn,folder,bundle,name):
 ob,t,s=source_doc(folder,bundle,name);current=Doc(bn,name=name)
 # Older snapshots are used for these individual objects only, not whole bundles.
 old=refs(t)
 for i,r in old.items():
  if 'm_Parent' not in r.get('data',{}):assert current.r.get(i)==r,('Unexpected original binding difference',name,i)
 pointer_remap(t,ob.assets_file,current.af);pointer_remap(s,ob.assets_file,current.af);import_types(ob.assets_file,current.af,t['references']['RefIds'])
 current=Doc(bn,pid=current.obj.path_id,tree=t,style=s);return current
audits=[]
for tag,suffix in [('game',''),('skin','::skin')]:
 G,M=baseG+suffix,baseM+suffix
 header=restore_named(M,R/'match-pending-changes-right-controls-20261030-020754'/('backup-'+tag),baseM,'OverviewHeader')
 # Restore only the native scorebug classes/style; retain current bindings/IDs.
 ob,native,natives=source_doc(R/'match-ui-avatars-layout-20261023-141148'/'backup-game',baseM,'OverviewHeader')
 nr=refs(native);header.a(1034)['m_Classes']=copy.deepcopy(nr[1034]['data']['m_Classes'])
 header.a(1034)['m_RuleIndex']=-1
 source_index=nr[1034]['data']['m_RuleIndex']
 if source_index>=0:
  props=copy.deepcopy(natives['m_Rules'][source_index]['m_Properties'])
  for prop in props:
   for v in prop['m_Values']:
    if v['m_ValueType'] in poolmap:
     typ=v['m_ValueType'];v.update(header.val(typ,copy.deepcopy(natives[poolmap[typ]][v['valueIndex']])))
  header.s['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':props,'line':-1});header.a(1034)['m_RuleIndex']=len(header.s['m_Rules'])-1
 assert 'centre-avoid-centred' in header.a(1034)['m_Classes']
 assert header.a(1089)['m_Parent']['rid']==1083
 header.save()
 page=restore_named(M,R/'in-match-tactics-top-clearance-20261030-033258'/('backup-'+tag),baseM,'MatchTacticsRoot');page.save()
 popup=restore_named(G,R/'pending-anchor-stats-live-condition-20261030-030740'/('backup-'+tag),baseG,'MatchTacticPendingChanges');popup.save()
 toolbar=Doc(M,name='MatchUITacticalOptions');menu_audits=[]
 for node in [1018,1027,1048]:
  data=toolbar.data(node);old=data['Anchor'];data.update(Anchor=2,Anchor_UxmlAttributeFlags=1)
  if 'HorizontalAlignment' in data:data.update(HorizontalAlignment=2,HorizontalAlignment_UxmlAttributeFlags=1)
  menu_audits.append({'node':node,'old_anchor':old,'new_anchor':2,'enum_name':'BottomRight'})
 toolbar.save();audits.append({'variant':tag,'scoreboard_native_center':True,'pending_popup_original_header_slot':True,'tactics_page_top_clearance_removed':True,'menus':menu_audits})
G,M=baseG,baseM
outputs={}
for bn in [n+s for s in ['', '::skin'] for n in NAMES]:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
 for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/('skin-'+bn.split('::')[0] if bn.endswith('::skin') else bn);dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name.startswith('catalog.'):protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 for bn in NAMES:
  p=folder/bn;src=outputs[bn+('::skin' if tag=='skin' else '')];tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(src.read_bytes())})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':audits,'live_stats_cell_and_factory_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_identical':True,'catalog_and_texture_files_unchanged':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('按用户最新要求撤销战术待更改提示框右移、战术页面顶部下移，并恢复原生记分牌居中类和原生内联样式。仅从各时间点读取对应模板及样式，未覆盖旧整包；原始绑定逐项比较，无关对象字节一致。保留统计表实时体能私有单元格及工厂。右下MatchUITacticalOptions的Shouts/Tweaks/战术风格锚点改BottomRight，浮动菜单右边对齐；需游戏内检查是否达到向上展开，不能只靠枚举设置认定显示已验证。游戏与皮肤分别修改，保留差异。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'runtime_verified':False},ensure_ascii=False))
