from pathlib import Path
import sys,json,struct,re
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','scoreboard-native-abbreviation-fix-').replace('NAMES=[W,G,M,F]','NAMES=[M]')
exec(compile(boot,'backup-current-scoreboards-and-load-codecs','exec'))

def decode(raw):
 b=bytes(raw);p=1;args=[]
 for _ in range(b[0]):l=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+l]);p+=l
 assert p==len(b);return args
def encode(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))

original_bundle=R/'scoreboard-three-letter-names-20261023-235308'/'backup-game'/M
oldenv=UnityPy.load(str(original_bundle));original_objects={o.path_id:o for o in oldenv.objects}
fallback_guid='9c4b0d2ce94a68d4ab1567ed4b900d75'
vfenv=UnityPy.load(str(GAME/'ui-visualfunctions_assets_all.bundle'));vfo={o.path_id:o for o in vfenv.objects};vmeta=next(o for o in vfo.values() if o.type.name=='AssetBundle').read_typetree();vpid=next(e['asset']['m_PathID'] for k,e in vmeta['m_Container'] if k==fallback_guid);vf=vfo[vpid].read_typetree()
assert vf['m_Name']=='BindStringIsEmptyToAOrBTranslationBinding'
assert [x['m_name'] for x in vf['m_inputs']]==['BindingBag','Target','Source','Fallback']

# Use a native BindingPath argument's exact wire format, not translation-tag arguments.
template=None
for o in objs[M].values():
 if o.type.name!='MonoBehaviour' or not o.peek_name().startswith('Scoreboard'):continue
 for rr in o.read_typetree().get('references',{}).get('RefIds',[]):
  bv=rr.get('data',{}).get('TextBinding',{}).get('m_visualFunction',{})
  if bv.get('m_target',{}).get('m_guid')=='c0b4248e39d6df84d978dd6f8a209dcf':template=decode(bv['m_inputs']['m_variable']['m_argumentBytes'])[0];break
 if template is not None:break
oldpath=b'match.MatchCurrentTimeSlice';assert template.endswith(bytes([len(oldpath)])+oldpath)
def path_argument(path):
 data=path.encode('utf8');assert len(data)<128;return template[:-len(oldpath)-1]+bytes([len(data)])+data

audit=[];templates=[]
for pid,obj in objs[M].items():
 if obj.type.name!='MonoBehaviour' or not obj.peek_name().startswith('Scoreboard'):continue
 native=original_objects[pid].read_typetree();nr=refs(native);doc=obj.read_typetree();rr=refs(doc);old=copy.deepcopy(rr);edited=set()
 for rid,nref in nr.items():
  native_binding=nref.get('data',{}).get('TextBinding',{}).get('m_visualFunction',{})
  if native_binding.get('m_target',{}).get('m_guid')!='596043a56cb28154d905f709e29ca7c7':continue
  args=decode(native_binding['m_inputs']['m_variable']['m_argumentBytes'])
  if b'[%team#1-3letter]' not in args[0]:continue
  clubs=re.findall(rb'(?:match\.)?(?:home|away)?team\.club',args[3],flags=re.I);assert len(clubs)==1
  club=clubs[0].decode('utf8');team=club.rsplit('.',1)[0];source=club+'.ThreeLetterName';fallback=team+'.Name'
  bd=rr[rid]['data']['TextBinding'];assert bd['m_visualFunction']['m_target']['m_guid']=='aeb3536b8c3b6e64b8690d740a14587c'
  bd['m_visualFunction']['m_target']['m_guid']=fallback_guid;bd['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode([path_argument(source),path_argument(fallback)])
  assert decode(bd['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])==[path_argument(source),path_argument(fallback)]
  edited.add(rid);audit.append({'template':doc['m_Name'],'path_id':pid,'text_record':rid,'source':source,'fallback':fallback,'colors_changed':False})
 if not edited:continue
 for i in old:
  if i not in edited:assert rr[i]==old[i],('unrelated record modified',pid,i)
  else:
   expected=copy.deepcopy(old[i]);expected['data']['TextBinding']=rr[i]['data']['TextBinding'];assert expected==rr[i]
 validate_ui(doc,objs[M][doc['inlineSheet']['m_PathID']].read_typetree());obj.save_typetree(doc);changes[M][pid]=copy.deepcopy(doc);templates.append(pid)
 (OUT/'templates'/(doc['m_Name']+'-'+str(pid)+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
assert len(audit)==20 and len(templates)==9
output=env[M].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[M])
for pid,h in hashes[M].items():
 if pid not in changes[M]:assert sha(check[pid].get_raw_data())==h,('unrelated object modified',pid)
for pid,data in changes[M].items():assert check[pid].read_typetree()==data,('roundtrip mismatch',pid)
(OUT/M).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'passed':True,'native_field_evidence':['ClubCellThreeLetterName: club.ThreeLetterName','RecruitmentPlayerHeader: club.ThreeLetterName'],'native_function':vf['m_Name'],'changed_label_count':len(audit),'changed_template_count':len(templates),'colors_and_styles_unchanged':True,'unrelated_records_and_objects_unchanged':True,'serialization_roundtrip':True,'native_empty_string_fallback_retained':True,'runtime_verified':False}
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'diagnosis':'Previous patch forced an optional team translation format and removed the original empty-string fallback. Installed bundle hashes matched that patch. Native club.ThreeLetterName is used elsewhere in the game.','bindings':audit,'changes':{M:{str(pid):v['m_Name'] for pid,v in changes[M].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{M:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[],'unrelated_objects_unchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[M],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'native_field':'Club.ThreeLetterName','native_fallback':True,'changed_labels':len(audit),'colors_changed':False},ensure_ascii=False))
