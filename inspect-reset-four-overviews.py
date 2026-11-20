from pathlib import Path
import sys,hashlib,json
sys.path.insert(0,'.codex-deps');import UnityPy
R=Path.cwd();snap=Path((R/'LATEST-FM27-PROGRESS.txt').read_text('utf8').splitlines()[0]);game=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');base=R/'updated-game-last-skin-migration-20261020-132948'/'backup-game';names=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle']
for n in names:
 envs=[UnityPy.load(str(p/n)) for p in [snap/'skin-tf27-01'/'packages',game,base]];obs=[{o.path_id:o for o in e.objects} for e in envs]
 print('BUNDLE',n,'counts',[len(o) for o in obs],'CAB',[e.assets[0].name for e in envs])
 def idx(o):
  m=next(x.read_typetree() for x in o.values() if x.type.name=='AssetBundle');return {k:v['asset']['m_PathID'] for k,v in m['m_Container'] if v['asset']['m_FileID']==0}
 oi,ni,bi=[idx(o) for o in obs];mods=[]
 for guid,pid in oi.items():
  if guid not in bi or obs[0][pid].type.name!='MonoBehaviour':continue
  baseline=obs[2][bi[guid]]
  if baseline.get_raw_data()!=obs[0][pid].get_raw_data() and baseline.read_typetree()!=obs[0][pid].read_typetree():mods.append({'guid':guid,'old_id':pid,'new_id':ni.get(guid),'name':obs[0][pid].peek_name(),'native_name':baseline.peek_name()})
 print('CUSTOM_NATIVE',json.dumps(mods,ensure_ascii=True))
 for pid in [7857044477279960178,1332213496068314481,3901662990989568885]:
  if pid in obs[0]:print('special',pid,obs[0][pid].peek_name(),pid in obs[1])
bg=UnityPy.load(str(game/'ui-backgrounds_assets_common.bundle'));textures=[o.peek_name() for o in bg.objects if o.type.name=='Texture2D'];print('BG',len(textures),'rings',sum(x.startswith('FitnessPercentRing') for x in textures),'CA',sum(x.startswith('CA') for x in textures))
