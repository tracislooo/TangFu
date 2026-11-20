from pathlib import Path
import sys,json,struct
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','scoreboard-three-letter-names-').replace('NAMES=[W,G,M,F]','NAMES=[M]')
exec(compile(boot,'backup-installed-scoreboard-bundle-and-load-codecs','exec'))

def decode(raw):
 b=bytes(raw);p=1;args=[]
 for _ in range(b[0]):
  count=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+count]);p+=count
 assert p==len(b)
 return args
def encode(args):return list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))

FUNCTION='aeb3536b8c3b6e64b8690d740a14587c'
CJK_SWITCH='596043a56cb28154d905f709e29ca7c7'
changed_templates=[];changed_labels=[];already_three=[]
for obj in list(objs[M].values()):
 if obj.type.name!='MonoBehaviour' or not obj.peek_name().startswith('Scoreboard'):continue
 d=obj.read_typetree();old=copy.deepcopy(d);r=refs(d);changed=set()
 for i,record in r.items():
  data=record.get('data',{});binding=data.get('TextBinding',{});vf=binding.get('m_visualFunction',{});raw=vf.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
  if not raw or b'[%team#1-3letter]' not in bytes(raw):continue
  args=decode(raw)
  if vf['m_target']['m_guid']==CJK_SWITCH:
   assert len(args)==4 and b'[%team#1-3letter]' in args[0] and b'[%club#1-6letter]' in args[2]
   vf['m_target']['m_guid']=FUNCTION;vf['m_inputs']['m_variable']['m_argumentBytes']=encode(args[:2]);changed.add(i)
   changed_labels.append({'template':d['m_Name'],'path_id':obj.path_id,'record':i,'name':data.get('name',''),'team_argument':list(args[1])})
  else:
   assert vf['m_target']['m_guid'] in [FUNCTION,'f97abdf5a74842647ba921d183f4a3eb']
   already_three.append({'template':d['m_Name'],'path_id':obj.path_id,'record':i})
 if changed:
  oldr=refs(old)
  assert set(r)==set(oldr)
  for i in r:
   if i not in changed:assert r[i]==oldr[i],('unrelated record changed',obj.path_id,i)
   else:
    prior=oldr[i]['data']['TextBinding']['m_visualFunction'];after=r[i]['data']['TextBinding']['m_visualFunction'];assert decode(after['m_inputs']['m_variable']['m_argumentBytes'])==decode(prior['m_inputs']['m_variable']['m_argumentBytes'])[:2]
    expected=copy.deepcopy(oldr[i]);expected['data']['TextBinding']['m_visualFunction']=after;assert expected==r[i]
  sheet=objs[M][d['inlineSheet']['m_PathID']].read_typetree();validate_ui(d,sheet)
  obj.save_typetree(d);changes[M][obj.path_id]=copy.deepcopy(d)
  (OUT/'templates'/(d['m_Name']+'-'+str(obj.path_id)+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  changed_templates.append({'template':d['m_Name'],'path_id':obj.path_id,'labels':len(changed)})
assert changed_labels and already_three
output=env[M].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[M])
for pid,h in hashes[M].items():
 if pid not in changes[M]:assert sha(check[pid].get_raw_data())==h,('unrelated asset modified',pid)
for pid,expected in changes[M].items():assert check[pid].read_typetree()==expected,('roundtrip mismatch',pid)
for obj in check.values():
 if obj.type.name!='MonoBehaviour' or not obj.peek_name().startswith('Scoreboard'):continue
 for r in obj.read_typetree().get('references',{}).get('RefIds',[]):
  raw=r.get('data',{}).get('TextBinding',{}).get('m_visualFunction',{}).get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[])
  assert b'[%club#1-6letter]' not in bytes(raw),('long club-name branch remains',obj.path_id)
(OUT/M).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'format':'[%team#1-3letter]','changed_templates':changed_templates,'changed_label_count':len(changed_labels),'already_three_letter_label_count':len(already_three),'changes':{M:{str(pid):d['m_Name'] for pid,d in changes[M].items()}},'position_dimensions_styles_and_score_time_bindings_unchanged':True,'other_match_ui_including_goal_popup_unchanged':True,'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{M:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[],'unrelated_objects_unchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps({'passed':True,'changed_templates':changed_templates,'changed_labels':len(changed_labels),'already_three_letters':len(already_three),'native_team_arguments_preserved':True,'six_letter_club_branches_remaining':0,'all_other_records_and_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[M],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'changed_templates':len(changed_templates),'changed_labels':len(changed_labels),'already_three_letter_labels':len(already_three)},ensure_ascii=False))
