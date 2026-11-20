from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
out=R/'list-portrait-inspection';out.mkdir(exist_ok=True)
lines=[]
for key in ['gameworld','global','match']:
 e=UnityPy.load(str(GAME/f'ui-visualtreeassets_assets_{key}visualtreeassetpreload.bundle'));obs={o.path_id:o for o in e.objects}
 for o in obs.values():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name()
  if not (any(x in name.lower() for x in ['personpicture','person-picture','playercell','namecell','portraitcell','playername','personname']) or name in ['PlayerKitNameCell','PlayerPortraitCell']):continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  s=obs[d['inlineSheet']['m_PathID']].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
  (out/(key+'-'+name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  (out/(key+'-'+name+'-style.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
  lines.append(f'\n{key} {name} {o.path_id} USINGS {d["m_Usings"]}')
  for i,x in r.items():
   a=x.get('data',{})
   if 'm_Parent' not in a:continue
   sd=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   vals={k:v for k,v in sd.items() if not k.endswith('UxmlAttributeFlags') and k not in ['uxmlAssetId','dataSourceUnityObject','dataSourcePathString','dataSourceTypeString','bindings'] and v not in [None,'',0,[],{},False]}
   props=[]
   if a.get('m_RuleIndex',-1)>=0:
    for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']:
     vs=[]
     for v in p['m_Values']:
      pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(v['m_ValueType']);vs.append(s[pool][v['valueIndex']] if pool else v)
     props.append((p['m_Id'],vs))
   lines.append(f'{i} parent={a["m_Parent"]} {a.get("m_FullTypeName") or a.get("m_TemplateAlias")} class={a.get("m_Classes")} {json.dumps(vals,ensure_ascii=False)} STYLE {props}')
(out/'summary.txt').write_text('\n'.join(lines),'utf8')
print(str(out))
