exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','overview-position-heading-final-'))
for folder in [GAME,SKIN]:
 e=UnityPy.load(before[folder/G]);obs={o.path_id:o for o in e.objects}
 for pid in [-940000000005000,-940000000008000]:
  d=obs[pid].read_typetree();rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=obs[sid].read_typetree()
  for r in rr.values():
   n=r.get('data',{})
   if n.get('m_FullTypeName')=='SI.Bindable.SIText' and rr[n['m_SerializedData']['rid']]['data'].get('name')=='player-pos-title-text':
    ri=n['m_RuleIndex'];sheet['m_Rules'][ri]['m_Properties']=[x for x in sheet['m_Rules'][ri]['m_Properties'] if x['m_Id']!=65540];override(n,[prop(131081,en('none'))])
  validate_ui(d,sheet);obs[pid].save_typetree(d);obs[sid].save_typetree(sheet)
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
 for pid in [-940000000005000,-940000000008000]:
  d=check[pid].read_typetree();rr=refs(d);s=check[d['inlineSheet']['m_PathID']].read_typetree()
  for r in rr.values():
   n=r.get('data',{})
   if n.get('m_FullTypeName')=='SI.Bindable.SIText' and rr[n['m_SerializedData']['rid']]['data'].get('name')=='player-pos-title-text':assert any(x['m_Id']==131081 and s['strings'][x['m_Values'][0]['valueIndex']]=='none' for x in s['m_Rules'][n['m_RuleIndex']]['m_Properties'])
 (OUT/('game-final.bundle' if folder==GAME else 'skin-final.bundle')).write_bytes(b)
 assert (folder/G).read_bytes()==before[folder/G];(folder/G).write_bytes(b)
(OUT/'manifest.json').write_text(json.dumps({'installed':True,'runtime_verified':False,'display_property':131081,'corrected_heading_versions':[1,2],'versions3and4_heading_already_absent':True}),'utf8')
print(OUT)
