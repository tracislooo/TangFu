from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
ge=UnityPy.load(str(GAME/GN));go={o.path_id:o for o in ge.objects}
def inspect(d,ob,ids):
 rs={r['rid']:r for r in d['references']['RefIds']};ss=ob[d['inlineSheet']['m_PathID']].read_typetree()
 print('\nDOC',d['m_Name'])
 for i in ids:
  if i not in rs:continue
  a=rs[i]['data'];sd=rs.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  styles={p['m_Id']:[('keyword',h['valueIndex']) if h['m_ValueType']==1 else ss[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in ss['m_Rules'][a['m_RuleIndex']]['m_Properties']} if a.get('m_RuleIndex',-1)>=0 else {}
  print('NODE',i,a.get('m_FullTypeName'),sd.get('name'),a.get('m_Parent'),a.get('m_Children'),'CLASSES',a.get('m_Classes'), 'STYLES',json.dumps(styles))
  nonbase={k:v for k,v in sd.items() if k not in ['uxmlAssetId','name','bindings','tooltip','dataSourcePathString','dataSourceTypeString','dataSourceUnityObject','viewDataKey','pickingMode','usageHints','languageDirection','tabIndex','focusable','enabledSelf'] and not k.endswith('_UxmlAttributeFlags') and v}
  print('SERIALIZED',json.dumps(nonbase,ensure_ascii=True))
for pid in [-930000000001001,-930000000001003]:
 d=objects[pid].read_typetree();inspect(d,objects,[1002,1009,1011,1025,1029,1031,1033,1034,1035,1054,1055,1074,1075,1077,1078,1703])
inspect(go[-930000000001003].read_typetree(),go,[1001,1002,1004,1005,1007,1009,1011,1013,1025,1029,1030,1031,1032,1050,1056,1062,1063,1065,1097,1101,1135])
