from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
e=UnityPy.load(str(p/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));o={x.path_id:x for x in e.objects};d=o[-940000000010000].read_typetree();s=o[-940000000010001].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
for i in [1102,1114,1169,1703,1011,6298,1026,1043,1173,2242,1186,6286,2986,6304]:
 x=r[i]['data'];sd=r[x['m_SerializedData']['rid']]['data'];print(i,sd.get('name'),x.get('m_Children'))
 props=s['m_Rules'][x['m_RuleIndex']]['m_Properties'];pool={2:'floats',3:'dimensions',4:'colors',5:'strings',7:'strings'}
 print([(v['m_Id'],[(s[pool[t['m_ValueType']]][t['valueIndex']] if t['m_ValueType'] in pool else t) for t in v['m_Values']]) for v in props if v['m_Id'] in [131087,131096,131094,131084,131085,131082,131105,131088,131102,131104,131080]])
