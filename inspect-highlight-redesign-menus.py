from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
root=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');out=Path('inspect-highlight-redesign')
e=UnityPy.load(str(root/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));os={o.path_id:o for o in e.objects};meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle')
for guid in ['616bd74bd3ba564ba459e7627c25eec2','d61a9fc4c1ad5964a6493db08ae392fb']:
 v=next(v for k,v in meta['m_Container'] if k==guid);ob=os[v['asset']['m_PathID']];t=ob.read_typetree();print('CAROUSEL',t['m_Name'],ob.path_id);(out/(t['m_Name']+'.json')).write_text(json.dumps(t,ensure_ascii=False,indent=1),'utf8')
e=UnityPy.load(str(root/'ui-tileslayouts_assets_all.bundle'));os={o.path_id:o for o in e.objects}
for name in ['LiveTableTileDescription','LatestScoresTileDescription','MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 ob=next((o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name),None)
 if not ob:print('missing',name);continue
 t=ob.read_typetree();(out/(name+'.json')).write_text(json.dumps(t,ensure_ascii=False,indent=1),'utf8');print(name,ob.path_id,json.dumps(t,ensure_ascii=False)[:750])
print('DESCRIPTORS',[(o.path_id,o.peek_name()) for o in e.objects if o.type.name=='MonoBehaviour' and any(x in (o.peek_name() or '') for x in ['LiveTable','LatestScores'])])
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');print('CACHE',[(p.name,p.stat().st_size) for p in cache.glob('*') if p.name.startswith('MatchExperience')])
