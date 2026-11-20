from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
out={}
for bn in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/bn));rows=[]
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name() or ''
  if 'styles_assets' in bn:
   d=o.read_typetree()
   for i,r in enumerate(d.get('m_Rules',[])):
    ss=json.dumps(r.get('m_ComplexSelectors',[]))
    if any(x in ss.lower() for x in ['layout-tile','layout-module','layout-ui-card','match-state','in-match','game-world','main-card-report-body']):
     ps=[]
     for p in r['m_Properties']:
      if p['m_Id']==458752 or p.get('m_CustomName','').startswith('--layout'):
       ps.append({'prop':p,'resolved':[d.get({4:'colors',7:'strings',8:'strings'}.get(v['m_ValueType'],'NONE'),[])[v['valueIndex']] if v['m_ValueType'] in [4,7,8] else v for v in p['m_Values']]})
     if ps:rows.append({'name':name,'rule':i,'selectors':r['m_ComplexSelectors'],'props':ps})
  elif name in ['GameWorld','GameWorldRoot','GameWorldScreen','MainMenu','MatchRoot'] or name.startswith('tile-figma-'):
   d=o.read_typetree();rows.append({'name':name,'pid':o.path_id,'tree':d})
 out[bn]=rows
(R/'inspect-nonmatch-surfaces.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
print([(k,len(v)) for k,v in out.items()])
