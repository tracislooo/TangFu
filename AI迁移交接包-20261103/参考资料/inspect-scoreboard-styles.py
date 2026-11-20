from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path.cwd()/'.codex-deps'))
import UnityPy
roots=[Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64'),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')]
for root in roots:
 rows=[]
 for o in UnityPy.load(str(root/'ui-styles_assets_default.bundle')).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  for rule in d.get('m_Rules',[]):
   if any(p['m_Value'] in ['centre-avoid-centred','match-header-scorebug','match-header'] for sel in rule['m_ComplexSelectors'] for s in sel['m_Selectors'] for p in s['m_Parts']):
    pools={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
    rows.append([d['m_Name'],rule['m_ComplexSelectors'],[(p['m_Id'],[d[pools[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pools else h for h in p['m_Values']]) for p in rule['m_Properties']]])
 print(str(root),json.dumps(rows,ensure_ascii=False))
