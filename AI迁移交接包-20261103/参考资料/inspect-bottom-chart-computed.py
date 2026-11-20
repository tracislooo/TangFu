exec(compile(open('inspect-highlight-bottom-charts.py',encoding='utf8').read().split('for i in [3123')[0],'inspect-highlight-bottom-charts.py','exec'))
import copy
GAME=p.parent
old_refs=r;old_style=s
def data_before(i):return r.get(r[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
code=(R/'reflow-highlight-comparison-four-by-four.py').read_text('utf8').split('# Resolve the existing desktop style metrics.')[1].split('\n',1)[1].split('f32=lambda value:')[0]
exec(code)
nodes=[3134,3443,3449,3452,3457,3461,3453,3136,3140,3143,3148,3178,3471,3474,3479,3483,3475,3180,3184,3186,3188,3191,3195,3199,3204,3210,3211,3221,3274,3493,3496,3501,3505,3497,3276,3281,3284,3285]
for i in nodes:
 values={}
 for _,_,_,sheet,selector,properties in selectors:
  if matches(i,selector['m_Selectors']):
   for prop in properties:values[prop['m_Id']]=(sheet,prop['m_Values'])
 idx=r[i]['data'].get('m_RuleIndex',-1)
 if idx>=0:
  for prop in s['m_Rules'][idx]['m_Properties']:values[prop['m_Id']]=(s,prop['m_Values'])
 out={}
 for k,(sheet,handles) in values.items():
  if not (131072<=k<=131105 or k==65537):continue
  try:v=resolve(sheet,handles)
  except AssertionError:v=None
  if v is None:
   v=[(h['m_ValueType'],sheet['strings'][h['valueIndex']]) for h in handles if h['m_ValueType'] in [7,8]]
  out[k]=v
 print(i,data_before(i).get('name'),json.dumps(out))
