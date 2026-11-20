from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,zlib
R=Path(__file__).resolve().parent
exec((R/'apply-navigation-background70.py').read_text('utf8').split('out=R/')[0])
a=R/'navigation-native-foreground-20261117-232255';b=R/'navigation-controls70-20261117-224348'
at=json.loads((a/'transaction.json').read_text('utf8'));bt=json.loads((b/'transaction.json').read_text('utf8'))
out=R/('rollback-navigation-background70-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
before={};payloads={};protected={};reports=[]
def objs(raw):return {o.path_id:o for o in UnityPy.load(raw).objects}
def merge_reverse(current,expected,desired):
    if expected==desired:return copy.deepcopy(current)
    if isinstance(expected,dict) and isinstance(desired,dict) and isinstance(current,dict):
        result=copy.deepcopy(current)
        for k in expected.keys()|desired.keys():
            if k not in desired:
                if k in expected and result.get(k)==expected[k]:result.pop(k,None)
            elif k not in expected:result[k]=copy.deepcopy(desired[k])
            elif k in current:result[k]=merge_reverse(current[k],expected[k],desired[k])
        return result
    return copy.deepcopy(desired)
for tag,folder in [('game',GAME),('skin',SKIN)]:
    changes=[]
    for bn in [W,'ui-styles_assets_default.bundle']:
        path=folder/bn;raw=path.read_bytes();before[path]=raw
        en=UnityPy.load(raw);current={o.path_id:o for o in en.objects}
        expected=objs(Path(at['sources'][str(path)]).read_bytes())
        desired=objs(Path(bt['before'][str(path)]).read_bytes())
        changed={}
        for pid,ob in current.items():
            if pid not in expected or pid not in desired:continue
            if expected[pid].get_raw_data()==desired[pid].get_raw_data():continue
            e=expected[pid].read_typetree();d=desired[pid].read_typetree();c=ob.read_typetree()
            if 'm_Rules' in c:
                if c['m_Name']=='AlwaysAppliedStyleSheet':
                    # All original pools remain available, including later layout values.
                    for pool in poolmap.values():
                        assert c[pool][:len(d[pool])]==d[pool],pool
                    new=copy.deepcopy(c)
                    rules=copy.deepcopy(d['m_Rules'])
                    for i in range(min(len(rules),len(e['m_Rules']),len(c['m_Rules']))):
                        if c['m_Rules'][i]==e['m_Rules'][i]:continue
                        text=json.dumps(e['m_Rules'][i])+json.dumps(c['m_Rules'][i])
                        if not any(s in text for s in ['MainNav','fm27-fixed','fm27-holiday']):
                            rules[i]=copy.deepcopy(c['m_Rules'][i])
                    new['m_Rules']=rules
                else:
                    new=copy.deepcopy(c)
                    for i in range(min(len(d['m_Rules']),len(e['m_Rules']))):
                        if d['m_Rules'][i]==e['m_Rules'][i]:continue
                        for p in d['m_Rules'][i]['m_Properties']:
                            if p['m_Id']!=458752:continue
                            oldp=next((p for p in e['m_Rules'][i]['m_Properties'] if p['m_Id']==458752),None)
                            if not oldp:continue
                            dh,=p['m_Values'];eh,=oldp['m_Values']
                            if dh['m_ValueType']!=4 or eh['m_ValueType']!=4:continue
                            dc=d['colors'][dh['valueIndex']];ec=e['colors'][eh['valueIndex']]
                            for r in new['m_Rules']:
                                for prop in r['m_Properties']:
                                    if prop['m_Id']!=458752:continue
                                    h,=prop['m_Values']
                                    if h['m_ValueType']==4 and new['colors'][h['valueIndex']]==ec:
                                        new['colors'].append(copy.deepcopy(dc));h['valueIndex']=len(new['colors'])-1
            elif 'references' in c:
                new=copy.deepcopy(c)
                er={r['rid']:r for r in e['references']['RefIds']};dr={r['rid']:r for r in d['references']['RefIds']}
                for i,r in enumerate(new['references']['RefIds']):
                    rid=r['rid']
                    if rid in er and rid in dr:
                        new['references']['RefIds'][i]=merge_reverse(r,er[rid],dr[rid])
            else:raise AssertionError(e.get('m_Name'))
            if new!=c:ob.save_typetree(new);changed[pid]=new;changes.append(new.get('m_Name'))
        if bn==W:
            for ob in current.values():
                if ob.type.name!='MonoBehaviour' or ob.peek_name() not in ['PrimaryNavigationBar','SecondaryNavigationBar']:continue
                doc=copy.deepcopy(changed.get(ob.path_id,ob.read_typetree()))
                rr={r['rid']:r for r in doc['references']['RefIds']}
                rid=1002 if doc['m_Name']=='PrimaryNavigationBar' else 1001
                dd=desired[ob.path_id].read_typetree();dr={r['rid']:r for r in dd['references']['RefIds']}
                ds=desired[dd['inlineSheet']['m_PathID']].read_typetree()
                prop=next(p for p in ds['m_Rules'][dr[rid]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==458752)
                color=ds['colors'][prop['m_Values'][0]['valueIndex']]
                assert abs(color['a']-.7)<1e-6
                sid=doc['inlineSheet']['m_PathID'];sheet=copy.deepcopy(changed.get(sid,current[sid].read_typetree()))
                st=Styles(sheet);st.edit(rr[rid],[st.p(458752,st.h(4,copy.deepcopy(color)))])
                for pid,data in [(ob.path_id,doc),(sid,sheet)]:
                    current[pid].save_typetree(data);changed[pid]=data
        packed=en.file.save(packer='lz4');saved=objs(packed);old=objs(raw)
        assert set(saved)==set(old)
        for pid,ob in saved.items():
            if pid in changed:assert ob.read_typetree()==changed[pid]
            else:assert ob.get_raw_data()==old[pid].get_raw_data()
        payloads[path]=packed
    cp=(GAME.parent if tag=='game' else SKIN)/'catalog.bin';hp=cp.with_suffix('.hash')
    before[cp]=cp.read_bytes();before[hp]=hp.read_bytes();cat=cm.Catalog(before[cp])
    locs={i for _,p in cat.keys() for i, in cat.array(p,'I')}
    for i in locs:
        v=cat.location(i);name=v['internal'].replace('\\','/').split('/')[-1]
        if not v['type'][1].endswith('IAssetBundleResource') or folder/name not in payloads:continue
        if v['raw'][5]==cm.NULL:continue
        typ,pp=cat.unpack(v['raw'][5],'2I');opts=list(cat.unpack(pp,'5I'));data=payloads[folder/name]
        opts[2:4]=[crc(data),len(data)]
        newp=cat.append(struct.pack('<5I',*opts));extra=cat.append(struct.pack('<2I',typ,newp))
        struct.pack_into('<I',cat.data,i+20,extra)
    if bytes(cat.data)!=before[cp]:
        payloads[cp]=bytes(cat.data);payloads[hp]=hashlib.md5(payloads[cp]).hexdigest().encode('ascii')
    for p in list(folder.glob('*.bundle'))+[cp,hp]:
        if p not in payloads and p.exists():protected[str(p)]=sha(p.read_bytes())
    reports.append(dict(target=tag,changed_objects=changes,later_layout_preserved=True))
statepath=R/'current-ui-surface-theme.json';before[statepath]=statepath.read_bytes();state=json.loads(before[statepath])
desiredstate=json.loads(Path(bt['before'][str(statepath)]).read_text('utf8'))
state['navigation_backgrounds']=desiredstate['navigation_backgrounds'];state['navigation_backgrounds']['rollback_record']=str(out/'manifest.json')
payloads[statepath]=json.dumps(state,ensure_ascii=False,indent=2).encode('utf8')
out.mkdir();tx=dict(game=str(GAME),skin=str(SKIN),workspace=str(R),sources={},before={})
for p,data in payloads.items():
    assert p.read_bytes()==before[p],p
    tag='game' if p.parent in [GAME,GAME.parent] else 'skin' if p.parent==SKIN else 'workspace'
    dst=out/tag/p.name;bak=out/('backup-'+tag)/p.name
    for q,v in [(dst,data),(bak,before[p])]:
        q.parent.mkdir(exist_ok=True);q.write_bytes(v)
    tx['sources'][str(p)]=str(dst);tx['before'][str(p)]=str(bak)
m=dict(installed=False,runtime_verified=False,reports=reports,protected_sha256=protected,before_sha256={str(p):sha(before[p]) for p in payloads},after_sha256={str(p):sha(v) for p,v in payloads.items()})
for name,d in [('manifest.json',m),('transaction.json',tx),('verification.json',dict(passed=True,runtime_verified=False))]:(out/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
(out/'restore.ps1').write_text("& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'install-native-background-overrides.py')+"' '"+str(out)+"' --restore\n",'utf8')
(R/'pending-rollback-navigation-background70.json').write_text(json.dumps(dict(patch=str(out))),'utf8')
print(out)
