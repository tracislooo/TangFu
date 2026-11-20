exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-gk-list-height-'))
doc=objs[G][-930000000001003].read_typetree();rr=refs(doc);sheet=objs[G][doc['inlineSheet']['m_PathID']].read_typetree()
def dump(i):
 r=rr[i]['data'];s=rr.get(r.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(i,r.get('m_FullTypeName'),{k:v for k,v in s.items() if k in ['name','FixedElementSize','FixedElementSizeControllerOrTouch','Binding','RowTemplate','DynamicElements','ScrollViewMode','VerticalScrollerVisibility']})
 for p in sheet['m_Rules'][r['m_RuleIndex']]['m_Properties'] if r.get('m_RuleIndex',-1)>=0 else []:
  if p['m_Id'] in [131087,131094,131096,131084,131085,131093,458768]:
   print(p['m_Id'],[(sheet[{2:'floats',3:'dimensions',7:'strings'}[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in [2,3,7] else v) for v in p['m_Values']])
 for c in r.get('m_Children',[]):
  if 'm_FullTypeName' in rr[c['rid']].get('data',{}):dump(c['rid'])
dump(1025);dump(1063)
