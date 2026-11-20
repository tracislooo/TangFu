from pathlib import Path
import sys,json
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));root=Path(cfg['bundle_root'])
out=R/'club-dashboard-inspection';out.mkdir(exist_ok=True)
names=['ClubScreenOverviewBlock','ClubScreen','ClubSiteBlock','ClubSiteHeader','ClubSiteHeaderTemplate','ClubSiteHeaderSeasonInformationTemplate','ClubFacilitiesStadiumBlock','StadiumInfo','ClubFinancesSummaryBlock','ClubFinancesTile_4x4','ClubFinancesTile_4x2','ClubHistoryHonoursBlock','ClubHistoryHonours_4x4','ClubStatsBlock','ClubStatsShortBlock','ClubStatsTile_4x2','ClubComposition-Large','ClubComposition-Standard','ClubComposition-Small','ClubScreenOverviewBlockDescription']
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for short in ['gameworldvisualtreeassetpreload','globalvisualtreeassetpreload','TILES']:
 fn='ui-tileslayouts_assets_all.bundle' if short=='TILES' else 'ui-visualtreeassets_assets_'+short+'.bundle'
 a=UnityPy.load((root/fn).read_bytes()).assets[0]
 if short=='gameworldvisualtreeassetpreload':print('Candidates:',[o.peek_name() for o in a.objects.values() if o.type.name=='MonoBehaviour' and any(x in o.peek_name().lower() for x in ['stadium','finances','honours','clubstats'])])
 for ob in a.objects.values():
  if ob.type.name!='MonoBehaviour' or ob.peek_name() not in names:continue
  d=ob.read_typetree();name=d['m_Name'];(out/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  print('\nDOC',name,ob.path_id)
  if 'inlineSheet' not in d:
   if 'm_gridComponents' in d:print('slots',[(s['m_elementID'],s['m_location']) for s in d['m_gridComponents']])
   continue
  s=a.objects[d['inlineSheet']['m_PathID']].read_typetree();(out/(name+'-style.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8');rr={x['rid']:x for x in d['references']['RefIds']}
  print('USINGS',[(u['alias'],u['path']) for u in d['m_Usings']])
  def walk(i,depth=0):
   x=rr[i]['data'];sd=rr.get(x.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   props={p['m_Id']:[s[pool[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in pool else v for v in p['m_Values']] for p in s['m_Rules'][x['m_RuleIndex']]['m_Properties']} if x.get('m_RuleIndex',-1)>=0 else {}
   detail={k:v for k,v in sd.items() if k in ['Mappings','Parameters','ImageBinding','Binding','TextureBinding','DebugDisplay','FixedElementSize']}
   detail={k:v for k,v in detail.items() if k!='Binding' or v.get('m_kind')==1}
   print(' '*depth,i,x.get('m_TemplateAlias',x.get('m_FullTypeName','').split('.')[-1]),sd.get('name',''),x.get('m_Classes'),props,detail)
   if 'm_components' in sd:
    for ptr in sd['m_components']:
     z=rr[ptr['rid']];print(' '*(depth+1),'COMP',z['type']['class'],{k:v for k,v in z['data'].items() if k in ['Parameters','Mappings','ValueVariables','ReferenceVariables']})
   for ch in x.get('m_Children',[]):walk(ch['rid'],depth+1)
  walk(d['m_VisualTree']['rid'])
