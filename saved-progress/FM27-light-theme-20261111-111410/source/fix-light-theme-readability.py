"""Repair formatted name ink, scale-dependent glyphs and transparent hit layers.

Prepare only. Keep current geometry, picture bindings and value-to-colour data.
"""
from pathlib import Path
import copy,datetime,importlib.util,json,re,sys,zoneinfo

R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('global_palette',R/'build-global-light-theme.py')
g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
ui=g.ui;UnityPy=ui.UnityPy
state=json.loads((R/'current-global-light-theme.json').read_text('utf8'))
ORIGINAL=Path(state.get('original_global_record',state['record']))
om=json.loads((ORIGINAL/'manifest.json').read_text('utf8'))
W,G,M=ui.W,ui.G,ui.W.replace('gameworld','match')
FILES=[*g.STYLE_FILES,*[f'ui-styles_assets_{i}x.bundle' for i in range(1,5)],W,G,M]
INK='tf-light-neutral-name'
STYLE_FLAGS=['IgnoreEmbeddedDataStyling','DisableLinkStyling']
NAME=re.compile(r'Name|TeamCellSmall|ClubCell|NationCell|CompetitionCell')
VALUE=re.compile(r'Rating|Ability|Potential|Foot|Fitness|Condition|Morale|BodyLanguage|Attribute|Role|Position|Status',re.I)
GAUGE=re.compile(r'TacticalEffectiveness|Complexity|PercentageGauge|PercentageLabel')
PITCH={'TacticsPositionCombined','TacticsPositionDetailed'}
ICON=re.compile(r'^(?:ui-concepts-|nd-)')
ICON_DATA=re.compile(r'condition|injur|morale|rating|foot|shirt|kit-|booking|red-card|yellow-card|flag|crest|badge|positive|negative|warning|success|danger',re.I)
SEMANTIC_TINT=re.compile(r'positive|negative|thumb|condition|injur|morale|fatigue|sharpness|status|foot|rating|attribute|linear|ranges-|scout-match|attend-match|image-tint-(?:cyan|orange)',re.I)

def alias_map(envs):
    result={}
    for bn,obs in envs.items():
        meta=next(o.read_typetree() for o in obs.values() if o.type.name=='AssetBundle')
        for key,item in meta['m_Container']:
            pid=item['asset']['m_PathID'];o=obs.get(pid)
            if o is None or o.type.name!='MonoBehaviour' or not re.fullmatch('[0-9a-f]{32}',key):continue
            d=o.read_typetree()
            if 'inlineSheet' in d:result[key]=(bn,pid)
    return result

def leaf_paths(doc,docs,aliases,depth=0,prefix=(),seen=()):
    if depth>3:return []
    rr=ui.refs(doc);using={u['alias']:u['path'] for u in doc.get('m_Usings',[])};out=[]
    for rid,rec in rr.items():
        a=rec.get('data',{})
        if 'm_Parent' not in a or 'm_Id' not in a:continue
        sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        if a.get('m_FullTypeName')=='SI.Bindable.SIText':
            if VALUE.search((sd.get('name') or '')+' '+' '.join(a.get('m_Classes',[]))):continue
            out.append(((*prefix,a['m_Id']),rr[a['m_SerializedData']['rid']]))
        alias=a.get('m_TemplateAlias')
        if not alias or re.search(r'Picture|Icon|Tooltip|Preview|Popover|Image',alias,re.I):continue
        key=using.get(alias)
        if key not in aliases or key in seen:continue
        child=docs[aliases[key]]
        out.extend(leaf_paths(child,docs,aliases,depth+1,(*prefix,a['m_Id']),(*seen,key)))
    return out

def literal(sh,key,c):
    return {'m_Id':key,'m_CustomName':'','m_Line':-1,'m_Values':[ui.handle(sh,4,c)]}

def edit_node(sh,rec,props):
    a=rec['data'];i=a.get('m_RuleIndex',-1)
    old=copy.deepcopy(sh['m_Rules'][i]['m_Properties']) if i>=0 else []
    keys={p['m_Id'] for p in props}
    a['m_RuleIndex']=len(sh['m_Rules'])
    sh['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':[p for p in old if p['m_Id'] not in keys]+props,'line':-1})

