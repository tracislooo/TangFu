from pathlib import Path
import sys,json
R=Path(__file__).parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')
e=UnityPy.load(str(p));o={x.path_id:x for x in e.objects};d=o[-7710242645031577538].read_typetree();s=o[d['inlineSheet']['m_PathID']].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def visit(i,depth=0):
 a=r[i]['data'];v=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 props={p['m_Id']:[s[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else h for h in p['m_Values']] for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']} if a.get('m_RuleIndex',-1)>=0 else {}
 print(' '*depth,str(i),a.get('m_FullTypeName'),v.get('name',''),a.get('m_TemplateAlias',''),a.get('m_Classes'),json.dumps(props),json.dumps({k:x for k,x in v.items() if any(z.lower() in k.lower() for z in ['aspect','pitch','height','width','direction'])}))
 for x in a.get('m_Children',[]):visit(x['rid'],depth+1)
for i in [3123,3169,3261]:visit(i)
(R/'highlight-bottom-current-style.json').write_text(json.dumps(s),'utf8')
