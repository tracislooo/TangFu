from pathlib import Path
import sys,json,re,importlib.util
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
O=R/'analysis/comeback-stadium-20261115';O.mkdir(exist_ok=True)
cfg=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
for tag,folder in [('donor',Path(r'K:\桌面\FM27 Comeback Skin v1.8.3\Skin files')),('game',Path(cfg['bundle_root'])),('skin',Path(cfg['skin_packages']))]:
 for bn in [W,'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
  e=UnityPy.load(str(folder/bn));obs={o.path_id:o for o in e.objects}
  for p,o in obs.items():
   if o.type.name!='MonoBehaviour':continue
   n=o.peek_name()
   if not (re.search('stadium|ClubInfoBackground|ClubInfoReport',n,re.I) or n=='ClubOverviewStadiumStack'):continue
   d=o.read_typetree();(O/f'{tag}-{n}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
   if 'references' not in d:continue
   rs={r['rid']:r.get('data',{}) for r in d['references']['RefIds']}
   st=obs[d['inlineSheet']['m_PathID']].read_typetree() if 'inlineSheet' in d else {}
   (O/f'{tag}-{n}-style.json').write_text(json.dumps(st,ensure_ascii=False,indent=2),'utf8')
   print(tag,n,p,'usings',d.get('m_Usings'),flush=True)
   for i,a in rs.items():
    if 'm_SerializedData' not in a:continue
    sd=rs[a['m_SerializedData']['rid']];typ=a.get('m_FullTypeName','');s=json.dumps(sd,ensure_ascii=False)
    if 'SIImage' in typ or any(x in s.lower() for x in ['selectedstadium','graphics/','background','stadium','bindings']):
     print(' NODE',i,'parent',a.get('m_Parent'),'type',typ,'alias',a.get('m_TemplateAlias'),'SD',s)
     ix=a.get('m_RuleIndex',-1)
     if ix>=0:
      print(' STYLE',[(pr['m_Id'],[st.get({2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}.get(v['m_ValueType'],''),[])[v['valueIndex']] if v['m_ValueType']>1 else v for v in pr['m_Values']]) for pr in st['m_Rules'][ix]['m_Properties']])
spec=importlib.util.spec_from_file_location('cm',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for tag,cp in [('game',Path(cfg['aa_root'])/'catalog.bin'),('skin',Path(cfg['skin_packages'])/'catalog.bin')]:
 c=cm.Catalog(cp.read_bytes());ks=dict(c.keys());print('CATALOG',tag,'stadium-keys',sum(isinstance(k,str) and 'stadium' in k for k in ks))
 for k in ['1040','tf27/stadium/id/1040/background','graphics/pictures/stadium/1040/background','41e6b45ba23e8834c8c178c2ae247e6c']:
  print(tag,k,[c.location(x[0]) for x in c.array(ks[k],'I')] if k in ks else 'MISSING')
