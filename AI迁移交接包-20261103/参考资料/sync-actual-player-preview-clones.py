from pathlib import Path
import sys,copy,json,ast,struct,datetime,hashlib,importlib.util
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
oldwrite=TypeTreeHelper.write_value;h=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in h.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<writer>','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};refs=lambda d:{r['rid']:r for r in d['references']['RefIds']};sha=lambda b:hashlib.sha256(b).hexdigest()
before={p/W:(p/W).read_bytes() for p in [GAME,SKIN]};protected={p:sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name!=W};outputs={};audit=[]
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
def collect(rr,start):
 seen=set()
 def scan(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    i=v['rid']
    if i!=-2 and i not in seen:seen.add(i);scan(rr[i]['data'])
   else:
    for k,x in v.items():
     if k!='m_Parent':scan(x)
  elif isinstance(v,list):
   for x in v:scan(x)
 scan({'rid':start});return seen
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in e.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};expected={}
 src=oo[-3760232355926433866].read_typetree();sr=refs(src);ss=oo[src['inlineSheet']['m_PathID']].read_typetree();keep=collect(sr,1010)
 assert any(r.get('data',{}).get('name')=='PopupStackedLeftColumn' for r in sr.values())
 for pid in [-970000000012000,-990000000060032]:
  o=oo[pid];d=o.read_typetree();old=copy.deepcopy(d);rr=refs(d);so=oo[d['inlineSheet']['m_PathID']];s=so.read_typetree();oldkeep=collect(rr,1010);outside=set(rr)-oldkeep;assert not (keep-{1010})&outside
  parent=rr[1010]['data']['m_Parent'];cache={}
  for rid in keep:
   r=copy.deepcopy(sr[rid]);a=r.get('data',{})
   if rid==1010:a['m_Parent']=parent
   index=a.get('m_RuleIndex',-1)
   if index>=0:
    if index not in cache:
     rule=copy.deepcopy(ss['m_Rules'][index]);rule['m_ComplexSelectors']=[]
     for p in rule['m_Properties']:
      for v in p['m_Values']:
       if v['m_ValueType'] in poolmap:
        pool=poolmap[v['m_ValueType']];value=copy.deepcopy(ss[pool][v['valueIndex']]);v['valueIndex']=len(s[pool]);s[pool].append(value)
     cache[index]=len(s['m_Rules']);s['m_Rules'].append(rule)
    a['m_RuleIndex']=cache[index]
   rr[rid]=r
  for rid in oldkeep-keep:del rr[rid]
  d['references']['RefIds']=list(rr.values())
  for rid in outside:assert rr[rid]==refs(old)[rid],('Icon or trigger changed',pid,rid)
  for u in src['m_Usings']:
   found=[v for v in d['m_Usings'] if v['alias']==u['alias']]
   if found:assert found[0]==u or u['alias']=='PlayerHeader','Unexpected clone-specific template alias'
   else:d['m_Usings'].append(copy.deepcopy(u))
  visited=set();ids=set()
  def walk(i):
   assert i not in visited;visited.add(i);a=rr[i]['data'];assert a['m_Id'] not in ids;ids.add(a['m_Id'])
   for c in a.get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']=={'rid':i};walk(c['rid'])
  walk(d['m_VisualTree']['rid']);assert all(r['rid'] in visited for r in rr.values() if 'm_Parent' in r.get('data',{}))
  for ob,data in [(o,d),(so,s)]:ob.save_typetree(data);expected[ob.path_id]=data
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(oo)
 for i,o in check.items():
  if i in expected:assert json.dumps(o.read_typetree(),sort_keys=True)==json.dumps(expected[i],sort_keys=True),i
  else:assert sha(o.get_raw_data())==hashes[i],i
 # Discover every embedded FC popup, rather than assuming there are only three paths.
 found=[]
 for o in check.values():
  if o.type.name=='MonoBehaviour' and b'Fixed_VerticalPositionPitch' in o.get_raw_data():
   assert b'PopupStackedLeftColumn' in o.get_raw_data(),o.peek_name();found.append(o.peek_name())
 assert len(found)==5,found
 c=cm.Catalog((GAME.parent/'catalog.bin' if folder==GAME else folder/'catalog.bin').read_bytes())
 for guid in ['e66d81290cb854d4877e005e29dcf6a3','5d818e9e8bd85d3ea164d7b0dc6ac7c1']:
  matches=[c.location(i) for i in c.locations(guid) if c.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert matches
  for v in matches:assert c.location(v['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
 outputs[folder/W]=b;audit.append({'folder':str(folder),'all_five_popup_templates_stacked':found,'modified_objects':list(expected),'icon_and_original_trigger_preserved':True,'other_world_objects_unchanged':len(oo)-len(expected)})
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S');out=R/('actual-player-preview-clones-fix-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:(out/('backup-'+tag+'.bundle')).write_bytes(before[folder/W])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'output':str(out),'root_cause':'Independent tactics white-icon and outside-match square-card popup clones retained old body layout while shared pitch updated','audits':audit,'other_bundles_unchanged':True};(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
note='\n\n## 2026-11-01 实际入口遗漏修复\n\n截图仍旧并排的原因已经定位：实际战术入口使用 `TacticsWhitePlayerReportPreview`（-970000000012000，GUID e66d81290cb854d4877e005e29dcf6a3），比赛外方形卡入口使用 `OutsideMatchSquare_PlayerReportPreviewTooltip`（-990000000060032，GUID 5d818e9e8bd85d3ea164d7b0dc6ac7c1）；它们独立复制了旧弹窗主体。此前只更新常规三入口，因而出现共用球场已横放、外层仍旧并排。本次仅把已确认的上下两栏主体同步到这两个私有副本，保留各自图标／触发／参数。以后P06必须扫描所有含FC球场的VTA，现有共5份都应包含明确左右栏；不能只按三个旧名称检查。脚本 `sync-actual-player-preview-clones.py`；记录 `'+out.name+'/manifest.json`。包内五份布局和目录校验通过，运行中游戏尚需重启加载确认。\n'
for name in ['球员弹窗最终版本说明.md','球员弹窗最新修改汇总与恢复步骤.md','球员位置模块统一恢复顺序.md']:
 p=R/name;(out/name).write_bytes(p.read_bytes());p.write_text(p.read_text('utf8')+note,'utf8')
p=R/'球员弹窗最终版本资源快照.json';(out/p.name).write_bytes(p.read_bytes());snap=json.loads(p.read_text('utf8'));current={o.path_id:o for o in UnityPy.load(outputs[GAME/W]).objects}
for pid,guid in [(-970000000012000,'e66d81290cb854d4877e005e29dcf6a3'),(-990000000060032,'5d818e9e8bd85d3ea164d7b0dc6ac7c1')]:
 t=current[pid].read_typetree();entry={'bundle':W,'name':t['m_Name'],'path_id_reference_only':pid,'container_keys':[guid],'tree':t,'inline_style':current[t['inlineSheet']['m_PathID']].read_typetree()};existing=next((i for i,a in enumerate(snap['assets']) if a['bundle']==W and a['path_id_reference_only']==pid),None)
 if existing is None:snap['assets'].append(entry)
 else:snap['assets'][existing]=entry
snap['bundles'][W]=sha(outputs[GAME/W]);snap['runtime_verified']=False;p.write_text(json.dumps(snap,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=True))
