exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','compare-reference-pitch-control-settings-'))
OLD=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');oo={o.path_id:o for o in UnityPy.load(str(OLD/G)).objects};doc=oo[-4928795461599700197].read_typetree();rr=refs(doc);native=rr[rr[1023]['data']['m_SerializedData']['rid']]['data'];sheet=oo[doc['inlineSheet']['m_PathID']].read_typetree()
for i in [1010,1022,1023]:print('REF STYLE',i,rr[i]['data']['m_Classes'],sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if rr[i]['data'].get('m_RuleIndex',-1)>=0 else [])
for pid in [-940000000005000,-940000000008000,-940000000010020,-960000000003030]:
 d=objs[G][pid].read_typetree();r=refs(d);s=r[r[1023]['data']['m_SerializedData']['rid']]['data'];print('DIFF',pid,{k:(v,s.get(k)) for k,v in native.items() if s.get(k)!=v})
print('REF dimensions',sheet['dimensions']);print('REF classes',doc['m_Stylesheets'] if 'm_Stylesheets' in doc else 'none')
