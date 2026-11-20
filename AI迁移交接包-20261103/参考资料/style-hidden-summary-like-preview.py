from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def st(i,ps):override(rr[i]['data'],[prop(k,v) for k,v in ps])
def nst(name,ps):st(named(name)['rid'],ps)
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
panel=named('OverviewHiddenAttributesPanel')['rid'];cw=30
assert dimension(rr[panel],131105)==210
new=[];rid=max(rr)+1;eid=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
template=copy.deepcopy(named('CardCurrentAbilityValue'));tsd=copy.deepcopy(rr[template['data']['m_SerializedData']['rid']])
for prefix,x,arrow in [('CA',0,'\u2197'),('PA',62,'\u2198')]:
 dot=named('Overview'+prefix+'WhiteDot')['rid']
 st(dot,[(131089,px(x)),(131104,px(6)),(131105,px(12)),(131087,px(12)),(262147,px(6)),(131102,en('absolute'))])
 n,s=copy.deepcopy(template),copy.deepcopy(tsd);n['rid'],s['rid']=rid,rid+1;rid+=2
 n['data'].update(m_Id=eid,m_Parent={'rid':dot},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=-1,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 s['data'].update(uxmlAssetId=eid,name='Overview'+prefix+'DirectionArrow',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1,text=arrow,text_UxmlAttributeFlags=1,DebugDisplay='')
 s['data']['TextBinding']['m_kind']=0;s['data']['TextBinding_UxmlAttributeFlags']=1;eid+=1
 override(n['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,px(12)),prop(131087,px(12)),prop(262150,px(0)),prop(262151,px(0)),prop(65537,px(10)),prop(65536,color(0,0,0)),prop(65543,en('bold')),prop(65546,en('middle-center')),prop(65552,en('nowrap'))])
 rr[n['rid']]=n;rr[s['rid']]=s;new.extend([n,s]);rr[dot]['data']['m_Children'].append({'rid':n['rid']})
 nst('Overview'+prefix+'NativeTitle',[(131081,en('none'))])
 nst('Overview'+prefix+'NativeNumberAvailable',[(131089,px(x+15)),(131105,px(43))])
 for suffix in ['Missing','Value']:nst('Overview'+prefix+'NativeNumber'+suffix,[(131105,px(43)),(65537,px(18)),(65543,en('bold')),(65536,color(255,255,255)),(65546,en('middle-left'))])
gray=color(160,160,160)
nst('OverviewCurrentReputationTitle',[(131089,px(124)),(131105,px(48)),(65537,px(9)),(65536,gray)])
nst('OverviewCurrentReputationAvailable',[(131089,px(174)),(131105,px(36))])
for suffix in ['Missing','Value']:nst('OverviewCurrentReputation'+suffix,[(131105,px(36)),(65537,px(9)),(65536,gray),(65543,en('normal')),(65546,en('middle-left'))])
nst('OverviewHiddenNativeTitle',[(131105,px(28)),(65537,px(9)),(65536,gray)])
bar=named('OverviewCAPALayeredBar')['rid']
def resize_bar(i):
 a=rr[i]['data']
 if a.get('m_RuleIndex',-1)>=0:
  ids={p['m_Id'] for p in sheet['m_Rules'][a['m_RuleIndex']]['m_Properties']}
  ps=[]
  for pid in [131105,131097]:
   if pid in ids and dimension(rr[i],pid)==166:ps.append((pid,px(178)))
  if ps:st(i,ps)
 for child in a.get('m_Children',[]):resize_bar(child['rid'])
resize_bar(bar)
override(rr[bar]['data'],[prop(131089,px(32)),prop(327681,num(1),num(f32(6/19)))])
doc['references']['RefIds'].extend(new)
# Existing serialized bindings and all third/fourth row records are unchanged.
for i,r in old_refs.items():
 if 'UxmlSerializedData' in r['type']['class']:assert rr[i]==r,('binding changed',i)
def protect(i):
 assert rr[i]==old_refs[i],i
 for c in rr[i]['data'].get('m_Children',[]):protect(c['rid'])
for name in ['OverviewHiddenAttributeRow1','OverviewHiddenAttributeRow2']:protect(named(name)['rid'])
assert rr[panel]==old_refs[panel]
assert dimension(rr[bar],131089)+dimension(rr[bar],131105)==210
for suffix in ['Missing','Value']:
 v=named('OverviewCurrentReputation'+suffix);t=named('OverviewCurrentReputationTitle')
 assert property_value(v,65536)==property_value(t,65536) and dimension(v,65537)==dimension(t,65537)==9
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('hidden-summary-preview-style-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 bp=out/('backup-'+tag);bp.mkdir();(bp/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'changed_assets':[FULL,sid],'width':210,'ability_numbers_px':18,'ability_direction_icons':['up-right','down-right'],'reputation_title_and_value':{'font_px':9,'color':'#A0A0A0'},'layered_bar_logical_size':[178,19],'layered_bar_display_height':6,'all_existing_bindings_unchanged':True,'third_fourth_rows_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':sha(output),'unchanged_objects_verified':len(old_hashes)-2}
mf=out/'manifest.json';mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;mf.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'sha256':sha(output)},ensure_ascii=False))
