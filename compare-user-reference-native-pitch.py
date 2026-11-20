exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','compare-user-reference-native-pitch-'))
OLD=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');oo={bn:{o.path_id:o for o in UnityPy.load(str(OLD/bn)).objects} for bn in [W,G]}
for label,ob in [('REFERENCE',oo[W]),('CURRENT',objs[W])]:
 d=ob[4269476442492208794].read_typetree();rr=refs(d);s=ob[d['inlineSheet']['m_PathID']].read_typetree();print(label,'DOT')
 for i,r in rr.items():
  a=r.get('data',{})
  if 'm_FullTypeName' not in a:continue
  print(i,a['m_FullTypeName'],a.get('m_Classes'),s['m_Rules'][a['m_RuleIndex']]['m_Properties'] if a.get('m_RuleIndex',-1)>=0 else [])
for pid,o in oo[G].items():
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree()
 if 'references' not in d:continue
 rr=refs(d)
 for i,r in rr.items():
  a=r.get('data',{})
  if a.get('m_FullTypeName')=='FM.UI.FMTacticsPanel':
   sd=rr[a['m_SerializedData']['rid']]['data']
   if sd.get('PositionTemplateAsset',{}).get('m_AssetGUID')=='d6b3b3e4fa729864cbe89c7957538b2c':print('NATIVE PANEL',pid,d['m_Name'],i,{k:v for k,v in sd.items() if 'Size' in k or 'Width' in k or 'Length' in k or 'Scale' in k})