def fix_regular(sh,old,defs):
    edits=[]
    # Undo opaque versions of paints which are also used as image hit layers.
    source={}
    for rule in old['m_Rules']:
        for sel in rule['m_ComplexSelectors']:
            key=g.cname(sel)
            for p in rule['m_Properties']:
                if p['m_Id'] in [-1,458752]:source[(key,p['m_Id'],p.get('m_CustomName',''))]=(old,p)
    for i,rule in enumerate(sh['m_Rules']):
        if i<len(old['m_Rules']):continue
        for p in rule['m_Properties']:
            name=p.get('m_CustomName','')
            prev=next((source[(g.cname(s),p['m_Id'],name)] for s in rule['m_ComplexSelectors'] if (g.cname(s),p['m_Id'],name) in source),None)
            if prev is None:continue
            if p['m_Id']==-1 and name.startswith(('--global-sink-surface-','--global-lift-surface-')):
                c=g.rgba(prev[0],prev[1],defs)
                if c is not None:p['m_Values']=[ui.handle(sh,4,c)];edits.append({'rule':i,'restored_shared_swatch':name})
            elif p['m_Id']==458752:
                before=g.rgba(prev[0],prev[1],defs);now=g.rgba(sh,p,defs)
                if before and now and before['a']<.999 and now['a']>before['a']+1e-6:
                    c=copy.deepcopy(now);c['a']=before['a'];p['m_Values']=[ui.handle(sh,4,c)]
                    edits.append({'rule':i,'restored_alpha':before['a']})
    return edits

def add_icons(sh):
    classes=set()
    for rule in list(sh['m_Rules']):
        if not any(p['m_Id']==458753 for p in rule['m_Properties']):continue
        for s in rule['m_ComplexSelectors']:
            if len(s['m_Selectors'])!=1:continue
            parts=s['m_Selectors'][0]['m_Parts']
            if len(parts)!=1 or parts[0]['m_Type']!=3:continue
            cl=parts[0]['m_Value']
            if ICON.search(cl) and not ICON_DATA.search(cl):classes.add(cl)
    if classes:
        ui.append(sh,['.'+cl for cl in sorted(classes)],{196610:'text','--unity-image-tint-color':'text'})
        ui.append(sh,['.fm27-lake-action .'+cl for cl in sorted(classes)],{196610:'FFFFFF','--unity-image-tint-color':'FFFFFF'})
    return sorted(classes)

def protect_colored_icons(sh,defs):
    """Keep explicit semantic tint classes stronger than a neutral glyph default."""
    count=0
    for rule in list(sh['m_Rules']):
        p=next((p for p in rule['m_Properties'] if p['m_Id']==196610),None)
        if not p:continue
        c=g.rgba(sh,p,defs)
        if not c or max(c[k] for k in ['r','g','b'])-min(c[k] for k in ['r','g','b'])<.15:continue
        for source in rule['m_ComplexSelectors']:
            if not SEMANTIC_TINT.search(g.cname(source)):continue
            selector=copy.deepcopy(source)
            part=next(((s,p) for s in reversed(selector['m_Selectors']) for p in s['m_Parts'] if p['m_Type']==3),None)
            if not part:continue
            part[0]['m_Parts'].append(copy.deepcopy(part[1]));selector['m_Specificity']+=10
            i=len(sh['m_Rules']);selector['ruleIndex']=i
            tint=literal(sh,196610,c)
            custom={'m_Id':-1,'m_CustomName':'--unity-image-tint-color','m_Line':-1,'m_Values':[ui.handle(sh,4,c)]}
            sh['m_Rules'].append({'m_ComplexSelectors':[selector],'m_Properties':[tint,custom],'line':-1});count+=1
    return count

def neutral_glyph_inventory():
    glyphs=set()
    for i in range(1,5):
        p=ui.GAME/f'ui-styles_assets_{i}x.bundle'
        if not p.exists():continue
        for o in UnityPy.load(str(p)).objects:
            if o.type.name!='MonoBehaviour':continue
            d=o.read_typetree()
            if 'm_Rules' in d:glyphs.update(add_icons(d))
    return sorted(glyphs)

