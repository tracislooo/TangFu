"""Repair the private staff hover actually referenced by name/icon cells."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, subprocess, sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
helpers=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'helpers','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PRIVATE='a86c2c3a1a935f6494217908265a8ce7'
sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/('staff-hover-active-private-route-'+stamp);OUT.mkdir()
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name!=W}
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
audits=[];tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 en=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in en.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
 header=obs[-4246927470610052519].read_typetree()
 using=copy.deepcopy(next(u for u in header['m_Usings'] if u['alias']=='PersonPicture'))
 # Independent skin header may already use an inline portrait; its existing using
 # still identifies the same complete private component as the working game page.
 assert using['asset']['m_FileID']==0
 assert obs[using['asset']['m_PathID']].peek_name()=='ReportMiddleSquarePersonPicture'
 meta=next(o.read_typetree() for o in en.objects if o.type.name=='AssetBundle')
 targets={e['asset']['m_PathID'] for k,e in meta['m_Container'] if k==PRIVATE and e['asset']['m_FileID']==0}
 assert len(targets)==2,targets
 callers=[]
 for o in obs.values():
  if o.type.name!='MonoBehaviour':continue
  tree=o.read_typetree()
  if 'inlineSheet' in tree and any(u['path']==PRIVATE for u in tree.get('m_Usings',[])):
   callers.append({'name':tree['m_Name'],'path_id':str(o.path_id)})
 assert any(x['name']=='NonPlayerIconNameCell' for x in callers)
 assert any(x['name']=='NonPlayerNameWNationalityCell' for x in callers)
 changed={};target_audits=[]
 for pid in sorted(targets):
  ob=obs[pid];d=ob.read_typetree();old=copy.deepcopy(d)
  assert d['m_Name']=='OutsideMatchSquare_NonPlayerReportPreviewTooltip'
  rr={r['rid']:r for r in d['references']['RefIds']}
  instance=rr[1024];assert instance['data']['m_TemplateAlias']=='PersonPicture'
  assert not instance['data']['m_SerializedDataOverride']
  old_using=copy.deepcopy(next(u for u in d['m_Usings'] if u['alias']=='PersonPicture'))
  assert old_using['path']!=using['path']
  d['m_Usings']=[copy.deepcopy(using) if u['alias']=='PersonPicture' else u for u in d['m_Usings']]
  instance['data']['m_Classes']=[]
  sid=d['inlineSheet']['m_PathID'];sob=obs[sid];s=sob.read_typetree();st=Styles(s)
  st.edit(instance,[st.p(k,st.px(180)) for k in [131105,131087,131097,131096,131095,131094]]+[st.p(131084,st.num(0)),st.p(131085,st.num(0))])
  expected=copy.deepcopy(old);expected['m_Usings']=copy.deepcopy(d['m_Usings'])
  er=next(r for r in expected['references']['RefIds'] if r['rid']==1024)
  for k in ['m_Classes','m_RuleIndex']:er['data'][k]=copy.deepcopy(instance['data'][k])
  assert d==expected,'Unexpected change to staff bindings/content'
  d['m_ContentHash']+=1
  for o,data in [(ob,d),(sob,s)]:o.save_typetree(data);changed[o.path_id]=data
  target_audits.append({'path_id':str(pid),'name':d['m_Name'],'old_portrait_guid':old_using['path'],'new_portrait_guid':using['path'],'portrait_local_path_id':str(using['asset']['m_PathID']),'size':[180,180],'all_serialized_person_contract_attribute_bindings_unchanged':True})
 cat=cm.Catalog(((folder.parent if tag=='game' else folder)/'catalog.bin').read_bytes());keys=dict(cat.keys())
 def ls(k):return [i for (i,) in cat.array(keys[k],'I')]
 for guid in [PRIVATE,using['path']]:
  vtas=[i for i in ls(guid) if cat.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert len(vtas)==1
  assert cat.location(cat.location(vtas[0])['dependencies'][0])['internal'].endswith(W)
  assert vtas[0] in ls('GameWorldVisualTreeAssetPreload')
 assert {e['asset']['m_PathID'] for k,e in meta['m_Container'] if k==PRIVATE and e['asset']['m_FileID']==0}<=set(changed)
 payload=en.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(payload).objects};assert set(check)==set(obs)
 for i,o in check.items():
  if i in changed:assert o.read_typetree()==changed[i]
  else:assert sha(o.get_raw_data())==hashes[i],i
 dest=OUT/tag/W;dest.parent.mkdir();dest.write_bytes(payload)
 backup=OUT/('backup-'+tag)/W;backup.parent.mkdir();backup.write_bytes(before[folder/W])
 tx.append({'target':str(folder/W),'source':str(dest),'backup':str(backup),'before':sha(before[folder/W]),'after':sha(payload)})
 audits.append({'variant':tag,'active_hover_guid':PRIVATE,'name_icon_callers':callers,'all_registered_private_hover_objects_patched':True,'targets':target_audits,'unrelated_objects_byte_identical':True,'original_hover_and_player_popups_unchanged':True,'catalog_types_owners_and_actual_preload_verified':True})
report={'installed':False,'runtime_verified':False,'cause_evidence':'Staff icon/name cells reference private GUID a86c2c3a1a935f6494217908265a8ce7, while earlier attempts modified native GUID 435b45f976d924542ba614581a0191d1. Both private registered copies still had the old outside-match portrait and thumbnail style.','previous_repairs_targeted_wrong_route':True,'audits':audits,'protected_sha256':{str(p):h for p,h in protected.items()},'desktop_control_used':False}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
proc=subprocess.run([sys.executable,str(OUT/'installer.py'),str(OUT)],capture_output=True,text=True);print(proc.stdout);print(proc.stderr)
assert proc.returncode==0,'Prepared; installation did not complete'
(R/'current-staff-hover-portrait.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'installed':True,'runtime_verified':False,'active_hover_guid':PRIVATE,'portrait':'working full staff-page portrait component in all registered private hover copies','size':[180,180]},ensure_ascii=False,indent=2),'utf8')
note='\n- 2026-11-05：用户重置布局后仍无头像，查明此前修错入口：多数职员姓名/图标单元格（含NonPlayerIconNameCell、NonPlayerNameWNationalityCell等）实际引用私有悬浮GUID a86c2c3a1a935f6494217908265a8ce7，而非此前修改的原生435b45f976d924542ba614581a0191d1。私有GUID在W容器两份对象-990000000060050/-950000000000069均仍为旧OutsideMatchSquare头像。现仅将两套资源中这两份私有悬浮的PersonPicture引用改为职员主页面完整组件13f75dc8f7df868150944efb2b46036c及其本地PPtr，实例180×180、移除缩略图类，原姓名/合同/属性/事件及球员弹窗保持；未改共享头像。实际调用者→私有GUID→所有容器副本→头像组件、本地对象/目录类型/所属包首项/预加载均检查通过。补丁'+OUT.name+'/manifest.json已安装，索引current-staff-hover-portrait.json；restore.ps1带哈希保护。此前参数/单图/原生模板修改未解决用户实际问题，不应视为有效修复。未启动游戏或操作桌面，实际显示待用户确认。\n'
with (R/'AGENTS.md').open('a',encoding='utf8') as f:f.write(note)
print(json.dumps({'installed':True,'output':str(OUT),'active_route':PRIVATE,'target_copies_per_variant':2,'runtime_verified':False},ensure_ascii=True))
