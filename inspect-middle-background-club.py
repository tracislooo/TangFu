exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-middle-background-club-'))
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();print(pid,[u for u in doc['m_Usings'] if 'ReportIconsBelow' in u['alias']])
doc=objs[W][-940000000020000].read_typetree();rr=refs(doc);sheet=objs[W][doc['inlineSheet']['m_PathID']].read_typetree();print('PRIVATE',doc['inlineSheet'])
for i in [1148,1150,1154]:
 n=rr[i]['data'];s=rr[n['m_SerializedData']['rid']]['data'];print(i,s.get('name'),n.get('m_Classes'));print({k:v for k,v in s.items() if 'Binding' in k and not k.endswith('UxmlAttributeFlags')});print(sheet['m_Rules'][n['m_RuleIndex']])
