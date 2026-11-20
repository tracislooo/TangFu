from pathlib import Path
import sys,json,struct
sys.path.insert(0,str(Path(__file__).parent/'.codex-deps'));import UnityPy
out=Path(sys.argv[1]);checks=[]
for prefix in ['', 'skin-']:
 env=UnityPy.load(str(out/(prefix+'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')))
 def tree(n):return next(o.read_typetree() for o in env.objects if o.type.name=='MonoBehaviour' and o.peek_name()==n)
 for side in ['Home','Away']:
  d=tree('HighlightNative'+side+'OOPHorizontal');assert any(m.get('from')=='inpossession' and m['to']['m_path']=='const.False' for r in d['references']['RefIds'] for m in r.get('data',{}).get('Mappings',[])),('OOP',side)
  assert any(u['path']!='f677caec43d6c1342b1bba39c5ae2c5f' for u in d['m_Usings'] if u['alias']=='tile-tall-4x6')
 stats=tree('HighlightRestoredNativeEightStats');rows=[r['data'] for r in stats['references']['RefIds'] if 'FactoryAsset' in r.get('data',{})];assert len(rows)==2 and all(r['FixedElementSize']==20 for r in rows)
 for n in ['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard','HighlightFormationCompactTitleTile']:tree(n)
 tiles=UnityPy.load(str(out/(prefix+'ui-tileslayouts_assets_all.bundle')))
 for n in ['PastMatchTeamReportGridComposition-Large','PastMatchTeamReportGridComposition-Large-FMC']:
  d=next(o.read_typetree() for o in tiles.objects if o.type.name=='MonoBehaviour' and o.peek_name()==n);cells=set()
  for b in d['m_gridComponents']:
   q=b['m_location']
   for x in range(q['x'],q['x']+q['width']):
    for y in range(q['y'],q['y']+q['height']):assert (x,y) not in cells;cells.add((x,y))
  assert len(cells)==200
  assert len(d['m_gridComponents'])==6
 # Check final catalog owner and explicit source-bundle dependencies for private rows.
 spec=__import__('importlib.util',fromlist=['spec_from_file_location']);s=spec.spec_from_file_location('catalog',Path(__file__).parent/'catalog-binary-v35.py');m=spec.module_from_spec(s);s.loader.exec_module(m)
 cat=m.Catalog((out/(('skin-' if prefix else 'game-')+'catalog.bin')).read_bytes())
 import uuid
 for n in ['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard','HighlightFormationCompactTitleTile']:
  guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/highlight-five-columns/'+n).hex;loc=cat.location(cat.locations(guid)[0]);assert 'globalvisualtreeassetpreload' in cat.location(loc['dependencies'][0])['internal'];assert loc['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
 checks.append({'variant':prefix or 'game','oop_fixed':True,'both_stats_tables_row_height':20,'compact_templates_present':True,'replay_grid_complete_without_overlap':True,'new_catalog_entries_valid':True})
(out/'verification-eight-items.json').write_text(json.dumps({'checks':checks,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
(out/'修改说明.md').write_text('八项调整：号码底板直接读取卡片现有kit.BackgroundColour；两侧表格行高20；第二轮播页私有作用域固定无球；阵型标题11并让球场使用可用空间；替补超过11时整张卡片75%且列表单元宽度同步缩小；体能圆环移至头像右下角；历史/回放报告大屏两套复用当前赛后报告网格，取消额外三张图表卡片并增加历史球员头像；回放专用播放控件右移。\n文件检查：序列化回读、未指定对象一致性、新模板目录登记及原所属包依赖、网格覆盖与无重叠。未完成游戏内验证：号码颜色、球场伸展、替补人数切换及回放中/结束后实际显示。\n恢复运行同目录restore.ps1。\n','utf8')
print(json.dumps({'passed':True,'checks':checks,'runtime_verified':False}))
