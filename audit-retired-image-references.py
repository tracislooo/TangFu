from pathlib import Path
import sys,json,collections
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
folders={'game':Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64'),'skin':Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')}
terms=['ReportBlueLightBelowPlayerTopBackground','PlayerTopBackground','PlayerTopBlueLight']
result=[]
for label,folder in folders.items():
 for p in sorted(folder.glob('*.bundle')):
  if not any(s in p.name for s in ['ui-visualtreeassets','ui-styles','ui-backgrounds']):continue
  e=UnityPy.load(str(p));oo={o.path_id:o for o in e.objects}
  for o in e.objects:
   if o.type.name not in ['MonoBehaviour','Texture2D','AssetBundle']:continue
   d=o.read_typetree();txt=str(d) if o.type.name!='Texture2D' else str(d.get('m_Name'))
   hits=[t for t in terms if t in txt]
   if hits:
    row={'folder':label,'bundle':p.name,'pid':o.path_id,'name':d.get('m_Name'),'terms':hits}
    if 'm_Rules' in d:
     row['selectors']=[s for s in d.get('m_ComplexSelectors',[]) if any(t in json.dumps(s) for t in terms)]
     row['rules']=[(i,r) for i,r in enumerate(d['m_Rules']) if any(t in json.dumps(r) for t in terms)]
    elif 'inlineSheet' in d:
     row['nodes']=[r for r in d.get('references',{}).get('RefIds',[]) if any(t in json.dumps(r) for t in terms)]
    result.append(row)
   if 'm_Rules' not in d:continue
   for i,r in enumerate(d['m_Rules']):
    for prop in r['m_Properties']:
     if prop['m_Id']!=458753:continue
     for h in prop['m_Values']:
      if h['m_ValueType']==7:
       result.append({'folder':label,'bundle':p.name,'pid':o.path_id,'name':d.get('m_Name'),'enum_background':d['strings'][h['valueIndex']],'rule':i})
      if h['m_ValueType']==6:
       ptr=d['assets'][h['valueIndex']]
       if not ptr['m_PathID']:result.append({'folder':label,'bundle':p.name,'pid':o.path_id,'name':d.get('m_Name'),'null_image':ptr,'rule':i})
  print(label,p.name,flush=True)
(R/'retired-image-reference-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print('findings',len(result))
