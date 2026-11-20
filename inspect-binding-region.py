exec(open('inspect-region.py',encoding='utf-8-sig').read().split('for i,r in rr.items():')[0])
for i in [1184,1219,1234,1236,2032,2038,2045,2057,2063,2067]:
 a=rr[i]['data'];s=rr[a['m_SerializedData']['rid']]['data'];print(i,s.get('name'),json.dumps(s.get('TextBinding'),ensure_ascii=False)[:700],a.get('m_Children'))
for i,r in rr.items():
 a=r.get('data',{});s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if a.get('m_TemplateAlias','').startswith('IdentityClub'):print(i,a,s.get('name'))
