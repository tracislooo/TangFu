"""Use the stadium context already resolved by the native panel and log its image key."""
import ast,copy,datetime,hashlib,json,struct,sys,uuid
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
tree=ast.parse((root/'build-club-stadium-overlay-local.py').read_text('utf8'))
head=[]
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pack' for t in n.targets):break
 head.append(n)
exec(compile(ast.Module(head,[]),'helpers','exec'),globals())
out=root/('club-stadium-context-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
tx=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ('stage','bundle'):
  exec(compile(ast.Module([n],[]),'helpers','exec'),globals())
source=UnityPy.load(str(game/'ui-visualfunctions_assets_all.bundle')).assets[0]
record=None
for o in source.objects.values():
 if o.type.name!='MonoBehaviour':continue
 for r in o.read_typetree().get('references',{}).get('RefIds',[]):
  if r['type']['class']=='GeneralVisualFunction_Log_void_string':
   record=copy.deepcopy(r)
   break
 if record:break
assert record
def path_fix(af):
 pid=-991100000000030
 d=af.objects[pid].read_typetree()
 p=next(r['data'] for r in d['references']['RefIds'] if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto')
 v=p['Binding']['m_visualFunction']['m_inputs']['m_variable']
 old=bytes(v['m_argumentBytes'])
 assert b'club.MainTeam.Stadium.UniqueId' in old
 kind=b'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
 path=b'selectedstadium.UniqueId'
 arg=bytes([len(kind)])+kind+bytes([1,len(path)])+path
 v['m_argumentBytes']=list(b'\x01'+struct.pack('<I',len(arg))+arg)
 return {pid:d}
def log_fix(af):
 pid=-991100000000070
 d=af.objects[pid].read_typetree()
 recs=d['references']['RefIds']
 r=copy.deepcopy(record)
 r['rid']=max(x['rid'] for x in recs)+1
 data=r['data']
 data['m_parentID']=d['m_id']
 for k,v in data.items():
  if isinstance(v,dict) and 'm_id' in v:
   v['m_id']={'m_idBytes':list(uuid.uuid5(uuid.NAMESPACE_URL,'tf27/stadium-diagnostics/'+k).bytes_le)}
 suffix=next(x['data'] for x in recs if x['type']['class']=='TextFunctions_Concat' and x['data']['m_dataInText1']['m_defaultSocketValue'].get('m_value')=='/background')
 inputexec=next(v for k,v in data.items() if k.startswith('m_execIn'))
 outputexec=next(v for k,v in data.items() if k.startswith('m_execOut'))
 textinput=next(v for k,v in data.items() if k.startswith('m_dataIn'))
 outputexec['m_destinationID']=suffix['m_execOutExecOutput']['m_destinationID']
 suffix['m_execOutExecOutput']['m_destinationID']=inputexec['m_id']
 textinput['m_sourceID']=suffix['m_dataOutString']['m_id']
 recs.append(r)
 d['m_nodes'].append({'rid':r['rid']})
 import_types(source,af,[r])
 return {pid:d}
for tag,folder in [('game',game),('skin',Path(cfg['skin_packages']))]:
 bundle(tag,folder/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',path_fix)
 bundle(tag,folder/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',log_fix)
for n,d in [('transaction',tx),('manifest',dict(installed=False,runtime_verified=False,protected_sha256={},binding='selectedstadium.UniqueId',diagnostic='logs computed image key before existence check',unrelated_objects_verified=True))]:
 (out/(n+'.json')).write_text(json.dumps(d,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(root/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+"\nexit $LASTEXITCODE\n",'utf-8-sig')
print(out)
