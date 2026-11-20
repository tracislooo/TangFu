import sys,json
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path(json.loads((R/'current-game-location.json').read_text())['bundle_root'])
P=R/'lake-palette-inspection-20261117';P.mkdir(exist_ok=True)
for bn in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']:
 for o in UnityPy.load(str(G/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for i,r in enumerate(d['m_Rules']):
   text=json.dumps(r.get('m_ComplexSelectors',[]))
   if any(k in text.lower() for k in ['progress','segmented-button-row-active','playpause']):
    print(d['m_Name'],i,text[:240],[(p['m_Id'],p.get('m_CustomName'),[(v['m_ValueType'],d['strings'][v['valueIndex']] if v['m_ValueType']==8 else d['colors'][v['valueIndex']] if v['m_ValueType']==4 else v['valueIndex']) for v in p['m_Values']]) for p in r['m_Properties'] if p['m_Id'] in [458752,65536,-1]])
   for p in r['m_Properties']:
    if p.get('m_CustomName') in ['--buttons-toggle-active-primary-surface','--buttons-toggle-active-primary-hover','--data-progress-indicator-foreground']:
     print('VAR',d['m_Name'],p, [d['colors'][v['valueIndex']] if v['m_ValueType']==4 else d['strings'][v['valueIndex']] if v['m_ValueType']==8 else '' for v in p['m_Values']])
for bn in ['ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/bn));oo={o.path_id:o for o in e.objects}
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if n!='DefaultMatchUI' and not any(k in n.lower() for k in ['loading','loadgame','progressbar','adaptive','textscaling']):continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  print('TEMPLATE',bn,n,o.path_id)
  if n=='DefaultMatchUI' or any(k in n.lower() for k in ['loading','progressbar']):(P/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
