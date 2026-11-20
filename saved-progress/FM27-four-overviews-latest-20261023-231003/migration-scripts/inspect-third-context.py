from pathlib import Path
exec(Path('inspect-third-current.py').read_text('utf8').split('for n,pid,ids')[0])
e=UnityPy.load(str(p/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));d=next(o for o in e.objects if o.path_id==-940000000010000).read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
for i in [1119,1166,1167,6312,6314,6316,6318,6320,6322,1703,1011,6298,6228,1035]:
 x=r[i]['data'];s=r.get(x.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(i,s)

