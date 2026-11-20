import sys,struct,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
game=Path('F:/Steam/steamapps/common/Project Taco/fm_Data')
b=(game/'il2cpp_data/Metadata/global-metadata.dat').read_bytes();s=[struct.unpack_from('<III',b,8+i*12) for i in range(31)]
def name(i):
 p=s[2][0]+i;return b[p:b.index(0,p)].decode('utf8',errors='replace')
for i in range(s[19][2]):
 p=s[19][0]+i*76;n=name(struct.unpack_from('<I',b,p)[0]);ns=name(struct.unpack_from('<I',b,p+4)[0]);fs,ms=struct.unpack_from('<II',b,p+20);mc,pc,fc=struct.unpack_from('<HHH',b,p+52)
 if 'positionaptitude' in n.lower() or n in ['WrappedObjectList','ScalableBindableGridLayoutElement','PitchElement','Pitch','BindableUxmlList']:
  methods=[name(struct.unpack_from('<I',b,s[5][0]+j*int(s[5][1]/s[5][2]))[0]) for j in range(ms,ms+mc)]
  print(ns,n,methods if n not in ['Person','PersonModel','PersonViewModel'] else [x for x in methods if 'Pos' in x])
g=game/'StreamingAssets/aa/StandaloneWindows64'
for bn in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(g/bn));obs={o.path_id:o for o in e.objects}
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  d=o.read_typetree();rr={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
  for r in rr.values():
   if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.WrappedObjectList':
    ss=rr[r['data']['m_SerializedData']['rid']]['data']
    if 'Squad' not in n and 'Scout' not in n:print('WRAPPED',bn,o.path_id,n,json.dumps(ss));break
