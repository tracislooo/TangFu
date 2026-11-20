exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
e=UnityPy.load(str(GAME/'ui-tileslayouts_assets_all.bundle'));oo={o.path_id:o for o in e.objects}
for pid in [7230795055274863540,1332213496068314481]:
 d=oo[pid].read_typetree();print(pid,json.dumps(d,ensure_ascii=False)[:6500])
