from collections import Counter
def unpack(raw):
 b=bytes(raw);p=1;args=[]
 for _ in range(b[0]):
  size=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+size]);p+=size
 assert p==len(b);return args
def verify_node_styles(doc):
 for rid,a in doc.r.items():
  a=a.get('data',{});ri=a.get('m_RuleIndex',-1)
  if ri<0:continue
  for p in doc.s['m_Rules'][ri]['m_Properties']:
   assert all(h['m_ValueType']!=10 for h in p['m_Values']),('Unsafe inline variable introduced',doc.d['m_Name'],rid)
combined=Doc(W,pid=-970000000001000)
def styleval(doc,node,key):
 p=next(p for p in doc.s['m_Rules'][doc.a(node)['m_RuleIndex']]['m_Properties'] if p['m_Id']==key)
 h=p['m_Values'][0];return doc.s[poolmap[h['m_ValueType']]][h['valueIndex']]
def evaluate(doc,node,value):
 while doc.a(node).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
  raw=doc.data(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'];args=unpack(raw)
  limit=struct.unpack_from('<i',args[1],len(args[1])-4)[0]
  node=doc.a(node)['m_Children'][int(value is not None and value>limit)]['rid']
 return node
def colour_tuple(c):return tuple(round(c[k]*255) for k in ['r','g','b'])
bgenv=UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle'));textures={o.path_id:o for o in bgenv.objects if o.type.name=='Texture2D'}
percent_cases=0;pixel_checks=0
for metric,size in [('Condition',22),('Sharpness',12)]:
 root=combined.named('Combined'+metric+'Above-1')
 for v in range(101):
  leaf=evaluate(combined,root,v);assert combined.data(leaf)['name']=='Combined'+metric+'Value'+str(v)
  children=combined.a(leaf)['m_Children'];text=next(x['rid'] for x in children if 'Percent' in combined.data(x['rid']).get('name',''));ring=next(x['rid'] for x in children if 'Ring' in combined.data(x['rid']).get('name',''))
  assert combined.data(text)['text']==f'{v}%'
  assert styleval(combined,ring,131105)['value']==styleval(combined,ring,131087)['value']==size
  x,y=styleval(combined,ring,131089)['value'],styleval(combined,ring,131104)['value']
  assert (x+size/2,y+size/2)==(45,12)
  imageptr=styleval(combined,ring,458753);image=textures[imageptr['m_PathID']].read().image.convert('RGBA')
  rgba=Counter(tuple(p[:3]) for p in image.getdata() if p[3]>220)
  if rgba and v>0:
   textcol=colour_tuple(styleval(combined,text,65536));col=min(rgba,key=lambda c:max(abs(a-b) for a,b in zip(c,textcol)));assert max(abs(a-b) for a,b in zip(col,textcol))<=2,(metric,v,col,textcol)
   pixel_checks+=1
  percent_cases+=1
 assert combined.data(evaluate(combined,root,None))['name'].endswith('ValueNone')
fatdoc=Doc(W,pid=-970000000004000);root=fatdoc.a(1001)['m_Children'][0]['rid'];cases=0
def fatigue_colour(v):
 v=max(-500,min(1000,v));hue=(1-v/1000)/3 if v>=0 else 1/3-(-v/500)/4
 return tuple(round(x*255) for x in colorsys.hsv_to_rgb(hue,.75,.88))
for v in list(range(-500,1001))+[-501,-999,1001,2000]:
 leaf=evaluate(fatdoc,root,v);d=fatdoc.data(leaf)
 assert d['TextBinding']['m_direct']['Path']['m_path']=='binding' and d['TextBinding']['m_kind']==1
 actual=colour_tuple(styleval(fatdoc,leaf,65536));assert actual==fatigue_colour(v),(v,actual,fatigue_colour(v));cases+=1
assert fatdoc.data(evaluate(fatdoc,root,None))['text']=='--'
for doc in [photo]:verify_node_styles(doc)
for factory,condition_id in [(talk,'halftime-condition-sharpness'),(tactic,'condition')]:
 cols=factory['m_rowData'];c=next(x for x in cols if x['m_id']==condition_id);f=next(x for x in cols if x['m_id']=='tactics-fatigue-value')
 for row,width in [(c,90),(f,40)]:assert row['m_defaultWidth']==row['m_minimumWidth']==width and not row['m_allowWidthAutoResizing']
assert next(c for c in talk['m_rowData'] if c['m_id']=='playerselection')['m_uxmlRef']['m_AssetGUID']=='f394b6c993e756cfa0ff3db880427c5c'
assert next(c for c in tactic['m_rowData'] if c['m_id']=='name')['m_uxmlRef']['m_AssetGUID']==portrait_guid
for bn in [V,VS]:
 for pid,tree in changes[bn].items():
  if 'm_tableView' not in tree:continue
  cfg=tree['m_tableView']['m_tableConfig'];ids=[c['m_columnID'] for c in cfg];ix=ids.index('halftime-condition-sharpness' if 'halftime-condition-sharpness' in ids else 'condition')
  assert ids[ix+1]=='tactics-fatigue-value' and 'sharpness' not in ids
  assert cfg[ix]['m_columnMetadata']['m_widthOverride']==90 and cfg[ix+1]['m_columnMetadata']['m_widthOverride']==40
component_checks={'percent_cases':percent_cases,'ring_text_colour_pixel_checks':pixel_checks,'rings_same_center':[45,12],'ring_sizes_px':[22,12],'fatigue_cases':cases,'raw_fatigue_binding_preserved':True,'missing_states_checked':True,'separate_avatar_and_fixed_width_columns':True,'private_views_keep_original_other_columns':True,'unsafe_inline_variables_added':0}
