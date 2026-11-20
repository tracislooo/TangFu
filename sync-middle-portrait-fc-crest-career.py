"""Match the current FC crest position and career panel, preserving the portrait."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','owned_refs','rid_links'}),('add-card-six-ratings.py',{'validate_ui'}),('split-season-radar-two-charts.py',{'graph'})]:
    t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
# Reuse the verified managed-reference and inline-style subtree importer.
source=(R/'add-approved-left-fc-hidden-overview.py').read_text('utf8')
source=source[source.index('def graft_fc('):source.index(' # Fit the complete original card')]
source=source.replace('def graft_fc(doc,sheet,donor,ds):','def graft(doc,sheet,donor,ds,oldroot,newroot):')
source=source.replace(" rr,dr=refs(doc),refs(donor);oldroot=named(doc,'ReportPortraitStatusColumn');newroot=named(donor,'ReportPortraitStatusColumn')"," rr,dr=refs(doc),refs(donor)")
source+='\n return dict(root=ridmap[newroot],ridmap=ridmap,removed=removed,parent=parent)\n'
exec(compile(source,'verified-subtree-importer','exec'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001000
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-portrait-fc-crest-career-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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
    donor=oo[-930000000001001].read_typetree();dr=refs(donor);ds=oo[donor['inlineSheet']['m_PathID']].read_typetree()
    def copystyle(target,origin):
        props=copy.deepcopy(ds['m_Rules'][dr[origin]['data']['m_RuleIndex']]['m_Properties'])
        for p in props:
            for h in p['m_Values']:
                pool=poolmap.get(h['m_ValueType'])
                if pool:
                    sheet[pool].append(copy.deepcopy(ds[pool][h['valueIndex']]))
                    h['valueIndex']=len(sheet[pool])-1
        st.edit(rr[target],props,reset=True);changed.add(target)
    def crestwrapper(d,r):
        ctx=named(d,'MiddleFCPrivateFlagClubContext')
        club=next(i for i in owned_refs(r,ctx) if r[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and data(r,i).get('name')=='ClubImage')
        return r[r[club]['data']['m_Parent']['rid']]['data']['m_Parent']['rid']
    copystyle(crestwrapper(doc,rr),crestwrapper(donor,dr))
    # Match both centre columns so the career panel has the same page coordinates.
    def columns(d,r):
        return [i for i in r if r[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and data(r,i).get('name')=='ReportPortraitStatusColumn']
    targetcols=columns(doc,rr);sourcecols=columns(donor,dr)
    for ti in targetcols:
        fore=rr[ti]['data']['m_Parent']=={'rid':1169}
        si,=[i for i in sourcecols if (dr[i]['data']['m_Parent']=={'rid':1169})==fore]
        copystyle(ti,si)
    detail=graft(doc,sheet,donor,ds,named(doc,'OverviewTopRightStatusPanel'),named(donor,'OverviewTopRightStatusPanel'))
    rr=refs(doc)
    graph(doc)
    for i,x in refs(old).items():
        if i in detail['removed'] or i==detail['parent']:continue
        expected=copy.deepcopy(x)
        if i in changed:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
        assert expected==rr[i],('Unexpected data change',i)
    doc['m_ContentHash']=zlib.crc32(json.dumps(sheet,sort_keys=True).encode())&0x7fffffff
    validate_ui(doc,sheet)
    meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle')
    key,entry=next((k,e) for k,e in meta['m_Container'] if e['asset']=={'m_FileID':0,'m_PathID':PAGE})
    assert [e['asset']['m_PathID'] for k,e in meta['m_Container'] if k==key]==[PAGE]
    oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet)
    output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
    for i,h in hashes.items():
        if i not in[PAGE,sid]:assert sha(new[i].get_raw_data())==h
    assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
    src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
    tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
    checks.append(dict(target=tag,career_panel_copied_from_current_fc=True,crest_position_copied_from_current_fc=True,centre_columns_match_current_fc=True,portrait_image_unchanged=True,all_bindings_and_lower_regions_unchanged=True,all_other_objects_byte_identical=True,unique_guid=True))
    print('Verified '+tag,flush=True)
m=dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)
for name,value in [('manifest.json',m),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
    (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-portrait-fc-crest-career-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
