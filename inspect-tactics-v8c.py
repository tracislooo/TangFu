from pathlib import Path
exec(Path('inspect-tactics-v8.py').read_text('utf8').split('for pid in [312759')[0])
for pid,node in [(-966834888143150418,1004),(-970000000009000,1022),(-970000000010000,1027)]:
 d=objs[pid].read_typetree();r=refs(d)
 print('SPECIAL',pid,node,json.dumps(serial(r,node)['data'],ensure_ascii=False))
 if node!=1004:
  def sub(i):
   print('SUB',i,r[i]['data'].get('m_TemplateAlias'),r[i]['data'].get('m_FullTypeName'))
   for c in r[i]['data'].get('m_Children',[]):sub(c['rid'])
  sub(node)
print('HEADER GRADIENT BINDINGS')
