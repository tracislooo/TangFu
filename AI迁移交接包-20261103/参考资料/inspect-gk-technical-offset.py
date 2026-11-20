exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-gk-technical-offset-'))
doc=objs[G][-930000000001003].read_typetree();rr=refs(doc);sheet=objs[G][doc['inlineSheet']['m_PathID']].read_typetree()
for i in [1011,1025,1063]:
 r=rr[i]['data'];s=rr.get(r.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print('NODE',i,r);print('SERIAL', {k:v for k,v in s.items() if k in ['name','FixedElementSize','Binding','RowTemplate']});print('STYLE',sheet['m_Rules'][r['m_RuleIndex']])
print('SHEET dimensions',sheet['dimensions'])
