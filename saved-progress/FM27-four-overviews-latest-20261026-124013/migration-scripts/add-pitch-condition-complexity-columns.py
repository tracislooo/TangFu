from pathlib import Path
import struct,colorsys
source=Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig');exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-','pitch-condition-complexity-two-columns-'),'boot','exec'))
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'styles','exec'))
src=ast.parse((R/'combine-tactics-condition-sharpness.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in ['decode','encode','f32','colour']],type_ignores=[]),'helpers','exec'))
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def named(r,n):return next(i for i,a in r.items() if a.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(r,i)['data'].get('name')==n)
class Tree:
 def __init__(self,d,s):
  self.d=d;self.r=refs(d);self.s=s;self.st=Styles(s);self.nr=max(self.r)+1;self.ni=max(a.get('data',{}).get('m_Id',0) for a in self.r.values())+1
 def add(self,source,i,parent,name=None,sheet=None,deep=False):
  a=copy.deepcopy(source[i]);sd=copy.deepcopy(serial(source,i));a['rid']=self.nr;sd['rid']=self.nr+1;self.nr+=2;a['data'].update(m_Id=self.ni,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':sd['rid']});sd['data']['uxmlAssetId']=self.ni;self.ni+=1
  if name:sd['data'].update(name=name,name_UxmlAttributeFlags=1)
  self.r[a['rid']]=a;self.r[sd['rid']]=sd;self.d['references']['RefIds'] += [a,sd];self.r[parent]['data']['m_Children'].append({'rid':a['rid']})
  ri=source[i]['data'].get('m_RuleIndex',-1)
  if sheet is not None and ri>=0:
   ps=copy.deepcopy(sheet['m_Rules'][ri]['m_Properties'])
   for p in ps:
    for h in p['m_Values']:
     if h['m_ValueType'] in poolmap:
      pool=poolmap[h['m_ValueType']];self.s[pool].append(copy.deepcopy(sheet[pool][h['valueIndex']]));h['valueIndex']=len(self.s[pool])-1
   self.st.edit(a,ps,True)
  if deep:
   for c in source[i]['data'].get('m_Children',[]):self.add(source,c['rid'],a['rid'],sheet=sheet,deep=True)
  return a['rid']
 def sd(self,i):return serial(self.r,i)['data']
 def edit(self,i,ps):self.st.edit(self.r[i],ps)
 def save(self,pid):
  validate_ui(self.d,self.s);objs[pid].save_typetree(self.d);objs[self.d['inlineSheet']['m_PathID']].save_typetree(self.s);changed[pid]=copy.deepcopy(self.d);changed[self.d['inlineSheet']['m_PathID']]=copy.deepcopy(self.s)
changed={};base=objs[-970000000001000].read_typetree();br=refs(base);sw=named(br,'CombinedConditionAbove-1');tx=named(br,'CombinedConditionPercent0');ve=1006
checks=[]
for pid in [-8273082868742719783,3127595210179668386]:
 d=objs[pid].read_typetree();t=Tree(d,objs[d['inlineSheet']['m_PathID']].read_typetree());st=t.st;P=st.p;frame=named(t.r,'TacticsPlayerPortraitFrame')
 gate=t.add(t.r,1036 if pid==-8273082868742719783 else 1047,frame,'PitchFitnessPlayerVisible')
 # Both prototypes are SIVisible; remove swapped-wing semantics.
 t.sd(gate).update(InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1);t.sd(gate)['Binding']={'m_kind':1,'m_direct':{'Path':{'m_path':'position.Player'},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}};t.sd(gate)['Binding_UxmlAttributeFlags']=1
 t.sd(gate).update(pickingMode=1,pickingMode_UxmlAttributeFlags=1);t.r[gate]['data']['m_Classes']=[]
 t.edit(gate,[P(131102,st.en('absolute')),P(131103,st.pct(100)),P(131093,st.px(2)),P(131104,st.px(0)),P(131105,st.px(32)),P(131087,st.px(14)),P(131084,st.num(0)),P(131085,st.num(0))])
 leaves={}
 def switch(parent,limit):
  i=t.add(br,sw,parent,'PitchFitnessAbove'+str(limit));s=t.sd(i);args=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);struct.pack_into('<i',args[1],len(args[1])-4,limit);old=b'player.Condition';new=b'position.Player.Condition';assert args[2].endswith(bytes([len(old)])+old);args[2][-len(old)-1:]=bytes([len(new)])+new;s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args);s.update(pickingMode=1,pickingMode_UxmlAttributeFlags=1);t.edit(i,[P(131105,st.pct(100)),P(131087,st.pct(100))]);return i
 def leaf(parent,v):
  i=t.add(br,tx,parent,'PitchFitnessPercent'+str(v));s=t.sd(i);s.update(text='--' if v is None else str(v)+'%',pickingMode=1,pickingMode_UxmlAttributeFlags=1);t.r[i]['data']['m_Classes']=[];t.edit(i,[P(131105,st.px(32)),P(131087,st.px(14)),P(65537,st.px(10)),P(65543,st.en('bold')),P(65546,st.en('middle-right')),P(65552,st.en('nowrap')),P(65536,st.h(4,colour(v)))]);leaves[i]=v;return i
 def build(parent,lo,hi):
  if lo==hi:return leaf(parent,lo)
  mid=(lo+hi)//2;i=switch(parent,mid);build(i,lo,mid);build(i,mid+1,hi);return i
 root=switch(gate,-1);leaf(root,None);build(root,0,100)
 for v in [None,-1]+list(range(111)):
  i=root
  while i not in leaves:
   args=decode(t.sd(i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);lim=struct.unpack_from('<i',args[1],len(args[1])-4)[0];i=t.r[i]['data']['m_Children'][int(v is not None and v>lim)]['rid']
  assert leaves[i]==(None if v is None or v<0 else min(100,v))
 checks.append({'template':d['m_Name'],'values':113});t.save(pid)
# Embed the native popup heading and key-factor list in the existing lower module.
module=1593217430813700770;d=objs[module].read_typetree();t=Tree(d,objs[d['inlineSheet']['m_PathID']].read_typetree());st=t.st;P=st.p
left=named(t.r,'TrainingTacticalEffectivenessScroll');outer=t.r[left]['data']['m_Parent']['rid'];siblings=copy.deepcopy(t.r[outer]['data']['m_Children']);row=t.add(br,ve,outer,'EffectivenessAndComplexityRow');t.r[outer]['data']['m_Children']=[{'rid':row} if c['rid']==left else c for c in siblings];t.r[left]['data']['m_Parent']={'rid':row};t.r[row]['data']['m_Children']=[{'rid':left}];t.r[row]['data']['m_Classes']=[]
t.edit(row,[P(131105,st.pct(100)),P(131087,st.pct(100)),P(131083,st.en('row')),P(131097,st.px(0)),P(131096,st.px(0)),P(131084,st.num(1)),P(131085,st.num(1))])
right=t.add(t.r,left,row,'ComplexityFactorsScroll');t.sd(right).update(horizontalScrollerVisibility=2,verticalScrollerVisibility=2,horizontalScrollerVisibility_UxmlAttributeFlags=1,verticalScrollerVisibility_UxmlAttributeFlags=1)
for i,grow in [(left,2),(right,1)]:t.edit(i,[P(131105,st.px(0)),P(131082,st.px(0)),P(131097,st.px(0)),P(131095,{'m_ValueType':1,'valueIndex':3}),P(131087,st.pct(100)),P(131084,st.num(grow)),P(131085,st.num(1))])
t.edit(left,[P(131093,st.px(8))])
headerdoc=objs[-966834888143150418].read_typetree();hr=refs(headerdoc);hs=objs[headerdoc['inlineSheet']['m_PathID']].read_typetree()
popup=objs[5092198112228141680].read_typetree();pr=refs(popup);ps=objs[popup['inlineSheet']['m_PathID']].read_typetree()
config=t.add(hr,1047,right,'ComplexityNativeModeSwitch');t.edit(config,[P(131105,st.pct(100)),P(131097,st.px(0))])
for origin in [1068,1069]:
 mapper=t.add(hr,origin,config,'ComplexityContext'+str(origin));t.sd(mapper)['Mappings'] += [{'m_serialisedType':0,'from':'isCreatingTactics','to':{'m_path':'const.False'},'type':{'id':0}},{'m_serialisedType':0,'from':'levelString','to':{'m_path':'const.EmptyString'},'type':{'id':0}}];t.edit(mapper,[P(131105,st.pct(100)),P(131097,st.px(0))])
 heading=t.add(pr,1007,mapper,'EmbeddedComplexityHeading',ps,True);t.edit(heading,[P(131105,st.pct(100)),P(131097,st.px(0)),P(131083,st.en('row'))])
 title=next(c['rid'] for c in t.r[heading]['data']['m_Children'] if t.r[c['rid']]['data']['m_FullTypeName']=='SI.Bindable.SIText');t.edit(title,[P(65537,st.px(12)),P(65552,st.en('normal')),P(131097,st.px(0)),P(131085,st.num(1))])
 factors=t.add(pr,1023,mapper,'ComplexityKeyFactors',ps,True);listing=t.r[factors]['data']['m_Children'][0]['rid'];s=t.sd(listing)
 for k,v in {'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':2,'DynamicElements':1}.items():s[k]=v;s[k+'_UxmlAttributeFlags']=1
 t.edit(factors,[P(131105,st.pct(100)),P(131097,st.px(0))]);t.edit(listing,[P(131105,st.pct(100)),P(131097,st.px(0)),P(65552,st.en('normal'))])
 assert s['Binding']['m_direct']['Path']['m_path']=='keyfactor.KeyFactors'
for u in popup['m_Usings']:
 if not any(x['alias']==u['alias'] for x in d['m_Usings']):d['m_Usings'].append(copy.deepcopy(u))
t.save(module)
# Native row descriptions already support full description strings; source templates unchanged.
metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==module);src=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==5092198112228141680);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for ptr in meta['m_PreloadTable'][src['preloadIndex']:src['preloadIndex']+src['preloadSize']]:
 if ptr not in span:span.append(copy.deepcopy(ptr))
entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span);metaobj.save_typetree(meta);changed[metaobj.path_id]=meta
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==objs.keys()
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h,i
for i,data in changed.items():assert check[i].read_typetree()==data,i
(OUT/W).write_bytes(output)
report={'installed':False,'runtime_verified':False,'portrait_badges':checks,'badge_position':'outside upper-left;32x14;10px bold;2px gap','percentage':'direct 0..100','columns':[2,1],'gap':8,'complexity_native_mode_switch':True,'header':'native Tactical Complexity + native gauge','list':'keyfactor.KeyFactors','scrollbars_hidden':True,'native_popup_and_all_other_objects_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"];installer=list(restore)
for p,b in before.items():
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/W)+"' -Destination '"+str(p)+"' -Force");installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Package changed since preparation.' }")
for p in before:installer.append("Copy-Item -LiteralPath '"+str(OUT/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p in before:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'badges':2,'layout':[2,1]}))
