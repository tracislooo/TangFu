"""Compose disjoint current player/sidebar object deltas into four switchable packs."""
from pathlib import Path
import ast, datetime, hashlib, importlib.util, json, struct, sys, zipfile, zlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
read=lambda p:json.loads(p.read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
cfg=read(R/'current-game-location.json');GAME=Path(cfg['bundle_root']);AA=GAME.parent
editions=Path(sys.argv[1]).resolve();side=Path(sys.argv[2]).resolve();main=Path(sys.argv[3]).resolve()
em=read(editions/'manifest.json');sm=read(side/'manifest.json');base_report=read(main/'文件校验.json')
assert em['sources_unchanged_verified'] and not sm['installed']
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
D='ui-styles_assets_default.bundle';M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
BUNDLES=[W,L,D,M,'ui-tableviews_assets_all.bundle','ui-tablefactories_assets_all.bundle']
fixspec=importlib.util.spec_from_file_location('export_fixes',R/'verify-player-export-latest-fixes.py')
fixes=importlib.util.module_from_spec(fixspec);fixspec.loader.exec_module(fixes)
latest_fixes=fixes.verify(GAME)
before={bn:(GAME/bn).read_bytes() for bn in BUNDLES};cat_before=(AA/'catalog.bin').read_bytes()
for bn,h in em['source_sha256'].items():assert sha(before[bn])==h
assert sha(cat_before)==em['catalog_source_sha256']
for row in base_report['files']:
    assert sha((AA/Path(row['path']).relative_to('aa')).read_bytes())==row['sha256'],('Main snapshot drift',row['path'])
tx=read(side/'transaction.json')
for row in tx:assert sha(Path(row['target']).read_bytes())==row['before'],('Sidebar base drift',row['target'])
base_objects={bn:{o.path_id:o for o in UnityPy.load(raw).objects} for bn,raw in before.items()}
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT=R/'exports'/('FM27-FC大头像与导航-四套替换文件-'+stamp);OUT.mkdir(parents=True)
side_raw={bn:(side/'packages'/bn).read_bytes() if (side/'packages'/bn).exists() else before[bn] for bn in BUNDLES}
side_catalog=(side/'packages/catalog.bin').read_bytes()
sid=cm.Catalog(side_catalog)
for key in ['2f7f33f147615f32bb80061b0ecda1bf','2384a857dfa15051ac87a35445fa03ab']:
    assert len(sid.locations(key))==1 and sid.locations(key)[0] in sid.locations('GameWorldVisualTreeAssetPreload')

def crc(raw):
    rd=EndianBinaryReader(raw);bu=object.__new__(BundleFile)
    bu.signature=rd.read_string_to_null();bu.version=rd.read_u_int();bu.version_player=rd.read_string_to_null();bu.version_engine=rd.read_string_to_null()
    _,block=bu.read_fs(rd);return zlib.crc32(block.bytes)

def pair_catalog(raw,bundles):
    cat=cm.Catalog(raw);locations={i:cat.location(i) for _,ls in cat.keys() for i, in cat.array(ls,'I')};found=set();rows=[]
    for bn,payload in bundles.items():
        checksum=crc(payload)
        for i,v in locations.items():
            if not v['type'][1].endswith('IAssetBundleResource') or v['internal'].replace('\\','/').rsplit('/',1)[-1]!=bn:continue
            typ,p=cat.unpack(v['raw'][5],'2I');request=list(cat.unpack(p,'5I'));request[2:4]=[checksum,len(payload)]
            record=list(v['raw']);record[5]=cat.append(struct.pack('<2I',typ,cat.append(struct.pack('<5I',*request))))
            struct.pack_into('<7I',cat.data,i,*record);found.add(bn)
        rows.append(dict(bundle=bn,crc=checksum,size=len(payload)))
    assert found==set(bundles)
    checked=cm.Catalog(bytes(cat.data))
    for i,v in locations.items():
        if not v['type'][1].endswith('IAssetBundleResource'):continue
        name=v['internal'].replace('\\','/').rsplit('/',1)[-1]
        if name in bundles:
            _,p=checked.unpack(checked.location(i)['raw'][5],'2I');assert checked.unpack(p,'5I')[2:4]==(crc(bundles[name]),len(bundles[name]))
    return bytes(cat.data),rows

reports=[];all_files={}
for mode,label in [('fc','FC卡面'),('portrait','大头像')]:
    er=next(r for r in em['reports'] if r['edition']==mode)
    ep=editions/('FC卡面版' if mode=='fc' else '大头像版')/'aa/StandaloneWindows64'
    edition_raw={bn:(ep/bn).read_bytes() for bn in [W,L]}
    for bn,raw in edition_raw.items():assert sha(raw)==er['sha256']['aa/StandaloneWindows64/'+bn]
    for nav,nlabel in [('top','顶部导航'),('sidebar','侧边栏')]:
        title=label+'＋'+nlabel;print('Preparing '+mode+' '+nav,flush=True)
        payloads=dict(before) if nav=='top' else dict(side_raw);audits=[]
        for bn in [W,L]:
            eb={o.path_id:o for o in UnityPy.load(edition_raw[bn]).objects}
            player_changes={i for i,o in eb.items() if o.get_raw_data()!=base_objects[bn][i].get_raw_data()}
            assert player_changes==set(er['changed_objects'][bn])
            if nav=='top':payloads[bn]=edition_raw[bn];continue
            env=UnityPy.load(payloads[bn]);sb={o.path_id:o for o in env.objects}
            sidebar_changes={i for i,o in sb.items() if i not in base_objects[bn] or o.get_raw_data()!=base_objects[bn][i].get_raw_data()}
            assert player_changes.isdisjoint(sidebar_changes),('Overlapping deltas',bn,player_changes&sidebar_changes)
            old={i:o.get_raw_data() for i,o in sb.items()}
            for i in player_changes:
                assert [e.name for e in sb[i].assets_file.externals][:len(eb[i].assets_file.externals)]==[e.name for e in eb[i].assets_file.externals]
                sb[i].set_raw_data(eb[i].get_raw_data())
            raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects}
            assert set(check)==set(sb)
            for i,o in check.items():assert o.get_raw_data()==(eb[i].get_raw_data() if i in player_changes else old[i]),(title,bn,i)
            payloads[bn]=raw;audits.append(dict(bundle=bn,player_changed_objects=sorted(player_changes),sidebar_changed_objects=sorted(sidebar_changes),disjoint=True,all_other_objects_identical=True))
        # Check selectors, defaults, hover edition, sidebar registration and sidebar background.
        lo={o.path_id:o for o in UnityPy.load(payloads[L]).objects};wo={o.path_id:o for o in UnityPy.load(payloads[W]).objects}
        ts=lo[1332213496068314481].read_typetree();choices=[]
        for p in ts['m_gridElementDescriptions']:
            if p['m_FileID']:continue
            d=lo[p['m_PathID']].read_typetree()
            if d.get('<ID>k__BackingField','').startswith('PlayerOverview'):
                isfc='FC' in d['m_directTitlePath']['m_path'];assert isfc==(mode=='fc');choices.append(d['<ID>k__BackingField'])
        assert len(choices)==(3 if mode=='fc' else 6)
        comp=lo[3901662990989568885].read_typetree();slot=next(x for x in comp['m_gridComponents'] if x['m_elementID']=='PlayerAttributesBlock')
        assert slot['m_configDescriptions'][0]['m_PathID']==(-950000000000232 if mode=='fc' else -950000000000231)
        side_objects=[o for o in wo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='TFReferenceBookmarkSidebar']
        assert len(side_objects)==(1 if nav=='sidebar' else 0)
        for pid in [-960000000003010,-950000000000141]:
            ed={o.path_id:o for o in UnityPy.load(edition_raw[W]).objects}
            assert wo[pid].get_raw_data()==ed[pid].get_raw_data()
        if nav=='sidebar':
            styles={o.path_id:o for o in UnityPy.load(payloads[D]).objects}
            sheet=next(o.read_typetree() for o in styles.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
            rule=next(rule for rule in sheet['m_Rules'] if any([p['m_Value'] for s in sel['m_Selectors'] for p in s['m_Parts']]==['tf-reference-sidebar-active','TFReferenceSidebar'] for sel in rule['m_ComplexSelectors']))
            prop=next(p for p in rule['m_Properties'] if p['m_Id']==458752)
            assert abs(sheet['colors'][prop['m_Values'][0]['valueIndex']]['a']-.7)<.00001
        cb,metadata=pair_catalog(cat_before if nav=='top' else side_catalog,payloads)
        catalog=cm.Catalog(cb);keys=dict(catalog.keys())
        assert ('2384a857dfa15051ac87a35445fa03ab' in keys)==(nav=='sidebar')
        if nav=='sidebar':
            for key in ['2f7f33f147615f32bb80061b0ecda1bf','2384a857dfa15051ac87a35445fa03ab']:
                loc,=catalog.locations(key);assert loc in catalog.locations('GameWorldVisualTreeAssetPreload')
                assert catalog.location(catalog.location(loc)['dependencies'][0])['internal'].endswith(W)
        files={'aa/StandaloneWindows64/'+bn:raw for bn,raw in payloads.items()}
        files['aa/catalog.bin']=cb;files['aa/catalog.hash']=hashlib.md5(cb).hexdigest().encode('ascii')
        dest=OUT/title;dest.mkdir();rows=[]
        for relative,raw in files.items():
            p=dest/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            rows.append(dict(path=relative,size=len(raw),sha256=sha(raw)))
        regression=fixes.verify(dest/'aa/StandaloneWindows64')
        assert regression==latest_fixes
        report=dict(edition=mode,navigation=nav,export_only=True,installed=False,runtime_verified=False,base_main=str(main),choices=choices,files=rows,sidebar_background_alpha=.7 if nav=='sidebar' else None,merge_audits=audits,bundle_request_options=metadata,latest_fixes_verified=regression)
        (dest/'文件校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
        (dest/'使用说明.txt').write_text(title+'\n配合本次最新主皮肤使用，8个文件为同一套组合成品。\n安装程序应根据FC/大头像及顶部/侧边栏两个选项，选取一整套aa覆盖，不再依次叠加旧头像包或旧侧边栏包。四套文件集合相同，可以从任何组合切换到任意另一组合；必须覆盖整套8文件，包括catalog.bin和catalog.hash。\n顶部导航套装包含恢复顶部导航所需的样式和比赛包，以清除此前侧边栏布局及比赛补偿。侧边栏沿用19固定入口、400px书签区域和70%深灰蓝背景。球员选择器FC仅3页、大头像仅6页，悬浮层与所选版本对应。\n已逐套核验昵称按钮及原生动作、192px消息头像、tangfu A默认列表和六套战术列表的90px体能/比赛状态及40px疲劳列；表格视图和工厂包一并提供。\n完全退出游戏后再覆盖。适用主皮肤及文件哈希见文件校验.json与安装包映射.json；游戏或主皮肤更新后须重新迁移。字体/图片等共用资源由主皮肤提供。\n本次仅导出，未安装或操作游戏。对象回读、合并互不覆盖、目录登记/预加载、CRC/大小及ZIP校验通过；游戏内显示和交互尚未验证。若旧球员布局仍被保留，请在游戏内重置该概览布局。\n','utf-8-sig')
        zp=OUT/(title+'.zip')
        with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in dest.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(dest))
        with zipfile.ZipFile(zp) as z:
            assert z.testzip() is None
            for relative,raw in files.items():assert z.read(relative)==raw
        report['zip']=str(zp);report['zip_sha256']=sha(zp.read_bytes());reports.append(report);all_files[mode+'_'+nav]={k:sha(v) for k,v in files.items()}
        print('Verified '+mode+' '+nav,flush=True)

sets=[set(v) for v in all_files.values()];assert all(s==sets[0] for s in sets)
# Simulate all twelve directional switches: the whole six-file group is replaced.
for source in all_files.values():
    for target in all_files.values():
        installed=dict(source);installed.update(target);assert installed==target
mapping=dict(base_main=str(main),base_main_files=base_report['files'],replace_entire_group=True,files_per_choice=8,latest_fixes_verified=latest_fixes,choices=[dict(player=r['edition'],navigation=r['navigation'],zip=Path(r['zip']).name,sha256=r['zip_sha256'],files=r['files']) for r in reports],all_direction_switches_verified=True)
(OUT/'安装包映射.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),'utf8')
for p,h in em['protected_sources_sha256'].items():assert sha(Path(p).read_bytes())==h,('Live/source drift',p)
(OUT/'导出验证.json').write_text(json.dumps(dict(passed=True,installed=False,runtime_verified=False,live_sources_unchanged=True,edition_source=str(editions),sidebar_source=str(side),combinations=reports),ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(output=str(OUT),zips=[r['zip'] for r in reports],passed=True,files_per_choice=8,live_sources_unchanged=True),ensure_ascii=True),flush=True)
