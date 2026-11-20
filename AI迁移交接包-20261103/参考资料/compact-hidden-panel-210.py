from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def nst(name,ps):st(named(name)['rid'],ps)
panel=named('OverviewHiddenAttributesPanel')['rid']
assert dimension(rr[panel],131105)==240
st(panel,[(131105,px(210)),(131097,px(210)),(131095,px(210))])
for name in ['OverviewHiddenSummaryLine','OverviewHiddenBarLine']:nst(name,[(131105,px(210))])
for prefix,x in [('CA',0),('PA',64)]:
 nst('Overview'+prefix+'WhiteDot',[(131089,px(x))])
 nst('Overview'+prefix+'NativeTitle',[(131089,px(x+9)),(131105,px(32)),(65537,px(8))])
 nst('Overview'+prefix+'NativeNumberAvailable',[(131089,px(x+41)),(131105,px(20))])
 for suffix in ['Missing','Value']:nst('Overview'+prefix+'NativeNumber'+suffix,[(131105,px(20)),(65537,px(11))])
nst('OverviewCurrentReputationTitle',[(131089,px(128)),(131105,px(48)),(65537,px(8))])
nst('OverviewCurrentReputationAvailable',[(131089,px(176)),(131105,px(34))])
for suffix in ['Missing','Value']:nst('OverviewCurrentReputation'+suffix,[(131105,px(34))])
# Narrow all three stacked image layers together; keep their original textures and aspect fitting.
bar=named('OverviewCAPALayeredBar')['rid']
def narrow(i):
 a=rr[i]['data']
 if a.get('m_RuleIndex',-1)>=0:
  ps=sheet['m_Rules'][a['m_RuleIndex']]['m_Properties'];ids={p['m_Id'] for p in ps}
  props=[]
  for pid in [131105,131097]:
   if pid in ids and dimension(rr[i],pid)==196:props.append((pid,px(166)))
  if props:st(i,props)
 for c in a.get('m_Children',[]):narrow(c['rid'])
narrow(bar)
rows=[['adaptability','ambition','controversy','loyalty','pressure','professionalism','sportsmanship'],['temperament','versatility','consistency','dirtiness','important-matches','injury-proneness']]
cw=30
for rowindex,keys in enumerate(rows):
 nst('OverviewHiddenAttributeRow'+str(rowindex+1),[(131089,px(15 if rowindex else 0)),(131105,px(cw*len(keys)))])
 for index,key in enumerate(keys):
  nst('OverviewHiddenCell_'+key,[(131089,px(index*cw)),(131105,px(cw))])
  nst('OverviewHiddenNumber_'+key+'Available',[(131105,px(cw))])
  for suffix in ['Missing','Value']:nst('OverviewHiddenNumber_'+key+suffix,[(131105,px(cw))])
  nst('OverviewHiddenTitle_'+key,[(131105,px(cw))])
  nst('OverviewHiddenImagePositive_'+key,[(131089,px(12.5))])
  if index<len(keys)-1:nst('OverviewHiddenDivider_'+key,[(131089,px(29))])
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('binding changed',i)
assert rr[panel]['data']['m_Parent']==old_refs[panel]['data']['m_Parent']=={'rid':1349}
assert dimension(rr[panel],131104)==0 and dimension(rr[panel],131105)==210
assert dimension(rr[bar],131089)+dimension(rr[bar],131105)==210
for i in [1186,1202,1203,1217,1043,1349]:assert rr[i]==old_refs[i],i
tail=(R/'compact-hidden-panel-240-top-aligned.py').read_text(encoding='utf8').split('validate_ui(doc,sheet)',1)[1]
tail='validate_ui(doc,sheet)'+tail
tail=tail.replace('hidden-panel-width240-top-aligned-','hidden-panel-width210-top-aligned-').replace("'panel_size':[240,168]","'panel_size':[210,168]")
exec(compile(tail,'<validated build backup and install>','exec'))
