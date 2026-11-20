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
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S');dest=R/'FM27-V27.0.4.zip';report={'package_version':'V27.0.4','created':stamp,'files':[{'path':arc,'size':p.stat().st_size,'sha256':h} for p,arc,h in files],'catalog_hash_verified':True,'active_custom_images':len(r['textures']),'image_registry_version':r['version'],'retired_images_absent':True,'contract_template_native_ids_preserved':True,'updated_since_previous_package':changed,'runtime_tested':False}
readme='''FM27 V27.0.4 完整修改包

游戏目录：F:/Steam/steamapps/common/Football Manager 27
包含14个bundle及配套catalog.bin、catalog.hash，共16个游戏文件，全部取自本次打包时的游戏安装目录。

安装：完全退出游戏，先备份自己安装目录中将被替换的文件，再把本包aa文件夹复制到游戏的fm_Data/StreamingAssets/下，合并并覆盖。catalog和bundle必须整套配套安装。恢复时使用你自己安装前的备份。

本包包含打包时已安装的全部后续修复和调整，包括合同模板控件ID修复。图片使用V74清单的178张有效自定义图片，PlayerTopBackground和PlayerTopBlueLight已移除。V27.0.4是本修改包版本标签。不得把其他版本的旧文件混入。
本包匹配当前本机游戏资源版本，其他游戏版本需重新适配。独立安装的外部头像/队徽图片包不包含在内。
已校验压缩包CRC、每个文件SHA256、catalog.hash、有效图片及禁用资源规则、合同模板ID；未启动游戏进行画面与交互测试。
文件校验清单.json列出当前文件哈希及相对上次完整包变动的bundle。
'''
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,arc,h in files:z.write(p,arc)
 z.writestr('VERSION.txt','V27.0.4\n');z.writestr('安装说明.txt',readme.encode('utf-8-sig'));z.writestr('文件校验清单.json',json.dumps(report,ensure_ascii=False,indent=2).encode('utf8'))
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for p,arc,h in files:assert sha(z.read(arc))==h,arc
assert all(sha(p.read_bytes())==h for p,arc,h in files),'Files changed during packaging'
print(json.dumps({'zip':str(dest),'size_mib':round(dest.stat().st_size/1024**2,1),'game_files':len(files),'updated_bundles':changed,'verified':True},ensure_ascii=False))
