exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
for f in p.glob('ui-icons*.bundle'):
 e=UnityPy.load(str(f))
 if any(a.name=='CAB-a3a70b4698bf88030ad46480ea0c2413' for a in e.assets):
  print(f)
  o=next(x for x in e.objects if x.path_id==-5959038453500707990);v=o.read();print(o.type, v.image.size,v.image.getcolors(65536)[:6])
