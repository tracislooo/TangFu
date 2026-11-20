exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
p=R/'Action移入属性区-20261016-002020/backup/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';e=UnityPy.load(str(p));oo={o.path_id:o for o in e.objects};d=oo[-4194025542157271532].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};ss=oo[d['inlineSheet']['m_PathID']].read_typetree()
for i in [1020,1037,1057,1058,1080,1083,1108,1109]:
 a=sr[i]['data'];print('NATIVE',i,a['m_Classes'])
 if a['m_RuleIndex']>=0:print(ss['m_Rules'][a['m_RuleIndex']])
rep=json.loads((R/'gk-no-title-left-stars-horizontal-loans-20261019-011613/manifest.json').read_text(encoding='utf8'));club={int(k):v for k,v in rep['inline_imports'][2]['mapping'].items()}
print('CLUBMAP',[(i,club[i],rr[club[i]]['data'].get('m_Classes')) for i in [1001,1002,1004,1007,1012,1013,1020,1021,1025,1026]])
