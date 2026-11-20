"""Prepare a reversible lake-blue UI palette from each currently installed bundle."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
S='ui-styles_assets_default.bundle'
C='ui-styles_assets_common.bundle'
BG='ui-backgrounds_assets_common.bundle'
ACTION='fm27-lake-action'; GRAD='fm27-lake-action-gradient'; CONT='fm27-lake-continue-root'
sha=lambda b:hashlib.sha256(b).hexdigest()
f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
refs=lambda d:{r['rid']:r for r in d['references']['RefIds']}
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='write' or isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'<codec-and-styles>','exec'))
TypeTreeHelper.write_value=write
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'<validate-ui>','exec'))
source=ast.parse((R/'fix-primary-navigation-grey-lake-blue.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='selector'],type_ignores=[]),'<selector-compiler>','exec'))

def color(code,alpha=1.):
    return dict(zip(['r','g','b','a'],[f32(int(code[i:i+2],16)/255) for i in [0,2,4]]+[f32(alpha)]))
LEFT=color('35C6E8');RIGHT=color('078BC4');WHITE=color('FFFFFF')
HOVER=(color('50D2EE'),color('119DD5'));PRESSED=(color('24AFD1'),color('067BAE'))
PRIMARY={'buttons-button-primary-default','buttons-quick-action-primary',
         'buttons-hero-toggle-buttons-active--border-radius-none','buttons-hero-toggle-buttons-active--border-radius-left',
         'buttons-hero-toggle-buttons-active--border-radius-right','tutorial-floating-continue-button-continue-part',
         'speakto-button-interaction-button-choices-primary','continue-button'}
# Text roles only. Never replace the base purple/pink palette or data-category roles.
TEXT_ROLES={'fm-news-link-test','title-link-primary-text','colours-brand-foundation-horizon',
    'colours-brand-foundation-horizon-soft','communication-feedback-information','modal-text-primary',
    'shuffle-draft-header-text','thematic-modal','news-footer-mens-primary-small-12px-regular',
    'tifo-text-brand-horizon','tifo-text-men-primary','tifo-text-brand-tints-horizon-120',
    'tifo-text-brand-highlight-pink','tifo-text-base-purple-50','tifo-text-base-purple-60','tifo-text-base-purple-80',
    'brand-foundation-horizon-color','tile-secondary-title--timestamp','ios-navigation-links-colour',
    'main-menu-navigation-default-text','notificationmessagestatus-action-colour',
    'biography-property1-stepper','tutorial-text-step-color','whatsnew-panel-title-colour',
    'layout-modules-tiles-title-color','create-club-selected-club-edit-text'}
TEXT_VARS={'--modal-text-primary','--data-progress-indicator-foreground'}
BUTTON_VARS={'--buttons-primary-surface-default':RIGHT,'--buttons-primary-surface-hover':HOVER[1]}
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned={int(t['path_id']) for t in reserved};banned_names={t['name'].lower() for t in reserved}

names=[p.name for p in GAME.glob('*visualtree*.bundle')]+[S,C]
before={};cache={};patches={}
for folder in [GAME,SKIN]:
    for name in names:
        p=folder/name
        if not p.exists():continue
        raw=p.read_bytes();before[p]=raw;key=(name,sha(raw))
        if key not in cache:
            en=UnityPy.load(raw);oo={o.path_id:o for o in en.objects}
            cache[key]={'env':en,'objects':oo,'expected':{},'hashes':{i:sha(o.get_raw_data()) for i,o in oo.items()},
                        'templates':[],'style_edits':[],'added_rules':[],'source_name':name}
        patches[p]=cache[key]
protected={}
for folder in [GAME,SKIN]:
    for name in [BG,'ui-visualfunctions_assets_all.bundle','ui-tileslayouts_assets_all.bundle','ui-textures_assets_all.bundle']:
        p=folder/name
        if p.exists():protected[p]=sha(p.read_bytes())
    for name in ['catalog.bin','catalog.hash']:
        p=(GAME.parent if folder==GAME else folder)/name
        if p.exists():protected[p]=sha(p.read_bytes())
for name in ['AGENTS.md','reserved-texture-ids.json','current-custom-textures.json','球员弹窗最终版本说明.md','球员弹窗最终版本资源快照.json']:
    p=R/name
    if p.exists():protected[p]=sha(p.read_bytes())

global_objects=patches[GAME/G]['objects']
proto=next(o.read_typetree() for o in global_objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='button-primary-leading-icon-label')
pr=refs(proto)
gradient_proto=copy.deepcopy(pr[1002]);gradient_sd_proto=copy.deepcopy(pr[gradient_proto['data']['m_SerializedData']['rid']])

def put(patch,obj,data):
    if data!=obj.read_typetree():obj.save_typetree(data);patch['expected'][obj.path_id]=copy.deepcopy(data)

def empty_function():
    return {'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}

def patch_templates(patch):
    oo=patch['objects']
    for ob in list(oo.values()):
        if ob.type.name!='MonoBehaviour':continue
        d=ob.read_typetree()
        if 'inlineSheet' not in d:continue
        rr=refs(d);targets=[r for r in rr.values() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIButton' and PRIMARY.intersection(r['data'].get('m_Classes',[]))]
        if not targets:continue
        old=copy.deepcopy(d);oldrr=refs(old);sid=d['inlineSheet']['m_PathID'];so=oo[sid]
        s=so.read_typetree();old_s=copy.deepcopy(s);st=Styles(s)
        nr=max(rr)+1;ni=max((r.get('data',{}).get('m_Id',0) for r in rr.values()),default=0)+1
        modified_style=set();newrecords=set();added=[];gradients=[];rootmark=None;direction_records=set()
        def data(rec):return rr.get(rec['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        def descendants(rid):
            yield rid
            for ch in rr[rid].get('data',{}).get('m_Children',[]):yield from descendants(ch['rid'])
        for btn in targets:
            ba=btn['data'];assert ACTION not in ba['m_Classes'],('Already patched',d['m_Name'])
            ba['m_Classes'].append(ACTION)
            own=[rid for rid in descendants(btn['rid']) if rr[rid].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient']
            # Ordinary buttons own a direct gradient. Continue uses its existing two
            # nested sliding layers, so never insert another layer into that control.
            direct=[ch['rid'] for ch in ba['m_Children'] if rr[ch['rid']].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIGradient']
            use=own if 'continue-button' in ba['m_Classes'] else direct
            if not use:
                node=copy.deepcopy(gradient_proto);ser=copy.deepcopy(gradient_sd_proto)
                node['rid']=nr;ser['rid']=nr+1;nr+=2
                node['data'].update(m_Id=ni,m_Parent={'rid':btn['rid']},m_Children=[],m_RuleIndex=-1,m_Classes=[GRAD],m_SerializedData={'rid':ser['rid']})
                ser['data'].update(uxmlAssetId=ni,name='LakeBlueActionGradient',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
                ni+=1
                assert TypeTreeHelper.get_ref_type_node(ser,ob.assets_file) is not None
                d['references']['RefIds'].extend([node,ser]);rr[node['rid']]=node;rr[ser['rid']]=ser
                ba['m_Children'].insert(0,{'rid':node['rid']});newrecords.update([node['rid'],ser['rid']]);use=[node['rid']];added.append(node['rid'])
                st.edit(node,[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131103,st.px(0)),st.p(131104,st.px(0)),st.p(131080,st.px(0)),st.p(131105,st.pct(100)),st.p(131087,st.pct(100))])
            for rid in use:
                a=rr[rid]['data']
                if GRAD not in a['m_Classes']:a['m_Classes'].append(GRAD)
                gradients.append(rid)
                serdata=data(rr[rid])
                if serdata.get('GradientDirection')!=1 or serdata.get('GradientDirection_UxmlAttributeFlags')!=1:
                    serdata['GradientDirection']=1;serdata['GradientDirection_UxmlAttributeFlags']=1
                    direction_records.add(a['m_SerializedData']['rid'])
                # Keep native callbacks, reverse/slide animation and picking mode.
                assert data(rr[rid]).get('pickingMode')==1
            # An inline color on a primary action must not conceal the gradient or
            # override its white label. Other inline style values remain identical.
            for rid in descendants(btn['rid']):
                rec=rr[rid];a=rec.get('data',{});idx=a.get('m_RuleIndex',-1)
                if idx<0:continue
                props=s['m_Rules'][idx]['m_Properties'];updates=[]
                if rid==btn['rid'] and any(p['m_Id']==458752 for p in props):updates.append(st.p(458752,st.h(4,RIGHT)))
                if a.get('m_FullTypeName')=='SI.Bindable.SIText' and any(p['m_Id']==65536 for p in props):updates.append(st.p(65536,st.h(4,WHITE)))
                if updates:st.edit(rec,updates);modified_style.add(rid)
        if d['m_Name']=='continue-button':
            rootmark=1001;rr[rootmark]['data']['m_Classes'].append(CONT)
        # Verify preexisting children/order, events, field bindings and serialized
        # data records. Only color handles, marker classes and new children vary.
        for rid,record in oldrr.items():
            actual=copy.deepcopy(rr[rid]);prior=record.get('data',{})
            if 'm_FullTypeName' in prior:
                if 'm_Classes' in prior:actual['data']['m_Classes']=copy.deepcopy(prior['m_Classes'])
                if rid in modified_style:actual['data']['m_RuleIndex']=prior['m_RuleIndex']
                if rid in [t['rid'] for t in targets]:
                    actual['data']['m_Children']=[c for c in actual['data']['m_Children'] if c['rid'] not in newrecords]
            if rid in direction_records:
                for k in ['GradientDirection','GradientDirection_UxmlAttributeFlags']:actual['data'][k]=prior[k]
            assert actual==record,('Original behavior changed',d['m_Name'],rid)
        assert set(rr)==set(oldrr)|newrecords
        for k,v in old_s.items():
            if isinstance(v,list):assert s[k][:len(v)]==v,k
            else:assert s[k]==v,k
        validate_ui(d,s);put(patch,ob,d);put(patch,so,s)
        patch['templates'].append({'name':d['m_Name'],'path_id':str(ob.path_id),'style_path_id':str(sid),
            'buttons':[r['rid'] for r in targets],'gradients':gradients,'new_gradients':added,'continue_root':rootmark,
            'original_bindings_events_geometry_preserved':True})

def append_rule(sh,selectors,properties,relationship=2):
    st=Styles(sh);idx=len(sh['m_Rules']);props=[]
    for key,value in properties:
        handle=st.h(4,copy.deepcopy(value)) if isinstance(value,dict) else st.num(value)
        props.append({'m_Id':-1 if isinstance(key,str) else key,'m_CustomName':key if isinstance(key,str) else '', 'm_Line':-1,'m_Values':[handle]})
    sels=[selector(t,idx) for t in selectors]
    sh['m_Rules'].append({'m_ComplexSelectors':sels,'m_Properties':props,'line':-1})
    return {'index':idx,'selectors':selectors,'properties':[k for k,v in properties]}

def patch_sheets(patch):
    for ob in patch['objects'].values():
        if ob.type.name!='MonoBehaviour':continue
        sh=ob.read_typetree()
        if 'm_Rules' not in sh:continue
        old=copy.deepcopy(sh);st=Styles(sh);edits=[]
        for idx,r in enumerate(old['m_Rules']):
            for pi,p in enumerate(r['m_Properties']):
                key=p['m_CustomName']
                if key in TEXT_VARS or key in BUTTON_VARS:
                    val=LEFT if key in TEXT_VARS else BUTTON_VARS[key]
                    sh['m_Rules'][idx]['m_Properties'][pi]['m_Values']=[st.h(4,copy.deepcopy(val))]
                    edits.append({'kind':'dedicated-variable','rule':idx,'property':key})
            text=next((p for p in r['m_Properties'] if p['m_Id']==65536),None)
            if text is None:continue
            selected=[]
            for sel in r['m_ComplexSelectors']:
                classes={part['m_Value'] for item in sel['m_Selectors'] for part in item['m_Parts'] if part['m_Type']==3}
                if TEXT_ROLES.intersection(classes):selected.append(copy.deepcopy(sel))
            if selected:
                newidx=len(sh['m_Rules'])
                for sel in selected:sel['ruleIndex']=newidx
                # Split shared rules: preserve unrelated player/status selectors.
                alpha=1.
                if len(text['m_Values'])==1 and text['m_Values'][0]['m_ValueType']==4:alpha=old['colors'][text['m_Values'][0]['valueIndex']]['a']
                sh['m_Rules'].append({'m_ComplexSelectors':selected,'m_Properties':[st.p(65536,st.h(4,color('35C6E8',alpha)))],'line':-1})
                edits.append({'kind':'emphasis-text','source_rule':idx,'rule':newidx,'selectors':selected})
        if sh['m_Name']=='AlwaysAppliedStyleSheet':
            rules=[];base='SIButton.'+ACTION;grad=base+' SIGradient.'+GRAD
            for state,ends in [('',(LEFT,RIGHT)),(':hover:enabled',HOVER),(':active:enabled',PRESSED)]:
                rules.append(append_rule(sh,[base+state+' SIGradient.'+GRAD],[('--start-colour',ends[0]),('--end-colour',ends[1])]))
                rules.append(append_rule(sh,[base+state,'#continue-button.'+ACTION+state],[(458752,ends[1])]))
            rules.append(append_rule(sh,[base+':disabled SIGradient.'+GRAD],[(458767,.25)]))
            rules.append(append_rule(sh,[base+':enabled SIText',base+':enabled .global-text-primary','#continue-button.'+ACTION+':enabled SIText'],[(65536,WHITE)]))
            rules.append(append_rule(sh,[base+':enabled #leading-icon',base+':enabled #trailing-icon',base+':enabled .ui-concepts-tick_small',
                base+':enabled .ui-concepts-chevron-right_small',base+':enabled .ui-concepts-chevron-left_small',
                base+':enabled #primary-icon-image',base+':enabled .ui-concepts-continue_medium',base+':enabled .ui-concepts-person_small',
                '#continue-button.'+ACTION+':enabled #primary-icon-image'],[(196610,WHITE)]))
            rules.append(append_rule(sh,['.'+CONT+' #continue-button-background','.'+CONT+' .continue-button--background-image'],[(458767,0.)]))
            # Dynamic primary style classes use the same palette even when applied
            # after instantiation by native state/style setters.
            for state,ends in [('',(LEFT,RIGHT)),(':hover:enabled',HOVER),(':active:enabled',PRESSED)]:
                dynamic=['.'+c+state+' .sigradient' for c in PRIMARY if c!='continue-button']
                rules.append(append_rule(sh,sorted(dynamic),[('--start-colour',ends[0]),('--end-colour',ends[1])]))
            # Retain the previously fixed gray/black navigation and give its
            # existing continue override the same hover/press colors.
            for state,ends in [(':hover:enabled',HOVER),(':active:enabled',PRESSED)]:
                prefix='#MainNav.fm27-fixed-primary-nav #ContinueButton'
                rules.append(append_rule(sh,[prefix+' .continue-button'+state+' .continue-button---gradient'],[('--start-colour',ends[0]),('--end-colour',ends[1])]))
            patch['added_rules']=rules
        if sh!=old:
            # No preexisting selector, non-target property, background or tint changes.
            for i,r in enumerate(old['m_Rules']):
                expected=copy.deepcopy(r)
                for p in expected['m_Properties']:
                    if p['m_CustomName'] in TEXT_VARS|set(BUTTON_VARS):
                        actual=next(q for q in sh['m_Rules'][i]['m_Properties'] if q['m_CustomName']==p['m_CustomName'])
                        p['m_Values']=copy.deepcopy(actual['m_Values'])
                assert sh['m_Rules'][i]==expected,('Unrelated style changed',sh['m_Name'],i)
            for k,v in old.items():
                if k=='m_Rules':continue
                if isinstance(v,list):assert sh[k][:len(v)]==v,k
                else:assert sh[k]==v,k
            put(patch,ob,sh);patch['style_edits'].append({'name':sh['m_Name'],'path_id':str(ob.path_id),'edits':edits})

for key,patch in cache.items():
    if key[0] in [S,C]:patch_sheets(patch)
    else:patch_templates(patch)

# Full bundle roundtrip plus byte-level preservation of every unrelated object.
for key,patch in cache.items():
    if not patch['expected']:continue
    raw=patch['env'].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
    assert set(saved)==set(patch['objects']) and banned.isdisjoint(saved)
    for pid,ob in saved.items():
        if pid in patch['expected']:assert ob.read_typetree()==patch['expected'][pid],('Roundtrip mismatch',key[0],pid)
        else:assert sha(ob.get_raw_data())==patch['hashes'][pid],('Unrelated asset changed',key[0],pid)
    for item in patch['templates']:validate_ui(saved[int(item['path_id'])].read_typetree(),saved[int(item['style_path_id'])].read_typetree())
    patch['payload']=raw;patch['saved']=saved

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
audits=[]
for folder in [GAME,SKIN]:
    catpath=(GAME.parent if folder==GAME else SKIN)/'catalog.bin';cat=cm.Catalog(catpath.read_bytes());rows=[];native=[]
    for bn in [n for n in names if 'visualtree' in n and folder/n in patches]:
        patch=patches[folder/bn];oo=patch.get('saved',patch['objects'])
        meta=next(ob.read_typetree() for ob in oo.values() if ob.type.name=='AssetBundle')
        template_ids={int(x['path_id']) for x in patch['templates']}
        for guid,entry in meta['m_Container']:
            if not re.fullmatch('[0-9a-f]{32}',guid) or entry['asset']['m_FileID']!=0:continue
            ob=oo.get(entry['asset']['m_PathID'])
            if ob is None or ob.type.name!='MonoBehaviour':continue
            custom=-1000000000000000<ob.path_id<-900000000000000
            if not custom and ob.path_id not in template_ids:continue
            d=ob.read_typetree();kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else 'SI.VisualScripting.VisualFunction' if 'm_nodes' in d else None
            if kind is None:continue
            locs=[l for l in cat.locations(guid) if cat.location(l)['type'][1]==kind];assert locs,(guid,kind)
            for loc in locs:
                v=cat.location(loc);assert v['internal']==guid and v['dependencies']
                owner=cat.location(v['dependencies'][0])['internal'].replace('\\','/');assert owner.endswith('/'+bn),(guid,owner)
                if custom:assert any(cat.location(l)['internal'].replace('\\','/').endswith('/'+BG) for l in v['dependencies']),guid
            (rows if custom else native).append({'name':ob.peek_name(),'guid':guid,'type':kind,'bundle':bn,'path_id':str(ob.path_id)})
    assert len(rows)>=82
    audits.append({'catalog':str(catpath),'custom_resources':rows,'modified_native_templates':native})

active=json.loads((R/'current-custom-textures.json').read_text('utf8'))['textures'];assert len(active)==176
for folder in [GAME,SKIN]:
    be=UnityPy.load(str(folder/BG));bo={o.path_id:o for o in be.objects};meta=next(o.read_typetree() for o in bo.values() if o.type.name=='AssetBundle')
    assert banned.isdisjoint(bo)
    assert all(o.peek_name().lower() not in banned_names for o in bo.values() if o.type.name=='Texture2D')
    assert all(k.lower() not in banned_names and v['asset']['m_PathID'] not in banned for k,v in meta['m_Container'])
    assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
    for t in active:
        ob=bo[int(t['path_id'])];assert ob.type.name=='Texture2D' and ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256'],t['name']
for p,b in before.items():assert p.read_bytes()==b,p
for p,h in protected.items():assert sha(p.read_bytes())==h,p

stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('lake-blue-controls-'+stamp);out.mkdir();sources={};backups={};after={};reports={}
for p,patch in patches.items():
    if not patch['expected']:
        protected[p]=sha(before[p]);continue
    tag='game' if p.parent==GAME else 'skin'
    (out/tag).mkdir(exist_ok=True);(out/('backup-'+tag)).mkdir(exist_ok=True)
    target=out/tag/p.name;target.write_bytes(patch['payload']);backup=out/('backup-'+tag)/p.name;backup.write_bytes(before[p])
    sources[str(p)]=str(target);backups[str(p)]=str(backup);after[str(p)]=sha(patch['payload'])
    reports[str(p)]={'modified_objects':{str(pid):d['m_Name'] for pid,d in patch['expected'].items()},'templates':patch['templates'],'style_edits':patch['style_edits'],'added_rules':patch['added_rules']}
old_nav=json.loads((R/'primary-navigation-grey-lake-blue-20261027-234809/manifest.json').read_text('utf8'))
verification={'palette':{'normal':['#35C6E8','#078BC4'],'hover':['#50D2EE','#119DD5'],'pressed':['#24AFD1','#067BAE'],'text_and_progress':'#35C6E8'},
    'serialization_roundtrip':True,'unrelated_objects_byte_identical':True,'original_events_bindings_geometry_preserved':True,
    'new_bundle_object_ids':0,'all_176_texture_hashes_verified':True,'reserved_70_absent_objects_container_preload':True,
    'catalog_audits':audits,'bundle_changes':reports,'background_decoration_and_semantic_color_rules_preserved':True,
    'appended_scoped_rules':old_nav['verification']['appended_scoped_rules'],'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(out),'before_sha256':{p:sha(before[Path(p)]) for p in sources},
    'after_sha256':after,'protected_sha256':{str(p):h for p,h in protected.items()},'verification':verification,'missing_before':[]}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':sorted({Path(p).name for p in sources}),'sources':sources,'before':backups,'missing':[]},ensure_ascii=False,indent=2),'utf8')
(out/'installer.py').write_bytes((R/'install-primary-navigation-patch.py').read_bytes())
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'修改说明.md').write_text('全游戏同类主操作按钮统一为湖水蓝渐变：常态 #35C6E8 → #078BC4，悬停 #50D2EE → #119DD5，按下 #24AFD1 → #067BAE。按钮文字和功能图标白色；禁用状态保留淡化。\n原紫色强调文字与通用进度条填充改为 #35C6E8。只修改专用控件变量及文字规则，不替换品牌紫色基础调色板；背景图片、装饰线、队徽、红绿提示、体能/伤病/评分状态颜色保留。\n缺少渐变层的主按钮追加原生 SIGradient 子节点，忽略拾取；按钮点击和绑定、进度数值与动画不变。未新增资源对象、GUID、Path ID 或目录依赖。\n以各目录当前资源为底包，保留游戏与皮肤目录差异；install.ps1 安装，restore.ps1 回退。需先退出游戏。静态校验与实际游戏显示验证分别记录。\n','utf8')
print(json.dumps({'prepared':True,'output':str(out),'files':len(sources),'game_button_templates':sum(len(patch['templates']) for p,patch in patches.items() if p.parent==GAME),
    'game_button_nodes':sum(len(t['buttons']) for p,patch in patches.items() if p.parent==GAME for t in patch['templates']),
    'game_added_gradient_nodes':sum(len(t['new_gradients']) for p,patch in patches.items() if p.parent==GAME for t in patch['templates']),
    'catalog_custom_resources':[len(x['custom_resources']) for x in audits],'runtime_verified':False},ensure_ascii=False),flush=True)
