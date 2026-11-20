"""Read current selectable player overview radar geometry without running UI."""
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
L = 'ui-tileslayouts_assets_all.bundle'
POOLS = {2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
NAMES = {131087:'height',131094:'max-height',131096:'min-height',131105:'width',131095:'max-width',
         131097:'min-width',131084:'grow',131085:'shrink',131082:'basis',131083:'direction',
         131073:'align',131074:'self',131088:'justify',458768:'overflow',131102:'position',
         131089:'left',131103:'right',131104:'top',131080:'bottom',131091:'margin-left',
         131092:'margin-right',131093:'margin-top',131090:'margin-bottom',262151:'padding',
         131101:'padding-top',131098:'padding-bottom',131099:'padding-left',131100:'padding-right'}


def discover(base):
    banks, keys, docs = {}, {}, {}
    for bn in [W, G, L]:
        banks[bn] = {o.path_id:o for o in UnityPy.load(str(base/bn)).objects}
        if bn == L:
            continue
        meta = next(o for o in banks[bn].values() if o.type.name=='AssetBundle').read_typetree()
        for key, entry in meta['m_Container']:
            obj = banks[bn][entry['asset']['m_PathID']]
            if obj.type.name!='MonoBehaviour':
                continue
            # Styles and templates can share a container key.
            if 'inlineStyle' in (obj.peek_name() or ''):
                continue
            d = obj.read_typetree()
            if 'm_VisualTree' in d:
                docs[bn,obj.path_id] = d
                keys.setdefault(key,[]).append((bn,obj.path_id))
    pages=[]
    for ptr in banks[L][1332213496068314481].read_typetree()['m_gridElementDescriptions']:
        if ptr['m_FileID']:
            continue
        d=banks[L][ptr['m_PathID']].read_typetree()
        ident=d.get('<ID>k__BackingField','')
        if not (ident.startswith('PlayerOverview') or ident=='PlayerAttributesBlock'):
            continue
        for cfg in d['<Configurations>k__BackingField']:
            for bn,pid in keys.get(cfg['AssetRef']['m_AssetGUID'],[]):
                pages.append(dict(ident=ident,bundle=bn,pid=pid,guid=cfg['AssetRef']['m_AssetGUID']))
    visited=set()

    def visit(bn,pid):
        if (bn,pid) in visited:
            return
        visited.add((bn,pid))
        d=docs[bn,pid]
        aliases={r.get('data',{}).get('m_TemplateAlias') for r in d['references']['RefIds']} - {None,''}
        for use in d['m_Usings']:
            if use['alias'] in aliases:
                for nb,np in keys.get(use.get('path'),[]):
                    visit(nb,np)

    for p in pages:
        visit(p['bundle'],p['pid'])
    targets={k:docs[k] for k in visited if any(r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMSpiderChart'
                                            for r in docs[k]['references']['RefIds'])}
    return banks,pages,targets


def geometry(d,sheet):
    rr={r['rid']:r.get('data',{}) for r in d['references']['RefIds']}
    def sd(i):return rr.get(rr[i].get('m_SerializedData',{}).get('rid'),{})
    def node(i):
        a=rr[i];ix=a.get('m_RuleIndex',-1)
        props={NAMES.get(p['m_Id'],str(p['m_Id'])):[sheet[POOLS[h['m_ValueType']]][h['valueIndex']]
               if h['m_ValueType'] in POOLS else h for h in p['m_Values']]
               for p in (sheet['m_Rules'][ix]['m_Properties'] if ix>=0 else [])}
        return dict(rid=i,name=sd(i).get('name',''),type=a.get('m_FullTypeName'),classes=a.get('m_Classes'),style=props)
    out=[]
    for i,a in rr.items():
        if a.get('m_FullTypeName')!='FM.UI.FMSpiderChart':continue
        parents=[];p=a.get('m_Parent',{}).get('rid')
        while p in rr:
            parents.append(node(p));p=rr[p].get('m_Parent',{}).get('rid')
        out.append(dict(chart=node(i),parameters={k:v for k,v in sd(i).items()if k in ['LabelDistanceFromChart','SpiderChartRadiusPercentage']},ancestors=parents))
    return out


if __name__=='__main__':
    loc=json.loads((R/'current-game-location.json').read_text('utf8'));results=[]
    for tag,base in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
        banks,pages,targets=discover(base)
        rows=[]
        for (bn,pid),d in sorted(targets.items()):
            charts=geometry(d,banks[bn][d['inlineSheet']['m_PathID']].read_typetree())
            rows.append(dict(bundle=bn,pid=pid,name=d['m_Name'],charts=charts))
        results.append(dict(target=tag,pages=pages,documents=rows))
        print(tag,'choices',len(pages),'radar documents',len(rows),'charts',sum(len(r['charts']) for r in rows))
        for row in rows:print(row['pid'],row['name'],[(x['chart']['rid'],x['chart']['name'],x['ancestors'][0]['name']) for x in row['charts']])
    (R/'current-overview-radar-diagnosis.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf8')
