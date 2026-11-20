exec(open('inspect-tactical-percent.py',encoding='utf-8-sig').read().split('for bn in')[0])
e=UnityPy.load(str(p/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'))
for o in e.objects:
 if o.path_id!=-930000000001001:continue
 d=o.read_typetree();r={a['rid']:a for a in d['references']['RefIds']}
 for i,x in r.items():
  if x.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':
   s=r[x['data']['m_SerializedData']['rid']]['data']
   if 'Above' in s.get('name',''):print(i,json.dumps(s));break
