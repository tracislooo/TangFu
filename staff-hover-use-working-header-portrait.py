"""Use the complete portrait chain from the user-confirmed working staff page."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, subprocess, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'helpers','exec'))
TypeTreeHelper.write_value=write
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PID=-1465827634544911600
sha=lambda b:hashlib.sha256(b).hexdigest()
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/('staff-hover-working-header-chain-'+stamp);OUT.mkdir()
before={f/W:(f/W).read_bytes() for f in [GAME,SKIN]}
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in f.glob('*.bundle') if p.name!=W}
for f in [GAME.parent,SKIN]:
 for n in ['catalog.bin','catalog.hash']:protected[f/n]=sha((f/n).read_bytes())
se=UnityPy.load(before[GAME/W]);so={o.path_id:o for o in se.objects}
source=so[-4246927470610052519].read_typetree();sr={r['rid']:r for r in source['references']['RefIds']}
ss=so[source['inlineSheet']['m_PathID']].read_typetree()
using=copy.deepcopy(next(u for u in source['m_Usings'] if u['alias']=='PersonPicture'))
assert sr[1025]['data']['m_TemplateAlias']=='PersonPicture'
assert using['asset']['m_FileID']==0 and using['asset']['m_PathID']!=0
portrait=so[using['asset']['m_PathID']].read_typetree()
assert portrait['m_Name']=='ReportMiddleSquarePersonPicture'
source_ids=[1016,1019,1025]+[sr[i]['data']['m_SerializedData']['rid'] for i in [1016,1019,1025]]
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
audits=[];tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 en=UnityPy.load(before[folder/W]);obs={o.path_id:o for o in en.objects};hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
 ob=obs[PID];d=ob.read_typetree();old=copy.deepcopy(d);rr={r['rid']:r for r in d['references']['RefIds']}
 styleob=obs[d['inlineSheet']['m_PathID']];s=styleob.read_typetree();st=Styles(s)
 def sd(i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 oldroot=next(i for i in rr if sd(i).get('name')=='StaffPortraitResourceBinding')
 parent=rr[oldroot]['data']['m_Parent']['rid'];removed=set()
 def collect(i):
  removed.add(i);removed.add(rr[i]['data']['m_SerializedData']['rid'])
  for c in rr[i]['data']['m_Children']:collect(c['rid'])
 collect(oldroot);assert len(removed)==6
 nr=max(rr)+1;mapping={i:nr+j for j,i in enumerate(source_ids)}
 ni=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 ids={sr[i]['data']['m_Id']:ni+j for j,i in enumerate([1016,1019,1025])}
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:return {'rid':mapping.get(v['rid'],v['rid'])}
   return {k:remap(x) for k,x in v.items()}
  if isinstance(v,list):return [remap(x) for x in v]
  return v
 cache={}
 for i in source_ids:
  row=remap(copy.deepcopy(sr[i]));row['rid']=mapping[i];a=row.get('data',{})
  for k in ['m_Id','uxmlAssetId']:
   if k in a:a[k]=ids[a[k]]
  ix=a.get('m_RuleIndex',-1)
  if ix>=0:
   if ix not in cache:
    rule=copy.deepcopy(ss['m_Rules'][ix]);rule['m_ComplexSelectors']=[]
    for p in rule['m_Properties']:
     for h in p['m_Values']:
      if h['m_ValueType'] in poolmap:
       pool=poolmap[h['m_ValueType']];value=copy.deepcopy(ss[pool][h['valueIndex']]);h['valueIndex']=len(s[pool]);s[pool].append(value)
    cache[ix]=len(s['m_Rules']);s['m_Rules'].append(rule)
   a['m_RuleIndex']=cache[ix]
  rr[row['rid']]=row
 root=mapping[1016];rr[root]['data']['m_Parent']={'rid':parent}
 rr[parent]['data']['m_Children']=[{'rid':root} if c['rid']==oldroot else c for c in rr[parent]['data']['m_Children']]
 for i in removed:del rr[i]
 # Keep the complete header component and native mapping; give the hover its own frame.
 for i in [1016,1019,1025]:
  node=rr[mapping[i]]
  st.edit(node,[st.p(k,st.px(180)) for k in [131105,131087,131097,131096,131095,131094]]+[st.p(131084,st.num(0)),st.p(131085,st.num(0))])
 assert sd(mapping[1019])['Mappings']==sr[sr[1019]['data']['m_SerializedData']['rid']]['data']['Mappings']
 actual=copy.deepcopy(sd(mapping[1025]));original_sd=copy.deepcopy(sr[sr[1025]['data']['m_SerializedData']['rid']]['data'])
 actual['uxmlAssetId']=original_sd['uxmlAssetId'];assert actual==original_sd
 assert obs[using['asset']['m_PathID']].peek_name()==portrait['m_Name']
 d['m_Usings']=[copy.deepcopy(using) if u['alias']=='PersonPicture' else u for u in d['m_Usings']]
 d['references']['RefIds']=list(rr.values());d['m_ContentHash']+=1
 for i,r in {r['rid']:r for r in old['references']['RefIds']}.items():
  if i in removed:continue
  v=copy.deepcopy(rr[i])
  if i==parent:v['data']['m_Children']=r['data']['m_Children']
  assert v==r,('Unrelated hover content changed',i)
 # Shared portrait and both player/staff page templates remain byte-identical.
 keys_needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in rr.values() if r['type']['class']}
 known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in ob.assets_file.ref_types}
 for t in so[-4246927470610052519].assets_file.ref_types:
  key=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
  if key in keys_needed and key not in known:ob.assets_file.ref_types.append(copy.deepcopy(t));known.add(key)
 assert keys_needed<=known
 cat=cm.Catalog(((folder.parent if tag=='game' else folder)/'catalog.bin').read_bytes());keys=dict(cat.keys())
 locations=[i for (i,) in cat.array(keys[using['path']],'I') if cat.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert len(locations)==1
 assert cat.location(cat.location(locations[0])['dependencies'][0])['internal'].endswith(W)
 preload=[i for (i,) in cat.array(keys['GameWorldVisualTreeAssetPreload'],'I')];assert locations[0] in preload
 ob.save_typetree(d);styleob.save_typetree(s);payload=en.file.save(packer='lz4')
 check={o.path_id:o for o in UnityPy.load(payload).objects};assert set(check)==set(obs)
 for i,o in check.items():
  if i==PID:assert o.read_typetree()==d
  elif i==styleob.path_id:assert o.read_typetree()==s
  else:assert sha(o.get_raw_data())==hashes[i],i
 target=OUT/tag/W;target.parent.mkdir();target.write_bytes(payload)
 backup=OUT/('backup-'+tag)/W;backup.parent.mkdir();backup.write_bytes(before[folder/W])
 tx.append({'target':str(folder/W),'source':str(target),'backup':str(backup),'before':sha(before[folder/W]),'after':sha(payload)})
 audits.append({'variant':tag,'source':'current game NonPlayerReportHeader, user confirms page photo works','complete_frame_remapper_template_copied':True,'portrait_guid':using['path'],'portrait_path_id':str(using['asset']['m_PathID']),'native_mapping_and_template_serialized_data_identical':True,'hover_size':[180,180],'single_image_branch_removed':True,'all_other_objects_byte_identical':True,'portrait_owner_type_preload_verified':True})
report={'installed':False,'runtime_verified':False,'user_evidence':'Same staff member has a photo on the full page, but not in hover; earlier single-image fixes were ineffective.','audits':audits,'protected_sha256':{str(p):h for p,h in protected.items()},'desktop_control_used':False}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-independent-resource-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n",'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
proc=subprocess.run([sys.executable,str(OUT/'installer.py'),str(OUT)],capture_output=True,text=True);print(proc.stdout);print(proc.stderr)
assert proc.returncode==0,'Prepared; installation did not complete'
(R/'current-staff-hover-portrait.json').write_text(json.dumps({'manifest':str(OUT/'manifest.json'),'installed':True,'runtime_verified':False,'portrait':'complete portrait chain from user-confirmed working staff page','size':[180,180]},ensure_ascii=False,indent=2),'utf8')
note='\n- 2026-11-05：用户确认同一职员完整个人页有头像，但悬浮窗无头像；此前单图片绑定及useDefaultPicture参数调整均经用户反馈无效，不能记作成功修复。最新将当前游戏NonPlayerReportHeader实际使用的完整PersonPictureFrame→PictureTeamRemapper→PersonPicture三层接入两套NonPlayerReportPreviewTooltip，沿用个人页完整头像组件GUID/本地PPtr及原生传参，替代截取的单一图片分支；悬浮区独立180×180。仅两套悬浮VTA及样式修改，职员主页面/共享头像/球员弹窗/Highlight等其他对象字节保持；目录类型、所属包首项与预加载检查通过。记录'+OUT.name+'/manifest.json，索引current-staff-hover-portrait.json；已安装，restore.ps1带哈希保护。未启动游戏或控制桌面，实际显示仍待用户确认。\n'
with (R/'AGENTS.md').open('a',encoding='utf8') as f:f.write(note)
print(json.dumps({'installed':True,'output':str(OUT),'runtime_verified':False},ensure_ascii=True))
