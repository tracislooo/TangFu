exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-four-overview-number-colours-'))
for bn,pids in [(G,[-930000000001001,-940000000021000]),(W,[-930000000001001,-930000000001003,-940000000010000,-940000000012000])]:
 for pid in pids:
  doc=objs[bn][pid].read_typetree();rr=refs(doc);sheet=objs[bn][doc['inlineSheet']['m_PathID']].read_typetree();hits=[]
  for i,r in rr.items():
   n=r.get('data',{})
   if n.get('m_FullTypeName')!='SI.Bindable.SIText':continue
   sd=rr[n['m_SerializedData']['rid']]['data'];name=sd.get('name','');ix=n.get('m_RuleIndex',-1)
   if any(k in name for k in ['Value','Condition','Sharpness','Fatigue']) or (bn==G and i in [1017,1034]):
    p=next((p for p in sheet['m_Rules'][ix]['m_Properties'] if p['m_Id']==65536),None) if ix>=0 else None
    hits.append((i,name,p['m_Values'] if p else 'class colour'))
  print(bn,pid,doc['m_Name'],'values',len(hits),'examples',hits[:10])
