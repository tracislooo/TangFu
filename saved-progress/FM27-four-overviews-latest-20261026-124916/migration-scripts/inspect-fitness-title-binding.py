exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
d=objects[-8181614945060108653].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']}
print(json.dumps(sr[1007],ensure_ascii=False));print('NODE',[(i,r['data'].get('m_FullTypeName')) for i,r in sr.items() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==1007])
d=objects[5775949770471550939].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
for r in rr.values():
 s=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 if s.get('name')=='HeaderFitnessSixMetrics':print('ORDER',[(c['rid'],rr[rr[c['rid']]['data']['m_SerializedData']['rid']]['data'].get('name')) for c in r['data']['m_Children']])
