"""Three-way field and inline-style merge for the current native build."""
import copy
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('semantic',Path(__file__).with_name('semantic-ui-update.py'))
semantic=importlib.util.module_from_spec(spec);spec.loader.exec_module(semantic)
ABSENT=object()
conflicts=[]

def merge(a,b,c,path=''):
    if a==b:return copy.deepcopy(c) if c is not ABSENT else ABSENT
    if a==c or b==c:return copy.deepcopy(b) if b is not ABSENT else ABSENT
    if path.endswith(('/m_Id','/uxmlAssetId','/m_ContentHash','/m_Script')) and c is not ABSENT:return copy.deepcopy(c)
    if isinstance(a,dict) and isinstance(b,dict) and isinstance(c,dict):
        result={}
        for k in dict.fromkeys(list(c)+list(b)+list(a)):
            value=merge(a.get(k,ABSENT),b.get(k,ABSENT),c.get(k,ABSENT),path+'/'+k)
            if value is not ABSENT:result[k]=value
        return result
    if isinstance(a,list) and isinstance(b,list) and isinstance(c,list):
        for field in ['rid','alias','m_columnID','m_id','m_elementID','DescriptionName','m_Id','m_PathID']:
            seqs=[a,b,c]
            if not all(all(isinstance(v,dict) and field in v for v in s) for s in seqs):continue
            keys=[[str((v[field],v.get('m_CustomName',''))) if field=='m_Id' else str(v[field]) for v in s] for s in seqs]
            if any(len(set(k))!=len(k) for k in keys):continue
            maps=[dict(zip(k,s)) for k,s in zip(keys,seqs)]
            merged=merge(*maps,path+'/'+field)
            order=[k for k in keys[1] if k in merged]
            for i,k in enumerate(keys[2]):
                if k not in merged or k in order:continue
                prev=next((v for v in reversed(keys[2][:i]) if v in order),None)
                order.insert(order.index(prev)+1 if prev is not None else 0,k)
            return [merged[k] for k in order]
        if path.endswith(('/m_Classes','/m_StylesheetPaths')) and all(isinstance(x,str) for s in [a,b,c] for x in s):
            return list(dict.fromkeys([x for x in b if x not in a or x in c]+[x for x in c if x not in a]))
        if len(a)==len(b)==len(c):return [merge(x,y,z,path+'/'+str(i)) for i,(x,y,z) in enumerate(zip(a,b,c))]
    if a is ABSENT and b is ABSENT:return copy.deepcopy(c)
    if b is ABSENT:return ABSENT
    if c is ABSENT:return copy.deepcopy(b)
    conflicts.append({'path':path,'original':str(a)[:180],'skin':str(b)[:180],'native':str(c)[:180]})
    return copy.deepcopy(b)

POOLS={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings',9:'strings',10:'strings',12:'scalableImages',13:'strings'}
def decode_rule(sheet,i):
    if i<0:return None
    r=copy.deepcopy(sheet['m_Rules'][i])
    for selector in r['m_ComplexSelectors']:selector.pop('ruleIndex',None)
    for prop in r['m_Properties']:
        for h in prop['m_Values']:
            pool=POOLS.get(h['m_ValueType'])
            if pool:h['valueIndex']={'decoded':copy.deepcopy(sheet[pool][h['valueIndex']])}
    return r

def encode_rule(sheet,rule):
    if rule is None:return -1
    r=copy.deepcopy(rule)
    for prop in r['m_Properties']:
        for h in prop['m_Values']:
            pool=POOLS.get(h['m_ValueType'])
            if pool:
                v=h['valueIndex']['decoded']
                if v not in sheet[pool]:sheet[pool].append(v)
                h['valueIndex']=sheet[pool].index(v)
    i=len(sheet['m_Rules'])
    for selector in r['m_ComplexSelectors']:selector['ruleIndex']=i
    sheet['m_Rules'].append(r)
    return i

def merge_ui(a,b,c,ash,bsh,csh):
    b=semantic.normalize_refs(a,b,100000)[0]
    c=semantic.normalize_refs(a,c,200000)[0]
    for t,sh in [(a,ash),(b,bsh),(c,csh)]:
        for ref in t['references']['RefIds']:
            d=ref.get('data',{})
            if 'm_RuleIndex' in d:d['__inline']=decode_rule(sh,d.pop('m_RuleIndex'))
    result=merge(a,b,c,a['m_Name'])
    sheet=copy.deepcopy(csh)
    for ref in result['references']['RefIds']:
        d=ref.get('data',{})
        if '__inline' in d:d['m_RuleIndex']=encode_rule(sheet,d.pop('__inline'))
    # The selected tree must have a consistent parent graph after insertion/removal.
    refs={r['rid']:r for r in result['references']['RefIds']}
    for rid,r in refs.items():
        for child in r.get('data',{}).get('m_Children',[]):
            if child['rid'] in refs:refs[child['rid']]['data']['m_Parent']={'rid':rid}
    return result,sheet

def merge_styles(a,b,c):
    def keyed(t):
        counts={};result={};order=[]
        for i,r in enumerate(t['m_Rules']):
            selectors=copy.deepcopy(r['m_ComplexSelectors'])
            for selector in selectors:selector.pop('ruleIndex',None)
            key=json.dumps(selectors,sort_keys=True)
            count=counts.get(key,0);counts[key]=count+1
            key+=f'#{count}';result[key]=decode_rule(t,i);order.append(key)
        return result,order
    aa,ao=keyed(a);bb,bo=keyed(b);cc,co=keyed(c)
    rr=merge(aa,bb,cc,'styles')
    result=copy.deepcopy(c);result['m_Rules']=[]
    order=[k for k in co if k in rr]+[k for k in bo if k not in cc and k in rr]
    for k in order:encode_rule(result,rr[k])
    return result
