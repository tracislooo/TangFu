from pathlib import Path
import sys,ast,itertools,json
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';go={o.path_id:o for o in UnityPy.load(str(p/G)).objects};wo={o.path_id:o for o in UnityPy.load(str(p/W)).objects}
graph=go[-940000000013000].read_typetree();grefs=graph['references']['RefIds'];bind=next(r['data'] for r in grefs if r.get('type',{}).get('class')=='BindNode');bound=bind['m_outputAsyncExecSocket']['m_dataOutputSockets'];gid=lambda x:bytes(x['m_idBytes'])
src=ast.parse(Path('fourth-transfer-fallback-radar250.py').read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate'],type_ignores=[]),'truth-table','exec'))
for a,b in itertools.product([None,[],[1]],[None,[],[1]]):assert evaluate(a,b,None)==int(bool(a) or bool(b))
out=next(x for x in sorted(Path.cwd().glob('first-native-pros-cons-text-transfer-fallback-*'),reverse=True) if (x/'manifest.json').exists());base={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/W)).objects}
for pid in [-930000000001003,-940000000010000,-940000000012000]:assert wo[pid].get_raw_data()==base[pid].get_raw_data()
d=wo[-930000000001001].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};assert 6230 not in r
module=go[-940000000015000].read_typetree();mr={x['rid']:x for x in module['references']['RefIds']}
for i in [1008,1011]:
 s=mr[mr[i]['data']['m_SerializedData']['rid']]['data'];assert s['RowTemplate']['m_AssetGUID']=='d6b5a3f852c7d8b40892e4489465bbc4' and s['Direction']==0
verification={'passed':True,'availability_cases':9,'both_empty_uses_transfer':True,'native_text_rows_restored':True,'other_three_pages_unchanged':True,'runtime_verified':False};(out/'verification.json').write_text(json.dumps(verification,indent=2),'utf8');print(json.dumps(verification))
