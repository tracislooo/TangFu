from pathlib import Path
import json,hashlib,sys,struct,ast
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text(encoding='utf8'))
for folder in ['F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64','G:/Doc/FM Skin Builder/skins/tf27-01/packages']:
 for n,h in m['after_sha256'].items():assert hashlib.sha256((Path(folder)/n).read_bytes()).hexdigest()==h
objects={o.path_id:o for o in UnityPy.load(str(out/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
d=objects[-930000000001001].read_typetree();ss=objects[d['inlineSheet']['m_PathID']].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
helpers=ast.parse((R/'build-seven-badges-v39.py').read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['decode']],type_ignores=[]),'<codec>','exec'))
def named(n):return next(r for r in rr.values() if rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==n)
def props(r):
 ps={p['m_Id']:p['m_Values'][0] for p in ss['m_Rules'][r['data']['m_RuleIndex']]['m_Properties']}
 def get(i):
  h=ps[i];pool={3:'dimensions',4:'colors',6:'assets'}[h['m_ValueType']];return ss[pool][h['valueIndex']]
 return get
def select(i,raw):
 a=rr[i]['data'];sd=rr[a['m_SerializedData']['rid']]['data']
 if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  args=decode(sd['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack('<i',args[1][1])[0]
  return select(a['m_Children'][int(raw is not None and raw>limit)]['rid'],raw)
 return sd['name']
row=props(named('OverviewFitnessPercentRow'));panel=props(named('OverviewHiddenAttributesPanel'))
assert row(131104)['value']==170 and row(131105)['value']==210
assert row(131104)['value']+row(131087)['value']<=panel(131087)['value']
transitions=0
for idx,a in enumerate(m['metrics']):
 key=a['key'];cell=props(named('OverviewFitness_'+key));assert cell(131089)['value']==70*idx and cell(131105)['value']==70
 assert props(named('OverviewFitness_'+key+'_Title'))(65536)==props(named('OverviewCurrentReputationTitle'))(65536)
 # A -> B -> unavailable -> A verifies every selected serialized branch is independent of prior selections.
 for percent in [0,1,50,99,100,50,1,0,100]:
  raw=percent*a['raw_scale'];expected=f'OverviewFitness_{key}_Percent{percent:03}'
  assert select(named('OverviewFitness_'+key+'_Available')['rid'],raw)==expected
  leaf=named(expected);num=rr[leaf['data']['m_Children'][1]['rid']]
  assert rr[num['data']['m_SerializedData']['rid']]['data']['text']==str(percent)+'%'
  assert props(num)(65536)=={'r':1.,'g':1.,'b':1.,'a':1.}
  img=rr[leaf['data']['m_Children'][0]['rid']];assert props(img)(131105)['value']==props(img)(131087)['value']==34
  assert select(named('OverviewFitness_'+key+'_Available')['rid'],None)==f'OverviewFitness_{key}_Missing'
  transitions+=1
textures={o.peek_name():o for o in UnityPy.load(str(out/'ui-backgrounds_assets_common.bundle')).objects if o.type.name=='Texture2D'}
for p in range(101):
 im=textures[f'FitnessPercentRing{p:03}'].read().image
 assert im.size==(68,68) and im.convert('RGBA').getpixel((0,0))[3]==0
assert textures['FitnessPercentRing000'].read().image.tobytes()!=textures['FitnessPercentRing100'].read().image.tobytes()
print(json.dumps({'installed_hashes_match':True,'texture_count_verified':101,'layout_and_colors_verified':True,'serialized_value_transition_checks':transitions,'actual_game_runtime_verified':False}))
