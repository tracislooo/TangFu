"""Install approved calibrated pitch and card layers without changing coordinates."""
from pathlib import Path
import shutil

source=Path(__file__).with_name('trial-tactics-combined-layered-card.py').read_text('utf8')
boot=source.split('# Keep the pitch anchor / footprint')[0]
boot=boot.replace("OUT = R / ('tactics-combined-layered-card-trial-' + stamp)\nOUT.mkdir()", "OUT = Path(sys.argv[1]); assert OUT.exists()")
exec(compile(boot,'pitch-background-boot','exec'))
from PIL import Image,ImageChops,ImageStat
from UnityPy.export.Texture2DConverter import image_to_texture2d
from UnityPy.classes import PPtr
BN='ui-backgrounds_assets_common.bundle';GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
ALIGNED=-910000000000148;CARD=-910000000000147;ORIGINAL=-910000000000146
assert not (OUT/'manifest.json').exists(), 'Use a new preparation directory for another installation.'
registry_path=R/'current-custom-textures.json';registry_raw=registry_path.read_bytes();registry=json.loads(registry_raw)
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];banned={int(x['path_id']) for x in reserved}
assert registry['active_custom_texture_count']==len(registry['textures'])==178
before.update({f/BN:(f/BN).read_bytes() for f in [GAME,SKIN]})
assert before[GAME/BN]==before[SKIN/BN]
for folder in [GAME.parent,SKIN]:
    for n in ['catalog.bin','catalog.hash']:
        p=folder/n
        if p.exists():before[p]=p.read_bytes();protected.pop(p,None)
for f in [GAME,SKIN]:protected.pop(f/BN,None)
before[registry_path]=registry_raw
for path,raw in before.items():
    tag='backup-registry' if path==registry_path else ('backup-game' if path.parent in [GAME,GAME.parent] else 'backup-skin')
    (OUT/tag).mkdir(exist_ok=True);(OUT/tag/path.name).write_bytes(raw)

be=UnityPy.load(before[GAME/BN]);ba=be.assets[0];bo=ba.objects
bh={i:sha(o.get_raw_data()) for i,o in bo.items()}
assert ALIGNED not in bo and ALIGNED not in objs and ALIGNED not in banned
assert bo[ORIGINAL].peek_name()=='TF patch' and bo[CARD].peek_name()=='patchplayerbg'
assert sha(before[GAME/BN])==registry['source_bundle_sha256']
for row in registry['textures']:assert bo[int(row['path_id'])].peek_name()==row['name']
bmobj=next(o for o in bo.values() if o.type.name=='AssetBundle');bm=bmobj.read_typetree();oldbm=copy.deepcopy(bm)
template=bo[-910000000000005];texture=copy.copy(template);texture.path_id=ALIGNED;texture.data=None;texture._read_until=None;texture.set_raw_data(template.get_raw_data());bo[ALIGNED]=texture
im=Image.open(OUT/'TF patch aligned.png').convert('RGBA');td=copy.deepcopy(template.read_typetree())
pixels,fmt=image_to_texture2d(im,12,texture.platform,td['m_PlatformBlob']);assert int(fmt)==12
td.update(m_Name='TF patch aligned',m_Width=im.width,m_Height=im.height,m_CompleteImageSize=len(pixels));td['image data']=pixels;td['m_StreamData']={'offset':0,'size':0,'path':''};assert td['m_MipCount']==1
texture.save_typetree(td);ptr={'m_FileID':0,'m_PathID':ALIGNED}
assert 'tf patch aligned' not in dict(bm['m_Container'])
bm['m_Container'].append(('tf patch aligned',{'preloadIndex':len(bm['m_PreloadTable']),'preloadSize':1,'asset':ptr}));bm['m_PreloadTable'].append(copy.deepcopy(ptr));bm['m_Container'].sort(key=lambda x:x[0]);bmobj.save_typetree(bm)
bgout=be.file.save(packer='lz4');bcheck=UnityPy.load(bgout);bco=bcheck.assets[0].objects
assert bcheck.assets[0].name==ba.name and set(bco)==set(bh)|{ALIGNED}
for i,h in bh.items():
    if i!=bmobj.path_id:assert sha(bco[i].get_raw_data())==h,('Original background object changed',i)
