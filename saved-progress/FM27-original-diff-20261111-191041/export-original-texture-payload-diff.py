from pathlib import Path
import sys,json,hashlib
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=sorted((R/'saved-progress').glob('FM27-original-diff-*'))[-1];snap=Path(json.loads((R/'current-main-sidebar-snapshot.json').read_text('utf8'))['archive']);G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');rows=[];errors=[]
sha=lambda x:hashlib.sha256(x).hexdigest()
def payload(o):
 if o is None:return None
 t=o.read()
 if not t.image_data and (t.m_StreamData is None or t.m_StreamData.size==0):return b''
 return t.get_image_data()
for mode in ['main','sidebar']:
 for p in (snap/mode/'aa/StandaloneWindows64').glob('*.bundle'):
  if 'background' not in p.name and 'font' not in p.name:continue
  q=G/p.name
  ne=UnityPy.load(str(p));oe=UnityPy.load(str(q)) if q.exists() else None
  oo={o.path_id:o for o in oe.objects} if oe else {};no={o.path_id:o for o in ne.objects}
  for pid in sorted(set(oo)|set(no)):
   a=oo.get(pid);b=no.get(pid)
   if (b or a).type.name!='Texture2D':continue
   try:
    x=payload(a);y=payload(b)
    if x==y:continue
    base=O/mode/p.name/'texture-payloads'/str(pid);base.mkdir(parents=True,exist_ok=True)
    for name,data in [('original',x),('modified',y)]:
     if data is not None:(base/(name+'.texture-data.bin')).write_bytes(data)
    row={'mode':mode,'bundle':p.name,'path_id':str(pid),'name':(b or a).peek_name(),'before_payload_sha256':sha(x) if x is not None else None,'after_payload_sha256':sha(y) if y is not None else None,'detail':str(base.relative_to(O))};rows.append(row)
   except Exception as ex:errors.append({'mode':mode,'bundle':p.name,'id':str(pid),'error':str(ex)})
(O/'texture-payload-changes.json').write_text(json.dumps({'changes':rows,'errors':errors},ensure_ascii=False,indent=2),'utf8');print('texture payload differences',len(rows),'errors',len(errors))

