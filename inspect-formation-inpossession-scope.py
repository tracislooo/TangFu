import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
e=UnityPy.load('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle');t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='HighlightHomeHorizontalFormation');r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']}
for i,a in r.items():
 if 'm_Parent' not in a:continue
 s=r.get(a.get('m_SerializedData',{}).get('rid'),{});n=s.get('name','')
 if i in [1004,1005] or (1008<i<1066):
  print(i,a['m_Parent']['rid'],a.get('m_FullTypeName') or a.get('m_TemplateAlias'),n,{k:v for k,v in s.items() if k in ['Mappings','ValueVariables','Binding','Parameters']},a.get('m_Properties') if i in [1004,1005] else '')
