"""Semantic matching of serialized UI Toolkit nodes across native rebuilds."""
import collections
import copy
import difflib


def nodes(tree):
    refs = {r['rid']:r for r in tree.get('references',{}).get('RefIds',[])}
    assets = {rid:r for rid,r in refs.items() if 'm_FullTypeName' in r.get('data',{})}
    def serialized(rid):
        return refs.get(assets[rid]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
    return refs,assets,serialized


def match_nodes(before, after):
    ar,aa,ad = nodes(before)
    br,ba,bd = nodes(after)
    mapping = {}
    used = set()
    def name(assets,data,rid):
        d = assets[rid]['data']
        props = d.get('m_Properties',[])
        names = [props[i+1] for i in range(0,len(props)-1,2) if props[i]=='name']
        return data(rid).get('name') or (names[0] if names else '')
    def signature(assets,data,rid):
        d=assets[rid]['data']
        return d['m_FullTypeName'],name(assets,data,rid),d.get('m_TemplateAlias','')
    def put(a,b):
        if a in mapping or b in used:return False
        if aa[a]['data']['m_FullTypeName']!=ba[b]['data']['m_FullTypeName']:return False
        mapping[a]=b;used.add(b)
        return True
    # Names and preserved UXML identities provide stable anchors independent of RID numbering.
    for keyfn in [lambda assets,data,rid:(name(assets,data,rid),assets[rid]['data']['m_FullTypeName']) if name(assets,data,rid) else None,
                  lambda assets,data,rid:assets[rid]['data'].get('m_Id')]:
        ai=collections.defaultdict(list);bi=collections.defaultdict(list)
        for rid in aa:ai[keyfn(aa,ad,rid)].append(rid)
        for rid in ba:bi[keyfn(ba,bd,rid)].append(rid)
        for key,ids in ai.items():
            if key and len(ids)==len(bi[key])==1:put(ids[0],bi[key][0])
    aroot=before.get('m_VisualTree',{}).get('rid')
    broot=after.get('m_VisualTree',{}).get('rid')
    if aroot in aa and broot in ba:put(aroot,broot)
    for _ in range(len(aa)+1):
        count=len(mapping)
        for a,b in list(mapping.items()):
            ac=[x['rid'] for x in aa[a]['data']['m_Children'] if x['rid'] in aa and x['rid'] not in mapping]
            bc=[x['rid'] for x in ba[b]['data']['m_Children'] if x['rid'] in ba and x['rid'] not in used]
            sa=[signature(aa,ad,i) for i in ac];sb=[signature(ba,bd,i) for i in bc]
            for block in difflib.SequenceMatcher(None,sa,sb,autojunk=False).get_matching_blocks():
                for k in range(block.size):put(ac[block.a+k],bc[block.b+k])
        if len(mapping)==count:break
    return mapping


def normalize_refs(tree, target, offset=100000):
    """Rename target's matched RIDs into source identity space for a meaningful audit."""
    mapping=match_nodes(tree,target)
    ar,aa,ad=nodes(tree);br,ba,bd=nodes(target)
    reverse={v:k for k,v in mapping.items()}
    for a,b in mapping.items():
        asd=aa[a]['data'].get('m_SerializedData',{}).get('rid',-2)
        bsd=ba[b]['data'].get('m_SerializedData',{}).get('rid',-2)
        if asd!=-2 and bsd!=-2:reverse[bsd]=asd
    assigned=set(reverse.values())
    def nested(a,b):
        if isinstance(a,dict) and isinstance(b,dict):
            if set(a)==set(b)=={'rid'}:
                x,y=a['rid'],b['rid']
                if x in ar and y in br and x!=-2 and y!=-2 and ar[x]['type']==br[y]['type']:
                    if y not in reverse and x not in assigned:
                        reverse[y]=x;assigned.add(x)
                return
            for k in a.keys() & b.keys():
                if k not in {'m_Children','m_Parent'}:nested(a[k],b[k])
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for x,y in zip(a,b):nested(x,y)
    for _ in range(20):
        count=len(reverse)
        for b,a in list(reverse.items()):
            if a in ar and b in br:nested(ar[a].get('data',{}),br[b].get('data',{}))
        if len(reverse)==count:break
    next_id=max([1000]+list(ar))+offset
    for rid in br:
        if rid!=-2 and rid not in reverse:
            reverse[rid]=next_id;next_id+=1
    def convert(v):
        if isinstance(v,dict):
            return {k:(reverse.get(x,x) if k=='rid' else convert(x)) for k,x in v.items()}
        if isinstance(v,list):return [convert(x) for x in v]
        return copy.deepcopy(v)
    return convert(target),mapping
