"""Compact the old left portrait personal details and reduce nation/club text by three pixels."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','owned_refs','rid_links'}),('add-card-six-ratings.py',{'validate_ui'})]:
    t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001010
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('old-left-portrait-compact-details-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
    for name in ['catalog.bin','catalog.hash']:
        p=(root.parent if tag=='game'else root)/name;protected[str(p)]=sha(p.read_bytes())
    before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
    doc=oo[PAGE].read_typetree();old=copy.deepcopy(doc);rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
    changed=set()
    def edit(i,props):
        st.edit(rr[i],[st.p(k,v)for k,v in props]);changed.add(i)
    personal=owned_refs(rr,1184)
    height_changes={140:108,92:72,44:36,16:12}
    for i in sorted(personal):
        a=rr[i].get('data',{});idx=a.get('m_RuleIndex',-1)
        if idx<0:continue
        props=[]
        for p in sheet['m_Rules'][idx]['m_Properties']:
            if len(p['m_Values'])!=1:continue
            h=p['m_Values'][0]
            if h['m_ValueType']!=3:continue
            dim=sheet['dimensions'][h['valueIndex']]
            if dim['unit']!=1:continue
            val=dim['value'];key=p['m_Id']
            if key in [131087,131096,131094]and val in height_changes:props.append((key,st.px(height_changes[val])))
            if key==131090 and val==4:props.append((key,st.px(0)))
        if props:edit(i,props)
    edit(6268,[(131104,st.px(35))]);edit(6270,[(131104,st.px(71))])
    # Scope font rules to this page's bottom nation/club row, including nested templates.
    a=rr[1295]['data'];a['m_Classes'].append('tf-old-left-portrait-nation-club');changed.add(1295)
    ptr={'m_FileID':0,'m_PathID':sid}
    if ptr not in a['m_Stylesheets']:a['m_Stylesheets'].append(ptr)
    def font_rule(part,typ,size):
        ix=len(sheet['m_Rules'])
        sheet['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':22 if typ==3 else 12,'m_Selectors':[{'m_Parts':[{'m_Value':'tf-old-left-portrait-nation-club','m_Type':3}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':part,'m_Type':typ}],'m_PreviousRelationship':2}],'ruleIndex':ix}],'m_Properties':[st.p(65537,st.px(size))],'line':-1})
    font_rule('SIText',1,11)
    for size,label in [(10,'xs'),(12,'sm'),(14,'md'),(16,'lg')]:
        for suffix in ['', '-regular','-strong']:font_rule('body-'+label+suffix,3,size-3)
    # No bindings, child ordering, graphic sizes or lower-page content change.
    for i,x in refs(old).items():
        expected=copy.deepcopy(x)
        if i in changed:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
        if i==1295:
            expected['data']['m_Classes']=rr[i]['data']['m_Classes'];expected['data']['m_Stylesheets']=rr[i]['data']['m_Stylesheets']
        assert expected==rr[i],('Unexpected data change',i)
    doc['m_ContentHash']=zlib.crc32(json.dumps(sheet,sort_keys=True).encode())&0x7fffffff
    validate_ui(doc,sheet)
    meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle')
    assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='4874947676d35ad2bcc95789754f22e0']==[PAGE]
    oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet)
    output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
    for i,h in hashes.items():
        if i not in[PAGE,sid]:assert sha(new[i].get_raw_data())==h
    assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
    src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,personal_details_height_before_px=140,personal_details_height_after_px=108,detail_row_height_before_px=44,detail_row_height_after_px=36,nation_and_club_font_reduction_px=3,portrait_and_feet_unchanged=True,all_bindings_unchanged=True,all_other_objects_byte_identical=True,unique_guid=True))
    print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for name,value in [('manifest.json',m),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'old-left-portrait-compact-details-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
