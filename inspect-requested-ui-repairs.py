from pathlib import Path
import sys,json,ast
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));folder=Path(cfg['bundle_root'])
out={}
for n in ['ui-tablefactories_assets_all.bundle','ui-tableviews_assets_all.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(folder/n));oo={o.path_id:o for o in e.objects};items=[]
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name()
  if 'tablefactories' in n and 'Tactic' in name:
   d=o.read_typetree();items.append(d)
  elif 'tableviews' in n and (name.startswith('TacticTeamSelection') or name in ['FirstTeamSquadAndYouthTeamSquadCollection','tangfu A']):items.append(o.read_typetree())
  elif 'visualtreeassets' in n and (name in ['PortalMessagesContentBlock','NewsItemPortalMessagesSearch','TeamSquadBlock','SquadOverviewTableBlock'] or ('sender' in name.lower() and 'primary' in name.lower())):
   d=o.read_typetree();d['_pid']=o.path_id
   if d.get('inlineSheet',{}).get('m_PathID') in oo:d['_style']=oo[d['inlineSheet']['m_PathID']].read_typetree()
   items.append(d)
 out[n]=items
(R/'requested-ui-live-inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
for n,items in out.items():
 for d in items:
  print(n,d['m_Name'])
  if 'm_rowData' in d:print([(c['m_id'],c['m_defaultWidth'],c['m_minimumWidth']) for c in d['m_rowData']])
  if 'm_tableView' in d:print([(c['m_columnID'],c['m_columnMetadata']['m_widthOverride'],c['m_columnMetadata']['m_minWidthOverride']) for c in d['m_tableView']['m_tableConfig']])
  if 'm_tableViewSettings' in d:print({k:v for k,v in d.items() if k!='m_tableViewSettings'});print('first',d['m_tableViewSettings'][:1])
  if '_pid' in d and 'references' in d:
   rr={x['rid']:x for x in d['references']['RefIds']}
   for i,x in rr.items():
    a=x.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
    if 'm_Parent' not in a:continue
    print(i,a.get('m_TemplateAlias') or a.get('m_FullTypeName'),sd.get('name'),a.get('m_Classes'),{k:v for k,v in sd.items() if 'default' in k.lower() or 'selected' in k.lower() or 'view' in k.lower()})
    if a.get('m_RuleIndex',-1)>=0:
     s=d['_style'];print(' styles',{p['m_Id']:[s[{2:'floats',3:'dimensions',4:'colors',5:'strings',7:'strings'}.get(v['m_ValueType'],'strings')][v['valueIndex']] if v['m_ValueType'] in [2,3,4,5,7] else v for v in p['m_Values']] for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']})
