import sys,json,hashlib,re
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.enums import TextureFormat
P=R/'游戏更新后恢复243张图片-V54';m=json.loads((P/'恢复与校验记录.json').read_text('utf-8'))
e=UnityPy.load(str(P/'ui-backgrounds_assets_common.bundle'));af=e.assets[0]
meta=next(o for o in e.objects if o.type.name=='AssetBundle').read_typetree();containers=dict(meta['m_Container']);objs={o.path_id:o for o in e.objects}
def group(n):
 if n.startswith('FitnessPercentRing'):return '体能百分比环'
 if n in ['CA000','CA120','CA140','CA160','CA180']:return 'CA卡面'
 if n.startswith('CA') and n!='CAPAbg':return 'CA标记'
 if n.startswith('PA'):return 'PA进度条'
 if n.startswith('HIDEstats'):return '隐藏属性'
 if n.startswith('level'):return '等级图片'
 if n.startswith('90stats'):return '90stats徽章'
 if n=='CAPAbg':return 'CA/PA底图'
 if n.startswith('PlayerTop'):return '头部背景与光效'
 return '属性徽章 '+re.sub(r'\d+$','',n)
rows=[]
for t in m['textures']:
 o=objs[t['path_id']];assert o.peek_name()==t['name'];assert hashlib.sha256(o.get_raw_data()).hexdigest()==t['source_texture_sha256']
 c=containers[t['container_names'][0]];assert c['asset']=={'m_FileID':0,'m_PathID':t['path_id']}
 rows.append([group(t['name']),t['name'],str(t['path_id']),0,', '.join(t['container_names']),*t['size'],TextureFormat(t['texture_format_id']).name,t['texture_format_id'],t['mip_count'],str(t['decoded_alpha_range']),af.name,'ui-backgrounds_assets_common.bundle',c['preloadIndex'],c['preloadSize'],t['source_texture_sha256']])
game=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
snap=[]
for tag in ['gameworld','global']:
 p=game/f'ui-visualtreeassets_assets_{tag}visualtreeassetpreload.bundle';ee=UnityPy.load(str(p));a=ee.assets[0]
 matches=[i+1 for i,x in enumerate(a.externals) if af.name in x.path]
 snap.append([tag,a.name,str(matches) if matches else '未登记 backgrounds CAB',hashlib.sha256(p.read_bytes()).hexdigest()])
assert len(rows)==243 and len({r[2] for r in rows})==243
out={'rows':rows,'cab':af.name,'source':str(P/'恢复与校验记录.json'),'bundle':str(P/'ui-backgrounds_assets_common.bundle'),'hash':hashlib.sha256((P/'ui-backgrounds_assets_common.bundle').read_bytes()).hexdigest(),'target':str(game/'ui-backgrounds_assets_common.bundle'),'external':'archive:/'+af.name+'/'+af.name,'references':snap}
(R/'image-inventory-data.json').write_text(json.dumps(out,ensure_ascii=False),'utf-8')
print(json.dumps({'count':len(rows),'references':snap,'hash':out['hash']},ensure_ascii=False))
