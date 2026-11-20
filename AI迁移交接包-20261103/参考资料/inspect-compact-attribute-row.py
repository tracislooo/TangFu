exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-compact-attribute-row-'))
ab=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
for key,v in meta['m_Container']:
 if key=='aa5993dcecf4529d9fa280f078b11b0c':
  pid=v['asset']['m_PathID'];d=objs[G][pid].read_typetree();print('ROW',pid,d.get('m_Name'),d.get('inlineSheet'));rr=refs(d);sheet=objs[G][d['inlineSheet']['m_PathID']].read_typetree()
  for i,r in rr.items():
   v=r.get('data',{});ix=v.get('m_RuleIndex',-1)
   if 'm_FullTypeName' not in v:continue
   pp=[]
   for p in sheet['m_Rules'][ix]['m_Properties'] if ix>=0 else []:
    if p['m_Id'] in [131087,131096,131094]:
     q=p['m_Values'][0];pp.append((p['m_Id'],sheet['dimensions'][q['valueIndex']] if q['m_ValueType']==3 else q))
   print(i,v.get('m_FullTypeName'),v.get('m_Classes'),pp)
for pid in [-930000000001001,-930000000001003,-940000000010000,-940000000012000]:
 d=objs[W][pid].read_typetree();print('PAGE',pid,[u for u in d['m_Usings'] if 'AttributesTable' in u['alias']])
