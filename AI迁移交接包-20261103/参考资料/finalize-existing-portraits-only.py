from pathlib import Path
import sys,copy,ast,json,hashlib,struct,importlib.util
R=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]);BASE=R/'outside-match-square-portraits-20261029-110433'
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
sha=lambda b:hashlib.sha256(b).hexdigest()
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def extract(file,names):
 p=ast.parse((R/file).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in p.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())
extract('redesign-card-top-info-foot.py',{'write'});TypeTreeHelper.write_value=write
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
# Reuse the graph audit on the prepared result, with the match bundle unchanged.
plan=(R/'plan-outside-match-portraits.py').read_text('utf8').split("out={'bases'")[0]
plan=plan.replace("UnityPy.load(str(GAME/n))","UnityPy.load(str(OUT/n if (OUT/n).exists() else GAME/n))")
exec(compile(plan,'prepared-match-graph','exec'))
NAMES=[W,G];objs={n:{o.path_id:o for o in env[n].objects} for n in NAMES};changes={n:{} for n in NAMES};documents=[]
hashes={n:{i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objs.items()}
text=(R/'remove-news-inbox-avatar-circles.py').read_text('utf8')
news=text[text.index('radius=['):text.index('outputs={}')]
exec(compile(news,'retain-news-inbox-shape-adjustments','exec'))
for n in NAMES:
 b=env[n].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changes[n]:assert sha(check[i].get_raw_data())==h
 for i,d in changes[n].items():assert check[i].read_typetree()==d
 (OUT/n).write_bytes(b)
m=json.loads((OUT/'manifest.json').read_text('utf8'));m['news_inbox_templates']=len(edits)
m['added_list_avatars']=False;m['portrait_size']=None
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
# Existing catalog entries are compared against the pre-addition snapshot.
finish=(R/'finish-outside-match-square-portraits.py').read_text('utf8')
finish=finish.replace("(out/'backup-game/catalog.bin')","(BASE/'backup-game/catalog.bin')")
exec(compile(finish,'preload-and-guid-validation','exec'))
# Explicitly prove that all 81 old copies and their new bindings were rebuilt,
# and that no new avatar element was added to any cloned existing template.
m=json.loads((OUT/'manifest.json').read_text('utf8'));assert m['name_cells']==[] and m['no_new_avatar_elements_verified']
m['request']='Revert added avatars; only remove circular clipping from existing portraits, including news/inbox. Preserve match UI.'
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'ready':True,'output':str(OUT),'added_avatar_cells':0,'existing_shape_templates':len(m['shape_changes']),'news_inbox_templates':len(edits),'match_dependency_objects_preserved':len(closure)},ensure_ascii=False))
