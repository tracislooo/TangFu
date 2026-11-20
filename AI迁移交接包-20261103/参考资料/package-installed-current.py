from pathlib import Path
import json,hashlib,zipfile,datetime,sys
R=Path.cwd();AA=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa');O=R/'pinned-1-14-update-20261029-122441';base=json.loads((O/'manifest.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
files=[];changed=[]
for n,h in base['after_sha256'].items():
 p=AA/'StandaloneWindows64'/n;actual=sha(p.read_bytes());files.append((p,'aa/StandaloneWindows64/'+n,actual))
 if actual!=h:changed.append(n)
cat=(AA/'catalog.bin').read_bytes();assert (AA/'catalog.hash').read_text().strip()==hashlib.md5(cat).hexdigest()
for n in ['catalog.bin','catalog.hash']:
 p=AA/n;files.append((p,'aa/'+n,sha(p.read_bytes())))
r=json.loads((R/'current-custom-textures.json').read_text('utf8'));bg=AA/'StandaloneWindows64/ui-backgrounds_assets_common.bundle';assert sha(bg.read_bytes())==r['source_bundle_sha256']
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']+r.get('removed_textures',[]);ids={int(t['path_id']) for t in reserved};names={t['name'].lower() for t in reserved};ids.update([-910000000000001,-910000000000002,-910000000000146]);names.update(['playertopbackground','playertopbluelight','tf patch'])
en=UnityPy.load(str(bg));obs={o.path_id:o for o in en.objects};meta=next(o.read_typetree() for o in en.objects if o.type.name=='AssetBundle');assert ids.isdisjoint(obs);assert all(p['m_PathID'] not in ids for p in meta['m_PreloadTable']);assert all(k.lower() not in names and v['asset']['m_PathID'] not in ids for k,v in meta['m_Container'])
for t in r['textures']:assert int(t['path_id']) in obs and obs[int(t['path_id'])].peek_name()==t['name']
wn='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';we=UnityPy.load(str(AA/'StandaloneWindows64'/wn));doc=next(o.read_typetree() for o in we.objects if o.peek_name()=='ContractNegotiationToolTemplate');native=UnityPy.load(str(O/'backup-game'/wn));nd=next(o.read_typetree() for o in native.objects if o.peek_name()=='ContractNegotiationToolTemplate');nr={x['rid']:x for x in nd['references']['RefIds']}
for row in doc['references']['RefIds']:
 for field in ['m_Id','uxmlAssetId']:
  if field in row.get('data',{}):assert row['data'][field]==nr[row['rid']]['data'][field]
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');dest=R/('FM27-当前游戏已安装修改文件-'+stamp+'.zip');report={'created':stamp,'files':[{'path':arc,'size':p.stat().st_size,'sha256':h} for p,arc,h in files],'catalog_hash_verified':True,'active_custom_images':len(r['textures']),'image_registry_version':r['version'],'retired_images_absent':True,'contract_template_native_ids_preserved':True,'updated_since_previous_package':changed,'runtime_tested':False}
readme='FM27 当前游戏已安装修改文件\n\n本包全部游戏文件直接取自：\nF:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/\n包含14个bundle和配套catalog.bin、catalog.hash，共16个游戏文件。\n当前游戏未安装侧边栏，本包不加入侧栏归档、试装文件或书签预设。不包含整个游戏程序及外部独立头像、队徽图片包。\n\n安装方法：\n1. 完全退出游戏，先备份自己游戏中将被覆盖的文件。\n2. 将本包aa文件夹复制到游戏的fm_Data/StreamingAssets/下，合并并覆盖对应文件。\n3. catalog和bundle必须配套使用，不要混入旧版本。\n4. 需要回退时，用安装前自己的备份恢复。\n\n本包对应打包时本机的游戏资源版本；其他游戏版本需重新适配。\n保留当前已安装的BUG修复、背景、开始页视频/TFWX各50%布局，以及偏好设置图片网格修复和DY左/BB右布局。\n图片依据当前V75清单，共180张有效自定义图片。永久停用资源和已删除的TF patch、PlayerTopBackground、PlayerTopBlueLight不恢复。\n仅做文件完整性检查，未启动游戏进行视觉和交互验收。具体文件及SHA256见文件校验清单.json。\n'
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,arc,h in files:z.write(p,arc)
 z.writestr('安装说明.txt',readme.encode('utf-8-sig'));z.writestr('文件校验清单.json',json.dumps(report,ensure_ascii=False,indent=2).encode('utf8'))
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for p,arc,h in files:assert sha(z.read(arc))==h,arc
assert all(sha(p.read_bytes())==h for p,arc,h in files),'Files changed during packaging'
print(json.dumps({'zip':str(dest),'size_mib':round(dest.stat().st_size/1024**2,1),'game_files':len(files),'updated_bundles':changed,'verified':True},ensure_ascii=False))
