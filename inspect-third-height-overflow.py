exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-third-height-overflow-'))
doc=objs[W][-940000000010000].read_typetree();rr=refs(doc);sheet=objs[W][doc['inlineSheet']['m_PathID']].read_typetree()
def dump(i,depth=0):
 v=rr[i]['data'];s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});props=sheet['m_Rules'][v['m_RuleIndex']]['m_Properties'] if v.get('m_RuleIndex',-1)>=0 else [];pp=[]
 for p in props:
  if p['m_Id'] in [131087,131096,131094,131084,131085,131082,131090,131093,458768]:
   vs=[]
   for q in p['m_Values']:
    pool={2:'floats',3:'dimensions',7:'strings'}.get(q['m_ValueType']);vs.append(sheet[pool][q['valueIndex']] if pool else q)
   pp.append((p['m_Id'],vs))
 print(' '*depth,i,v.get('m_FullTypeName'),s.get('name'),pp,{k:s[k] for k in ['VerticalScrollerVisibility','HorizontalScrollerVisibility','ScrollViewMode'] if k in s})
 if depth<5:
  for c in v.get('m_Children',[]):
   if 'm_FullTypeName' in rr[c['rid']].get('data',{}):dump(c['rid'],depth+1)
dump(6322)