def main():
    out=R/('light-ui-readability-fix-'+datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S'));out.mkdir()
    snapshots={folder/bn:(folder/bn).read_bytes() for folder in [ui.GAME,ui.SKIN] for bn in FILES if (folder/bn).exists()}
    protected={str(p):ui.filehash(p) for folder in [ui.GAME,ui.SKIN] for p in folder.glob('*.bundle') if p not in snapshots}
    for folder in [ui.GAME.parent,ui.SKIN]:
        for n in ['catalog.bin','catalog.hash']:
            p=folder/n
            if p.exists():protected[str(p)]=ui.filehash(p)
    for n in ['current-custom-textures.json','reserved-texture-ids.json','current-sidebar-version.json']:
        protected[str(R/n)]=ui.filehash(R/n)
    manifest={'installed':False,'runtime_verified':False,'palette':g.PALETTE,'scope':'Global light theme: formatted names, neutral glyphs, percentage labels, tactical portraits and hover layers',
              'original_global_record':str(ORIGINAL),'before_sha256':{},'after_sha256':{},'protected_sha256':protected,
              'objects':{},'changes':[],'original_ui_surface_index':json.loads((R/'current-ui-surface-theme.json').read_text('utf8')),
              'previous_global_state':state,'new_inline_color_variables':0}
    tx={'game':str(ui.GAME),'skin':str(ui.SKIN),'workspace':str(R),'sources':{},'before':{}}
    shared_glyphs=neutral_glyph_inventory()
    for tag,folder in [('game',ui.GAME),('skin',ui.SKIN)]:
        print(tag,'load focused resources',flush=True)
        env={bn:UnityPy.load(snapshots[folder/bn]) for bn in FILES if folder/bn in snapshots}
        obs={bn:{o.path_id:o for o in e.objects} for bn,e in env.items()}
        previous={bn:{o.path_id:o for o in UnityPy.load(str(ORIGINAL/('backup-'+tag)/bn)).objects}
                  for bn in [W,G,M,*g.STYLE_FILES] if (ORIGINAL/('backup-'+tag)/bn).exists()}
        aliases=alias_map({bn:obs[bn] for bn in [W,G,M] if bn in obs})
        docs={}
        for pair in set(aliases.values()):docs[pair]=obs[pair[0]][pair[1]].read_typetree()
        # Embedded native VTAs do not have public address keys.
        for bn in [W,G,M]:
            if bn not in obs:continue
            for o in obs[bn].values():
                if o.type.name!='MonoBehaviour':continue
                if (bn,o.path_id) not in docs:
                    d=o.read_typetree()
                    if 'inlineSheet' in d:docs[(bn,o.path_id)]=d
        defs,_=g.make_definitions(ORIGINAL/('backup-'+tag))
        expected={bn:{} for bn in env};details={bn:[] for bn in env}
        # Standalone sheets: retain their original selectors and fix only paint.
        for bn in [*g.STYLE_FILES,*[f'ui-styles_assets_{i}x.bundle' for i in range(1,5)]]:
            if bn not in obs:continue
            for o in obs[bn].values():
                if o.type.name!='MonoBehaviour':continue
                d=o.read_typetree()
                if 'm_Rules' not in d:continue
                before=copy.deepcopy(d);edits=[]
                if bn in previous and o.path_id in previous[bn]:edits=fix_regular(d,previous[bn][o.path_id].read_typetree(),defs)
                glyphs=add_icons(d)
                if bn in g.STYLE_FILES:protect_colored_icons(d,defs)
                if bn==ui.S:
                    if d['m_Name']=='AlwaysAppliedStyleSheet':
                        ui.append(d,['.'+cl for cl in shared_glyphs],{196610:'text','--unity-image-tint-color':'text'})
                        ui.append(d,['.fm27-lake-action .'+cl for cl in shared_glyphs],{196610:'FFFFFF','--unity-image-tint-color':'FFFFFF'})
                        ui.append(d,['.'+INK+' SIText','.'+INK+' .sitext','.'+INK+'.sitext'],{65536:'text'})
                        clear=ui.color('000000');clear['a']=0.
                        # The full-window anchor owns geometry; only the small menu paints a surface.
                        for selector in ['.floating-element-root.full-screen-floating-block-anchor-primary-layer-root',
                                         '.full-screen-floating-block-anchor-root',
                                         '.full-screen-floating-block-anchor-root .full-screen-floating-block-anchor-container']:
                            i=len(d['m_Rules']);d['m_Rules'].append({'m_ComplexSelectors':[ui.selector(selector,i)],'m_Properties':[literal(d,458752,clear)],'line':-1})
                        ui.append(d,['.cascading-menu__folder','.si-dropdown__binding-root'],{458752:'card',65536:'text'})
                        ui.append(d,['.indicator-arrow','.indicator-tick','.indicator-open','.si-dropdown__selection-arrow'],
                                  {196610:'text',65536:'text','--unity-image-tint-color':'text'})
                if d!=before:o.save_typetree(d);expected[bn][o.path_id]=d;details[bn].append({'sheet':d['m_Name'],'id':o.path_id,'transparency':edits,'glyph_classes':glyphs})
        style_cache={}
        for (bn,pid),source in docs.items():
            name=source['m_Name']
            host=bool(NAME.search(name)) and bool(re.search(r'Cell|Row|Button|Link|Name',name)) and name not in PITCH
            gauge=bool(GAUGE.search(name)) and not re.search(r'Condition|Fitness|Pitch|Highlight',name)
            had_global=next((d for c in om['changes'] if Path(c['target'])==folder/bn for d in c['documents'] if d['id']==pid),None)
            # Also inspect direct name bindings in page templates.
            if not host and not gauge and not had_global:continue
            d=copy.deepcopy(source);rr=ui.refs(d);oldrr=ui.refs(source)
            sid=d['inlineSheet']['m_PathID']
            if sid not in obs[bn]:continue
            key=(bn,sid)
            if key not in style_cache:style_cache[key]=obs[bn][sid].read_typetree()
            sh=style_cache[key];changes=[];field_changes=[];overrides=[]
            nr=max(rr)+1
            def data(rid):return rr.get(rr[rid].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
            def mark(rec):
                if INK not in rec['data']['m_Classes']:rec['data']['m_Classes'].append(INK)
            def ignore(sd):
                for f in STYLE_FLAGS:sd[f]=1;sd[f+'_UxmlAttributeFlags']=1
            # Restore paint of pitch cards exactly from before the global pass.
            if had_global:
                od=previous[bn][pid].read_typetree();osh=previous[bn][od['inlineSheet']['m_PathID']].read_typetree()
                for e in had_global['nodes']:
                    rid=e['rid'];a=rr[rid]['data'];i=a.get('m_RuleIndex',-1)
                    if i<0:continue
                    props=sh['m_Rules'][i]['m_Properties'];op=osh['m_Rules'][e['old_rule']]['m_Properties'] if e['old_rule']>=0 else []
                    updates=[]
                    for p in props:
                        prev=next((p0 for p0 in op if p0['m_Id']==p['m_Id']),None)
                        if p['m_Id'] not in e['paint_ids'] or not prev:continue
                        c0=g.rgba(osh,prev,defs);c=g.rgba(sh,p,defs)
                        if not c0 or not c:continue
                        if name in PITCH:
                            updates.append(literal(sh,p['m_Id'],c0))
                        elif p['m_Id']==458752 and c0['a']<.999 and c['a']>c0['a']+1e-6:
                            c=copy.deepcopy(c);c['a']=c0['a'];updates.append(literal(sh,458752,c))
                    if updates:
                        edit_node(sh,rr[rid],updates);changes.append({'rid':rid,'reason':'restore_pitch_paint' if name in PITCH else 'restore_hit_layer_alpha','ids':[p['m_Id'] for p in updates]})
            for rid,rec in list(rr.items()):
                a=rec.get('data',{})
                if 'm_Parent' not in a:continue
                sd=data(rid)
                if name=='GameWorldBackground' and sd.get('name') in ['background_image','TFBlueDynamicBackground']:
                    # USS none is a StyleValueKeyword, never an Enum string.
                    edit_node(sh,rec,[{'m_Id':458753,'m_CustomName':'','m_Line':-1,'m_Values':[{'m_ValueType':1,'valueIndex':6}]}])
                    changes.append({'rid':rid,'reason':'correct_image_none_keyword','ids':[458753]})
                if a.get('m_FullTypeName')=='SI.Bindable.SIText' and name not in PITCH:
                    path=sd.get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path','')
                    own=(sd.get('name') or '')+' '+' '.join(a.get('m_Classes',[]))
                    direct_name=bool(re.search(r'(?:^|\.)(?:\w*Name\w*)$',path,re.I)) and not VALUE.search(path+' '+own)
                    wanted=(host and not VALUE.search(own)) or direct_name
                    idx=a.get('m_RuleIndex',-1);paint=sh['m_Rules'][idx]['m_Properties'] if idx>=0 else []
                    white=any(p['m_Id']==65536 and (lambda c:c and min(c[k] for k in ['r','g','b'])>.85)(g.rgba(sh,p,defs)) for p in paint)
                    if wanted or (gauge and white):
                        ignore(sd);mark(rec);edit_node(sh,rec,[literal(sh,65536,ui.color('242424'))])
                        field_changes.append({'rid':a['m_SerializedData']['rid'],'fields':STYLE_FLAGS,'reason':'formatted_name' if wanted else 'percentage_ink'})
                        changes.append({'rid':rid,'reason':'name_ink' if wanted else 'percentage_ink','ids':[65536]})
                alias=a.get('m_TemplateAlias')
                if not host or not alias or re.search(r'Picture|Icon|Tooltip|Preview|Popover|Image',alias,re.I):continue
                using=next((u for u in d['m_Usings'] if u['alias']==alias),None)
                if not using or using['path'] not in aliases:continue
                leaves=leaf_paths(docs[aliases[using['path']]],docs,aliases)
                for path,leaf in leaves:
                    entry=next((e for e in a['m_SerializedDataOverride'] if tuple(e['m_ElementIdsPath'])==path),None)
                    if entry:
                        target=rr[entry['m_SerializedData']['rid']]['data'];ignore(target)
                        field_changes.append({'rid':entry['m_SerializedData']['rid'],'fields':STYLE_FLAGS,'reason':'name_override'})
                    else:
                        item=copy.deepcopy(leaf);item['rid']=nr;nr+=1
                        for k in item['data']:
                            if k.endswith('_UxmlAttributeFlags'):item['data'][k]=0
                        ignore(item['data']);item['data']['uxmlAssetId']=path[-1]
                        assert ui.TypeTreeHelper.get_ref_type_node(item,obs[bn][pid].assets_file) is not None
                        d['references']['RefIds'].append(item);rr[item['rid']]=item
                        a['m_SerializedDataOverride'].append({'m_ElementId':path[-1],'m_ElementIdsPath':list(path),'m_SerializedData':{'rid':item['rid']}})
                        overrides.append({'node':rid,'path':list(path),'rid':item['rid']})
                if leaves:mark(rec)
            if d!=source:
                obs[bn][pid].save_typetree(d);expected[bn][pid]=d
                details[bn].append({'document':name,'id':pid,'style':sid,'paint':changes,'fields':field_changes,'overrides':overrides})
        for (bn,sid),d in style_cache.items():
            if d!=obs[bn][sid].read_typetree():obs[bn][sid].save_typetree(d);expected[bn][sid]=d
        for bn,e in env.items():
            p=folder/bn
            if not expected[bn]:protected[str(p)]=ui.sha(snapshots[p]);continue
            raw=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};old={o.path_id:o for o in UnityPy.load(snapshots[p]).objects}
            assert set(saved)==set(old)
            for pid,o in saved.items():
                if pid in expected[bn]:assert o.read_typetree()==expected[bn][pid],('Roundtrip',bn,pid)
                else:assert o.get_raw_data()==old[pid].get_raw_data(),('Unrelated object',bn,pid)
            for sub,data in [(tag,raw),('backup-'+tag,snapshots[p])]:
                dst=out/sub/bn;dst.parent.mkdir(exist_ok=True);dst.write_bytes(data)
            manifest['before_sha256'][str(p)]=ui.sha(snapshots[p]);manifest['after_sha256'][str(p)]=ui.sha(raw)
            manifest['objects'][str(p)]={'changed_ids':[str(i) for i in expected[bn]],'total_objects':len(saved),'all_other_objects_byte_identical':True}
            manifest['changes'].append({'target':str(p),'details':details[bn]})
            tx['sources'][str(p)]=str(out/tag/bn);tx['before'][str(p)]=str(out/('backup-'+tag)/bn)
            print(tag,bn,'changed objects',len(expected[bn]),flush=True)
    for p,raw in snapshots.items():assert p.read_bytes()==raw,('Baseline changed',p)
    for path,h in protected.items():assert ui.filehash(Path(path))==h,('Protected changed',path)
    manifest['coverage']={'files':len(tx['sources']),'repaired_documents':sum('document' in d for c in manifest['changes'] for d in c['details'])}
    manifest['prepared_verified']=True
    for name,data in [('manifest.json',manifest),('transaction.json',tx)]: (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
    for src,dst in [('fix-light-theme-readability.py','fix-light-theme-readability.py'),('install-global-light-theme.py','installer.py')]: (out/dst).write_bytes((R/src).read_bytes())
    for name,flag in [('install',''),('restore',' --restore'),('verify',' --verify')]:
        (out/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
    ns={'status':'prepared','installed':False,'record':str(out),'manifest':str(out/'manifest.json'),'palette':g.PALETTE,'scope':manifest['scope'],'runtime_verified':False,'original_global_record':str(ORIGINAL)}
    (R/'current-light-readability-fix.json').write_text(json.dumps(ns,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps({'prepared':True,'record':str(out),'files':len(tx['sources'])},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
