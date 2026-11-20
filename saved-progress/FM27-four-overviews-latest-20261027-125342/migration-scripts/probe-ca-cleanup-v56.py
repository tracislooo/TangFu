import sys,json,re,hashlib,struct
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
old=json.loads((Path('游戏更新后恢复243张图片-V54')/'恢复与校验记录.json').read_text('utf8'))
ids={t['path_id']:t['name'] for t in old['textures'] if re.fullmatch(r'(ATT|DEF|FED|KIK|SPD|SPT|TCN)\d+',t['name']) or t['name'] in ['CA000','CA120','CA140','CA160','CA180']}
needles={i:struct.pack('<q',i) for i in ids}
report=[]
for folder in [GAME,SKIN]:
 for n in ['ui-backgrounds_assets_common.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
  p=folder/n
  if not p.exists():continue
  e=UnityPy.load(str(p));a=e.assets[0];rec={'path':str(p),'hash':hashlib.sha256(p.read_bytes()).hexdigest(),'cab':a.name,'externals':[(i+1,x.path) for i,x in enumerate(a.externals)],'textures':[],'references':[]}
  for o in e.objects:
   if o.type.name=='Texture2D':
    name=o.peek_name()
    if o.path_id in ids or name in ids.values():rec['textures'].append([str(o.path_id),name])
   elif any(v in o.get_raw_data() for v in needles.values()):
    try:t=o.read_typetree()
    except Exception as ex:rec['references'].append({'id':str(o.path_id),'error':str(ex)});continue
    found=[]
    def walk(v,path=''):
     if isinstance(v,dict):
      if 'm_PathID' in v and v['m_PathID'] in ids:found.append([path,ids[v['m_PathID']],str(v['m_PathID']),v.get('m_FileID')])
      for k,x in v.items():walk(x,path+'/'+k)
     elif isinstance(v,list):
      for i,x in enumerate(v):walk(x,path+'/'+str(i))
    walk(t)
    if found:rec['references'].append({'id':str(o.path_id),'type':o.type.name,'name':o.peek_name(),'links':found})
  report.append(rec);print(str(p),len(rec['textures']),len(rec['references']),flush=True)
Path('probe-ca-cleanup-v56.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for r in report:
 print(r['path'], 'textures',len(r['textures']),'links',sum(len(x.get('links',[])) for x in r['references']))
 print('non metadata',[(x.get('name'),x.get('id'),len(x.get('links',[]))) for x in r['references'] if x.get('type')!='AssetBundle'])
