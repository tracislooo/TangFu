from pathlib import Path
import sys,json,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
names=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle']
result={}
for name in names:
 new=UnityPy.load(str(GAME/name));old=UnityPy.load(str(SKIN/name));no={o.path_id:o for o in new.objects};oo={o.path_id:o for o in old.objects}
 print('BUNDLE',name,'CAB',[(a.name,a.unity_version) for a in new.assets],[(a.name,a.unity_version) for a in old.assets],'objects',len(no),len(oo))
 added=set(oo)-set(no);diff=[]
 for pid in set(oo)&set(no):
  if oo[pid].get_raw_data()!=no[pid].get_raw_data():
   diff.append({'id':pid,'type':oo[pid].type.name,'oldname':oo[pid].peek_name() if oo[pid].type.name in ['MonoBehaviour','Texture2D','Font'] else '', 'newname':no[pid].peek_name() if no[pid].type.name in ['MonoBehaviour','Texture2D','Font'] else ''})
 print('CUSTOM',[(i,oo[i].type.name,oo[i].peek_name() if oo[i].type.name in ['MonoBehaviour','Texture2D'] else '') for i in sorted(added)])
 print('DIFFERENT',len(diff),diff[:35])
 result[name]={'old_ids_missing_in_new':[{'id':i,'type':oo[i].type.name,'name':oo[i].peek_name() if oo[i].type.name in ['MonoBehaviour','Texture2D'] else ''} for i in sorted(added)],'shared_differences':diff,'new_count':len(no),'old_count':len(oo)}
bg=UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle'));bn={o.peek_name():o.path_id for o in bg.objects if o.type.name=='Texture2D'}
print('BACKGROUND',len(bn),'rings',sum(n.startswith('FitnessPercentRing') for n in bn),'CA',sum(n.startswith('CA') for n in bn),'hidden',[n for n in bn if n.startswith('HIDE')])
result['background_names']=bn
(R/'update-migration-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
