import sys,json,hashlib
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
O=R/'outputs/fm27-resource-inventory-20261023';O.mkdir(parents=True,exist_ok=True)
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BASE=R/'restore-approved-four-overviews-20261022-134518/backup-game'
names=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle','ui-backgrounds_assets_common.bundle']
images=json.loads((R/'image-inventory-data.json').read_text('utf-8'))
image_ids={int(r[2]) for r in images['rows']}
ui=[];graphics=[];bundles=[];styles=[]
for name in names:
 p=G/name;e=UnityPy.load(str(p));obs={o.path_id:o for o in e.objects};be=UnityPy.load(str(BASE/name));old={o.path_id:o for o in be.objects}
 cab=e.assets[0].name;meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle');keys={}
 for key,v in meta['m_Container']:keys.setdefault(v['asset']['m_PathID'],[]).append(key)
 selected=[]
 for pid,o in obs.items():
  if o.type.name=='AssetBundle':continue
  status='新增' if pid not in old else ('修改' if o.get_raw_data()!=old[pid].get_raw_data() else '')
  if name==names[3] and pid in image_ids and not status:status='已有自定义图片（沿用）'
  if not status:continue
  t=o.read_typetree();n=t.get('m_Name','');sid=t.get('inlineSheet',{}).get('m_PathID',0);fid=t.get('inlineSheet',{}).get('m_FileID',0)
  stylecab=cab if not fid else e.assets[0].externals[fid-1].path
  kind='界面组件' if 'm_VisualTree' in t else ('内联样式' if 'm_Rules' in t else o.type.name)
  row=[n,str(pid),str(sid) if sid else '不适用',cab,name,kind,status,'; '.join(keys.get(pid,[])),stylecab if sid else '不适用']
  if kind=='内联样式':styles.append(row)
  elif o.type.name=='Texture2D':graphics.append(row+[t.get('m_Width',''),t.get('m_Height','')])
  else:ui.append(row)
  selected.append(pid)
 bundles.append([name,cab,str(p),str(S/name),hashlib.sha256(p.read_bytes()).hexdigest(),len(selected),'一致' if (S/name).exists() and p.read_bytes()==(S/name).read_bytes() else '不同或不存在'])
 print(name,len(selected),flush=True)
# Record the earlier font replacement using its manifest, and verify that each object exists now.
fm=R/'font-replacement-20261018-000452/manifest.json'
fontmanifest=json.loads(fm.read_text('utf-8')) if fm.exists() else {}
(O/'font-manifest-source.json').write_text(json.dumps(fontmanifest,ensure_ascii=False,indent=2),'utf-8')
for entry in fontmanifest.get('bundles',[]):
 p=G/entry['name'];e=UnityPy.load(str(p));obs={o.path_id:o for o in e.objects};cab=e.assets[0].name
 matched=hashlib.sha256(p.read_bytes()).hexdigest()==entry['after_sha256']
 for pid in entry['changed_objects']:
  o=obs[pid];t=o.read_typetree()
  graphics.append([t.get('m_Name',''),str(pid),'不适用',cab,p.name,o.type.name,'字体替换（历史记录，整包哈希匹配）' if matched else '字体替换历史记录（当前哈希不同）','','不适用',t.get('m_Width',''),t.get('m_Height','')])
 bundles.append([p.name,cab,str(p),str(S/p.name),hashlib.sha256(p.read_bytes()).hexdigest(),len(entry['changed_objects']),'一致' if (S/p.name).exists() and p.read_bytes()==(S/p.name).read_bytes() else '皮肤包中无同名包或不一致'])
pages={'-930000000001001':0,'-930000000001003':1,'-940000000010000':2,'-940000000012000':3}
ui.sort(key=lambda r:(pages.get(r[1],99) if r[4]==names[0] else 99,r[4],r[0]))
config=[]
for p,label in [(G.parent/'catalog.bin','资源目录'),(G.parent/'catalog.hash','目录校验'),(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large'),'已保存布局')]:
 if p.exists():config.append([p.name,label,'不适用','不适用','不适用',str(p),hashlib.sha256(p.read_bytes()).hexdigest()])
data={'ui':ui,'styles':styles,'graphics':graphics,'bundles':bundles,'config':config,'baseline':str(BASE),'game':str(G),'date':'2026-10-23'}
(O/'inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:len(data[k]) for k in ['ui','styles','graphics','bundles','config']}))
