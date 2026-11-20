exec(open('inspect-position-blocks.py',encoding='utf8').read().split('for i in range(s[19][2]):')[0])
def decode(raw):
 b=bytes(raw);p=1;a=[]
 if not b:return a
 for _ in range(b[0]):
  n=struct.unpack_from('<I',b,p)[0];p+=4;a.append(b[p:p+n]);p+=n
 return [v.decode('utf8','backslashreplace') for v in a]
g=game/'StreamingAssets/aa/StandaloneWindows64'
for bn in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(g/bn));obs={o.path_id:o for o in e.objects}
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree();rr={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
  for r in rr.values():
   a=r.get('data',{})
   if a.get('m_FullTypeName')=='SI.Bindable.SIButton':
    sd=rr[a['m_SerializedData']['rid']]['data'];ss=json.dumps(sd)
    if 'position' in ss.lower() or ('Setter' in d.get('m_Name','') and 'Button' in d.get('m_Name','')):
     print('BUTTON',o.path_id,d['m_Name'],json.dumps(sd));
   if a.get('m_FullTypeName')=='SI.Bindable.BindingSetter' and 'position' in json.dumps(rr[a['m_SerializedData']['rid']]).lower():print('SETTER',o.path_id,d['m_Name'],json.dumps(rr[a['m_SerializedData']['rid']]))
