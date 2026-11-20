from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
loc=json.loads(Path('current-game-location.json').read_text('utf8'));e=UnityPy.load(str(Path(loc['bundle_root'])/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));o={x.path_id:x for x in e.objects}
for pid in [-940000000010000,-941100000001020]:
 d=o[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree()
 Path('inspect-old-fc-'+str(pid)+'.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
 print('\nPAGE',pid,d['m_Name'])
 def walk(i,depth=0):
  a=rr[i]['data'];sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});n=sd.get('name','');alias=a.get('m_TemplateAlias','');rule=a.get('m_RuleIndex',-1)
  if a.get('m_FullTypeName'):
   print(' '*depth,i,n,alias,'rule',rule)
  for c in a.get('m_Children',[]):walk(c['rid'],depth+1)
 walk(d['m_VisualTree']['rid'])
 print('USINGS',d['m_Usings'])
