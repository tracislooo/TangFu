from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path(json.loads((R/'current-game-location.json').read_text('utf8'))['bundle_root'])
OUT=R/'squad-hidden-view-research';OUT.mkdir(exist_ok=True)
for n in ['ui-tablefactories_assets_all.bundle','ui-tableviews_assets_all.bundle']:
 e=UnityPy.load(str(GAME/n));lines=[]
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name();d=o.read_typetree()
  if 'tableviews' in n:
   if re.search('FirstTeam|PlayerSelection|Squad.*Collection',name,re.I):
    (OUT/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8');lines.append({'pid':o.path_id,'name':name,'data':d})
  elif 'm_rowData' in d:
   rows=d['m_rowData'];cols=[{'id':c.get('m_id'),'bind':c.get('m_valueBindings'),'sort':c.get('m_sortBinding'),'title':c.get('m_translationID')} for c in rows if re.search('ability|potential|reputation|adapt|ambit|loyal|profession|temper|pressure|sports|controvers|consisten|dirt|important|injury|versatil|hidden',json.dumps(c),re.I)]
   if name=='PlayerTableFactory' or cols:
    lines.append({'pid':o.path_id,'name':name,'cols':cols})
    if name=='PlayerTableFactory':(OUT/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
 (OUT/('views.txt' if 'tableviews' in n else 'factory-columns.json')).write_text(json.dumps(lines,ensure_ascii=False,indent=2),'utf8')
print(str(OUT))
