from pathlib import Path
import sys,json,re,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
SRC=Path(r'K:\桌面\FM27 Comeback Skin v1.8.3\Skin files')
OUT=Path(__file__).parent; (OUT/'objects').mkdir(exist_ok=True)
pat=re.compile(r'troph|honour|cabinet',re.I)
index=[];hits=[]
for p in SRC.glob('*.bundle'):
 env=UnityPy.load(str(p));objs={o.path_id:o for o in env.objects};names={}
 for pid,o in objs.items():
  if o.type.name not in ('MonoBehaviour','AssetBundle','Texture2D','Sprite'):continue
  try:d=o.read_typetree()
  except Exception:continue
  name=d.get('m_Name','');names[pid]=name
  index.append({'bundle':p.name,'pid':pid,'name':name,'type':o.type.name})
  s=json.dumps(d,default=str,ensure_ascii=False)
  if pat.search(s):
   fn=f'{p.stem}__{pid}.json';(OUT/'objects'/fn).write_text(json.dumps(d,default=str,ensure_ascii=False,indent=2),encoding='utf8')
   h={'bundle':p.name,'pid':pid,'name':name,'file':fn,'matches':sorted(set(pat.findall(s)))};hits.append(h)
   sid=d.get('inlineSheet',{}).get('m_PathID')
   if sid in objs:(OUT/'objects'/f'{p.stem}__{sid}.json').write_text(json.dumps(objs[sid].read_typetree(),default=str,ensure_ascii=False,indent=2),encoding='utf8')
 print(p.name, 'objects',len(objs),'hits',sum(h['bundle']==p.name for h in hits),flush=True)
(OUT/'index.json').write_text(json.dumps(index,default=str,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'hits.json').write_text(json.dumps(hits,default=str,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(hits,default=str,ensure_ascii=False,indent=2))

