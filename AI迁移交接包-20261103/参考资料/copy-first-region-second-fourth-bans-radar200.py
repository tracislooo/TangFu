from pathlib import Path
import ast,copy,json
s=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8').split('ROW=-940000000006000;')[0].replace('photo-up3-titled-pros-cons-tactics-thirds-','copy-first-region-second-fourth-bans-radar200-')
exec(compile(s,'backup-and-helpers','exec'))
serial=lambda r,i:r[r[i]['data']['m_SerializedData']['rid']]
helper=ast.parse(Path('fourth-left-large-portrait-no-hidden.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['subtree_refs','remove_tree','import_subtree']],type_ignores=[]),'subtree-import','exec'))

def stretch(i):override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,px(0)),prop(131096,px(0)),prop(131094,pct(100)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(458768,en('hidden'))])
def fixed(i,h):override(rr[i]['data'],[prop(131087,px(h)),prop(131096,px(h)),prop(131094,px(h)),prop(131085,num(0))])
def save(pid,sid):
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet
source=-930000000001001;audits=[]
for pid,sid in [(-930000000001003,-930000000001002),(-940000000012000,-940000000012001)]:
 doc=objs[W][pid].read_typetree();sheet=objs[W][sid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 if pid==-930000000001003:
  remove_tree(6298)
  # Keep the second version's statistics at the top and contain the copied alternative beneath it.
  sc=rr[1703]['data']['m_SerializedData']['rid'];new=copy.deepcopy(serial(old,1011));new['rid']=sc;new['data'].update(uxmlAssetId=rr[1703]['data']['m_Id'],name='SecondOverviewRightContainedArea',name_UxmlAttributeFlags=1);rr[sc].clear();rr[sc].update(new);rr[1703]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
  for i in [1703,1011]:
   override(rr[i]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131085,num(1)),prop(131084,num(1)),prop(458768,en('hidden')),prop(131083,en('column'))])
  override(rr[1011]['data'],[prop(131082,px(0))])
  target=1011
 else:
  # Preserve the native bans and radar before removing the old tactics and icon-only report.
  radar=rr[1026]['data'];rr[radar['m_Parent']['rid']]['data']['m_Children'].remove({'rid':1026});radar['m_Parent']={'rid':6298};rr[6298]['data']['m_Children'].append({'rid':1026})
  remove_tree(named('FourthOverviewConditionalTacticalHalf'))
  remove_tree(named('FourthOverviewConditionalProsCons30Percent'))
  assert rr[6298]['data']['m_Children']==[{'rid':6228},{'rid':1026}]
  assert rr[1173]['data']['m_Children']==[]
  for i in [6298,6228,1026,1043]:fixed(i,200)
  override(rr[6298]['data'],[prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131083,en('row')),prop(458768,en('hidden'))])
  for i,grow in [(6228,2),(1026,3)]:override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(grow)),prop(131085,num(1)),prop(131091,px(0)),prop(131092,px(0))])
  stretch(1173);override(rr[1173]['data'],[prop(131083,en('column'))])
  target=1173
 # Each removed module was the only user of these aliases on its page.
 doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias'] not in ['OverviewTitledProsConsIcons','RightMiddleTacticalEffectiveness']]
 imported=import_subtree(source,6298,target);root=imported[6298];stretch(root)
 # Preserve all source condition/description bindings, and native template references, after ID remapping.
 assert rr[root]['data']['m_Children']==[{'rid':imported[6310]}]
 assert rr[imported[6310]]['data']['m_Children']==[{'rid':imported[6312]},{'rid':imported[6306]}]
 assert serial(rr,imported[6310])['data']['Binding']==serial(refs(objs[W][source].read_typetree()),6310)['data']['Binding']
 names=[rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name') for r in rr.values()]
 assert 'RightMiddleTacticalEffectiveness' not in names
 save(pid,sid);audits.append({'page':pid,'copied_source':source,'region_root':root,'copied_records':len(imported),'condition_unchanged':True})
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
(OUT/W).write_bytes(output)
report={'installed':False,'runtime_verified':False,'first_and_third_unchanged':True,'second_and_fourth_regions':audits,'fourth_second_row_height':200,'fourth_second_row_bans_radar_ratio':[2,3],'conditional_pros_or_transfers_and_favoured_copied':True,'transparent_cards_and_inner_scroll_preserved':True,'catalog_and_shared_components_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==GAME else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert (folder/W).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'second_and_fourth_regions_replaced':True,'fourth_row2_height':200,'bans_radar_ratio':'2:3'}))
