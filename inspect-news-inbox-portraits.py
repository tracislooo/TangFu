from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent
src=(R/'plan-outside-match-portraits.py').read_text('utf8').split("out={'bases'")[0]
exec(compile(src,'current-template-graph','exec'))
out=R/'news-inbox-portrait-inspection';out.mkdir(exist_ok=True)
lines=[];candidates=[]
for (n,pid),d in docs.items():
 if n not in [W,G] or 'inlineSheet' not in d or not re.search('news|inbox|message|sender|feed|social|interaction-hub',d['m_Name'],re.I):continue
 oo={o.path_id:o for o in env[n].objects};sid=d['inlineSheet']['m_PathID']
 if not sid or sid not in oo:continue
 s=oo[sid].read_typetree();rr={x['rid']:x for x in d['references']['RefIds']};nodes=[]
 for rid,x in rr.items():
  a=x.get('data',{})
  if 'm_Parent' not in a:continue
  sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  props={}
  if a.get('m_RuleIndex',-1)>=0:
   for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']:
    vals=[]
    for v in p['m_Values']:
     pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(v['m_ValueType']);vals.append(s[pool][v['valueIndex']] if pool else v)
    props[p['m_Id']]=vals
  nodes.append({'rid':rid,'parent':a['m_Parent']['rid'],'type':a.get('m_TemplateAlias') or a.get('m_FullTypeName'),'name':sd.get('name'),'classes':a.get('m_Classes'),'styles':props})
 if not any(re.search('picture|portrait|avatar|circle|round|sender',json.dumps(x),re.I) for x in nodes):continue
 candidates.append((n,pid,d['m_Name'],(n,pid) in closure))
 lines.append('\n'+str(candidates[-1])+' USINGS '+str(d['m_Usings']))
 lines.extend(json.dumps(x,ensure_ascii=False) for x in nodes)
(out/'summary.txt').write_text('\n'.join(lines),'utf8');(out/'candidates.json').write_text(json.dumps(candidates,indent=2),'utf8')
print('candidates',len(candidates),str(out))
