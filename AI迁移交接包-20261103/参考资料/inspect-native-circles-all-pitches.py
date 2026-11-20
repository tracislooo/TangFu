exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-native-circles-all-pitches-'))
for pid in [-940000000005000,-940000000008000,-940000000010020,-960000000003030]:
 d=objs[G][pid].read_typetree();rr=refs(d);s=rr[rr[1023]['data']['m_SerializedData']['rid']]['data'];print(pid,'ORIENTATION',s.get('Orientation'),'TEMPLATE',s['PositionTemplateAsset'],'SELECT',s.get('SelectionEvent'));print('ZONE',[(i,rr[r['data']['m_SerializedData']['rid']]['data'].get('name')) for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.WrappedObjectList'])
for bn in [W,G]:
 ab=next(o for o in objs[bn].values() if o.type.name=='AssetBundle')
 for key,v in ab.read_typetree()['m_Container']:
  if key=='d6b3b3e4fa729864cbe89c7957538b2c':
   d=objs[bn][v['asset']['m_PathID']].read_typetree()
   if 'references' not in d:continue
   print('NATIVE',bn,v['asset']['m_PathID'],d['m_Name'],d['inlineSheet']);rr=refs(d);sheet=objs[bn][d['inlineSheet']['m_PathID']].read_typetree()
   for i,r in rr.items():
    n=r.get('data',{})
    if 'm_FullTypeName' in n:
     s=rr.get(n.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(i,n['m_FullTypeName'],s.get('name'),n.get('m_Parent'),n.get('m_Classes'))
