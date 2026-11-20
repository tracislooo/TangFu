from pathlib import Path
import json,sys
R=Path(__file__).parent
source=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('# 1. Prematch')[0]
source=source.replace('match-ui-avatars-layout-','match-ui-layout-refinement-').replace('NAMES=[W,G,M,F]','NAMES=[W,G,M]')
exec(compile(source,'current-bundle-backup-and-helpers','exec'))

# Explicit names prevent confusing margins with positional or padding properties.
HEIGHT=131087;MINHEIGHT=131096;MAXHEIGHT=131094;WIDTH=131105
POSITION=131102;TOP=131104;BOTTOM=131080;LEFT=131089;RIGHT=131103
MARGIN_TOP=131093;MARGIN_BOTTOM=131090;MARGIN_LEFT=131091;MARGIN_RIGHT=131092
GROW=131084;SHRINK=131085;DIRECTION=131083;ALIGN=131073;JUSTIFY=131088;DISPLAY=131081

# Home order is name / number / portrait; away keeps portrait / number / name.
for name in ['HomePlayersListRow','HomeSubPlayersListRow','AwayPlayersListRow','AwaySubPlayersListRow']:
 d=Doc(M,name=name);portrait_binding=d.named('PrematchPlayerPortraitBinding');parent=d.a(portrait_binding)['m_Parent']['rid']
 if name.startswith('Home'):d.move(portrait_binding,parent)
 d.st(portrait_binding,[(MARGIN_TOP,d.px(0)),(MARGIN_BOTTOM,d.px(0)),(MARGIN_LEFT,d.px(5)),(MARGIN_RIGHT,d.px(5))]);d.save()

# Paint the portrait before the rating/name subtree while retaining visual order.
d=Doc(G,name='TacticsMatchPositionFilled')
d.a(1005)['m_Children']=[{'rid':1008},{'rid':1007}]
d.st(1005,[(DIRECTION,d.enum('column'))])
d.st(1008,[(HEIGHT,d.px(32)),(MINHEIGHT,d.px(32)),(MAXHEIGHT,d.px(32)),(GROW,d.num(0)),(SHRINK,d.num(0))])
d.size(1017,32,32);pb=d.named('MatchPlayerPortraitBinding');d.size(pb,32,32)
d.st(1017,[(MARGIN_TOP,d.px(0)),(MARGIN_BOTTOM,d.px(0)),(MARGIN_LEFT,d.px(0)),(MARGIN_RIGHT,d.px(0))])
d.st(1007,[(GROW,d.num(0)),(SHRINK,d.num(0))]);d.st(1020,[(HEIGHT,d.px(16)),(MINHEIGHT,d.px(16)),(SHRINK,d.num(0))]);d.save()

# Anchor directly to the substitute group, including all expanded/collapsed breakpoints.
d=Doc(M,name='SquadOverview');host=d.named('MatchBottomTacticalToolbar')
d.a(host)['m_Classes']=[]
d.st(1009,[(POSITION,d.enum('relative'))])
d.st(host,[(POSITION,d.enum('absolute')),(BOTTOM,d.pct(100)),(LEFT,d.enum('auto')),(RIGHT,d.px(0)),(HEIGHT,d.px(32)),(MINHEIGHT,d.px(32)),(MAXHEIGHT,d.px(32)),(GROW,d.num(0)),(SHRINK,d.num(0)),(MARGIN_TOP,d.px(0)),(MARGIN_BOTTOM,d.px(0)),(MARGIN_LEFT,d.px(0)),(MARGIN_RIGHT,d.px(0)),(JUSTIFY,d.enum('flex-end'))])
def duplicate(i,parent,suffix):
 children=list(d.a(i)['m_Children']);a=copy.deepcopy(d.a(i));name=d.data(i).get('name','')
 new=d.add(d,i,parent,name+suffix);d.a(new)['m_RuleIndex']=a['m_RuleIndex'];d.a(new)['m_Classes']=a['m_Classes']
 for c in children:duplicate(c['rid'],new,suffix)
 return new
for index,(sub,variant) in enumerate([(1038,'Expanded'),(1041,'ExpandedSmall'),(1032,'Collapsed'),(1035,'CollapsedSmall')]):
 parent=d.a(sub)['m_Parent']['rid'];original=copy.deepcopy(d.a(sub));wrapper=ve(d,parent,'MatchSubstitutesAnchor_'+variant)
 d.a(wrapper)['m_Classes']=copy.deepcopy(original['m_Classes']);d.a(wrapper)['m_RuleIndex']=original['m_RuleIndex']
 d.st(wrapper,[(POSITION,d.enum('relative')),(458768,d.enum('visible'))])
 d.move(sub,wrapper);d.a(sub)['m_Classes']=[c for c in d.a(sub)['m_Classes'] if not c.startswith('margin-left-')]
 d.st(sub,[(WIDTH,d.pct(100)),(MARGIN_LEFT,d.px(0))])
 if index==0:d.move(host,wrapper)
 else:duplicate(host,wrapper,'_'+variant)
d.save()

