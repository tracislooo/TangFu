from pathlib import Path
exec(Path('inspect-nonmatch-surfaces.py').read_text('utf8').split('out={}')[0])
rows=[]
for p in G.glob('*visualtree*.bundle'):
 e=UnityPy.load(str(p))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  rr={z['rid']:z for z in d.get('references',{}).get('RefIds',[])}
  for z in rr.values():
   a=z.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   cs=a.get('m_Classes',[]);nm=sd.get('name','')
   if any(t in str(cs)+' '+str(nm) for t in ['main-card-report-body','main-menu-layer-body','MenuBody','ReportBody','match-mode','in-match','non-match']):
    rows.append({'bundle':p.name,'template':d['m_Name'],'pid':o.path_id,'rid':z['rid'],'classes':cs,'sd':sd})
    (R/('inspect-root-'+d['m_Name']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
(R/'inspect-nonmatch-roots.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(rows,ensure_ascii=False)[:20000])
