"""Restore the native carousel only; never restore a complete old bundle."""
from pathlib import Path
import json,copy
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-native-six-page-carousel-').replace('NAMES=[W,G,M,F]','NAMES=[G]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
exec(compile(boot,'backup-current-native-carousel-repair','exec'))
baseline=R/'highlight-six-page-persistent-selection-20261028-220017/backup-game'/G
oldenv=UnityPy.load(str(baseline));oldobjs={o.path_id:o for o in oldenv.objects};audits=[]
for side,pid in [('Home',-981028000007000),('Away',-981028000007010)]:
 src=oldobjs[pid];tree=copy.deepcopy(src.read_typetree());style=copy.deepcopy(oldobjs[tree['inlineSheet']['m_PathID']].read_typetree())
 assert tree['m_Name']=='HighlightLower'+side+'SixPageCarousel'
 pointer_remap(tree,src.assets_file,objs[G][pid].assets_file)
 pointer_remap(style,src.assets_file,objs[G][pid].assets_file)
 import_types(src.assets_file,objs[G][pid].assets_file,tree['references']['RefIds'])
 doc=Doc(G,pid=pid,tree=tree,style=style)
 natives=[i for i,r in doc.r.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableCarouselTileRoot']
 assert len(natives)==1
 root=natives[0];children=doc.a(root)['m_Children'];assert len(children)==6
 assert not any(r.get('data',{}).get('m_FullTypeName') in ['SI.Bindable.SIButton','SI.Bindable.ButtonGroup','SI.Bindable.TabGroup','SI.UI.SwitchElement'] for r in doc.r.values())
 assert doc.data(root)['PageIndicatorElementName']==''
 assert doc.data(root)['SharedPersistenceID']=='TF27.Highlight.Lower.'+side+'.SixPages.v1'
 guids={u['alias']:u['path'] for u in doc.d['m_Usings']}
 page_guids=[guids[doc.a(c['rid'])['m_TemplateAlias']] for c in children]
 assert page_guids[0]=='1ab3b171f1e25f8085d658e92ce964a4'
 assert page_guids[2:]==['c38af786a0ce00c40a23511259e88e19','8474a8838367004438fa336257d7dfb1','c2d724980d7f32b4b9005898db8174ba','dbda07217faf707419c93266465db7b8']
 doc.save();audits.append({'side':side,'native_carousel_count':1,'page_guids':page_guids,'custom_buttons_tabs_and_switches_removed':True,'native_indicator_position':'right 10px top 10px (unchanged game stylesheet)','selection_memory':'Native Session only; cross-restart persistence not implemented.'})
outputs={}
for bn in NAMES:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree
 for doc in documents:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/bn;dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name.startswith('catalog.'):protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for bn in NAMES:
  p=folder/bn;tx.append({'target':str(p),'source':str(outputs[bn]),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(outputs[bn].read_bytes())})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'wrappers':audits,'serialization_roundtrip':True,'all_other_objects_identical':True,'no_new_assets_or_catalog_changes':True,'cross_restart_persistence_implemented':False,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('撤回自写TabGroup、SwitchElement和12个圆点按钮，仅恢复两个已登记私有容器中的原生BindableCarouselTileRoot及其样式。保留六页原生引用和对应主客队绑定；原生carousel-page-indicator样式本身距右/顶部10px，不新增定位容器。当前G包的其他对象、统计表、阵型、上下布局、背景图、catalog全部不变。轮播原生记忆为Session（同次运行），重启后记忆尚未实现；不得记录为重启已验证或已实现。静态回读及无关对象一致性通过，运行内实际切换待游戏验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'native_carousels':2,'custom_selector_buttons':0,'cross_restart_persistence_implemented':False,'runtime_verified':False},ensure_ascii=False))
