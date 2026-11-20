"""Independent paint-only, crash-regression, and registration checks for the theme."""
from pathlib import Path
from collections import Counter
import copy, hashlib, importlib.util, json, re, sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
state=json.loads((R/'current-global-light-theme.json').read_text('utf8'))
out=Path(state['record']);m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
installed='--installed' in sys.argv
assert m['palette']['page']=='E7E7E7' and m['palette']['card']=='F7F7F5'
paint_ids={65536,458752,196610,262146,458758,458761,458762,458763}
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
spec=importlib.util.spec_from_file_location('catalog_qa',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalogs={}
sha=lambda b:hashlib.sha256(b).hexdigest()
for folder in [Path(tx['game']),Path(tx['skin'])]:
    p=folder.parent/'catalog.bin' if folder==Path(tx['game']) else folder/'catalog.bin'
    cat=cm.Catalog(p.read_bytes());keys=dict(cat.keys())
    catalogs[str(folder)]=(cat,keys)

def objects(raw):return {o.path_id:o for o in UnityPy.load(raw).objects}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def description(rr,rid):
    a=rr[rid].get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
    return ' '.join([sd.get('name','') or '',sd.get('templateId','') or '',*a.get('m_Classes',[])])
def protected_stage(rr,rid):
    seen=set()
    while rid in rr and rid not in seen:
        seen.add(rid);a=rr[rid].get('data',{})
        if re.search(r'PortraitLayerStage|OverviewCardSixRatings|OverviewCardGoalkeeperRatings|ReportMiddleCA\d+Layer',description(rr,rid)):
            return True
        rid=a.get('m_Parent',{}).get('rid')
    return False
def same_prefix(new,old):
    assert new['m_Rules'][:len(old['m_Rules'])]==old['m_Rules'],'An original rule was overwritten'
    norm=copy.deepcopy(new);norm['m_Rules']=norm['m_Rules'][:len(old['m_Rules'])]
    for pool in set(poolmap.values()):
        assert new[pool][:len(old[pool])]==old[pool]
        norm[pool]=norm[pool][:len(old[pool])]
    assert norm==old,'Stylesheet metadata changed'
    for i,rule in enumerate(new['m_Rules']):
        for p in rule['m_Properties']:
            for h in p['m_Values']:
                if h['m_ValueType'] in poolmap:assert 0<=h['valueIndex']<len(new[poolmap[h['m_ValueType']]])
        if i<len(old['m_Rules']) or not rule['m_ComplexSelectors']:continue
        for s in rule['m_ComplexSelectors']:
            assert s['ruleIndex']==i
        for p in rule['m_Properties']:
            assert p['m_Id'] in paint_ids or p['m_Id']==-1
            assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4,'New selector paint must be literal'
            if p['m_Id']==-1:
                assert not p['m_CustomName'].startswith(('--colours-base-','--linear-','--data-tables-accent','--tactics-','--ranges-'))
    for c in new['colors'][len(old['colors']):]:assert all(0<=c[k]<=1 for k in ['r','g','b','a'])

reports=[];all_counts=Counter();registrations=0;embedded_vtas=0
for target,source in tx['sources'].items():
    path=Path(target);raw=path.read_bytes() if installed else Path(source).read_bytes()
    assert sha(raw)==m['after_sha256'][target]
    before=Path(tx['before'][target]).read_bytes();assert sha(before)==m['before_sha256'][target]
    new,old=objects(raw),objects(before)
    assert set(new)==set(old),'Asset object IDs changed'
    changed={pid for pid in new if new[pid].get_raw_data()!=old[pid].get_raw_data()}
    assert changed=={int(i) for i in m['objects'][target]['changed_ids']}
    docs=[];sheet_count=0;node_count=0
    for pid in changed:
        assert new[pid].type.name=='MonoBehaviour'
        a,b=new[pid].read_typetree(),old[pid].read_typetree()
        if 'm_Rules' in a:
            same_prefix(a,b);sheet_count+=1;continue
        assert 'inlineSheet' in a
        rr,orr=refs(a),refs(b)
        assert set(rr)==set(orr)
        norm=copy.deepcopy(a);nr=refs(norm)
        sid=a['inlineSheet']['m_PathID'];sh=new[sid].read_typetree();osh=old[sid].read_typetree()
        for rid,rec in rr.items():
            data=rec.get('data',{});prior=orr[rid].get('data',{})
            if data.get('m_RuleIndex')==prior.get('m_RuleIndex'):continue
            ni,oi=data['m_RuleIndex'],prior['m_RuleIndex']
            assert ni>=len(osh['m_Rules']) and not sh['m_Rules'][ni]['m_ComplexSelectors']
            props=sh['m_Rules'][ni]['m_Properties'];oldprops=osh['m_Rules'][oi]['m_Properties'] if oi>=0 else []
            special=a['m_Name']=='GameWorldBackground'
            allowed=paint_ids|({458753} if special else set())
            assert [p for p in props if p['m_Id'] not in allowed]==[p for p in oldprops if p['m_Id'] not in allowed]
            for p in props:
                oldp=next((v for v in oldprops if v['m_Id']==p['m_Id']),None)
                if p in oldprops:continue
                assert p['m_Id'] in allowed,(a['m_Name'],rid,p['m_Id'])
                if p['m_Id']==458753:
                    assert special and len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==7
                    assert sh['strings'][p['m_Values'][0]['valueIndex']]=='none'
                else:
                    assert len(p['m_Values'])==1 and p['m_Values'][0]['m_ValueType']==4,'New inline color variable'
                if p['m_Id']==65536 and protected_stage(orr,rid):
                    assert oldp is not None
                    hs=oldp['m_Values']
                    if len(hs)==1 and hs[0]['m_ValueType']==4:
                        c=osh['colors'][hs[0]['valueIndex']]
                        assert not all(c[k]>.9 for k in ['r','g','b']),'White ink on FC picture was recolored'
            nr[rid]['data']['m_RuleIndex']=prior['m_RuleIndex'];node_count+=1
        assert norm==b,'Layout, binding, event, class, or serialized field changed'
        docs.append((pid,a['m_Name']))
    # Verify actual VTA GUID/type/bundle registrations, without mutating catalog.
    cat,keys=catalogs[str(path.parent)]
    meta=next(o.read_typetree() for o in new.values() if o.type.name=='AssetBundle')
    docids={pid for pid,name in docs};byguid={pid:[] for pid in docids}
    for guid,item in meta['m_Container']:
        pid=item['asset']['m_PathID']
        if pid in byguid and re.fullmatch('[0-9a-f]{32}',guid):byguid[pid].append(guid)
    for pid,name in docs:
        if not byguid[pid]:
            # Some native nested VTAs have no public address key; their original
            # direct references, owning bundle and object bytes metadata persist.
            embedded_vtas+=1
            continue
        for guid in byguid[pid]:
            assert guid in keys,('Missing existing catalog GUID',name,guid)
            locs=[cat.location(l[0]) for l in cat.array(keys[guid],'I')]
            typed=[l for l in locs if l['type'][1]=='UnityEngine.UIElements.VisualTreeAsset']
            assert typed,('Missing VTA catalog type',name)
            for loc in typed:
                assert loc['internal']==guid and loc['dependencies']
                owner=cat.location(loc['dependencies'][0])['internal'].replace('\\','/')
                assert owner.endswith('/'+path.name),('Owning bundle must be first dependency',name,owner)
            registrations+=1
    counts={'documents':len(docs),'style_objects':sheet_count,'nodes':node_count,'unchanged_objects':len(new)-len(changed)}
    all_counts.update(counts);reports.append({'target':target,**counts,'object_inventory_layout_and_bindings_preserved':True})
    print(path.parent.name,path.name,'checked',len(changed),'objects',flush=True)

def luminance(code):
    rgb=[int(code[i:i+2],16)/255 for i in [0,2,4]]
    return sum((c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4)*w for c,w in zip(rgb,[.2126,.7152,.0722]))
ratios=[]
for text in ['text','secondary','link']:
    for bg in ['page','card','control','odd','hover','selected','pressed']:
        lo,hi=sorted([luminance(m['palette'][text]),luminance(m['palette'][bg])]);ratio=(hi+.05)/(lo+.05)
        assert ratio>=4.5,(text,bg,ratio);ratios.append(round(ratio,2))
result={'passed':True,'mode':'installed' if installed else 'prepared','counts':dict(all_counts),'files':reports,
        'catalog_registrations_verified':registrations,'embedded_vtas_without_public_guid':embedded_vtas,
        'minimum_palette_text_contrast':min(ratios),
        'no_new_inline_color_variables':True,'pictures_state_data_and_geometry_preserved':True,'runtime_verified':False}
(out/('qa-installed.json' if installed else 'qa-prepared.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False),flush=True)
