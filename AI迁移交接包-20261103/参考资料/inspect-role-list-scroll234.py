exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-role-list-scroll234-'))
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 d=objs[G][pid].read_typetree();rr=refs(d);sheet=objs[G][d['inlineSheet']['m_PathID']].read_typetree();print('DOC',pid)
 table=next(i for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedTable' and rr[r['data']['m_SerializedData']['rid']]['data'].get('SelectedItemsBinding',{}).get('m_path')=='rolemask');s=rr[rr[table]['data']['m_SerializedData']['rid']]['data'];print('TABLE',table,{k:v for k,v in s.items() if any(x in k for x in ['Scroll','Size','Clamp','Truncate','Direction','Pagination']) and not k.endswith('UxmlAttributeFlags')})
 i=table
 while i>0:
  v=rr[i]['data'];sd0=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});ix=v.get('m_RuleIndex',-1);props=[]
  for p in sheet['m_Rules'][ix]['m_Properties'] if ix>=0 else []:
   if p['m_Id'] in [131087,131096,131094,131084,131085,131082,458768]:
    props.append((p['m_Id'],[(sheet[{2:'floats',3:'dimensions',7:'strings'}[q['m_ValueType']]][q['valueIndex']] if q['m_ValueType'] in [2,3,7] else q) for q in p['m_Values']]))
  print(i,sd0.get('name'),v.get('m_Classes'),props);i=v.get('m_Parent',{}).get('rid',-2)
