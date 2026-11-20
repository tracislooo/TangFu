from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
p=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')
e=UnityPy.load(str(p));oo={o.path_id:o for o in e.objects}
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 d=oo[pid].read_typetree();print('DOC',pid,d.get('m_Name'),d['inlineSheet']);print('USINGS',d.get('m_Usings'))
 rr={r['rid']:r for r in d['references']['RefIds']}
 for i,r in rr.items():
  v=r.get('data',{})
  if 'm_FullTypeName' in v:
   s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   print(i,v.get('m_FullTypeName'),v.get('m_Classes'), 'parent',v.get('m_Parent'),json.dumps(s,ensure_ascii=False)[:460])
Path('inspect-position-layout.json').write_text(json.dumps({str(pid):oo[pid].read_typetree() for pid in [-940000000005000,-940000000008000,-940000000010020]},ensure_ascii=False),'utf8')
