import importlib.util,json,struct,sys
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
OUT=R/'独立小数选图75-v35'
objects={o.path_id:o for o in UnityPy.load(str(OUT/'aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')).objects}
t=objects[-910000000000301].read_typetree()
rs=t['references']['RefIds'];byclass={r['type']['class']:r['data'] for r in rs}
key=lambda v:bytes(v['m_idBytes']).hex()
entry=byclass['EntryNode'];bind=byclass['BindNode'];cast=byclass['TypedValueVisualFunctionLibrary_TryCastToFloat']
cmp=byclass['GeneralVisualFunction_CompareFloatFloat'];branch=byclass['GeneralVisualFunction_Branch']
inputs={s['m_name']:s for s in entry['m_dataSockets']}
assert entry['m_outputExecSocket']['m_destinationID']==bind['m_inputExecSocket']['m_id']
assert bind['m_dynamicDataInputSockets'][0]['m_sourceID']==inputs['Binding']['m_id']
assert bind['m_outputAsyncExecSocket']['m_destinationID']==cast['m_execInExecInput']['m_id']
assert cast['m_dataInValue']['m_sourceID']==bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0]['m_id']
assert cast['m_execOutExecOutput']['m_destinationID']==cmp['m_execInExecInput']['m_id']
assert cmp['m_dataInA']['m_sourceID']==cast['m_dataOutFloatValue']['m_id']
assert cmp['m_dataInB']['m_sourceID']==inputs['CompareInt']['m_id']
assert cmp['m_dataInOp']['m_sourceID']==inputs['ComparisonOperator']['m_id']
assert cmp['m_execOutExecOutput']['m_destinationID']==branch['m_execInExecInput']['m_id']
assert branch['m_dataInCondition']['m_sourceID']==cmp['m_dataOutBoolean']['m_id']
setters={key(r['data']['m_execInExecInput']['m_id']):r['data'] for r in rs if r['type']['class']=='BindableSwitchElement_SetVisibleIndex'}
assert setters[key(branch['m_execOutTrue']['m_destinationID'])]['m_dataInIndex']['m_defaultSocketValue']['m_value']==1
assert setters[key(branch['m_execOutFalse']['m_destinationID'])]['m_dataInIndex']['m_defaultSocketValue']['m_value']==0
get=byclass['VisualDataGetterNode']
assert get['m_dataSocket']['m_dataID']==next(s['m_id'] for s in t['m_inputs'] if s['m_name']=='Target')
for setter in setters.values():assert setter['m_target']['m_sourceID']==get['m_dataSocket']['m_id']
# Check script reference really resolves to the live game's VisualFunction MonoScript.
ms={o.path_id:o for o in UnityPy.load('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/f87a5c426c04c02c5c32c1ef21ae2ad6_monoscripts.bundle').objects}
script=ms[t['m_Script']['m_PathID']].read_typetree()
assert script['m_ClassName']=='VisualFunction' and script['m_Namespace']=='SI.VisualScripting'
af=objects[-910000000000301].assets_file
ext=af.externals[t['m_Script']['m_FileID']-1]
assert ext.path.split('/')[-1]==ms[t['m_Script']['m_PathID']].assets_file.name
print(json.dumps({'graph_connections':'verified','false_branch':0,'true_branch':1,'numeric_type':'System.Single','monoscript':script['m_Namespace']+'.'+script['m_ClassName']}))
