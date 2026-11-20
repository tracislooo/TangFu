exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
w='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
oo={o.path_id:o for o in UnityPy.load(str(p/w)).objects}
for pid in [-8273082868742719783,-970000000009000,-970000000010000]:
 d=oo[pid].read_typetree();r={a['rid']:a.get('data',{}) for a in d['references']['RefIds']}
 for i,a in r.items():
  if 'm_Parent' not in a:continue
  sd=r.get(a.get('m_SerializedData',{}).get('rid'),{})
  bd=sd.get('Binding',{})
  name=sd.get('name','')
  if i<1070 and ('swap' in (name+str(bd)).lower() or 'drag' in str(sd).lower() or i in [1005,1008,1042,1063]):
   print(pid,i,a.get('m_FullTypeName'),a.get('m_Classes'),a['m_Parent'],name,bd.get('m_direct'),sd.get('InvertDirectBinding'),[k for k in sd if ('Drag' in k or 'Swap' in k) and 'Flags' not in k])
print([f.name for f in p.glob('*styles*.bundle')])