assert bm['m_PreloadTable'][:len(oldbm['m_PreloadTable'])]==oldbm['m_PreloadTable']
decoded=bco[ALIGNED].read().image.convert('RGBA');assert decoded.size==im.size and decoded.getchannel('A').getextrema()==(255,255)
rms=ImageStat.Stat(ImageChops.difference(decoded,im)).rms;assert max(rms)<25
decoded.save(OUT/'TF patch aligned-包内解码.png')
bg_file=next(i+1 for i,x in enumerate(objs[CP if 'CP' in globals() else 3127595210179668386].assets_file.externals) if x.path==f'archive:/{ba.name}/{ba.name}')

def named(r,name):return next(i for i,a in r.items() if r.get(a.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==name)
def save_tree(pid):
    for dim in t.s['dimensions']:dim['value']=f32(dim['value'])
    validate_ui(t.d,t.s)
    for i,data in [(pid,t.d),(t.d['inlineSheet']['m_PathID'],t.s)]:objs[i].save_typetree(data);expected[i]=copy.deepcopy(data)
def pv(i,key):
    rule=t.s['m_Rules'][t.r[i]['data']['m_RuleIndex']];v=next(p for p in rule['m_Properties'] if p['m_Id']==key)['m_Values'][0];return t.s[poolmap[v['m_ValueType']]][v['valueIndex']]

expected={};card_audits=[];pitch_audits=[];resource_requirements={}
for pid in [-8273082868742719783,3127595210179668386]:
    d=objs[pid].read_typetree();t=Tree(d,objs[d['inlineSheet']['m_PathID']].read_typetree());st=t.st;P=st.p;old=copy.deepcopy(t.r)
    frame=named(t.r,'TacticsPlayerPortraitFrame');surface=named(t.r,'DetailedCardInnerSurface' if pid<0 else 'CombinedCardInnerSurface');portrait=named(t.r,'TacticsPlayerPortraitBinding')
    assert pv(frame,131105)['value']==pv(frame,131087)['value']==75
    image=t.add(t.r,surface,frame,'TacticsPlayerCardBackgroundImage',t.s);ignore(image);t.r[image]['data']['m_Classes']=[]
    box(image,4,4,67,67);rounded(image,2,True)
    t.edit(image,[P(458753,st.h(6,{'m_FileID':bg_file,'m_PathID':CARD})),P(262153,st.en('stretch-to-fill')),P(458752,st.h(4,{'r':0.0,'g':0.0,'b':0.0,'a':0.0})),P(458767,st.num(1))])
    children=t.r[frame]['data']['m_Children'];children.remove({'rid':image});children.insert(children.index({'rid':portrait}),{'rid':image})
    assert children.index({'rid':surface})<children.index({'rid':image})<children.index({'rid':portrait})
    for i,a in old.items():
        if 'UxmlSerializedData' in a.get('type',{}).get('class',''):assert t.r[i]==a,('Native binding changed',pid,i)
    assert pv(image,131105)['value']==pv(image,131087)['value']==67
    assert pv(image,458753)=={'m_FileID':bg_file,'m_PathID':CARD} and t.sd(image)['pickingMode']==1
    save_tree(pid);resource_requirements[pid]=[CARD]
    card_audits.append({'name':d['m_Name'],'layer_rid':image,'size':[67,67],'inset':4,'picking_ignored':True,'order':'native position colour -> surface -> patchplayerbg -> portrait -> native controls'})

# Background on the native pitch renderer itself, not on its enclosing panel:
# the UI background paint precedes the native line mesh and all child cards.
for pid in [-4411574370150944845,3412805035020634299]:
    d=objs[pid].read_typetree();t=Tree(d,objs[d['inlineSheet']['m_PathID']].read_typetree());st=t.st;P=st.p;old=copy.deepcopy(t.r);hits=[]
    for i,a in list(t.r.items()):
        typ=a.get('data',{}).get('m_FullTypeName','')
        if not any(x in typ for x in ['FMTacticsPanel','FMTacticsWithAnalysis','FMTacticsWithPhases']):continue
        s=t.sd(i);assert s['FillAllAvailableSpace']==1 and s['UsePerspectiveDrawing']==0
        t.edit(i,[P(458753,st.h(6,{'m_FileID':bg_file,'m_PathID':ALIGNED})),P(262153,st.en('stretch-to-fill')),P(458752,st.h(4,{'r':0.0,'g':0.0,'b':0.0,'a':0.0}))])
        assert pv(i,458753)=={'m_FileID':bg_file,'m_PathID':ALIGNED}
        hits.append({'rid':i,'type':typ,'name':s.get('name',''),'original_geometry_and_bindings_unchanged':True})
    assert len(hits)==(5 if pid<0 else 1)
    for i,a in old.items():
        if 'UxmlSerializedData' in a.get('type',{}).get('class',''):assert t.r[i]==a,('Native pitch data changed',pid,i)
    save_tree(pid);resource_requirements[pid]=[ALIGNED];pitch_audits.append({'name':d['m_Name'],'renderers':hits})

wmobj=next(o for o in objs.values() if o.type.name=='AssetBundle');wm=wmobj.read_typetree();oldwm=copy.deepcopy(wm)
changed_guids=set()
for pid,textureids in resource_requirements.items():
    sid=expected[pid]['inlineSheet']['m_PathID']
    for key,entry in wm['m_Container']:
        if entry['asset']['m_FileID']!=0 or entry['asset']['m_PathID'] not in [pid,sid]:continue
        changed_guids.add(key);span=copy.deepcopy(wm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
        for textureid in textureids:
            p={'m_FileID':bg_file,'m_PathID':textureid}
            if p not in span:span.append(p)
        entry.update(preloadIndex=len(wm['m_PreloadTable']),preloadSize=len(span));wm['m_PreloadTable'].extend(span)
wmobj.save_typetree(wm);expected[wmobj.path_id]=copy.deepcopy(wm)
worldout=env.file.save(packer='lz4');wo={o.path_id:o for o in UnityPy.load(worldout).objects};assert set(wo)==set(hashes)
for i,h in hashes.items():
    if i not in expected:assert sha(wo[i].get_raw_data())==h,('Unrelated UI object changed',i)
for i,data in expected.items():assert wo[i].read_typetree()==data,('Roundtrip differs',i)
for meta,ids in [(bm,bco),(wm,wo)]:
    assert banned.isdisjoint(ids)
    assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
    assert all(v['asset']['m_PathID'] not in banned for _,v in meta['m_Container'])

# Resolve the new cross-bundle texture PPtrs against the actual finished bundle.
combined=UnityPy.load(worldout,bgout);world_asset=next(a for a in combined.assets if a.name!=ba.name)
for textureid in [ALIGNED,CARD,ORIGINAL]:
    target=PPtr(m_FileID=bg_file,m_PathID=textureid,assetsfile=world_asset).deref()
    assert sha(target.get_raw_data())==sha(bco[textureid].get_raw_data())
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};catalog_audits=[]
for folder in [GAME.parent,SKIN]:
    catpath=folder/'catalog.bin';oldcat=cm.Catalog(before[catpath]);cat=cm.Catalog(before[catpath]);oldlocs={loc for _,ptr in oldcat.keys() for (loc,) in oldcat.array(ptr,'I')}
    bg_loc=next(loc for loc in oldlocs if cat.location(loc)['provider'].endswith('.AssetBundleProvider') and cat.location(loc)['internal'].endswith('\\'+BN))
    modified=[]
    for guid in changed_guids:
        for loc in cat.locations(guid):
            x=cat.location(loc);assert x['dependencies'] and cat.location(x['dependencies'][0])['internal'].endswith('\\'+W)
            if bg_loc in x['dependencies']:continue
            row=list(cat.unpack(loc,'7I'));row[3]=cat.append(b''.join(struct.pack('<I',i) for i in x['dependencies']+[bg_loc]),True);struct.pack_into('<7I',cat.data,loc,*row);modified.append(loc)
    out=bytes(cat.data);newcat=cm.Catalog(out);assert newcat.keys()==oldcat.keys()
    for loc in oldlocs:
        if loc not in modified:assert newcat.unpack(loc,'7I')==oldcat.unpack(loc,'7I')
    for guid in changed_guids:
        for loc in newcat.locations(guid):assert bg_loc in newcat.location(loc)['dependencies']
    outputs[catpath]=out;outputs[folder/'catalog.hash']=hashlib.md5(out).hexdigest().encode('ascii')
    catalog_audits.append({'target':str(catpath),'changed_dependency_locations':modified,'asset_keys_and_other_locations_preserved':True})

for folder in [GAME,SKIN]:outputs[folder/W]=worldout;outputs[folder/BN]=bgout
current=copy.deepcopy(registry);row={'name':'TF patch aligned','path_id':str(ALIGNED),'texture_format_id':12,'size':list(im.size),'texture_sha256':sha(bco[ALIGNED].get_raw_data()),'decoded_alpha_range':[255,255]}
current['textures'].append(row);current.update(version=64,date='2026-10-28',authoritative_source_bundle=str(OUT/BN),source_bundle_sha256=sha(bgout),manifest=str(OUT/'manifest.json'),active_custom_texture_count=179)
assert len(current['textures'])==179
outputs[registry_path]=json.dumps(current,ensure_ascii=False,indent=2).encode('utf8')
(OUT/W).write_bytes(worldout);(OUT/BN).write_bytes(bgout);(OUT/'current-custom-textures.json').write_bytes(outputs[registry_path]);(OUT/'reserved-texture-ids.json').write_bytes((R/'reserved-texture-ids.json').read_bytes())
for p,raw in outputs.items():
    if p.name in [W,BN,'current-custom-textures.json']:continue
    tag='output-game' if p.parent==GAME.parent else 'output-skin';(OUT/tag).mkdir(exist_ok=True);(OUT/tag/p.name).write_bytes(raw)
report={'version':64,'installed':False,'runtime_verified':False,'textures':[row],'active_custom_texture_count':179,'original_178_textures_and_native_background_objects_unchanged':True,'retired_70_ids_absent':True,'card_layers':card_audits,'native_pitch_renderers':pitch_audits,'photo_lines_removed_native_lines_preserved':True,'alignment_parameters':'alignment.json','new_bundle_objects':1,'changed_world_objects':[str(i) for i in expected],'all_original_ui_bindings_and_coordinates_unchanged':True,'catalog_audits':catalog_audits,'new_texture_rgba_rms':rms,'new_texture_pptrs_resolved':True,'protected_files':{str(p):h for p,h in protected.items()},'after_sha256':{str(p):sha(b) for p,b in outputs.items()}}
def record():(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
record()
guard=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
restore=list(guard);installer=list(guard)
for p,raw in before.items():
    tag='backup-registry' if p==registry_path else ('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(raw)+"') { throw 'File changed since preparation.' }")
for p in outputs:
    src=OUT/p.name if p.name in [W,BN,'current-custom-textures.json'] else OUT/('output-game' if p.parent==GAME.parent else 'output-skin')/p.name
    installer.append("Copy-Item -LiteralPath '"+str(src)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,raw in before.items():assert p.read_bytes()==raw
for p,h in protected.items():assert sha(p.read_bytes())==h
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if running.stdout.strip():print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,raw in outputs.items():p.write_bytes(raw)
    for p,raw in outputs.items():assert p.read_bytes()==raw
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,raw in before.items():p.write_bytes(raw)
    raise
report.update(installed=True,installed_verified=True);record()
print(json.dumps({'installed':True,'output':str(OUT),'pitch_renderers':6,'card_layers':2,'active_custom_textures':179,'native_coordinates_unchanged':True}))
