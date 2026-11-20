from pathlib import Path
import sys,json
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
L='ui-tileslayouts_assets_all.bundle'
out=R/'club-overview-inspection';out.mkdir(exist_ok=True)
for n in [W,G,L]:
 a=UnityPy.load(str(GAME/n)).assets[0]
 names={o.peek_name():o for o in a.objects.values() if o.type.name=='MonoBehaviour'}
 print(n,[x for x in names if ('Club' in x and any(q in x for q in ['Screen','Site','Overview','Composition']))])
 for name in ['HumanActionsControlPanelBlock','ClubSiteHeaderTemplate','ClubSiteHeaderSeasonInformationTemplate','ClubScreenOverviewBlockDescription','HumanActionsControlPanelBlockDescription','ClubCompositionSet','ClubComposition-Large-FMC','ClubComposition-Standard-FMC','ClubComposition-Small-FMC','ClubComposition-Large','ClubComposition-Standard','ClubComposition-Small']:
  if name not in names:continue
  ob=names[name];d=ob.read_typetree();s=a.objects[d['inlineSheet']['m_PathID']].read_typetree() if 'inlineSheet' in d else None
  (out/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  if not s:
   print(name,str(d)[:1200]);continue
  (out/(name+'-style.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
  rr={r['rid']:r for r in d['references']['RefIds']}
  pools={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
  def show(i,depth=0):
   x=rr[i]['data'];sd=rr.get(x.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   props={p['m_Id']:[s[pools[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in pools else v for v in p['m_Values']] for p in s['m_Rules'][x['m_RuleIndex']]['m_Properties']} if x.get('m_RuleIndex',-1)>=0 else {}
   detail={k:v for k,v in sd.items() if not k.endswith('UxmlAttributeFlags') and v and k not in ['uxmlAssetId','name','pickingMode']}
   print(' '*depth,i,x.get('m_TemplateAlias') or x.get('m_FullTypeName'),sd.get('name'),x.get('m_Classes'),props,detail)
   for ch in x.get('m_Children',[]):show(ch['rid'],depth+1)
  print('\nTREE',name,ob.path_id,'USINGS',d['m_Usings'])
  show(d['m_VisualTree']['rid'])
