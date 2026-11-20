"""Undo native/team header palette only; retain current layout and actions."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,re,struct,sys
R=Path(__file__).resolve().parent
exec(compile((R/'disable-primary-shortcuts-hover.py').read_text('utf8').split('outputs={};reports=[]')[0],'helpers','exec'))
S='ui-styles_assets_default.bundle'
before={f/n:(f/n).read_bytes() for f in [GAME,SKIN] for n in [W,S]}
for p in before:protected.pop(p,None)
tree=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'selector','exec'))
outputs={}
for tag,folder in [('game',GAME),('skin',SKIN)]:
 env=UnityPy.load(before[folder/W]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};expected={}
 previous=UnityPy.load(str(R/'navigation-background70-20261117-223345'/('backup-'+tag)/W));po={o.path_id:o for o in previous.objects}
 def named(objects,name):return next(o for o in objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name)
 def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
 ob=named(oo,'PrimaryNavigationBar');d=ob.read_typetree();old=copy.deepcopy(d);rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
 pd=named(po,'PrimaryNavigationBar').read_typetree();pr=refs(pd);ps=po[pd['inlineSheet']['m_PathID']].read_typetree()
 for rid,key in [(1002,458752),(1005,131081),(1013,458767)]:
  prop=copy.deepcopy(next(p for p in ps['m_Rules'][pr[rid]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==key))
  for h in prop['m_Values']:
   pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ps[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
  st.edit(rr[rid],[prop])
 # Pin original menu text to the same fixed black used before the reverted change.
 for rid in [1002,1040]:st.edit(rr[rid],[st.p(65536,st.h(4,{'r':0.,'g':0.,'b':0.,'a':1.}))])
 allowed={1002,1005,1013,1040}
 for rid,prior in refs(old).items():
  actual=copy.deepcopy(rr[rid])
  if rid in allowed:actual['data']['m_RuleIndex']=prior['data']['m_RuleIndex']
  assert actual==prior,('Non-color record changed',rid)
 validate_ui(d,sheet);expected[ob.path_id]=d;expected[sid]=sheet
 # Restore the tab's pre-experiment opaque dark blue, independently of the white header.
 ob=named(oo,'SecondaryNavigationBar');d=ob.read_typetree();rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
 pd=named(po,'SecondaryNavigationBar').read_typetree();pr=refs(pd);ps=po[pd['inlineSheet']['m_PathID']].read_typetree()
 prop=copy.deepcopy(next(p for p in ps['m_Rules'][pr[1001]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458752))
 for h in prop['m_Values']:
  pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ps[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
 st.edit(rr[1001],[prop]);validate_ui(d,sheet);expected[ob.path_id]=d;expected[sid]=sheet
 ob=named(oo,'MenuBar');d=ob.read_typetree();old=copy.deepcopy(d);rr=refs(d);sid=d['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);changed=[]
 for rid,r in rr.items():
  a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=sd.get('name','')
  if name.startswith('PrimaryNav') and name.endswith('Label') and a.get('m_FullTypeName')=='SI.Bindable.SIText':
   st.edit(r,[st.p(65536,st.h(4,{'r':0.,'g':0.,'b':0.,'a':1.})),st.p(458767,st.num(.75))]);changed.append(rid)
 assert len(changed)==7
 for rid,prior in refs(old).items():
  actual=copy.deepcopy(rr[rid])
  if rid in changed:actual['data']['m_RuleIndex']=prior['data']['m_RuleIndex']
  assert actual==prior
 validate_ui(d,sheet);expected[ob.path_id]=d;expected[sid]=sheet
 for pid,data in expected.items():oo[pid].save_typetree(data)
 raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for pid,o in check.items():
  if pid in expected:assert o.read_typetree()==expected[pid]
  else:assert sha(o.get_raw_data())==hashes[pid]
 outputs[folder/W]=raw
 env=UnityPy.load(before[folder/S]);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in oo.items()};ob=named(oo,'AlwaysAppliedStyleSheet');d=ob.read_typetree();st=Styles(d);idx=len(d['m_Rules'])
 texts=['#MainNav #MenuBar .portal-text','#MainNav #MenuBar .portal-text:hover']
 d['m_Rules'].append({'m_ComplexSelectors':[selector(t,idx) for t in texts],'m_Properties':[st.p(65536,st.h(4,{'r':0.,'g':0.,'b':0.,'a':1.}))],'line':-1})
 ob.save_typetree(d);raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(oo)
 for pid,o in check.items():
  if pid==ob.path_id:assert o.read_typetree()==d
  else:assert sha(o.get_raw_data())==hashes[pid]
 outputs[folder/S]=raw
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
out=R/('primary-nav-color-following-undone-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();tx=[]
for p,raw in outputs.items():
 tag='game' if p.parent==GAME else 'skin';src=out/tag/p.name;bak=out/('backup-'+tag)/p.name;src.parent.mkdir(exist_ok=True);bak.parent.mkdir(exist_ok=True);src.write_bytes(raw);bak.write_bytes(before[p]);tx.append({'target':str(p),'source':str(src),'backup':str(bak),'before':sha(before[p]),'after':sha(raw)})
(out/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8')
(out/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'scope':'undo native/team palette only; preserve current typography/layout/routes/holiday/continue','protected_sha256':{str(p):h for p,h in protected.items()}},indent=2),'utf8')
for name,flag in [('install',''),('restore',' --restore')]:
 (out/(name+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\n",'utf-8-sig')
print(str(out))