for name,icon,frame in [('SquadOverviewPlayerBlock',1070,1063),('SquadOverviewPlayerBlockSmall',1083,1061)]:
 d=Doc(W,name=name);role=d.named('MatchCardPositionBinding');rv=d.named('MatchCardRoleAndDuty');rt=d.named('MatchCardRoleAndDutyText');condition_root=d.named('MatchCondition_Available')
 # Reproduce the native role-cell context: selection index and possession are inputs.
 d.data(role).update(Mappings=[{'m_serialisedType':0,'from':key,'to':{'m_path':value},'type':{'id':0}} for key,value in [('tactic','match.Tactic'),('binding','playerinfo'),('teamselectionindex','playerinfo.PlayerTeamSelectionIndex'),('inpossession','const.True')]],Mappings_UxmlAttributeFlags=1)
 # Use the native current indexed IP-role lookup, without the former missing position scope.
 variables=d.data(rv)['ValueVariables']
 for var in variables:
  if var['m_name']=='roledata':
   data=json.loads(var['m_scopeValue']['m_serializedData'])
   for field in data['m_data']:
    if field['PropertyID']['id']==1349481322:field['BindingPath']='tactic.IPRole'
    elif field['PropertyID']['id']==1265792339:field['BindingPath']='inpossession'
   var['m_scopeValue']['m_serializedData']=json.dumps(data,separators=(',',':'))
 d.move(role,1016);d.st(role,[(HEIGHT,d.px(16)),(MINHEIGHT,d.px(16)),(MAXHEIGHT,d.px(16)),(SHRINK,d.num(0)),(MARGIN_TOP,d.px(0)),(MARGIN_BOTTOM,d.px(0))])
 d.st(rv,[(GROW,d.num(1)),(MINHEIGHT,d.px(16)),(WIDTH,d.pct(100))]);d.st(rt,[(HEIGHT,d.px(16)),(MINHEIGHT,d.px(16)),(WIDTH,d.pct(100)),(65546,d.enum('middle-center')),(65552,d.enum('nowrap'))])
 # Keep the original injury branch; hide only the obsolete normal-condition heart.
 d.st(icon,[(DISPLAY,d.enum('none'))]);d.move(condition_root,1032,0)
 d.st(condition_root,[(POSITION,d.enum('relative')),(LEFT,d.px(0)),(TOP,d.px(0)),(MARGIN_TOP,d.px(0)),(MARGIN_BOTTOM,d.px(0)),(MARGIN_LEFT,d.px(0)),(MARGIN_RIGHT,d.px(0))]);d.size(condition_root,28,32)
 for i,x in list(d.r.items()):
  if 'm_Parent' not in x.get('data',{}):continue
  node_name=d.data(i).get('name','')
  if node_name.startswith('MatchCondition_') and ('_Ring' in node_name or node_name.endswith('MissingRing')):d.size(i,20,20)
 # Original card height: 32 header + (64 portrait/name + 34 condition/rating + 16 role + 6 padding).
 d.st(1016,[(HEIGHT,d.px(120)),(MINHEIGHT,d.px(120)),(MAXHEIGHT,d.px(120)),(JUSTIFY,d.enum('flex-start')),(262151,[d.px(0),d.px(8),d.px(6),d.px(8)])])
 d.st(1021,[(HEIGHT,d.px(64)),(MINHEIGHT,d.px(64)),(SHRINK,d.num(0)),(JUSTIFY,d.enum('space-between'))]);d.st(1028,[(HEIGHT,d.px(44)),(MINHEIGHT,d.px(44)),(SHRINK,d.num(0))]);d.st(1029,[(HEIGHT,d.px(20)),(MINHEIGHT,d.px(20)),(SHRINK,d.num(0))])
 d.st(1022,[(HEIGHT,d.px(34)),(MINHEIGHT,d.px(34)),(SHRINK,d.num(0)),(MARGIN_TOP,d.px(0)),(MARGIN_BOTTOM,d.px(0)),(262151,[d.px(0)])])
 d.st(1031,[(HEIGHT,d.px(1)),(MINHEIGHT,d.px(1)),(MAXHEIGHT,d.px(1)),(MARGIN_BOTTOM,d.px(0)),(MARGIN_TOP,d.px(0)),(SHRINK,d.num(0))]);d.st(1032,[(HEIGHT,d.px(33)),(MINHEIGHT,d.px(33)),(ALIGN,d.enum('center')),(JUSTIFY,d.enum('space-between')),(SHRINK,d.num(0))])
 d.save()

# Let the match grid consume the remaining height, with the natural footer kept intact.
d=Doc(M,name='OverviewPrototype');d.st(1002,[(MINHEIGHT,d.px(0)),(GROW,d.num(1)),(SHRINK,d.num(1))]);d.st(1004,[(GROW,d.num(0)),(SHRINK,d.num(0))]);d.save()

# No new assets or references: keep catalog/preload metadata byte-identical.
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changes[n]:assert sha(check[i].get_raw_data())==h,('unrelated object modified',n,i)
 for i,data in changes[n].items():assert check[i].read_typetree()==data,('roundtrip failed',n,i)
 for d in [d for d in documents if d.n==n]:validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
 (OUT/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'changes':{n:{str(pid):d.get('m_Name','') for pid,d in ps.items()} for n,ps in changes.items()},'home_portrait_after_number':True,'highlight_avatar_painted_before_rating':True,'toolbar_height':32,'toolbar_out_of_flow':True,'toolbar_alignment':'right:0 relative to substitute group in all four breakpoint/expansion variants','card_body_height':120,'condition_in_rating_row':True,'native_condition_heart_hidden':True,'role_below_rating':True,'role_binding':'tactic.IPRole with playerinfo.PlayerTeamSelectionIndex and inpossession=True','before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[],'unrelated_objects_unchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for n in ['install.ps1','restore.ps1']:(OUT/n).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/n).read_bytes())
print(json.dumps({'prepared':True,'output':str(OUT),'changed_objects':{n:len(x) for n,x in changes.items()}},ensure_ascii=False))
