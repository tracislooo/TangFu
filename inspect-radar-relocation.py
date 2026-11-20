from pathlib import Path
R=Path(__file__).parent
exec(compile((R/'refine-card-inner-layout.py').read_text(encoding='utf8').split('\nportrait = rr[1285]')[0],'<loader>','exec'))
def dump(d,ob,out):
 r={x['rid']:x for x in d['references']['RefIds']};s=ob[d['inlineSheet']['m_PathID']].read_typetree()
 lines=['NAME '+d['m_Name'],'USINGS '+json.dumps(d['m_Usings'])]
 def walk(i,dep):
  a=r[i]['data']; sd=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  styles=s['m_Rules'][a['m_RuleIndex']]['m_Properties'] if a.get('m_RuleIndex',-1)>=0 else []
  vals={str(p['m_Id']):[('kw',h['valueIndex']) if h['m_ValueType']==1 else s[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in styles}
  lines.append(' '*dep+str(i)+' '+r[i]['type']['class']+' '+str(sd.get('name',''))+' '+str(a.get('m_TemplateAlias',''))+' '+json.dumps(vals))
  if any(x in r[i]['type']['class'] for x in ['Binding','Switch','Chart','Radar','Toggle','Button']):lines.append(' '*dep+json.dumps(sd,ensure_ascii=False))
  for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
 walk(1001,0)
 (R/out).write_text('\n'.join(lines),encoding='utf8')
dump(doc,objects,'live-full-radar-tree.txt')
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects}
for pid in [-930000000001003]:dump(go[pid].read_typetree(),go,'live-private-attributes-tree.txt')
print('dumped')
