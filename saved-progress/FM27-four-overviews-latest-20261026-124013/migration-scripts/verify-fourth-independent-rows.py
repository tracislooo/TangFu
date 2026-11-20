from pathlib import Path
import sys,ast,itertools,json
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';go={o.path_id:o for o in UnityPy.load(str(p/G)).objects};graph=go[-940000000013010].read_typetree();grefs=graph['references']['RefIds'];bind=next(r['data'] for r in grefs if r.get('type',{}).get('class')=='BindNode');bound=bind['m_outputAsyncExecSocket']['m_dataOutputSockets'];gid=lambda x:bytes(x['m_idBytes'])
src=ast.parse(Path('fourth-transfer-fallback-radar250.py').read_text('utf-8-sig'));fn=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate');code=ast.unparse(fn).replace("elif c == 'BindableSwitchElement_SetVisibleIndex':", "elif c == 'IBindableVisible_Show':").replace("return val(d, 'm_dataInIndex')", "return val(d, 'm_dataInShouldShow')");exec(code)
cases=0
for pros,cons,err in itertools.product([None,[],[1]],[None,[],[1]],[None,True,False,0]):
 assert evaluate(pros,cons,err)==int(bool(pros) or bool(cons) or (type(err)is bool and not err));cases+=1
wo={o.path_id:o for o in UnityPy.load(str(p/W)).objects};d=wo[-940000000012000].read_typetree();rs={x['rid']:x for x in d['references']['RefIds']};assert [x['rid'] for x in rs[6298]['data']['m_Children']][0]==6228;assert [x['rid'] for x in rs[1173]['data']['m_Children']][0]==1026
names=[rs.get(x.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name') for x in rs.values()];assert 'FourthOverviewContentOrTransferSwitch' not in names;assert 'FourthOverviewTransferStatusFallback' not in names
out=next(p for p in sorted(Path.cwd().glob('fourth-bans-tactics-radar-pros-rows-*'),reverse=True) if (p/'manifest.json').exists());base={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/W)).objects}
for pid in [-930000000001001,-930000000001003,-940000000010000]:assert wo[pid].get_raw_data()==base[pid].get_raw_data()
audit={'verified':True,'availability_truth_cases':cases,'first_three_pages_unchanged':True,'transfer_fallback_removed':True,'independent_rows':True,'runtime_verified':False};(out/'verification.json').write_text(json.dumps(audit,indent=2),'utf8');print(json.dumps(audit))
