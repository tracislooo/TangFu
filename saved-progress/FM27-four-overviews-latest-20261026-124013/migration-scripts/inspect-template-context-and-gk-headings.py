exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for i in [1193,1203]:
 a=rr[i]['data'];sd=rr[a['m_SerializedData']['rid']]['data'];print(i,'node fields',[(k,v) for k,v in a.items() if k in ['m_AttributeOverrides','m_AttributeOverridesList','m_TemplateAlias','m_SlotUsages','m_SerializedData']]);print('sd',sd)
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects};d=go[-930000000001003].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']}
for i in [1085,1103,1113]:print('GKTITLE',i,sr[i]['data'].get('DebugDisplay'))
