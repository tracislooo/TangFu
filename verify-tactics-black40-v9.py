from pathlib import Path
source=Path('verify-tactics-black80-v8.py').read_text('utf8')
source=source.replace("v(stars,131104)[0]['value']==3","v(stars,131104)[0]['value']==-2")
exec(compile(source,'V9 independent installed verification','exec'))
for p in m['after_sha256']:
 if not p.endswith('ui-styles_assets_default.bundle'):continue
 count=0
 for o in UnityPy.load(p).objects:
  if o.type.name!='MonoBehaviour':continue
  data=o.read_typetree()
  for rule in data.get('m_Rules',[]):
   if not any(p['m_Value'] in ['tf-tactics-pitch-black','tf-tactics-pitch-black-dark-header'] for sel in rule['m_ComplexSelectors'] for s in sel['m_Selectors'] for p in s['m_Parts']):continue
   h=next(p for p in rule['m_Properties'] if p['m_Id']==458752)['m_Values'][0]
   assert data['colors'][h['valueIndex']]=={'r':0.,'g':0.,'b':0.,'a':struct.unpack('<f',struct.pack('<f',.6))[0]};count+=1
 assert count==4
d,r,sd,v=tree(1593217430813700770)
assert abs(v(1002,458752)[0]['a']-.6)<1e-6
d,r,sd,v=tree(-966834888143150418)
data=bytes(sd(1004)['BindGradientFunc']['m_inputs']['m_variable']['m_argumentBytes']);offset=1
for _ in range(data[0]):
 n=struct.unpack_from('<I',data,offset)[0];offset+=4
 assert all(abs(a-b)<1e-6 for a,b in zip(struct.unpack_from('<4f',data,offset+n-16),(0,0,0,.6)));offset+=n
print('V9: all affected background RGBA values verified at black/alpha 0.6; stars y=-2, scale=1.5.')
