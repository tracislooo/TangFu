exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for k,v in doc.items():
 if k!='references':print(k,str(v)[:1800])
