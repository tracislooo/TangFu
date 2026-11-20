exec((__import__('pathlib').Path(__file__).parent/'inspect-club-overview-current.py').read_text('utf8').split('for n in [W,G,L]:')[0])
for name in sys.argv[1:] or ['ClubScreen','ClubSite','ClubSiteBlock','ClubSiteBlockMidRes','ClubSiteBlockLowRes','ClubScreenControlPanelBar']:
 d=json.loads((out/(name+'.json')).read_text('utf8'));s=json.loads((out/(name+'-style.json')).read_text('utf8'));rr={r['rid']:r for r in d['references']['RefIds']}
 print('\n',name,'usings',d['m_Usings'])
 def show(i,depth=0):
  x=rr[i]['data'];sd=rr.get(x.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  props={p['m_Id']:[s[{2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in [2,3,4,5,6,7,8] else v for v in p['m_Values']] for p in s['m_Rules'][x['m_RuleIndex']]['m_Properties']} if x.get('m_RuleIndex',-1)>=0 else {}
  detail={k:v for k,v in sd.items() if k in ['Mappings','Keys','BindingName','BindingType','ExpectedBindings','CustomCompositionId','GridComposition','GridElementSet']}
  if 'Bindings' in sd:detail['Bindings']={k:v for k,v in sd['Bindings'].items() if k in ['m_nameBindings','m_gridCompositionSet']}
  print(' '*depth,i,(x.get('m_TemplateAlias') or x.get('m_FullTypeName','')).split('.')[-1],sd.get('name',''),x.get('m_Classes'),props,detail)
  for ch in x.get('m_Children',[]):show(ch['rid'],depth+1)
 show(d['m_VisualTree']['rid'])
