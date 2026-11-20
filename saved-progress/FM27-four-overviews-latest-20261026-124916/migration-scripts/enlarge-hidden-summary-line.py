from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def nst(name,ps):st(named(name)['rid'],ps)
panel=named('OverviewHiddenAttributesPanel')['rid'];cw=30
assert dimension(rr[panel],131105)==210
for prefix,x in [('CA',0),('PA',71)]:
 nst('Overview'+prefix+'WhiteDot',[(131089,px(x)),(131104,px(7)),(131105,px(10)),(131087,px(10)),(262147,px(5))])
 nst('Overview'+prefix+'NativeTitle',[(131089,px(x+11)),(131105,px(36)),(65537,px(9))])
 nst('Overview'+prefix+'NativeNumberAvailable',[(131089,px(x+47)),(131105,px(23))])
 for suffix in ['Missing','Value']:nst('Overview'+prefix+'NativeNumber'+suffix,[(131105,px(23)),(65537,px(13))])
nst('OverviewCurrentReputationTitle',[(131089,px(142)),(131105,px(36)),(65537,px(9))])
nst('OverviewCurrentReputationAvailable',[(131089,px(178)),(131105,px(32))])
for suffix in ['Missing','Value']:nst('OverviewCurrentReputation'+suffix,[(131105,px(32)),(65537,px(12))])
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('binding changed',i)
assert rr[panel]==old_refs[panel]
assert dimension(named('OverviewCurrentReputationAvailable'),131089)+dimension(named('OverviewCurrentReputationAvailable'),131105)==210
for prefix in ['CA','PA']:
 assert dimension(named('Overview'+prefix+'WhiteDot'),131105)==10
 assert dimension(named('Overview'+prefix+'NativeNumberValue'),65537)==13
tail=(R/'compact-hidden-panel-240-top-aligned.py').read_text(encoding='utf8').split('validate_ui(doc,sheet)',1)[1]
tail='validate_ui(doc,sheet)'+tail
tail=tail.replace('hidden-panel-width240-top-aligned-','hidden-summary-enlarged-width210-').replace("'panel_size':[240,168]","'panel_size':[210,168],'summary_sizes':{'dot':10,'titles':9,'ability_numbers':13,'reputation_number':12}")
exec(compile(tail,'<validated build backup and install>','exec'))
