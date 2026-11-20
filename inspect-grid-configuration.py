exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-grid-configuration-'))
d=objs[W][7857044477279960178].read_typetree();rr=refs(d)
for i in [1010,1038]:
 s=rr[rr[i]['data']['m_SerializedData']['rid']]['data'];print(i,json.dumps({k:v for k,v in s.items() if k not in ['InitialSelection','Binding']},ensure_ascii=False))
L='ui-tileslayouts_assets_all.bundle';e=UnityPy.load(str(GAME/L));oo={o.path_id:o for o in e.objects}
for pid in [3901662990989568885,1332213496068314481]:
 d=oo[pid].read_typetree();print(pid,json.dumps(d,ensure_ascii=False)[:9000])
