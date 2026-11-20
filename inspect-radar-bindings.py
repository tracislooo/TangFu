exec(open('inspect-radar-relocation.py',encoding='utf8').read().split('dump(doc,objects')[0])
for i in [1001,1002,1003,1004,1005,1009,1025,1026,1043,1046,1064,1080,1081,1094,1013,1038,1173,1351,1349,1167,1169]:
 a=rr[i];sd=rr.get(a['data'].get('m_SerializedData',{}).get('rid'),{})
 print(i,json.dumps(a,ensure_ascii=False),json.dumps(sd,ensure_ascii=False))
