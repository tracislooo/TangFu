exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-person-site-shells-'))
for bn in [W,G]:
 print(bn)
 for pid,o in objs[bn].items():
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if (any(k in n.lower() for k in ['background','personsite','playersite','personscreen','playerreport','persontool']) and not any(k in n.lower() for k in ['row','tooltip','block','detail','header','analysis','transfer','preview','injur','statistic'])):print(pid,n)
