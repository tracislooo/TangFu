"""Focused checks of the frozen installation, with no resource writes."""
from pathlib import Path
import sys,json,ast,collections,hashlib,importlib.util,gc
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=sorted((R/'saved-progress').glob('FM27-current-state-audit-*'))[-1]
read=lambda p:json.loads(Path(p).read_text('utf-8-sig'))
def dump(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
results=[];details={}
def check(mode,feature,ok,evidence,limit='仅检查文件结构，未验证游戏内显示及交互'):
 results.append({'mode':mode,'feature':feature,'status':'文件检查通过' if ok else '需核查','evidence':evidence,'limit':limit})
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';V='ui-tableviews_assets_all.bundle'
native=Path(read(R/'current-game-update-comparison.json')['archive'])
native_w=next(iter(native.rglob(W)),None)
nativeobs={o.path_id:o for o in UnityPy.load(str(native_w)).objects} if native_w else {}
native_names={o.peek_name():o for o in nativeobs.values() if o.type.name=='MonoBehaviour'}
for mode in ['game','skin']:
 print('Focused',mode,flush=True);root=O/'snapshot'/mode/'StandaloneWindows64';cat=cm.Catalog((root.parent/'catalog.bin').read_bytes());keys=dict(cat.keys())
 envs={p.name:UnityPy.load(str(p)) for p in list(root.glob('ui-visualtreeassets*.bundle'))+[root/V]};obs={n:{o.path_id:o for o in e.objects} for n,e in envs.items()};trees={};byname={};guidmap={}
 for n,pool in obs.items():
  for pid,o in pool.items():
   if o.type.name=='MonoBehaviour':byname.setdefault(o.peek_name(),[]).append((n,pid))
   elif o.type.name=='AssetBundle':
    for k,v in o.read_typetree()['m_Container']:
     if v['asset']['m_FileID']==0:
      pid=v['asset']['m_PathID'];ob=pool.get(pid)
      if ob and ob.type.name=='MonoBehaviour':guidmap.setdefault(k,[]).append((n,pid))
 def tree(n,pid):
  if (n,pid) not in trees:trees[n,pid]=obs[n][pid].read_typetree()
  return trees[n,pid]
 def named(name):
  matches=byname.get(name,[])
  return tree(*matches[0]) if len(matches)==1 else None
 def flat(t):return json.dumps(t,ensure_ascii=False) if t else ''
 def refs(t):return {x['rid']:x.get('data',{}) for x in t.get('references',{}).get('RefIds',[])}
 # Resolve the actual installed nested template override paths.
 NAME='ContractNegotiationToolTemplate';GUID='5f191fc6eb99dde47a955456fecb83e6';target=named(NAME);consumer=named('ContractNegotiationTool');index={}
 def resolve(t,path,seen=None):
  if not path:return False
  elements={x['m_Id']:x for x in refs(t).values() if 'm_Id' in x};node=elements.get(path[0])
  if node is None:return False
  if len(path)==1:return True
  u=next((u for u in t.get('m_Usings',[]) if u['alias']==node.get('m_TemplateAlias')),None)
  if not u:return False
  candidates=[]
  for n,pid in guidmap.get(u['path'],[]):
   tr=tree(n,pid)
   if 'm_VisualTree' in tr:candidates.append(tr)
  return len(candidates)==1 and resolve(candidates[0],path[1:])
 audit=[]
 if target and consumer:
  aliases={u['alias'] for u in consumer.get('m_Usings',[]) if u['path']==GUID}
  for d in refs(consumer).values():
   if d.get('m_TemplateAlias') in aliases:
    ovs=d.get('m_SerializedDataOverride',[]);audit.append({'total':len(ovs),'resolved':sum(resolve(target,x['m_ElementIdsPath']) for x in ovs),'unresolved_paths':[x['m_ElementIdsPath'] for x in ovs if not resolve(target,x['m_ElementIdsPath'])]})
 check(mode,'提供合同页面模板覆盖路径',bool(audit) and all(x['total']==x['resolved'] for x in audit),audit)
 vp=obs[V].get(-991112000001000);vt=vp.read_typetree() if vp else {};cols=[x['m_columnID'] for x in vt.get('m_tableView',{}).get('m_tableConfig',[])]
 db=read(R/'current-player-database-views.json');check(mode,'数据库总览+隐藏',all(x in cols for x in ['hidden-current-ability','hidden-potential-ability','average-rating']) and all(db[k] in keys for k in ['new_view_guid','new_row_guid']),{'columns':cols,'guid_registered':{k:db[k] in keys for k in ['new_view_guid','new_row_guid']}})
 pages=[]
 for n,pid in byname.get('PlayerOverviewLeftTest',[]):pages.append({'pid':pid,'name':'PlayerOverviewLeftTest'})
 expected={}
 for fn in ['current-old-left-fc-hidden-overview.json','current-old-left-portrait-hidden-overview.json','current-old-left-portrait-nonhidden-overview.json','current-player-overview-approved-hidden-variants.json','current-approved-left-portrait-nonhidden-overview.json','current-middle-player-overview-layout.json','current-middle-portrait-hidden-layout.json','current-middle-portrait-nonhidden-layout.json']:
  def walk(v):
   if isinstance(v,dict):
    if isinstance(v.get('page'),int):expected[v['page']]={'title':v.get('title'),'index':fn}
    for x in v.values():walk(x)
   elif isinstance(v,list):
    for x in v:walk(x)
  walk(read(R/fn))
 for pid,ex in expected.items():
  ob=obs[W].get(pid);tr=tree(W,pid) if ob else {};rr=refs(tr)
  pages.append({'pid':pid,**ex,'present':bool(ob),'actual_name':tr.get('m_Name'),'nodes':sum('m_FullTypeName' in x for x in rr.values()),'component_elements':sum(x.get('m_FullTypeName','').endswith('ComponentElement') for x in rr.values()),'radar_node_count':sum('radar' in x.get('m_FullTypeName','').lower() for x in rr.values())})
 pages=[x for x in pages if 'present' in x];check(mode,'球员概览各版本页面对象',bool(pages) and all(x['present'] for x in pages),pages,'页面存在不证明选择器、数据上下文及画面全部正确；逐版游戏内确认仍待完成')
 header=named('PlayerReportHeader');nick=[x for x in refs(header or {}).values() if x.get('name')=='PlayerTouchbarNickname'];check(mode,'球员昵称快捷按钮',len(nick)==1 and nick[0].get('ActionId')==1295398490,{'nodes':nick})
 pref=named('ProcessingPreferencesBlock');pref_values=refs(pref or {}).get(1146,{}).get('ValueVariables',[]);check(mode,'继续按钮偏好键修复','continue_button_cycle_messages' in flat(pref_values),{'node_rid':1146,'value_variables':pref_values})
 nav=named('PrimaryNavigationBar');navrr=refs(nav or {});names=[x.get('name') for x in navrr.values() if x.get('name')];classes=sorted({c for x in navrr.values() for c in x.get('m_Classes',[])})
 check(mode,'顶部导航与度假快捷区',bool(nav) and any('holiday' in c for c in classes),{'node_names':names,'holiday_classes':[c for c in classes if 'holiday' in c]})
 # The latest native instructions deliberately replace older custom layouts.
 instruction_names=[n for n in native_names if n and (n=='InstructionTileBaseTemplate' or n.startswith('TeamInstructionTile') or n.startswith('PlayerInstructionGroup'))]
 instr=[]
 for name in instruction_names:
  t=named(name)
  if not t:instr.append({'name':name,'status':'missing'});continue
  a=native_names[name].read_typetree();b=t
  def strip(v):
   if isinstance(v,dict):return {k:strip(x) for k,x in v.items() if k not in {'m_ContentHash','m_Script'}}
   if isinstance(v,list):return [strip(x) for x in v]
   return v
  instr.append({'name':name,'status':'same_serialized_fields' if strip(a)==strip(b) else 'different_or_schema_changed'})
 check(mode,'球队/球员指令恢复新版原生',bool(instr) and not any(x['status']=='missing' for x in instr),instr,'存在性及字段比较；独立皮肤架构不同或后续底色修改会造成差异，差异不等于丢失')
 # Texture contents, not merely identities, against the authoritative actual bundle.
 registry=read(R/'current-custom-textures.json');source=Path(registry['authoritative_source_bundle']);bn=source.name
 be=UnityPy.load(str(root/bn));bo={o.path_id:o for o in be.objects};se=UnityPy.load(str(source));so={o.path_id:o for o in se.objects};tex=[]
 for x in registry['textures']:
  pid=int(x['path_id']);a=so.get(pid);b=bo.get(pid);ok=bool(a and b) and a.get_raw_data()==b.get_raw_data()
  tex.append({'name':x['name'],'pid':pid,'raw_texture_object_matches_authoritative_source':ok})
 check(mode,'自定义纹理内容与最新登记源',all(x['raw_texture_object_matches_authoritative_source'] for x in tex),{'checked':len(tex),'mismatches':[x for x in tex if not x['raw_texture_object_matches_authoritative_source']]},'比较Texture2D对象字节；不代替外置图片包或界面关联核对')
 details[mode]={'feature_results':results[-10:]}
 dump('focused-feature-checks.json',results)
 del envs,obs,be,bo,se,so,trees;gc.collect()
print(json.dumps([{'mode':x['mode'],'feature':x['feature'],'status':x['status']} for x in results],ensure_ascii=False),flush=True)
