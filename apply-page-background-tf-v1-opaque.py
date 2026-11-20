"""Put an opaque TF skin V1 background on every existing page shell."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, zlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
from UnityPy.classes import PPtr

location = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(location['bundle_root']), Path(location['skin_packages'])
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BG = 'ui-backgrounds_assets_common.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
oldwrite = TypeTreeHelper.write_value
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
src = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in ['write','Styles']], type_ignores=[]), '<codecs>', 'exec'))
TypeTreeHelper.write_value = write
out = R / ('page-background-tf-v1-opaque-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
out.mkdir()
before = {}; payloads = {}; protected = {}; changes = []; audits = []
for tag, folder in [('game',GAME), ('skin',SKIN)]:
    for p in folder.glob('*.bundle'):
        if p.name not in [G,W]: protected[str(p)] = sha(p.read_bytes())
    catroot = GAME.parent if tag == 'game' else SKIN
    guid_bundles = {}
    for name in ['catalog.bin','catalog.hash']:
        p = catroot / name
        if p.exists(): protected[str(p)] = sha(p.read_bytes())
    background = UnityPy.load(str(folder / BG))
    texture = next(o for o in background.objects if o.path_id == -910000000000149)
    assert texture.peek_name() == 'TF skin V1'
    assert texture.read().image.getextrema()[-1] == (255,255)
    bg_asset = texture.assets_file
    target_count = 0
    for bn in [G,W]:
        path = folder / bn; raw = path.read_bytes(); before[path] = raw
        env = UnityPy.load(raw); oo = {o.path_id:o for o in env.objects}; expected = {}
        af = next(iter(oo.values())).assets_file
        fid = next(i+1 for i,x in enumerate(af.externals) if x.path.lower() == f'archive:/{bg_asset.name}/{bg_asset.name}'.lower())
        ptr = {'m_FileID':fid,'m_PathID':-910000000000149}
        changed_ids = set()
        if bn == W:
            backdrop = next(o for o in oo.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == 'GameWorldBackground')
            d = backdrop.read_typetree(); rr = {r['rid']:r for r in d['references']['RefIds']}
            sheet = oo[d['inlineSheet']['m_PathID']].read_typetree()
            rule = sheet['m_Rules'][rr[1004]['data']['m_RuleIndex']]
            prop = next(p for p in rule['m_Properties'] if p['m_Id'] == 458753)
            h = prop['m_Values'][0]; assert h['m_ValueType'] == 6
            pointer = sheet['assets'][h['valueIndex']]
            assert pointer['m_PathID'] == -910000000000149
            joint = UnityPy.load(raw, (folder / BG).read_bytes())
            af = next(a for a in joint.assets if a.name == backdrop.assets_file.name)
            resolved = PPtr(m_FileID=pointer['m_FileID'], m_PathID=pointer['m_PathID'], assetsfile=af).deref()
            assert resolved.get_raw_data() == texture.get_raw_data()
            assert 'Int|0|(Session,Explicit,{TF27.BackgroundPicker},{selected-image-v3})' in json.dumps(d)
            audits.append({'target':tag,'shared_default_texture':'TF skin V1','path_id':pointer['m_PathID'],
                           'background_pointer_resolved':True,'picker_default':0,'picker_and_backdrop_preserved':True})
        for obj in oo.values():
            if obj.type.name != 'MonoBehaviour': continue
            tree = obj.read_typetree()
            if 'inlineSheet' not in tree: continue
            rr = {r['rid']:r for r in tree['references']['RefIds']}
            targets = []
            for r in rr.values():
                sd = rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
                if sd.get('name') == 'Card-frame': targets.append(r)
            if not targets: continue
            sid = tree['inlineSheet']['m_PathID']; sheet = oo[sid].read_typetree(); original_sheet = copy.deepcopy(sheet)
            st = Styles(sheet)
            for r in targets:
                a = r['data']; sr = rr[a['m_SerializedData']['rid']]; old_sd = copy.deepcopy(sr)
                if a['m_FullTypeName'] == 'SI.Bindable.SIImage':
                    donor = next(z for z in rr.values() if z.get('data',{}).get('m_FullTypeName') == 'UnityEngine.UIElements.VisualElement')
                    new_sd = copy.deepcopy(rr[donor['data']['m_SerializedData']['rid']])
                    for k in new_sd['data']:
                        if k in old_sd['data']: new_sd['data'][k] = copy.deepcopy(old_sd['data'][k])
                    new_sd['rid'] = sr['rid']; new_sd['data']['uxmlAssetId'] = a['m_Id']
                    sr.clear(); sr.update(new_sd); a['m_FullTypeName'] = 'UnityEngine.UIElements.VisualElement'
                assert a['m_FullTypeName'] == 'UnityEngine.UIElements.VisualElement'
                st.edit(r, [st.p(458752,st.h(4,{k:struct.unpack('<f',struct.pack('<f',v))[0] for k,v in zip(['r','g','b','a'],[38/255,52/255,69/255,1.])})), st.p(458753,st.h(6,ptr.copy())), st.p(262153,st.en('scale-and-crop')), st.p(458767,st.num(1))])
                changes.append({'target':str(path),'template':tree['m_Name'],'node':a['m_Id'],'rid':r['rid'],
                                'page_shell_alpha':1,'direct_background':'TF skin V1','element_id_preserved':True})
                assert sr['data']['uxmlAssetId'] == old_sd['data']['uxmlAssetId']
                target_count += 1
            assert sheet['m_Rules'][:len(original_sheet['m_Rules'])] == original_sheet['m_Rules']
            obj.save_typetree(tree); oo[sid].save_typetree(sheet)
            expected[obj.path_id] = tree; expected[sid] = sheet
            changed_ids.update([obj.path_id,sid])
        if expected:
            metaobj = next(o for o in oo.values() if o.type.name=='AssetBundle')
            meta = metaobj.read_typetree(); oldpre = copy.deepcopy(meta['m_PreloadTable'])
            for key,entry in meta['m_Container']:
                span = copy.deepcopy(oldpre[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
                owned = entry['asset']['m_FileID']==0 and entry['asset']['m_PathID'] in changed_ids
                if owned: guid_bundles[key]=bn
                if owned or any(p['m_FileID']==0 and p['m_PathID'] in changed_ids for p in span):
                    if ptr not in span:
                        span.append(ptr.copy());entry['preloadIndex']=len(meta['m_PreloadTable']);entry['preloadSize']=len(span);meta['m_PreloadTable'].extend(span)
            if bg_asset.name.lower() not in meta['m_Dependencies']:meta['m_Dependencies'].append(bg_asset.name.lower())
            metaobj.save_typetree(meta);expected[metaobj.path_id]=meta
            data = env.file.save(packer='lz4'); check = {o.path_id:o for o in UnityPy.load(data).objects}
            original = {o.path_id:o for o in UnityPy.load(raw).objects}
            assert set(check) == set(original)
            for pid, ob in check.items():
                if pid in expected: assert ob.read_typetree() == expected[pid]
                else: assert ob.get_raw_data() == original[pid].get_raw_data(), (bn,pid)
            payloads[path] = data
        else: protected[str(path)] = sha(raw)
    spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
    cp=catroot/'catalog.bin';raw=cp.read_bytes();cat=cm.Catalog(raw)
    locations={q for _,p in cat.keys() for (q,) in cat.array(p,'I')}
    bg_loc=next(q for q in locations if cat.location(q)['provider'].endswith('.AssetBundleProvider') and cat.location(q)['internal'].replace('\\','/').endswith('/'+BG))
    for guid,owner in guid_bundles.items():
        if len(guid)!=32:continue
        locs=cat.locations(guid);assert locs,guid
        for q in locs:
            v=cat.location(q)
            if v['type'][1]!='UnityEngine.UIElements.VisualTreeAsset':continue
            deps=v['dependencies'];assert cat.location(deps[0])['internal'].replace('\\','/').endswith('/'+owner)
            if bg_loc not in deps:
                block=struct.pack('<'+'I'*(len(deps)+1),*(deps+[bg_loc]));ix=cat.append(block,True)
                struct.pack_into('<I',cat.data,q+12,ix);struct.pack_into('<I',cat.data,q+16,zlib.crc32(block))
            assert bg_loc in cat.location(q)['dependencies']
    if bytes(cat.data)!=raw:
        before[cp]=raw;payloads[cp]=bytes(cat.data);hp=cp.with_suffix('.hash');before[hp]=hp.read_bytes();payloads[hp]=hashlib.md5(bytes(cat.data)).hexdigest().encode('ascii')
        protected.pop(str(cp),None);protected.pop(str(hp),None)
    audits[-1]['page_shells'] = target_count
    print(tag, target_count, 'page shells', flush=True)
tx = {'game':str(GAME),'skin':str(SKIN),'workspace':str(R),'sources':{},'before':{}}
for p,data in payloads.items():
    assert p.read_bytes() == before[p]
    tag = 'game' if p.parent in [GAME,GAME.parent] else 'skin'
    dst = out / tag / p.name; bak = out / ('backup-'+tag) / p.name
    dst.parent.mkdir(exist_ok=True); bak.parent.mkdir(exist_ok=True)
    dst.write_bytes(data); bak.write_bytes(before[p])
    tx['sources'][str(p)] = str(dst); tx['before'][str(p)] = str(bak)
m = {'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(before[p]) for p in payloads},
     'after_sha256':{str(p):sha(b) for p,b in payloads.items()},'protected_sha256':protected,'changes':changes,'audits':audits,
     'module_alpha30_preserved':True,'desktop_control_used':False}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install.ps1',''),('restore.ps1','--restore')]:
    (out/name).write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' "+flag+'\n','utf8')
(R/'pending-page-background-tf-v1-opaque.json').write_text(json.dumps({'patch':str(out)},indent=2),'utf8')
print(out)
