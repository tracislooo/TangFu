from pathlib import Path
import json,re
O=Path(__file__).parent
hits=json.loads((O/'hits.json').read_text('utf8'))
names=['ClubHistoryHonoursBlock','ClubHistoryHonoursCard','ClubHistoryHonourCardRow','ClubHistoryHonours_4x4','ClubHistoryHonours_4x4_Row','TeamHistoryHonoursTemplateLarge','TeamHistoryHonoursTemplate','ClubInfoReportBlock','ClubInfoBackgroundBlock','ClubInfoDataBlock','NationInfoReportBlock']
lines=[]
def compact(x):
 if isinstance(x,dict):return {k:compact(v) for k,v in x.items() if v and not k.endswith('UxmlAttributeFlags') and k not in ('uxmlAssetId','dataSourceUnityObject','DebugDisplay')}
 if isinstance(x,list):
  if x and all(isinstance(i,int) and 0<=i<=255 for i in x):return re.findall(r'[ -~]{4,}',bytes(x).decode('latin1'))
  return [compact(v) for v in x]
 return x
def j(x):return json.dumps(compact(x),ensure_ascii=False)
def props(s,rule):
 pools={1:'keywords',2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings',9:'strings',10:'scalableImages'}
 out={}
 for p in rule.get('m_Properties',[]):
  vals=[]
  for v in p.get('m_Values',[]):
   t=v.get('m_ValueType');i=v.get('valueIndex');a=s.get(pools.get(t,''),[])
   vals.append(a[i] if isinstance(i,int) and 0<=i<len(a) else v)
  out[str(p['m_Id'])]=vals
 return out
for h in hits:
 if h['name'] not in names:continue
 d=json.loads((O/'objects'/h['file']).read_text('utf8'));rr={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
 lines.append('\n### '+h['name']+' '+str(h['pid']))
 lines.append('USINGS '+j(d.get('m_Usings')))
 sfile=O/'objects'/f"{Path(h['bundle']).stem}__{d.get('inlineSheet',{}).get('m_PathID')}.json"
 sheet=json.loads(sfile.read_text('utf8')) if sfile.exists() else {}
 for rid,r in rr.items():
  a=r.get('data',{})
  if 'm_FullTypeName' not in a:continue
  sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if h['name'].startswith(('ClubInfo','NationInfo')) and 'fmet-cab' not in str(a) and 'fmet-troph' not in str(a):continue
  lines.append(f"NODE {rid} parent={a.get('m_Parent')} type={a['m_FullTypeName']} classes={a.get('m_Classes')} properties={a.get('m_Properties')} DATA={j(sd)}")
  ri=a.get('m_RuleIndex',-1)
  if 0<=ri<len(sheet.get('rules',[])):lines.append('STYLE '+j(props(sheet,sheet['rules'][ri])))
(O/'structure.txt').write_text('\n'.join(lines),encoding='utf8')
for h in hits:
 if h['name']!='AlwaysAppliedStyleSheet':continue
 s=json.loads((O/'objects'/h['file']).read_text('utf8'))
 for rule in s.get('m_Rules',[]):
  sel=rule.get('m_ComplexSelectors',[])
  if re.search('fmet-cab|fmet-honour',str(sel)):
   lines.append('CSS '+j(sel)+' '+j(props(s,rule)))
(O/'compact.txt').write_text('\n'.join(lines),encoding='utf8')
