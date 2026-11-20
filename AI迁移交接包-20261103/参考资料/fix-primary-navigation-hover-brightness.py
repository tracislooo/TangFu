"""Remove the added gray hover darkening without replacing current bundles."""
import ast,copy,datetime,hashlib,importlib.util,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<codec>','exec'))
TypeTreeHelper.write_value=write
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
S='ui-styles_assets_default.bundle';BG='ui-backgrounds_assets_common.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
before={f/S:(f/S).read_bytes() for f in [GAME,SKIN]}
protected={}
for folder in [GAME,SKIN]:
 for p in folder.glob('*.bundle'):
  if p.name!=S:protected[str(p)]=sha(p.read_bytes())
 for name in ['catalog.bin','catalog.hash']:
  p=(GAME.parent if folder==GAME else SKIN)/name
  if p.exists():protected[str(p)]=sha(p.read_bytes())
for n in ['AGENTS.md','current-custom-textures.json','reserved-texture-ids.json']:
 p=R/n;protected[str(p)]=sha(p.read_bytes())
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in reserved};bnames={t['name'].lower() for t in reserved}
for folder in [GAME,SKIN]:
 be=UnityPy.load(str(folder/BG));oo={o.path_id:o for o in be.objects};meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
 assert banned.isdisjoint(oo)
 assert all(o.peek_name().lower() not in bnames for o in oo.values() if o.type.name=='Texture2D')
 assert all(v['asset']['m_PathID'] not in banned and k.lower() not in bnames for k,v in meta['m_Container'])
 assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
 for t in registry['textures']:
  ob=oo[int(t['path_id'])];assert ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256'],t['name']
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
audits=[]
for folder in [GAME,SKIN]:
 c=cm.Catalog(((GAME.parent if folder==GAME else folder)/'catalog.bin').read_bytes());count=0
 for n in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
  ee=UnityPy.load(str(folder/n));oo={o.path_id:o for o in ee.objects};meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
  for guid,item in meta['m_Container']:
   ob=oo.get(item['asset']['m_PathID'])
   if not re.fullmatch('[0-9a-f]{32}',guid) or ob is None or ob.type.name!='MonoBehaviour' or not(-1000000000000000<ob.path_id<-900000000000000):continue
   d=ob.read_typetree();kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else 'SI.VisualScripting.VisualFunction' if 'm_nodes' in d else None
   if not kind:continue
   locs=[l for l in c.locations(guid) if c.location(l)['type'][1]==kind];assert locs
   for loc in locs:
    v=c.location(loc);assert v['internal']==guid and v['dependencies']
    assert c.location(v['dependencies'][0])['internal'].replace('\\','/').endswith('/'+n)
    assert any(c.location(l)['internal'].replace('\\','/').endswith('/'+BG) for l in v['dependencies'])
   count+=1
 audits.append({'folder':str(folder),'custom_templates_functions_verified':count})
payloads={};changes={}
for p,raw in before.items():
 e=UnityPy.load(raw);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()}
 ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
 d=ob.read_typetree();old=copy.deepcopy(d);fixed=[]
 for i,r in enumerate(d['m_Rules']):
  sels=r['m_ComplexSelectors'];txt=json.dumps(sels)
  if not sels or not all('fm27-fixed-nav-ink' in json.dumps(s) and 'hover' in json.dumps(s) and 'ContinueButton' not in json.dumps(s) for s in sels):continue
  ps=[q for q in r['m_Properties'] if q['m_Id']==458752]
  if not ps:continue
  assert len(ps)==1 and len(ps[0]['m_Values'])==1
  h=ps[0]['m_Values'][0];assert h['m_ValueType']==4
  previous=d['colors'][h['valueIndex']];assert abs(previous['r']-215/255)<1e-6,previous
  gray={k:(231/255 if k!='a' else 1.) for k in ['r','g','b','a']}
  import struct
  gray={k:struct.unpack('<f',struct.pack('<f',v))[0] for k,v in gray.items()}
  d['colors'].append(gray);h['valueIndex']=len(d['colors'])-1;fixed.append(i)
 assert len(fixed)==1,fixed
 wanted=copy.deepcopy(old)
 wanted['colors']=d['colors']
 for i in fixed:wanted['m_Rules'][i]=copy.deepcopy(d['m_Rules'][i])
 assert wanted==d
 ob.save_typetree(d);outbytes=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(outbytes).objects}
 assert set(saved)==set(oo)
 for pid,o in saved.items():
  if pid==ob.path_id:assert o.read_typetree()==d
  else:assert sha(o.get_raw_data())==hashes[pid],pid
 payloads[str(p)]=outbytes;changes[str(p)]={'sheet':ob.peek_name(),'path_id':str(ob.path_id),'rules':fixed,'hover_background':'#E7E7E7','unrelated_objects_identical':True}
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S');out=R/('primary-nav-hover-no-dimming-'+stamp);out.mkdir()
sources={};backups={}
for p,b in payloads.items():
 tag='game' if Path(p).parent==GAME else 'skin';(out/tag).mkdir();(out/('backup-'+tag)).mkdir()
 target=out/tag/S;target.write_bytes(b);backup=out/('backup-'+tag)/S;backup.write_bytes(before[Path(p)])
 sources[p]=str(target);backups[p]=str(backup)
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{p:sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'catalog_audits':audits,'active_textures_verified':len(registry['textures']),'retired_70_absent':True}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[S],'sources':sources,'before':backups},ensure_ascii=False,indent=2),'utf8')
(out/'installer.py').write_bytes((R/'install-primary-navigation-patch.py').read_bytes())
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'说明.md').write_text('取消先前顶部普通导航新增的悬停深灰反馈：hover背景由 #D7D7D7 改为 #E7E7E7，与常态一致。仅修改各目录当前 AlwaysAppliedStyleSheet 中一条专用规则的颜色句柄；文字、图标、透明度、事件、禁用与按下状态不变，湖蓝操作按钮的悬停渐变保留。其他资源和所有背景图片保持原样。文件读回及当前有效图片、禁用资源、目录登记核对通过；游戏内实际显示待启动后确认。','utf8')
print(json.dumps({'prepared':True,'output':str(out),'changes':changes,'active_textures_verified':len(registry['textures'])},ensure_ascii=False),flush=True)
