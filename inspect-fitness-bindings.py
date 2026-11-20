exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
d=objects[5108509966786251923].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']}
for i in [1001,1002,1003]:print(i,json.dumps(sr[i]))
for i in [1028,1029,1030,1032,1033,1034,1104,1176,1064,1121,1110,1116,1192,1134,1178,1123]:
 a=sr[i]['data'];sd=sr[a['m_SerializedData']['rid']]['data'];print('NODE',i,a.get('m_Classes'),json.dumps(sd,ensure_ascii=False)[:2800])
