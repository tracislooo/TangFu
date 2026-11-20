from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'))
import UnityPy
p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
e=UnityPy.load(str(p));obs={o.path_id:o for o in e.objects}
for o in obs.values():
 if o.type.name!='MonoBehaviour':continue
 n=o.peek_name()
 if not (n.startswith('TacticsPosition') or n in ['PlayerPortraitCell','TacticsOverview','TacticsOverviewScreen']):continue
 d=o.read_typetree();r={x['rid']:x for x in d['references']['RefIds']};sh=obs[d['inlineSheet']['m_PathID']].read_typetree()
 print('\nASSET',n,o.path_id,'USINGS',d['m_Usings'])
 def walk(i,dep=0):
  a=r[i].get('data',{});s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*dep,i,a.get('m_FullTypeName'),a.get('m_TemplateAlias'),json.dumps({k:v for k,v in s.items() if not k.endswith('UxmlAttributeFlags') and v not in [None,'',0,[],{},False]},ensure_ascii=True))
  if a.get('m_RuleIndex',-1)>=0: print(' '*dep,'STYLE',json.dumps(sh['m_Rules'][a['m_RuleIndex']]['m_Properties']))
  for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
 walk(d['m_VisualTree']['rid'])
