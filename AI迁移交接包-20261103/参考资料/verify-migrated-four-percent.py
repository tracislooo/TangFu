from pathlib import Path
import sys,re,struct,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
out=next(p for p in sorted(Path.cwd().glob('updated-game-last-skin-migration-*'),reverse=True) if (p/'manifest.json').exists())
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
objs={o.path_id:o for o in UnityPy.load(str(out/W)).objects}
bg=UnityPy.load('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-backgrounds_assets_common.bundle');cab=bg.assets[0].name
textures={o.peek_name():o.path_id for o in bg.objects if o.type.name=='Texture2D' and o.peek_name().startswith('FM27StatusRingCW')}
def threshold(data):
 b=bytes(data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);p=1;args=[]
 for _ in range(b[0]):
  size=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+size]);p+=size
 return struct.unpack_from('<i',args[1],len(args[1])-4)[0]
for pid in [-930000000001001,-930000000001003,-940000000010000,-940000000012000]:
 doc=objs[pid].read_typetree();rr={x['rid']:x for x in doc['references']['RefIds']};sheet=objs[doc['inlineSheet']['m_PathID']].read_typetree()
 def sd(i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 fid=next(i+1 for i,e in enumerate(objs[pid].assets_file.externals) if e.name.lower()==cab.lower())
 def select(i,value):
  a=rr[i]['data']
  if a.get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':return select(a['m_Children'][int(value is not None and value>threshold(sd(i)))]['rid'],value)
  return i
 for metric in ['Condition','Sharpness']:
  root=next(i for i,r in rr.items() if sd(i).get('name')=='OverviewFitness_'+metric+'_Available')
  for raw in range(101):
   leaf=select(root,raw);children=rr[leaf]['data']['m_Children'];ring=next(c['rid'] for c in children if re.search(r'_Ring\d{3}$',sd(c['rid']).get('name','')));number=next(c['rid'] for c in children if re.search(r'_Number\d{3}$',sd(c['rid']).get('name','')))
   assert sd(number)['text']==f'{raw}%'
   prop0=next(p for p in sheet['m_Rules'][rr[ring]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458753)
   assert sheet['assets'][prop0['m_Values'][0]['valueIndex']]=={'m_FileID':fid,'m_PathID':textures[f'FM27StatusRingCW{raw:03}']}
print(json.dumps({'four_versions_percent_cases':808,'passed':True}))
