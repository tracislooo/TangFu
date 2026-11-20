"""Stop forcing the unlicensed/default picture branch in the staff hover only."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, subprocess, sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
VF='6579775e848422d42a8a5ab277ded932'
PID=-1465827634544911600
sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/('staff-hover-real-photo-argument-'+stamp);OUT.mkdir()
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name!=W}
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
outputs={};audits=[];tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 en=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in en.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
 ob=obs[PID];old=ob.read_typetree();d=copy.deepcopy(old)
 assert d['m_Name']=='NonPlayerReportPreviewTooltip'
 rr={r['rid']:r for r in d['references']['RefIds']}
 images=[r for r in rr.values() if r.get('data',{}).get('name')=='StaffPortraitImage']
 assert len(images)==1
 row=images[0];v=row['data'];b=v['Binding'];assert b['m_visualFunction']['m_target']['m_guid']==VF
 raw=bytes(b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
 assert raw[0]==4
 args=[];p=1
 for _ in range(raw[0]):
  size=struct.unpack_from('<I',raw,p)[0];p+=4;args.append(raw[p:p+size]);p+=size
 assert p==len(raw)
 assert args[-1]==bytes([35])+b'SI.VisualScripting.BooleanVisualArg'+bytes([1]),args[-1]
 args[-1]=args[-1][:-1]+bytes([0])
 fixed=bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args)
 assert len(fixed)==len(raw)
 assert sum(a!=b for a,b in zip(raw,fixed))==1
 b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(fixed)
 expected=copy.deepcopy(old)
 er=next(r for r in expected['references']['RefIds'] if r['rid']==row['rid'])
 er['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(fixed)
 assert d==expected
 d['m_ContentHash']+=1
 meta=next(o.read_typetree() for o in en.objects if o.type.name=='AssetBundle')
 guid=next(k for k,e in meta['m_Container'] if e['asset']=={'m_FileID':0,'m_PathID':PID})
 cat=cm.Catalog(((folder.parent if tag=='game' else folder)/'catalog.bin').read_bytes());keys=dict(cat.keys())
 def locations(k):return [x for (x,) in cat.array(keys[k],'I')]
 vl=[i for i in locations(guid) if cat.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert len(vl)==1
 assert cat.location(cat.location(vl[0])['dependencies'][0])['internal'].endswith(W)
 assert vl[0] in locations('GameWorldVisualTreeAssetPreload')
 fl=[i for i in locations(VF) if cat.location(i)['type'][1]=='SI.VisualScripting.VisualFunction'];assert len(fl)==1
 owner=cat.location(cat.location(fl[0])['dependencies'][0])['internal'].replace(chr(92),'/').split('/')[-1]
 # The input is not a generic fallback flag: inspect the actual native function.
 vfenv=UnityPy.load(str((GAME if not (folder/owner).exists() else folder)/owner))
 vo={o.path_id:o for o in vfenv.objects};vm=next(o.read_typetree() for o in vfenv.objects if o.type.name=='AssetBundle')
 vp=next(e['asset'] for k,e in vm['m_Container'] if k==VF);assert vp['m_FileID']==0
 vd=vo[vp['m_PathID']].read_typetree()
 assert vd['m_inputs'][-1]['m_name']=='useDefaultPicture'
 assert any(r.get('data',{}).get('m_name')=='ConvertDynamicReferenceToAddressableID' and 'm_dataInUseDefaultPicture' in r.get('data',{}) for r in vd['references']['RefIds'])
 ob.save_typetree(d);payload=en.file.save(packer='lz4')
 checked={o.path_id:o for o in UnityPy.load(payload).objects};assert set(checked)==set(obs)
 for i,o in checked.items():
  if i==PID:assert o.read_typetree()==d
  else:assert sha(o.get_raw_data())==hashes[i],i
 out=OUT/tag/W;out.parent.mkdir();out.write_bytes(payload)
 backup=OUT/('backup-'+tag)/W;backup.parent.mkdir();backup.write_bytes(before[folder/W])
 outputs[folder/W]=payload
 tx.append({'target':str(folder/W),'source':str(out),'backup':str(backup),'before':sha(before[folder/W]),'after':sha(payload)})
 audits.append({'variant':tag,'hover_guid':guid,'node_rid':row['rid'],'function_name':vd['m_Name'],'input_name':'useDefaultPicture','before':True,'after':False,'argument_bytes_changed':1,'only_vta_and_content_hash_changed':True,'all_other_objects_byte_identical':True,'actual_function_type_owner_and_preload_verified':True})
report={'installed':False,'runtime_verified':False,'cause':'Previous direct staff portrait copied native default/unlicensed picture branch and forced useDefaultPicture=true. It did not request the actual person portrait.', 'audits':audits,'player_popups_and_shared_portrait_objects_unchanged':True,'protected_sha256':{str(p):h for p,h in protected.items()},'desktop_control_used':False}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
proc=subprocess.run([sys.executable,str(OUT/'installer.py'),str(OUT)],capture_output=True,text=True)
print(proc.stdout);print(proc.stderr)
assert proc.returncode==0,'Prepared patch could not be installed'
index={'manifest':str(OUT/'manifest.json'),'installed':True,'runtime_verified':False,'portrait':'direct native resource binding, useDefaultPicture=false','size':[180,180]}
(R/'current-staff-hover-portrait.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),'utf8')
note='\n- 2026-11-05：职员悬浮头像继续空白，经检查先前直接头像错误复制了原生默认/非授权图片分支，DynamicReferenceToAddressableID第4项显式useDefaultPicture=true，强制请求默认图。仅在游戏与独立皮肤NonPlayerReportPreviewTooltip的StaffPortraitImage中将其改false，每份仅1个参数字节及VTA内容哈希变化；180×180、personBind、本人资源参数、职员信息及球员弹窗/共享头像/样式/Highlight均保持。原生函数输入定义和实际调用节点核对，目录类型/首项所属包/预加载及序列化回读通过。安装记录'+OUT.name+'/manifest.json，索引current-staff-hover-portrait.json，restore.ps1带哈希保护。已安装，未启动游戏或控制桌面，是否正常显示仍待用户确认；此前true参数不应恢复。\n'
with (R/'AGENTS.md').open('a',encoding='utf8') as f:f.write(note)
print(json.dumps({'installed':True,'output':str(OUT),'files':2,'runtime_verified':False},ensure_ascii=True))
